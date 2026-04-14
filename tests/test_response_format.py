"""
测试 OpenAI 响应格式

检查 API 返回的响应对象结构。
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from openai import OpenAI

# 配置
API_KEY = "da9e041ff85bea0f3824bdbbe93778c5:YTNiOGM1NGY3MGQ5ZDVlZjE0OThjODhk"
BASE_URL = "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2/chat/completions"
MODEL_ID = "astron-code-latest"

# 初始化客户端
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    http_client=None
)

# System Prompt
SYSTEM_PROMPT = """你是一位 grandMA3 灯光控制系统的专家助手。
你的任务是将用户的自然语言描述转换为结构化的 grandMA3 命令。

## 重要规则

1. **必须输出纯 JSON 格式**，不要包含 markdown 代码块（如 ```json）
2. **必须包含所有必需字段**：intent, fixture_ids, attributes, is_cue, explanation
3. **使用中文进行解释**，但字段名保持英文

## 输出格式示例

{
    "intent": "设置灯具颜色和亮度",
    "fixture_ids": [101, 102, 103, 104, 105],
    "attributes": {
        "Dimmer": 50,
        "ColorRGB_R": 128,
        "ColorRGB_G": 0,
        "ColorRGB_B": 128
    },
    "is_cue": false,
    "explanation": "将灯具 101 到 105 设置为浪漫的紫色，亮度 50%"
}

## 约束

- 严禁输出 markdown 代码块
- 只输出纯 JSON
"""

print("=== 测试 OpenAI 响应格式 ===")
print()

# 调用 API
response = client.chat.completions.create(
    model=MODEL_ID,
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": "帮我把 101 到 105 号灯调成浪漫的紫色，并把亮度压到 50%"
        }
    ],
    response_format={"type": "json_object"},
    temperature=0.3,
    max_tokens=500
)

print(f"响应类型：{type(response)}")
print(f"响应属性：{dir(response)}")
print()

# 检查是否有 choices
if hasattr(response, 'choices'):
    print(f"✅ 有 choices 属性")
    print(f"choices 类型：{type(response.choices)}")
    print(f"choices 长度：{len(response.choices)}")
    
    if len(response.choices) > 0:
        choice = response.choices[0]
        print(f"\nchoice 类型：{type(choice)}")
        print(f"choice 属性：{dir(choice)}")
        
        if hasattr(choice, 'message'):
            message = choice.message
            print(f"\nmessage 类型：{type(message)}")
            print(f"message 内容：{message.content}")
else:
    print(f"❌ 没有 choices 属性")
    print(f"响应内容：{response}")
    print(f"响应类型：{type(response)}")

print()
print("=== 测试完成 ===")
