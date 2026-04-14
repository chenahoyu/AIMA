#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整调试脚本 - 测试所有组件
"""

import sys
sys.path.insert(0, '/Users/chenhaoyu/AI-MA')

from config import settings
from src.osc.osc_client import GMA3Client, create_gma3_client

print("=" * 80)
print("🔍 完整调试脚本")
print("=" * 80)

# 1. 检查配置
print("\n1️⃣ 检查配置...")
print(f"   ma3_osc_host: {settings.ma3_osc_host}")
print(f"   ma3_osc_port: {settings.ma3_osc_port}")
print(f"   base_dir: {settings.base_dir}")
print("   ✅ 配置检查完成")

# 2. 创建客户端
print("\n2️⃣ 创建客户端...")
client = create_gma3_client()
print(f"   客户端：{client}")
print(f"   host: {client.host}")
print(f"   port: {client.port}")
print(f"   connected: {client.connected}")
print(f"   client: {client.client}")
print("   ✅ 客户端创建完成")

# 3. 测试连接
print("\n3️⃣ 测试连接...")
try:
    result = client.connect()
    print(f"   connect() 返回：{result}")
    print(f"   connected: {client.connected}")
    print(f"   client: {client.client}")
    print("   ✅ 连接测试完成")
except Exception as e:
    print(f"   ❌ 连接失败：{e}")
    import traceback
    traceback.print_exc()

# 4. 测试发送命令
print("\n4️⃣ 测试发送命令...")
if client.connected:
    try:
        success, message = client.send_command("ClearAll")
        print(f"   send_command 返回：(success={success}, message={message})")
        print("   ✅ 命令发送测试完成")
    except Exception as e:
        print(f"   ❌ 命令发送失败：{e}")
        import traceback
        traceback.print_exc()
else:
    print("   ⚠️  客户端未连接，跳过命令发送测试")

# 5. 清理
print("\n5️⃣ 清理...")
try:
    client.disconnect()
    print("   ✅ 断开连接成功")
except Exception as e:
    print(f"   ⚠️  断开连接失败：{e}")

print("\n" + "=" * 80)
print("🎉 调试完成！")
print("=" * 80)
