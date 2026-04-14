"""
测试 API 调用方式

检查正确的 API 调用方式。
"""

import json
import requests

# API 配置
API_KEY = "da9e041ff85bea0f3824bdbbe93778c5:YTNiOGM1NGY3MGQ5ZDVlZjE0OThjODhk"
BASE_URL = "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2/chat/completions"
MODEL_ID = "astron-code-latest"

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

print("=== API 测试 ===")
print()

payload = {
    "model": MODEL_ID,
    "messages": [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": "帮我把 101 到 105 号灯调成浪漫的紫色，并把亮度压到 50%"
        }
    ],
    "temperature": 0.3,
    "max_tokens": 500
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

print(f"URL: {BASE_URL}")
print(f"Headers: {headers}")
print()

try:
    response = requests.post(
        BASE_URL,
        json=payload,
        headers=headers,
        timeout=30
    )
    
    print(f"状态码：{response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API 调用成功!")
        
        # 提取内容
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            print()
            print("提取的内容:")
            print("-" * 60)
            print(content)
            print("-" * 60)
            
            # 尝试解析 JSON
            try:
                import re
                json_match = re.search(r'\{.*?\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    parsed = json.loads(json_str)
                    print()
                    print("✅ JSON 解析成功!")
                    print()
                    print("解析结果:")
                    print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except Exception as e:
                print()
                print(f"❌ JSON 解析失败：{e}")
        else:
            print("❌ 响应格式异常")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
    else:
        print("❌ API 调用失败!")
        print("响应内容:")
        print("-" * 60)
        print(response.text[:500])
        print("-" * 60)
        
except Exception as e:
    print(f"❌ 请求失败：{e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)
print("测试完成!")
print("="*60)
