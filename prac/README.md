# Agent Monitor Plugin - 测试用例

这个目录包含了多个 CrewAI Agent 示例，用于测试和演示 agent-monitor-plugin 的监控功能。

## 目录结构

```
prac/
├── README.md                           # 本文件
├── customer_service_crew/              # 客服团队
│   └── src/customer_service_crew/
│       ├── __init__.py
│       ├── crew.py
│       ├── main.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── tools/
│           └── __init__.py
├── research_analysis_crew/             # 研究分析团队
│   └── src/research_analysis_crew/
│       ├── __init__.py
│       ├── crew.py
│       ├── main.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── tools/
│           └── __init__.py
├── code_review_crew/                   # 代码审查团队
│   └── src/code_review_crew/
│       ├── __init__.py
│       ├── crew.py
│       ├── main.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── tools/
│           ├── __init__.py
│           └── custom_tool.py
├── translation_crew/                   # 翻译团队
│   └── src/translation_crew/
│       ├── __init__.py
│       ├── crew.py
│       ├── main.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── tools/
│           └── __init__.py
└── data_analysis_crew/                 # 数据分析团队
    └── src/data_analysis_crew/
        ├── __init__.py
        ├── crew.py
        ├── main.py
        ├── config/
        │   ├── agents.yaml
        │   └── tasks.yaml
        └── tools/
            └── __init__.py
```

## 快速开始

### 1. 启动监控服务器

首先需要启动监控服务器来接收 Agent 事件。

### 2. 设置环境变量

```bash
export AGENT_MONITOR_ENABLED=true
export AGENT_MONITOR_URL=http://localhost:8080
export AGENT_MONITOR_DEBUG=true   # 可选，启用调试模式
```

### 3. 运行测试 Agent

每个 Crew 都可以独立运行：

```bash
# 客服团队
cd customer_service_crew
python src/customer_service_crew/main.py

# 研究分析团队
cd research_analysis_crew
python src/research_analysis_crew/main.py

# 代码审查团队
cd code_review_crew
python src/code_review_crew/main.py

# 翻译团队
cd translation_crew
python src/translation_crew/main.py

# 数据分析团队
cd data_analysis_crew
python src/data_analysis_crew/main.py
```

## 监控事件类型

这些测试 Agent 会触发以下监控事件：

| 事件类型 | 说明 | 示例 |
|---------|------|------|
| `agent_online` | Agent 上线 | 当 Agent 开始执行任务时 |
| `agent_offline` | Agent 离线 | 当 Agent 完成任务时 |
| `agent_thinking` | Agent 思考中 | LLM 调用时 |
| `agent_working` | Agent 工作中 | 执行任务时 |
| `agent_error` | Agent 错误 | 任务执行失败时 |
| `tool_usage_started` | 工具使用开始 | Agent 调用工具时 |
| `tool_usage_finished` | 工具使用完成 | 工具调用完成时 |
| `agent_relationship` | Agent 关系 | Agent 间委派任务时 |

## 各 Crew 说明

### Customer Service Crew (客服团队)
- **目的**: 演示多 Agent 协作和任务委派
- **场景**: 处理客户咨询，包含前台接待、专家处理、主管监督
- **监控亮点**: Agent 关系、任务委派、错误处理

### Research Analysis Crew (研究分析团队)
- **目的**: 演示顺序任务执行和 LLM 调用监控
- **场景**: 收集资料、分析数据、生成报告
- **监控亮点**: Agent 思考状态、任务流程

### Code Review Crew (代码审查团队)
- **目的**: 演示工具使用监控
- **场景**: 审查代码质量、生成报告
- **监控亮点**: 工具调用、参数传递、结果返回

### Translation Crew (翻译团队)
- **目的**: 演示简单工作流
- **场景**: 翻译文本、质量检查、最终编辑
- **监控亮点**: 流程监控、质量保证

### Data Analysis Crew (数据分析团队)
- **目的**: 演示层级代理和复杂协作
- **场景**: 收集数据、分析趋势、生成洞察
- **监控亮点**: Agent 层级关系、数据流转

## 开发说明

### 添加新的 Crew

1. 创建新的目录结构
2. 创建 `config/agents.yaml` 和 `config/tasks.yaml`
3. 实现 `crew.py` 定义 Crew、Agent 和 Task
4. 实现 `main.py` 作为入口点
5. 添加自定义工具（可选）

### 自定义工具示例

```python
from crewai_tools import BaseTool
from pydantic import Field

class MyCustomTool(BaseTool):
    name: str = "my_custom_tool"
    description: str = "工具描述"

    def _run(self, argument: str) -> str:
        # 工具实现
        return result
```

## 故障排除

### 问题: 监控事件未发送
- 检查 `AGENT_MONITOR_URL` 是否正确
- 确认监控服务器是否运行
- 启用 `AGENT_MONITOR_DEBUG=true` 查看详细日志

### 问题: Agent 执行失败
- 检查 API 密钥是否设置
- 查看 Agent 日志输出
- 确认依赖包已安装

## 许可

MIT License
