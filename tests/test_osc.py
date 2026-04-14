"""
OSC 通信测试脚本

用于验证 Python 与 grandMA3 之间的 OSC 通信通路。
运行此脚本将发送测试命令到 grandMA3，验证连接是否正常。

使用方法:
    cd /Users/chenhaoyu/AI-MA
    source venv/bin/activate
    python tests/test_osc.py

注意:
    - 确保 grandMA3 正在运行
    - 确保 grandMA3 的 OSC 端口已启用（默认 8000）
    - 确保 IP 地址配置正确（默认 127.0.0.1）
"""

import sys
import time
import logging

# 添加 src 目录到路径
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from osc.osc_client import GMA3Client, create_gma3_client


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def test_basic_connection():
    """测试基本连接"""
    print("\n" + "="*60)
    print("测试 1: 基本连接测试")
    print("="*60)
    
    client = create_gma3_client()
    
    print(f"客户端配置:")
    print(f"  主机：{client.host}")
    print(f"  端口：{client.port}")
    print()
    
    success = client.connect()
    
    if success:
        print("✅ 连接成功!")
        print(f"   连接时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(client.connection_time))}")
    else:
        print("❌ 连接失败!")
        print("   请检查:")
        print("   1. grandMA3 是否正在运行")
        print("   2. OSC 端口是否已启用")
        print("   3. IP 地址配置是否正确")
    
    return client if success else None


def test_fixture_control(client: GMA3Client):
    """测试灯具控制"""
    print("\n" + "="*60)
    print("测试 2: 灯具控制测试")
    print("="*60)
    
    test_cases = [
        {
            "name": "设置灯具 1 亮度 100%",
            "func": lambda: client.set_fixture_dimmer(1, 100),
            "expected": "Fixture 1 At 100"
        },
        {
            "name": "设置灯具 2 亮度 50%",
            "func": lambda: client.set_fixture_dimmer(2, 50),
            "expected": "Fixture 2 At 50"
        },
        {
            "name": "设置灯具 3 红色",
            "func": lambda: client.set_fixture_color(3, 255, 0, 0),
            "expected": "Fixture 3 RGB(255,0,0)"
        },
        {
            "name": "设置灯具 4 绿色",
            "func": lambda: client.set_fixture_color(4, 0, 255, 0),
            "expected": "Fixture 4 RGB(0,255,0)"
        },
        {
            "name": "设置灯具 5 蓝色",
            "func": lambda: client.set_fixture_color(5, 0, 0, 255),
            "expected": "Fixture 5 RGB(0,0,255)"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   预期：{test_case['expected']}")
        
        result = test_case['func']()
        
        if result:
            print(f"   ✅ 发送成功")
        else:
            print(f"   ❌ 发送失败")
        
        time.sleep(0.5)  # 短暂延迟
    
    print("\n✅ 灯具控制测试完成!")


def test_group_control(client: GMA3Client):
    """测试组控制"""
    print("\n" + "="*60)
    print("测试 3: 组控制测试")
    print("="*60)
    
    test_cases = [
        {
            "name": "设置组 1 亮度 100%",
            "func": lambda: client.group_at(1, 100)
        },
        {
            "name": "设置组 1 亮度 50%",
            "func": lambda: client.group_at(1, 50)
        },
        {
            "name": "设置组 2 亮度 75%",
            "func": lambda: client.group_at(2, 75)
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        result = test_case['func']()
        
        if result:
            print(f"   ✅ 发送成功")
        else:
            print(f"   ❌ 发送失败")
        
        time.sleep(0.5)
    
    print("\n✅ 组控制测试完成!")


def test_preset_control(client: GMA3Client):
    """测试预设控制"""
    print("\n" + "="*60)
    print("测试 4: 预设控制测试")
    print("="*60)
    
    test_cases = [
        {
            "name": "执行预设 1.1",
            "func": lambda: client.preset_go("1.1")
        },
        {
            "name": "执行预设 1.2",
            "func": lambda: client.preset_go("1.2")
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        result = test_case['func']()
        
        if result:
            print(f"   ✅ 发送成功")
        else:
            print(f"   ❌ 发送失败")
        
        time.sleep(0.5)
    
    print("\n✅ 预设控制测试完成!")


def test_sequence_control(client: GMA3Client):
    """测试序列控制"""
    print("\n" + "="*60)
    print("测试 5: 序列控制测试")
    print("="*60)
    
    test_cases = [
        {
            "name": "执行序列 1 Go+",
            "func": lambda: client.go_plus(1)
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        result = test_case['func']()
        
        if result:
            print(f"   ✅ 发送成功")
        else:
            print(f"   ❌ 发送失败")
        
        time.sleep(0.5)
    
    print("\n✅ 序列控制测试完成!")


def test_clear_all(client: GMA3Client):
    """测试清除所有"""
    print("\n" + "="*60)
    print("测试 6: 清除所有测试")
    print("="*60)
    
    print("\n发送 ClearAll 命令...")
    result = client.clear_all()
    
    if result:
        print("✅ ClearAll 发送成功")
    else:
        print("❌ ClearAll 发送失败")
    
    print("\n✅ 清除所有测试完成!")


def show_statistics(client: GMA3Client):
    """显示统计信息"""
    print("\n" + "="*60)
    print("统计信息")
    print("="*60)
    
    status = client.get_status()
    
    print(f"\n连接状态：{'✅ 已连接' if status['connected'] else '❌ 未连接'}")
    print(f"主机：{status['host']}:{status['port']}")
    print(f"连接时间：{status['connection_time']}")
    print(f"\n命令统计:")
    print(f"  发送成功：{status['stats']['commands_sent']}")
    print(f"  发送失败：{status['stats']['commands_failed']}")
    print(f"  连接次数：{status['stats']['connections']}")
    print(f"  错误次数：{status['stats']['errors']}")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("AI-MA OSC 通信测试")
    print("="*60)
    print("\n此脚本将测试与 grandMA3 的 OSC 通信通路")
    print("请确保 grandMA3 正在运行并监听 OSC 端口")
    print()
    
    # 设置日志
    setup_logging()
    
    # 测试 1: 基本连接
    client = test_basic_connection()
    
    if not client:
        print("\n❌ 连接测试失败，终止测试")
        sys.exit(1)
    
    # 测试 2-6: 各种控制功能
    try:
        test_fixture_control(client)
        test_group_control(client)
        test_preset_control(client)
        test_sequence_control(client)
        test_clear_all(client)
        
        # 显示统计
        show_statistics(client)
        
        # 断开连接
        print("\n" + "="*60)
        print("测试完成!")
        print("="*60)
        print("\n正在断开连接...")
        client.disconnect()
        print("✅ 已断开连接")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        client.disconnect()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
        client.disconnect()
        sys.exit(1)


if __name__ == "__main__":
    main()
