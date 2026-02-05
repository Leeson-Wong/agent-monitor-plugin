"""
Agent Monitor Plugin - 通用 Agent 监控插件

支持多种 Python Agent 框架：
- CrewAI
- LangGraph (计划中)
- AutoGen (计划中)

安装:
    pip install agent-monitor-plugin

使用:
    export AGENT_MONITOR_ENABLED=true
    export AGENT_MONITOR_URL=http://localhost:8080
    python your_agent_app.py
"""

__version__ = "0.1.0"

from agent_monitor.transports.direct import DirectTransport, create_transport
from agent_monitor.plugins.crewai_plugin import CrewAIPlugin

__all__ = [
    "DirectTransport",
    "create_transport",
    "CrewAIPlugin",
]
