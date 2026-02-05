"""
统一监控事件协议
所有语言的 Agent 都使用这个格式
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    """支持的编程语言"""
    python = "python"
    typescript = "typescript"
    javascript = "javascript"
    rust = "rust"
    go = "go"
    java = "java"


class EventType(str, Enum):
    """事件类型"""
    # Agent 生命周期
    agent_online = "agent_online"
    agent_offline = "agent_offline"
    agent_error = "agent_error"

    # Agent 活动
    agent_working = "agent_working"
    agent_thinking = "agent_thinking"
    agent_using_tool = "agent_using_tool"

    # Agent 关系
    agent_relationship = "agent_relationship"

    # 通用方法调用
    method_call = "method_call"
    method_return = "method_return"
    method_error = "method_error"

    # LLM 调用
    llm_call_start = "llm_call_start"
    llm_call_end = "llm_call_end"
    llm_stream_chunk = "llm_stream_chunk"


class EventSource(BaseModel):
    """事件源信息"""
    server_id: str = Field(..., description="服务器唯一标识")
    agent_id: str = Field(..., description="Agent ID")
    framework: str = Field(..., description="框架名称 (crewai, openclaw, etc)")
    language: Language = Field(..., description="编程语言")
    process_id: Optional[int] = Field(None, description="进程 ID")


class EventMetadata(BaseModel):
    """元数据"""
    hostname: str = Field(..., description="主机名")
    ip_address: Optional[str] = Field(None, description="IP 地址")
    tags: Optional[Dict[str, str]] = Field(None, description="自定义标签")


class MonitorEvent(BaseModel):
    """统一监控事件"""
    protocol: str = Field(default="agent-monitor", description="协议标识")
    version: str = Field(default="1.0", description="协议版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="事件时间")
    source: EventSource = Field(..., description="事件源")
    event: Dict[str, Any] = Field(..., description="事件内容")
    metadata: EventMetadata = Field(..., description="元数据")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 JSON 序列化）"""
        return {
            "protocol": self.protocol,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source.dict(),
            "event": self.event,
            "metadata": self.metadata.dict()
        }

    class Config:
        use_enum_values = True
