"""
grandMA3 语义解析器

将自然语言转换为结构化的 grandMA3 命令。
使用 OpenAI API 进行语义理解和指令生成。
"""

import json
import logging
import re
import os
from typing import Optional
from openai import OpenAI
import httpx

from .models import GMA3Command, TranslationResult


class CommandTranslator:
    """
    grandMA3 命令翻译器
    
    使用 LLM 将自然语言转换为结构化的 grandMA3 命令。
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_id: str = "astron-code-latest",
        trust_env: bool = True,
        proxy_url: Optional[str] = None,
    ):
        """
        初始化翻译器
        
        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model_id: 模型 ID
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_id = model_id
        self.trust_env = trust_env
        self.proxy_url = (proxy_url or "").strip() or None
        
        # 初始化 OpenAI 客户端
        proxy = self.proxy_url

        http_client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
            trust_env=bool(trust_env),
            proxies=proxy,
        )
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client,
        )
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # System Prompt - 告知 AI 它是 grandMA3 专家
        self.system_prompt = """你是一位 grandMA3 灯光控制系统的专家助手。
你的任务是将用户的自然语言描述转换为结构化的 grandMA3 命令。

## 重要规则

1. **必须输出纯 JSON 格式**，不要包含 markdown 代码块（如 ```json）
2. **必须包含所有必需字段**：intent, actions, is_cue, explanation
3. **使用中文进行解释**，但字段名保持英文
4. **数值类型正确**：Dimmer 使用 0-100，RGB 通道使用 0-255
5. **支持多灯具多属性**：使用 actions 列表处理复杂场景

## 新数据结构说明

### actions 列表结构

**不要使用扁平的 fixture_ids 和 attributes**，而是使用 actions 列表：

```json
{
    "actions": [
        {
            "fixture_ids": [101, 102, 103],
            "attributes": {"Dimmer": 100, "Color": "Red"}
        },
        {
            "fixture_ids": [104, 105],
            "attributes": {"Dimmer": 75, "Color": "Blue"}
        }
    ]
}
```

### 使用场景

**场景 1：单一操作**（所有灯具相同属性）
- 用户输入："1 号灯变黄"
- 输出：`{"actions": [{"fixture_ids": [1], "attributes": {"Color": "Yellow"}}]}`

**场景 2：多组不同操作**（不同灯具不同属性）
- 用户输入："1 号灯变红，2 号灯变蓝"
- 输出：`{"actions": [{"fixture_ids": [1], "attributes": {"Color": "Red"}}, {"fixture_ids": [2], "attributes": {"Color": "Blue"}}]}`

**场景 3：范围 + 分组**（连续范围 + 不同颜色）
- 用户输入："101 到 103 号灯变红，104 到 105 号灯变蓝"
- 输出：`{"actions": [{"fixture_ids": [101, 102, 103], "attributes": {"Color": "Red"}}, {"fixture_ids": [104, 105], "attributes": {"Color": "Blue"}}]}`

**场景 4：渐变效果**（多个灯具不同亮度）
- 用户输入："1 号灯 100%，2 号灯 75%，3 号灯 50%"
- 输出：`{"actions": [{"fixture_ids": [1], "attributes": {"Dimmer": 100}}, {"fixture_ids": [2], "attributes": {"Dimmer": 75}}, {"fixture_ids": [3], "attributes": {"Dimmer": 50}}]}`

## 灯具 ID 识别

- 单个灯具："101 号灯" → [101]
- 连续范围："101 到 105 号灯" → [101, 102, 103, 104, 105]
- 多个灯具："1, 3, 5 号灯" → [1, 3, 5]
- 组："组 1" → 返回空列表（需要特殊处理）

## 属性识别

### 亮度相关
- "亮度 100%" / "全亮" → {"Dimmer": 100}
- "亮度 50%" / "半亮" → {"Dimmer": 50}
- "压到 50%" / "调暗到 50%" → {"Dimmer": 50}

### 颜色相关
- "红色" → {"Color": "Red"}
- "绿色" → {"Color": "Green"}
- "蓝色" → {"Color": "Blue"}
- "紫色" / "浪漫紫色" → {"Color": "Purple"}
- "黄色" → {"Color": "Yellow"}
- "白色" → {"Color": "White"}
- "忧郁的蓝色" → {"Color": "SadBlue"}

### 其他属性
- "存为 Cue" → is_cue: true

## grandMA3 OSC 核心语法指南（必须严格遵守）

### 1. 基础亮度 (Intensity)
**指令格式**：`Fixture [开始] Thru [结束] At [数值]`
**示例**：`Fixture 1 Thru 10 At 100`
**意思**：选中 1 到 10 号灯，亮度推到满（100%）
**注意**：MA3 里必须用 `Thru`，不能用横杠 `-`

### 2. 调用颜色预设 (Color Preset)
**指令格式**：`Fixture [开始] Thru [结束] At Preset "Color"."颜色名"`
**示例**：`Fixture 1 Thru 5 At Preset "Color"."Red"`
**意思**：选中 1 到 5 号灯，直接套用颜色池（Color Pool）里名字叫 Red 的预设
**优势**：这是最稳的做法，因为 AI 不需要知道具体的通道数值，只要名字对得上就行

### 3. 精确控制颜色属性 (Attribute)
**指令格式**：`Fixture [ID] Attribute "属性名" At 数值`
**示例**：`Fixture 201 Attribute "ColorRGB_R" At 100`
**意思**：只把 201 号灯的红色通道改成 100%
**注意**：属性名（如 ColorRGB_R）必须加双引号，否则控制台可能不认

### 4. 运行与停止程序 (Executor)
**指令格式**：`Go+ Executer [ID]` 或 `Off Executer [ID]`
**示例**：`Go+ Executer 101` 或 `Off Executer 101`
**意思**：触发或关闭 101 号推子（执行器）上的程序

### 5. 归位与清空 (Reset)
**指令**：`ClearAll`
**意思**：相当于按三次 Clear，把所有选中的灯和没存的动作全部清掉
**建议**：在每次发新动作前都先发一个 ClearAll

## 语法标准总结

- **范围选灯**：用 `Fixture [开始] Thru [结束]`
- **赋值**：用 `At`
- **颜色优先**：使用 `At Preset "Color"."颜色名"`
- **属性控制**：必须用 `Attribute "属性名" At 数值`

## 输出格式示例

### 示例 1：单一操作
```json
{
    "intent": "设置灯具颜色",
    "actions": [
        {
            "fixture_ids": [1],
            "attributes": {"Color": "Yellow"}
        }
    ],
    "is_cue": false,
    "explanation": "将 1 号灯设置为黄色"
}
```

### 示例 2：多组不同操作
```json
{
    "intent": "设置多组灯具的不同颜色",
    "actions": [
        {
            "fixture_ids": [101, 102, 103],
            "attributes": {"Color": "Red"}
        },
        {
            "fixture_ids": [104, 105],
            "attributes": {"Color": "Blue"}
        }
    ],
    "is_cue": false,
    "explanation": "将灯具 101-103 设置为红色，将灯具 104-105 设置为蓝色"
}
```

### 示例 3：渐变效果
```json
{
    "intent": "设置渐变亮度",
    "actions": [
        {
            "fixture_ids": [1],
            "attributes": {"Dimmer": 100}
        },
        {
            "fixture_ids": [2],
            "attributes": {"Dimmer": 75}
        },
        {
            "fixture_ids": [3],
            "attributes": {"Dimmer": 50}
        }
    ],
    "is_cue": false,
    "explanation": "将 1 号灯亮度设为 100%，2 号灯 75%，3 号灯 50%"
}
```

## 约束

- 严禁输出 markdown 代码块
- 只输出纯 JSON
- 确保 JSON 格式正确，可以被 Python json.loads() 解析
- 如果无法解析，返回空列表和错误说明
- **必须使用 actions 列表结构**，不要使用扁平的 fixture_ids 和 attributes
"""
    
    def translate(self, user_input: str) -> TranslationResult:
        """
        将自然语言翻译为 grandMA3 命令
        
        Args:
            user_input: 用户的自然语言输入
            
        Returns:
            TranslationResult: 翻译结果
        """
        try:
            self.logger.info(f"开始翻译：{user_input}")
            self.logger.info(f"API Base URL: {self.base_url}")
            self.logger.info(f"Model: {self.model_id}")
            
            # 调用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"请解析以下灯光控制需求：{user_input}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500
            )
            
            # 获取响应内容 - 处理不同的响应格式
            if hasattr(response, 'choices') and response.choices:
                raw_response = response.choices[0].message.content
            else:
                # 如果响应格式异常，尝试直接访问
                raw_response = str(response)
            
            if not raw_response:
                return TranslationResult(
                    success=False,
                    error="API 返回空响应"
                )
            
            # 🔍 增强：检测 HTML 响应（API 地址配置错误）
            raw_response_stripped = raw_response.strip()
            if raw_response_stripped.startswith('<!doctype html') or raw_response_stripped.startswith('<html'):
                self.logger.error(f"❌ API 返回了 HTML 响应，可能是 base_url 配置错误")
                self.logger.error(f"当前配置的 base_url: {self.base_url}")
                self.logger.error(f"响应内容前 500 字符：{raw_response_stripped[:500]}")
                return TranslationResult(
                    success=False,
                    error=f"API 地址无效或被拦截，返回了网页。请核实该模型的具体 API 路径版本（v1/v2/v4 等）。当前配置：{self.base_url}"
                )
            
            # 🔍 检测 JSON 错误响应
            if raw_response_stripped.startswith('{') and '"message"' in raw_response_stripped:
                try:
                    error_data = json.loads(raw_response)
                    if 'message' in error_data:
                        self.logger.error(f"❌ API 返回错误：{error_data['message']}")
                        return TranslationResult(
                            success=False,
                            error=f"API 错误：{error_data['message']}"
                        )
                except:
                    pass
            
            # 调试：打印原始响应
            self.logger.debug(f"原始响应：{raw_response[:200]}")
            
            # 尝试从响应中提取 JSON
            # 方法 1: 直接解析
            try:
                data = json.loads(raw_response)
                cleaned_response = raw_response
            except json.JSONDecodeError:
                # 方法 2: 查找 JSON 块
                json_match = re.search(r'\{.*?\}', raw_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(0)
                else:
                    return TranslationResult(
                        success=False,
                        error=f"无法从响应中提取 JSON: {raw_response[:200]}"
                    )
            
            if not cleaned_response:
                return TranslationResult(
                    success=False,
                    error="API 返回空响应"
                )
            
            # 清理响应（移除可能的 markdown 标记）
            cleaned_response = self._clean_response(cleaned_response)
            
            # 解析 JSON
            try:
                # 尝试标准解析
                data = json.loads(cleaned_response)
                
                # 验证并创建 GMA3Command 对象
                command = GMA3Command(**data)
                
                self.logger.info(f"翻译成功：{command.explanation}")
                
                return TranslationResult(
                    success=True,
                    command=command,
                    raw_response=cleaned_response
                )
                
            except json.JSONDecodeError as e:
                # 尝试修复常见的 JSON 格式问题
                try:
                    # 修复键名缺少引号的问题
                    # 匹配 {key: 或 , key: 格式并添加引号
                    fixed = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', cleaned_response)
                    data = json.loads(fixed)
                    
                    command = GMA3Command(**data)
                    self.logger.info(f"翻译成功（修复后）: {command.explanation}")
                    
                    return TranslationResult(
                        success=True,
                        command=command,
                        raw_response=fixed
                    )
                except Exception as fix_error:
                    self.logger.error(f"JSON 解析失败：{cleaned_response}")
                    self.logger.error(f"修复尝试失败：{fix_error}")
                    return TranslationResult(
                        success=False,
                        error=f"JSON 解析失败：{str(e)}"
                    )
                
        except Exception as e:
            self.logger.error(f"翻译失败：{str(e)}")
            import traceback
            traceback.print_exc()
            return TranslationResult(
                success=False,
                error=f"API 调用失败：{str(e)}"
            )
    
    def _clean_response(self, response: str) -> str:
        """
        清理响应，移除 markdown 代码块标记
        
        Args:
            response: 原始响应
            
        Returns:
            str: 清理后的响应
        """
        # 移除 ```json 和 ```
        response = response.strip()
        
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        return response.strip()
    
    def __repr__(self) -> str:
        """对象表示"""
        return f"CommandTranslator(model={self.model_id})"


# 快捷函数
def create_translator(
    api_key: str,
    base_url: str,
    model_id: str = "astron-code-latest",
    trust_env: bool = True,
    proxy_url: Optional[str] = None,
) -> CommandTranslator:
    """
    创建翻译器实例
    
    Args:
        api_key: API 密钥
        base_url: API 基础 URL
        model_id: 模型 ID
        
    Returns:
        CommandTranslator: 翻译器实例
    """
    return CommandTranslator(
        api_key=api_key,
        base_url=base_url,
        model_id=model_id,
        trust_env=trust_env,
        proxy_url=proxy_url,
    )


if __name__ == "__main__":
    # 模块测试代码
    import sys
    
    # 设置基础日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== CommandTranslator 模块测试 ===")
    print()
    
    # 创建翻译器
    print("1. 创建翻译器...")
    translator = create_translator(
        api_key="da9e041ff85bea0f3824bdbbe93778c5:YTNiOGM1NGY3MGQ5ZDVlZjE0OThjODhk",
        base_url="https://maas-coding-api.cn-huabei-1.xf-yun.com/v2/chat/completions",
        model_id="astron-code-latest"
    )
    print(f"   翻译器：{translator}")
    print()
    
    # 测试翻译
    print("2. 测试翻译...")
    
    test_inputs = [
        "帮我把 101 到 105 号灯调成浪漫的紫色，并把亮度压到 50%"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{i}. 输入：{user_input}")
        print("-" * 60)
        
        result = translator.translate(user_input)
        
        if result.success:
            print(f"✅ 翻译成功")
            print(f"\n解析结果:")
            print(f"  意图：{result.command.intent}")
            print(f"  灯具 ID: {result.command.fixture_ids}")
            print(f"  属性：{result.command.attributes}")
            print(f"  存为 Cue: {result.command.is_cue}")
            print(f"  解释：{result.command.explanation}")
        else:
            print(f"❌ 翻译失败：{result.error}")
        
        print()
    
    print("=== 测试完成 ===")
