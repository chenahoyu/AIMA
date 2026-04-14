"""
测试修复后的 JSON 解析

验证 JSON 解析逻辑是否正确。
"""

import json
import re

# 测试数据 - API 返回的 JSON 格式
test_json = '''{ "intent": "设置灯具颜色和亮度", "fixture_ids": [101, 102, 103, 104, 105], "attributes": { "Dimmer": 50, "ColorRGB_R": 128, "ColorRGB_G": 0, "ColorRGB_B": 128 }, "is_cue": false, "explanation": "将灯具 101 到 105 设置为浪漫的紫色，亮度 50%" }'''

print("=== JSON 解析测试 ===")
print()
print("原始 JSON:")
print(test_json)
print()

# 尝试标准解析
try:
    data = json.loads(test_json)
    print("✅ 标准解析成功!")
    print()
    print("解析结果:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
except json.JSONDecodeError as e:
    print(f"❌ 标准解析失败：{e}")
    print()
    
    # 尝试修复
    print("尝试修复...")
    fixed = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', test_json)
    print()
    print("修复后的 JSON:")
    print(fixed)
    print()
    
    try:
        data = json.loads(fixed)
        print("✅ 修复后解析成功!")
        print()
        print("解析结果:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e2:
        print(f"❌ 修复后解析失败：{e2}")

print()
print("="*60)
print("测试完成!")
print("="*60)
