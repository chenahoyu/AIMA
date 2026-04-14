"""
快速连接测试脚本

测试 OSC 连接是否正常工作。
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from osc.osc_client import create_gma3_client
from config import settings


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("快速连接测试")
    print("="*60)
    print()
    
    # 获取配置
    host = settings.ma3_osc_host
    port = settings.ma3_osc_port
    prefix = settings.ma3_osc_prefix
    
    print(f"配置信息:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Prefix: {prefix}")
    print()
    
    # 创建客户端
    print("1. 创建 OSC 客户端...")
    client = create_gma3_client(host=host, port=port)
    print(f"   ✅ 客户端创建成功")
    print(f"   目标：{host}:{port}")
    print()
    
    # 测试连接
    print("2. 测试连接...")
    print()
    
    # 测试命令列表
    test_commands = [
        "Test",
        "ClearAll",
        "Fixture 1 At 0",
        "Fixture 1 At 100"
    ]
    
    success_count = 0
    fail_count = 0
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"   {i}. 发送命令：{cmd}")
        
        try:
            result = client.send_command(cmd)
            
            if result:
                print(f"      ✅ 发送成功")
                success_count += 1
            else:
                print(f"      ❌ 发送失败")
                fail_count += 1
                
        except Exception as e:
            print(f"      ❌ 异常：{e}")
            fail_count += 1
        
        print()
    
    # 统计结果
    print("="*60)
    print("测试结果:")
    print(f"  总命令数：{len(test_commands)}")
    print(f"  成功数：{success_count}")
    print(f"  失败数：{fail_count}")
    print(f"  成功率：{success_count/len(test_commands)*100:.1f}%")
    print("="*60)
    print()
    
    if success_count > 0:
        print("✅ OSC 连接正常！")
    else:
        print("❌ OSC 连接失败！")
        print()
        print("可能的原因:")
        print("  1. grandMA3 未启动")
        print("  2. OSC 端口配置错误")
        print("  3. 防火墙阻止连接")
        print("  4. grandMA3 未启用 OSC 服务")
    
    print()


if __name__ == "__main__":
    main()
