# Agent Monitor Plugin

Python Agent 监控插件 - 支持 CrewAI 等框架的通用监控

## 安装

```bash
cd agent-monitor-plugin
pip install -e .
```

## 使用

### 方式 1：环境变量（推荐）

```bash
# 启用监控
export AGENT_MONITOR_ENABLED=true
export AGENT_MONITOR_URL=http://localhost:8080

# 运行 Agent
python your_crewai_app.py
```

### 方式 2：代码集成

```python
from agent_monitor import CrewAIPlugin

# 初始化插件
plugin = CrewAIPlugin(monitor_url="http://localhost:8080")
plugin.install()

# 正常使用 CrewAI
crew.kickoff()
```

## 支持的框架

- ✅ CrewAI (已实现)
- ⚠️ LangGraph (计划中)
- ⚠️ AutoGen (计划中)

## 事件类型

- `agent_online` - Agent 上线
- `agent_offline` - Agent 离线
- `agent_working` - Agent 工作中
- `agent_using_tool` - 使用工具
- `agent_relationship` - Agent 关系变化

## 配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `AGENT_MONITOR_ENABLED` | 是否启用监控 | `false` |
| `AGENT_MONITOR_URL` | 监控服务器 URL | - |
| `AGENT_SERVER_ID` | 服务器唯一标识 | 主机名 |

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black agent_monitor/
flake8 agent_monitor/
```
