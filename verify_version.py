#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本验证脚本 - 验证 v0.1-042201 版本的完整性和可用性
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(path: str, description: str) -> bool:
    """检查文件是否存在"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_directory_exists(path: str, description: str) -> bool:
    """检查目录是否存在"""
    exists = os.path.isdir(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_file_content(path: str, min_lines: int, description: str) -> bool:
    """检查文件内容是否有效"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        valid = len(lines) >= min_lines
        status = "✅" if valid else "❌"
        print(f"{status} {description}: {len(lines)} lines (min: {min_lines})")
        return valid
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def main():
    """主验证函数"""
    print("=" * 80)
    print("🔍 MA3 OSC 语义编程助手 - v0.1-042201 版本验证")
    print("=" * 80)
    print()
    
    project_root = Path(__file__).parent
    all_valid = True
    
    # 1. 检查核心文件
    print("📁 核心文件检查:")
    core_files = [
        ("app_complete.py", 500, "完整版应用"),
        ("app_simple.py", 100, "简化版应用"),
        ("config.py", 50, "配置管理"),
        ("requirements.txt", 10, "依赖列表"),
    ]
    
    for filename, min_lines, description in core_files:
        path = project_root / filename
        all_valid &= check_file_content(str(path), min_lines, description)
    
    print()
    
    # 2. 检查模块目录
    print("📦 模块目录检查:")
    module_dirs = [
        ("src/osc", "OSC 模块"),
        ("src/ai", "AI 模块"),
        ("src/utils", "工具模块"),
        ("tests", "测试目录"),
        ("docs", "文档目录"),
    ]
    
    for dirname, description in module_dirs:
        all_valid &= check_directory_exists(str(project_root / dirname), description)
    
    print()
    
    # 3. 检查核心模块文件
    print("📄 核心模块文件检查:")
    module_files = [
        ("src/osc/osc_client.py", 200, "OSC 客户端"),
        ("src/ai/translator.py", 100, "语义翻译器"),
        ("src/ai/models.py", 50, "数据模型"),
        ("src/utils/conversation_manager.py", 100, "对话管理器"),
        ("src/utils/api_key_cache.py", 100, "API Key 缓存"),
    ]
    
    for filename, min_lines, description in module_files:
        path = project_root / filename
        all_valid &= check_file_content(str(path), min_lines, description)
    
    print()
    
    # 4. 检查配置文件
    print("⚙️ 配置文件检查:")
    config_files = [
        (".env", 5, "环境变量配置"),
        (".env.example", 5, "环境变量示例"),
        ("TECH_STACK.md", 50, "技术栈文档"),
        ("VERSION_0.1-042201.md", 50, "版本说明"),
    ]
    
    for filename, min_lines, description in config_files:
        path = project_root / filename
        all_valid &= check_file_content(str(path), min_lines, description)
    
    print()
    
    # 5. 检查备份文件
    print("💾 备份文件检查:")
    backup_file = project_root / "backup" / "v0.1-042201.tar.gz"
    all_valid &= check_file_exists(str(backup_file), "版本备份")
    
    print()
    
    # 6. 检查缓存和对话目录（可选）
    print("💾 数据目录检查（可选）:")
    data_dirs = [
        (".api_cache", "API Key 缓存目录"),
        (".conversations", "对话历史目录"),
    ]
    
    for dirname, description in data_dirs:
        path = project_root / dirname
        exists = os.path.exists(path)
        status = "✅" if exists else "⚠️"
        print(f"{status} {description}: {path} (不存在则忽略)")
    
    print()
    
    # 7. 总结
    print("=" * 80)
    if all_valid:
        print("✅ 版本验证通过！所有核心文件完整可用。")
        print()
        print("📦 版本信息:")
        print(f"   版本：v0.1-042201")
        print(f"   备份：{backup_file}")
        print(f"   大小：{backup_file.stat().st_size / 1024:.1f} KB")
        print()
        print("🚀 使用方法:")
        print("   1. 解压备份：tar -xzf backup/v0.1-042201.tar.gz -C /tmp/")
        print("   2. 运行应用：streamlit run app_complete.py")
        print("   3. 访问应用：http://localhost:8502")
    else:
        print("❌ 版本验证失败！请检查缺失的文件。")
        sys.exit(1)
    
    print("=" * 80)

if __name__ == "__main__":
    main()
