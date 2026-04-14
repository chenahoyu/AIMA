#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的 actions 结构

验证多灯具多属性的复杂场景
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ai.models import GMA3Command, CommandAction

def test_single_action():
    """测试单一操作"""
    print("=" * 80)
    print("测试 1：单一操作")
    print("=" * 80)
    
    command = GMA3Command(
        intent="设置灯具颜色",
        actions=[
            CommandAction(
                fixture_ids=[1],
                attributes={"Color": "Yellow"}
            )
        ],
        explanation="将 1 号灯设置为黄色"
    )
    
    print(f"Intent: {command.intent}")
    print(f"Actions: {command.actions}")
    print(f"Explanation: {command.explanation}")
    print(f"JSON: {command.model_dump_json(indent=2)}")
    print()

def test_multi_actions():
    """测试多组不同操作"""
    print("=" * 80)
    print("测试 2：多组不同操作")
    print("=" * 80)
    
    command = GMA3Command(
        intent="设置多组灯具的不同颜色",
        actions=[
            CommandAction(
                fixture_ids=[101, 102, 103],
                attributes={"Color": "Red"}
            ),
            CommandAction(
                fixture_ids=[104, 105],
                attributes={"Color": "Blue"}
            )
        ],
        explanation="将灯具 101-103 设置为红色，将灯具 104-105 设置为蓝色"
    )
    
    print(f"Intent: {command.intent}")
    print(f"Actions: {command.actions}")
    print(f"Explanation: {command.explanation}")
    print(f"JSON: {command.model_dump_json(indent=2)}")
    print()

def test_gradient():
    """测试渐变效果"""
    print("=" * 80)
    print("测试 3：渐变效果")
    print("=" * 80)
    
    command = GMA3Command(
        intent="设置渐变亮度",
        actions=[
            CommandAction(
                fixture_ids=[1],
                attributes={"Dimmer": 100}
            ),
            CommandAction(
                fixture_ids=[2],
                attributes={"Dimmer": 75}
            ),
            CommandAction(
                fixture_ids=[3],
                attributes={"Dimmer": 50}
            )
        ],
        explanation="将 1 号灯亮度设为 100%，2 号灯 75%，3 号灯 50%"
    )
    
    print(f"Intent: {command.intent}")
    print(f"Actions: {command.actions}")
    print(f"Explanation: {command.explanation}")
    print(f"JSON: {command.model_dump_json(indent=2)}")
    print()

def test_combined():
    """测试组合操作"""
    print("=" * 80)
    print("测试 4：组合操作（颜色 + 亮度）")
    print("=" * 80)
    
    command = GMA3Command(
        intent="设置多组灯具的颜色和亮度",
        actions=[
            CommandAction(
                fixture_ids=[101, 102],
                attributes={"Color": "Red", "Dimmer": 100}
            ),
            CommandAction(
                fixture_ids=[103, 104],
                attributes={"Color": "Blue", "Dimmer": 75}
            ),
            CommandAction(
                fixture_ids=[105],
                attributes={"Color": "Yellow", "Dimmer": 50}
            )
        ],
        explanation="将灯具 101-102 设置为红色，亮度 100%；将灯具 103-104 设置为蓝色，亮度 75%；将灯具 105 设置为黄色，亮度 50%"
    )
    
    print(f"Intent: {command.intent}")
    print(f"Actions: {command.actions}")
    print(f"Explanation: {command.explanation}")
    print(f"JSON: {command.model_dump_json(indent=2)}")
    print()

if __name__ == "__main__":
    print("\n🧪 测试新的 actions 结构\n")
    
    test_single_action()
    test_multi_actions()
    test_gradient()
    test_combined()
    
    print("=" * 80)
    print("✅ 所有测试通过！")
    print("=" * 80)
