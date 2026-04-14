"""
AI 语义解析数据模型

使用 Pydantic 定义 grandMA3 命令的数据结构。
支持多灯具多属性的复杂场景。
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class CommandAction(BaseModel):
    """
    单个命令动作
    
    用于表示针对特定灯具 ID 列表的单个操作。
    """
    
    fixture_ids: List[int] = Field(
        default_factory=list,
        description="目标灯具 ID 列表，例如 [101, 102, 103]"
    )
    
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="属性字典，例如 {'Dimmer': 100, 'Color': 'Red'}"
    )
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "fixture_ids": [101, 102],
                "attributes": {
                    "Dimmer": 100,
                    "Color": "Red"
                }
            }
        }


class GMA3Command(BaseModel):
    """
    grandMA3 命令数据模型
    
    用于表示从自然语言解析出的结构化命令。
    支持多灯具多属性的复杂场景，通过 actions 列表实现。
    """
    
    intent: str = Field(
        ...,
        description="意图描述，例如 '设置灯具亮度', '设置颜色', '执行预设'"
    )
    
    actions: List[CommandAction] = Field(
        default_factory=list,
        description="命令动作列表，每个动作包含一组灯具 ID 和对应的属性"
    )
    
    is_cue: bool = Field(
        default=False,
        description="是否存为 Cue"
    )
    
    explanation: str = Field(
        default="",
        description="简短的中文逻辑解释，例如 '将灯具 101-105 设置为紫色，亮度 50%'"
    )
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "intent": "设置多组灯具的不同颜色和亮度",
                "actions": [
                    {
                        "fixture_ids": [101, 102, 103],
                        "attributes": {
                            "Dimmer": 100,
                            "Color": "Red"
                        }
                    },
                    {
                        "fixture_ids": [104, 105],
                        "attributes": {
                            "Dimmer": 75,
                            "Color": "Blue"
                        }
                    }
                ],
                "is_cue": False,
                "explanation": "将灯具 101-103 设置为红色，亮度 100%；将灯具 104-105 设置为蓝色，亮度 75%"
            }
        }


class TranslationResult(BaseModel):
    """
    翻译结果模型
    
    包含解析结果和元信息。
    """
    
    success: bool = Field(..., description="解析是否成功")
    command: Optional[GMA3Command] = Field(None, description="解析出的命令")
    error: Optional[str] = Field(None, description="错误信息")
    raw_response: Optional[str] = Field(None, description="原始响应")
    
    class Config:
        """Pydantic 配置"""
        arbitrary_types_allowed = True
