"""
对话记录管理模块

提供对话的保存、加载、删除和重命名功能。
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class ConversationManager:
    """对话管理器"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        初始化对话管理器
        
        Args:
            storage_dir: 存储目录，默认为项目根目录下的 .conversations
        """
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent / ".conversations"
        
        self.storage_dir = storage_dir
        self.storage_file = storage_dir / "conversations.json"
        
        # 确保存储目录存在
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载对话列表
        self.conversations = self._load_conversations()
    
    def _load_conversations(self) -> Dict[str, Dict[str, Any]]:
        """
        从文件加载对话列表
        
        Returns:
            对话字典 {conversation_id: conversation_data}
        """
        if not self.storage_file.exists():
            return {}
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 转换格式
            conversations = {}
            for conv_id, conv_data in data.items():
                conversations[conv_id] = conv_data
            
            return conversations
            
        except Exception as e:
            print(f"❌ 读取对话文件失败：{e}")
            return {}
    
    def _save_conversations(self):
        """保存对话列表到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存对话文件失败：{e}")
    
    def create_conversation(self, title: Optional[str] = None) -> str:
        """
        创建新对话
        
        Args:
            title: 对话标题（可选）
            
        Returns:
            对话 ID
        """
        conv_id = str(uuid.uuid4())
        
        # 生成默认标题
        if not title:
            title = f"对话 {len(self.conversations) + 1}"
        
        self.conversations[conv_id] = {
            "id": conv_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        self._save_conversations()
        return conv_id
    
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """
        获取对话
        
        Args:
            conv_id: 对话 ID
            
        Returns:
            对话数据或 None
        """
        return self.conversations.get(conv_id)
    
    def add_message(self, conv_id: str, role: str, content: str):
        """
        添加消息到对话
        
        Args:
            conv_id: 对话 ID
            role: 角色（user/assistant/system）
            content: 消息内容
        """
        if conv_id not in self.conversations:
            return
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversations[conv_id]["messages"].append(message)
        self.conversations[conv_id]["updated_at"] = datetime.now().isoformat()
        self._save_conversations()
    
    def get_messages(self, conv_id: str) -> List[Dict[str, Any]]:
        """
        获取对话消息列表
        
        Args:
            conv_id: 对话 ID
            
        Returns:
            消息列表
        """
        conv = self.get_conversation(conv_id)
        if conv:
            return conv.get("messages", [])
        return []
    
    def clear_messages(self, conv_id: str):
        """
        清空对话消息
        
        Args:
            conv_id: 对话 ID
        """
        if conv_id in self.conversations:
            self.conversations[conv_id]["messages"] = []
            self.conversations[conv_id]["updated_at"] = datetime.now().isoformat()
            self._save_conversations()
    
    def delete_conversation(self, conv_id: str):
        """
        删除对话
        
        Args:
            conv_id: 对话 ID
        """
        if conv_id in self.conversations:
            del self.conversations[conv_id]
            self._save_conversations()
    
    def rename_conversation(self, conv_id: str, new_title: str):
        """
        重命名对话
        
        Args:
            conv_id: 对话 ID
            new_title: 新标题
        """
        if conv_id in self.conversations:
            self.conversations[conv_id]["title"] = new_title
            self.conversations[conv_id]["updated_at"] = datetime.now().isoformat()
            self._save_conversations()
    
    def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取对话列表（按更新时间倒序）
        
        Args:
            limit: 返回数量限制
            
        Returns:
            对话列表
        """
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return conversations[:limit]
    
    def get_conversation_count(self) -> int:
        """获取对话总数"""
        return len(self.conversations)
    
    def update_conversation_title(self, conv_id: str, title: str):
        """
        更新对话标题
        
        Args:
            conv_id: 对话 ID
            title: 新标题
        """
        if conv_id in self.conversations:
            self.conversations[conv_id]["title"] = title
            self.conversations[conv_id]["updated_at"] = datetime.now().isoformat()
            self._save_conversations()


# 创建全局管理器实例
conversation_manager = ConversationManager()


def create_conversation(title: Optional[str] = None) -> str:
    """创建新对话"""
    return conversation_manager.create_conversation(title)


def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    """获取对话"""
    return conversation_manager.get_conversation(conv_id)


def add_message(conv_id: str, role: str, content: str):
    """添加消息"""
    conversation_manager.add_message(conv_id, role, content)


def get_messages(conv_id: str) -> List[Dict[str, Any]]:
    """获取消息列表"""
    return conversation_manager.get_messages(conv_id)


def clear_messages(conv_id: str):
    """清空消息"""
    conversation_manager.clear_messages(conv_id)


def delete_conversation(conv_id: str):
    """删除对话"""
    conversation_manager.delete_conversation(conv_id)


def rename_conversation(conv_id: str, new_title: str):
    """重命名对话"""
    conversation_manager.rename_conversation(conv_id, new_title)


def list_conversations(limit: int = 50) -> List[Dict[str, Any]]:
    """获取对话列表"""
    return conversation_manager.list_conversations(limit)


def get_conversation_count() -> int:
    """获取对话总数"""
    return conversation_manager.get_conversation_count()


if __name__ == "__main__":
    # 测试代码
    print("=== 对话管理器测试 ===")
    
    # 创建对话
    print("\n1. 创建对话...")
    conv_id = create_conversation("测试对话")
    print(f"   ✅ 创建成功：{conv_id}")
    
    # 添加消息
    print("\n2. 添加消息...")
    add_message(conv_id, "user", "你好")
    add_message(conv_id, "assistant", "你好！有什么可以帮助你的？")
    print("   ✅ 消息已添加")
    
    # 获取消息
    print("\n3. 获取消息...")
    messages = get_messages(conv_id)
    print(f"   消息数量：{len(messages)}")
    for msg in messages:
        print(f"   - [{msg['role']}] {msg['content'][:50]}...")
    
    # 获取对话列表
    print("\n4. 获取对话列表...")
    conversations = list_conversations()
    print(f"   对话数量：{len(conversations)}")
    
    # 删除对话
    print("\n5. 删除对话...")
    delete_conversation(conv_id)
    print("   ✅ 对话已删除")
    
    print("\n=== 测试完成 ===")
