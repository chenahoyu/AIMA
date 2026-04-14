"""
API Key 缓存管理模块

提供 API Key 的加密存储和自动加载功能。
"""

import json
import os
import base64
import hashlib
from pathlib import Path
from typing import Optional


class APIKeyCache:
    """API Key 缓存管理器"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录，默认为项目根目录下的 .api_cache
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / ".api_cache"
        
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / "api_keys.json"
        
        # 确保缓存目录存在
        cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _encrypt(self, data: str) -> str:
        """
        简单的 Base64 加密（实际生产环境应使用更安全的加密方式）
        
        Args:
            data: 原始数据
            
        Returns:
            加密后的字符串
        """
        # 使用简单的 Base64 编码（实际应使用更安全的加密）
        encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
        return encoded
    
    def _decrypt(self, encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密后的字符串
            
        Returns:
            解密后的原始数据
        """
        decoded = base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
        return decoded
    
    def load(self) -> dict:
        """
        从缓存文件加载 API Key
        
        Returns:
            包含 API Key 的字典
        """
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 解密所有密钥
            decrypted = {}
            for key, encrypted_value in cache_data.items():
                try:
                    decrypted[key] = self._decrypt(encrypted_value)
                except Exception as e:
                    print(f"⚠️ 解密 {key} 失败：{e}")
                    decrypted[key] = None
            
            return decrypted
            
        except Exception as e:
            print(f"❌ 读取缓存文件失败：{e}")
            return {}
    
    def save(self, api_keys: dict):
        """
        保存 API Key 到缓存文件
        
        Args:
            api_keys: 包含 API Key 的字典
        """
        try:
            # 加密所有密钥
            encrypted = {}
            for key, value in api_keys.items():
                if value:
                    encrypted[key] = self._encrypt(str(value))
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(encrypted, f, indent=2, ensure_ascii=False)
            
            # 设置文件权限（仅当前用户可读写）
            os.chmod(self.cache_file, 0o600)
            
        except Exception as e:
            print(f"❌ 保存缓存文件失败：{e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取单个 API Key
        
        Args:
            key: 密钥键名
            default: 默认值
            
        Returns:
            密钥值或默认值
        """
        cache = self.load()
        return cache.get(key, default)
    
    def set(self, key: str, value: str):
        """
        设置单个 API Key
        
        Args:
            key: 密钥键名
            value: 密钥值
        """
        cache = self.load()
        cache[key] = value
        self.save(cache)
    
    def clear(self):
        """清除所有缓存的 API Key"""
        if self.cache_file.exists():
            try:
                self.cache_file.unlink()
            except Exception as e:
                print(f"❌ 删除缓存文件失败：{e}")


# 创建全局缓存实例
api_key_cache = APIKeyCache()


def get_cached_api_key(key_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    获取缓存的 API Key
    
    Args:
        key_name: 密钥键名
        default: 默认值
        
    Returns:
        缓存的密钥值或默认值
    """
    return api_key_cache.get(key_name, default)


def save_api_key(key_name: str, value: str):
    """
    保存 API Key 到缓存
    
    Args:
        key_name: 密钥键名
        value: 密钥值
    """
    api_key_cache.set(key_name, value)


def clear_all_api_keys():
    """清除所有缓存的 API Key"""
    api_key_cache.clear()


if __name__ == "__main__":
    # 测试代码
    print("=== API Key Cache 测试 ===")
    
    # 测试保存
    print("\n1. 测试保存 API Key...")
    save_api_key("test_key", "test_value_123")
    print("   ✅ 已保存")
    
    # 测试加载
    print("\n2. 测试加载 API Key...")
    value = get_cached_api_key("test_key")
    print(f"   加载值：{value}")
    
    # 测试清除
    print("\n3. 测试清除 API Key...")
    clear_all_api_keys()
    value = get_cached_api_key("test_key")
    print(f"   清除后：{value}")
    
    print("\n=== 测试完成 ===")
