"""
语义解析器测试脚本

测试 LLM 将自然语言转换为 grandMA3 命令的能力。
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from ai.translator import CommandTranslator, create_translator


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("AI-MA 语义解析器测试")
    print("="*60)
    print()
    
    # 创建翻译器
    print("1. 创建翻译器...")
    translator = create_translator(
        api_key="da9e041ff85bea0f3824bdbbe93778c5:YTNiOGM1NGY3MGQ5ZDVlZjE0OThjODhk",
        base_url="https://maas-coding-api.cn-huabei-1.xf-yun.com/v2/chat/completions",
        model_id="astron-code-latest"
    )
    print(f"   ✅ 翻译器创建成功")
    print(f"   模型：{translator.model_id}")
    print()
    
    # 测试输入
    print("2. 测试语义解析...")
    print()
    
    test_cases = [
        {
            "name": "测试 1: 浪漫紫色 + 亮度 50%",
            "input": "帮我把 101 到 105 号灯调成浪漫的紫色，并把亮度压到 50%"
        },
        {
            "name": "测试 2: 忧郁的蓝色",
            "input": "来个忧郁的蓝色"
        },
        {
            "name": "测试 3: 单个灯具全亮",
            "input": "把 1 号灯调到全亮"
        },
        {
            "name": "测试 4: 单个灯具红色",
            "input": "设置 3 号灯为红色"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"{test_case['name']}")
        print(f"{'='*60}")
        print(f"输入：{test_case['input']}")
        print()
        
        # 执行翻译
        result = translator.translate(test_case['input'])
        
        if result.success:
            print("✅ 解析成功!")
            print()
            print("解析结果 (Pydantic 对象):")
            print("-" * 60)
            print(f"intent: {result.command.intent}")
            print(f"fixture_ids: {result.command.fixture_ids}")
            print(f"attributes: {result.command.attributes}")
            print(f"is_cue: {result.command.is_cue}")
            print(f"explanation: {result.command.explanation}")
            print("-" * 60)
            print()
            
            # 显示 JSON 格式
            print("JSON 格式:")
            print("-" * 60)
            print(result.command.model_dump_json(indent=2, ensure_ascii=False))
            print("-" * 60)
            
        else:
            print(f"❌ 解析失败：{result.error}")
            if result.raw_response:
                print()
                print("原始响应:")
                print("-" * 60)
                print(result.raw_response[:300])
                print("-" * 60)
        
        print()
        print()
    
    print("="*60)
    print("测试完成!")
    print("="*60)


if __name__ == "__main__":
    main()
