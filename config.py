# AI-MA 项目配置
# 基于 Pydantic 的配置管理

from pydantic import BaseModel
from pathlib import Path
from typing import Optional


class Settings(BaseModel):
    """项目配置类"""
    
    # 基础配置
    app_name: str = "AI-MA: grandMA3 语义编程助手"
    app_version: str = "1.0.0"
    
    # grandMA3 OSC 配置
    ma3_osc_host: str = "127.0.0.1"
    ma3_osc_port: int = 8000
    ma3_osc_prefix: str = "/cmd"
    
    # AI 配置
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://maas-coding-api.cn-huabei-1.xf-yun.com/v2"  # 不包含 /chat/completions
    openai_model: str = "gpt-4"
    model_id: str = "astron-code-latest"
    
    # 数据目录
    data_dir: str = "data"
    knowledge_base_dir: str = "data/knowledge_base"
    fixtures_dir: str = "data/fixtures"
    presets_dir: str = "data/presets"
    sequences_dir: str = "data/sequences"
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 定义 base_dir 为类属性，而不是属性
    _base_dir: Optional[Path] = None
    
    @property
    def base_dir(self) -> Path:
        """获取项目根目录"""
        if self._base_dir is None:
            self._base_dir = Path(__file__).parent
        return self._base_dir
    
    @property
    def data_path(self) -> Path:
        """获取数据目录路径"""
        return self.base_dir / self.data_dir
    
    @property
    def knowledge_base_path(self) -> Path:
        """获取知识库目录路径"""
        return self.base_dir / self.knowledge_base_dir
    
    @property
    def fixtures_path(self) -> Path:
        """获取灯具目录路径"""
        return self.base_dir / self.fixtures_dir
    
    @property
    def presets_path(self) -> Path:
        """获取预设目录路径"""
        return self.base_dir / self.presets_dir
    
    @property
    def sequences_path(self) -> Path:
        """获取序列目录路径"""
        return self.base_dir / self.sequences_dir
    
    @property
    def logs_path(self) -> Path:
        """获取日志目录路径"""
        return self.base_dir / "logs"
    
    @property
    def conversations_path(self) -> Path:
        """获取对话历史目录路径"""
        return self.base_dir / ".conversations"
    
    @property
    def api_cache_path(self) -> Path:
        """获取 API 缓存目录路径"""
        return self.base_dir / ".api_cache"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# 创建全局配置实例
settings = Settings()
