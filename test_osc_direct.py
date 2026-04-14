#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试脚本 - 直接发送 OSC 命令到 grandMA3
"""

import time
from pythonosc import udp_client

def send_command(host, port, command):
    """
    发送 OSC 命令到 grandMA3
    
    Args:
        host: OSC 服务器地址
        port: OSC 端口
        command: 命令字符串
    """
    print(f"🚀 准备发送命令到 {host}:{port}")
    print(f"📝 命令：{command}")
    
    try:
        # 创建 UDP 客户端
        client = udp_client.SimpleUDPClient(host, port)
        
        # 发送命令
        print(f"📤 发送 OSC 消息...")
        client.send_message("/cmd", command)
        
        print(f"✅ 命令已发送！")
        
        # 等待一小段时间
        time.sleep(0.1)
        
        # 关闭连接（python-osc 没有 close 方法，直接删除引用）
        del client
        
        return True
        
    except Exception as e:
        print(f"❌ 发送失败：{e}")
        return False

if __name__ == "__main__":
    # 配置
    HOST = "127.0.0.1"
    PORT = 8000
    
    # 测试命令
    commands = [
        "ClearAll",
        'Fixture 1 At Preset "Color"."Yellow"'
    ]
    
    print("=" * 60)
    print("🎭 grandMA3 OSC 独立测试脚本")
    print("=" * 60)
    
    # 发送每条命令
    for i, cmd in enumerate(commands, 1):
        print(f"\n📌 测试 {i}/{len(commands)}")
        print("-" * 60)
        
        success = send_command(HOST, PORT, cmd)
        
        if success:
            print(f"✅ 测试 {i} 成功")
        else:
            print(f"❌ 测试 {i} 失败")
        
        # 命令之间延迟
        if i < len(commands):
            print(f"⏱️  等待 0.1 秒...")
            time.sleep(0.1)
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)
