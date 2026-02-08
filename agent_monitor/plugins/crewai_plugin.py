"""
CrewAI Monitoring Plugin

Listens to CrewAI events and sends them to monitoring server
"""

import os
import socket
from typing import Optional
import logging

from transports.direct import DirectTransport
from protocol.unified_event import (
    MonitorEvent,
    EventSource,
    EventMetadata,
    Language,
)

logger = logging.getLogger(__name__)

# 配置日志输出
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class CrewAIPlugin:
    """
    CrewAI Framework Monitoring Plugin

    Captures CrewAI events and sends them to monitoring server
    """

    def __init__(
        self,
        monitor_url: Optional[str] = None,
        transport: Optional[DirectTransport] = None,
        debug: bool = False
    ):
        """
        Initialize CrewAI Plugin

        Args:
            monitor_url: Monitoring server URL
            transport: Transport instance (optional)
            debug: Enable debug logging and sync send
        """
        self.server_id = self._get_server_id()
        self.debug = debug

        if transport:
            self.transport = transport
        else:
            url = monitor_url or os.getenv("AGENT_MONITOR_URL")
            logger.info(f"初始化插件，监控服务器: {url}")
            self.transport = DirectTransport(
                url,
                silent_fail=not debug  # 调试模式显示错误
            )

        self._installed = False
        logger.info(f"CrewAI Plugin initialized (server_id: {self.server_id}, debug={debug})")

    def install(self):
        """Install monitoring hooks"""
        if self._installed:
            logger.warning("Plugin already installed, skipping")
            return

        try:
            from crewai.events import crewai_event_bus
        except ImportError:
            logger.warning("CrewAI not installed, skipping monitoring")
            return

        # Register event listeners
        self._setup_crew_monitoring()
        self._setup_agent_monitoring()
        self._setup_llm_monitoring()
        self._setup_task_monitoring()
        self._setup_tool_monitoring()
        self._setup_relationship_monitoring()

        self._installed = True
        logger.info("CrewAI monitoring plugin installed successfully")

    def _setup_crew_monitoring(self):
        """Monitor Crew lifecycle"""
        from crewai.events import crewai_event_bus
        from crewai.events.types.crew_events import (
            CrewKickoffStartedEvent,
            CrewKickoffCompletedEvent,
        )

        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_start(source, event):
            """Crew starts execution"""
            try:
                logger.info(f"[Crew开始] Crew: {event.crew_name}")
                # 使用事件本身的 agent_id 或者生成一个
                agent_id = event.agent_id or f"crew_{event.crew_name or 'unknown'}"

                monitor_event = MonitorEvent(
                    source=EventSource(
                        server_id=self.server_id,
                        agent_id=agent_id,
                        framework="crewai",
                        language=Language.python,
                        process_id=os.getpid(),
                    ),
                    event={
                        "type": "crew_started",
                        "data": {
                            "crew_name": event.crew_name,
                            "inputs": event.inputs,
                        }
                    },
                    metadata=EventMetadata(
                        hostname=socket.gethostname(),
                        ip_address=self._get_local_ip(),
                    ),
                )

                if self.debug:
                    success = self.transport.send_sync(monitor_event.to_dict())
                    logger.info(f"[Crew开始] 发送{'成功' if success else '失败'}")
                else:
                    self.transport.send(monitor_event.to_dict())
            except Exception as e:
                logger.error(f"[Crew开始] 处理失败: {e}", exc_info=True)

        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_complete(source, event):
            """Crew completes execution"""
            try:
                logger.info(f"[Crew完成] Crew: {event.crew_name}")
                agent_id = event.agent_id or f"crew_{event.crew_name or 'unknown'}"

                monitor_event = MonitorEvent(
                    source=EventSource(
                        server_id=self.server_id,
                        agent_id=agent_id,
                        framework="crewai",
                        language=Language.python,
                        process_id=os.getpid(),
                    ),
                    event={
                        "type": "crew_completed",
                        "data": {
                            "crew_name": event.crew_name,
                            "result": str(event.output)[:500] if event.output else None,
                            "total_tokens": event.total_tokens,
                        }
                    },
                    metadata=EventMetadata(
                        hostname=socket.gethostname(),
                        ip_address=self._get_local_ip(),
                    ),
                )

                self.transport.send(monitor_event.to_dict())
            except Exception as e:
                logger.error(f"[Crew完成] 处理失败: {e}", exc_info=True)

    def _setup_agent_monitoring(self):
        """Monitor Agent lifecycle"""
        from crewai.events import crewai_event_bus
        from crewai.events.types.agent_events import (
            AgentExecutionStartedEvent,
            AgentExecutionCompletedEvent,
            AgentExecutionErrorEvent,
        )

        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_start(source, event):
            """Agent comes online"""
            try:
                logger.info(f"[Agent上线] {event.agent.role} (ID: {event.agent.id})")
                monitor_event = MonitorEvent(
                    source=EventSource(
                        server_id=self.server_id,
                        agent_id=str(event.agent.id),
                        framework="crewai",
                        language=Language.python,
                        process_id=os.getpid(),
                    ),
                    event={
                        "type": "agent_online",
                        "data": {
                            "role": event.agent.role,
                            "goal": getattr(event.agent, 'goal', ''),
                            "backstory": getattr(event.agent, 'backstory', ''),
                        }
                    },
                    metadata=EventMetadata(
                        hostname=socket.gethostname(),
                        ip_address=self._get_local_ip(),
                    ),
                )

                if self.debug:
                    # 调试模式使用同步发送，便于调试
                    success = self.transport.send_sync(monitor_event.to_dict())
                    logger.info(f"[Agent上线] 发送{'成功' if success else '失败'}")
                else:
                    self.transport.send(monitor_event.to_dict())
            except Exception as e:
                logger.error(f"[Agent上线] 处理失败: {e}", exc_info=True)

        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_complete(source, event):
            """Agent goes offline"""
            monitor_event = MonitorEvent(
                source=EventSource(
                    server_id=self.server_id,
                    agent_id=event.agent.id,
                    framework="crewai",
                    language=Language.python,
                    process_id=os.getpid(),
                ),
                event={
                    "type": "agent_offline",
                    "data": {
                        "role": event.agent.role,
                        "result": str(event.output.raw)[:1000]
                        if event.output
                        else None,
                    }
                },
                metadata=EventMetadata(
                    hostname=socket.gethostname(),
                    ip_address=self._get_local_ip(),
                ),
            )

            self.transport.send(monitor_event.to_dict())

        @crewai_event_bus.on(AgentExecutionErrorEvent)
        def on_agent_error(source, event):
            """Agent error"""
            monitor_event = MonitorEvent(
                source=EventSource(
                    server_id=self.server_id,
                    agent_id=event.agent.id,
                    framework="crewai",
                    language=Language.python,
                    process_id=os.getpid(),
                ),
                event={
                    "type": "agent_error",
                    "data": {
                        "role": event.agent.role,
                        "error": str(event.error),
                    }
                },
                metadata=EventMetadata(
                    hostname=socket.gethostname(),
                    ip_address=self._get_local_ip(),
                ),
            )

            self.transport.send(monitor_event.to_dict())

    def _setup_llm_monitoring(self):
        """Monitor LLM calls (thinking state)"""
        from crewai.events import crewai_event_bus
        from crewai.events.types.llm_events import LLMCallStartedEvent, LLMCallCompletedEvent

        @crewai_event_bus.on(LLMCallStartedEvent)
        def on_llm_start(source, event):
            """Agent starts thinking (LLM call)"""
            try:
                agent_id = event.agent_id or event.agent_role or "unknown"
                logger.info(f"[Agent思考] {agent_id} 开始调用 LLM")
                monitor_event = MonitorEvent(
                    source=EventSource(
                        server_id=self.server_id,
                        agent_id=agent_id,
                        framework="crewai",
                        language=Language.python,
                        process_id=os.getpid(),
                    ),
                    event={
                        "type": "agent_thinking",
                        "data": {
                            "action": "thinking",
                            "model": event.model or 'unknown',
                        }
                    },
                    metadata=EventMetadata(
                        hostname=socket.gethostname(),
                        ip_address=self._get_local_ip(),
                    ),
                )

                if self.debug:
                    success = self.transport.send_sync(monitor_event.to_dict())
                    logger.info(f"[Agent思考] 发送{'成功' if success else '失败'}")
                else:
                    self.transport.send(monitor_event.to_dict())
            except Exception as e:
                logger.error(f"[Agent思考] 处理失败: {e}", exc_info=True)

        @crewai_event_bus.on(LLMCallCompletedEvent)
        def on_llm_complete(source, event):
            """Agent finishes thinking"""
            try:
                agent_id = event.agent_id or event.agent_role or "unknown"
                logger.info(f"[Agent思考完成] {agent_id}")
                monitor_event = MonitorEvent(
                    source=EventSource(
                        server_id=self.server_id,
                        agent_id=agent_id,
                        framework="crewai",
                        language=Language.python,
                        process_id=os.getpid(),
                    ),
                    event={
                        "type": "agent_thinking",
                        "data": {
                            "action": "completed",
                        }
                    },
                    metadata=EventMetadata(
                        hostname=socket.gethostname(),
                        ip_address=self._get_local_ip(),
                    ),
                )

                self.transport.send(monitor_event.to_dict())
            except Exception as e:
                logger.error(f"[Agent思考完成] 处理失败: {e}", exc_info=True)

    def _setup_task_monitoring(self):
        """Monitor task execution"""
        from crewai.events import crewai_event_bus, TaskStartedEvent

        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_start(source, event):
            """Agent starts working"""
            try:
                logger.info(f"[Agent工作] {event.task.agent.role} - {event.task.description[:50]}...")
                monitor_event = MonitorEvent(
                    source=EventSource(
                        server_id=self.server_id,
                        agent_id=str(event.task.agent.id),
                        framework="crewai",
                        language=Language.python,
                        process_id=os.getpid(),
                    ),
                    event={
                        "type": "agent_working",
                        "data": {
                            "task": event.task.description,
                            "expected_output": event.task.expected_output,
                        }
                    },
                    metadata=EventMetadata(
                        hostname=socket.gethostname(),
                        ip_address=self._get_local_ip(),
                        tags={}
                    ),
                )

                if self.debug:
                    success = self.transport.send_sync(monitor_event.to_dict())
                    logger.info(f"[Agent工作] 发送{'成功' if success else '失败'}")
                else:
                    self.transport.send(monitor_event.to_dict())
            except Exception as e:
                logger.error(f"[Agent工作] 处理失败: {e}", exc_info=True)

    def _setup_tool_monitoring(self):
        """Monitor tool usage"""
        from crewai.events import crewai_event_bus
        from crewai.events.types.tool_usage_events import ToolUsageStartedEvent, ToolUsageFinishedEvent

        @crewai_event_bus.on(ToolUsageStartedEvent)
        def on_tool_start(source, event):
            """Agent starts using tool"""
            try:
                agent_id = event.agent_id or event.agent_role or "unknown"
                logger.info(f"[工具使用] {agent_id} 使用 {event.tool_name}")
                monitor_event = MonitorEvent(
                    source=EventSource(
                        server_id=self.server_id,
                        agent_id=agent_id,
                        framework="crewai",
                        language=Language.python,
                        process_id=os.getpid(),
                    ),
                    event={
                        "type": "tool_usage_started",
                        "data": {
                            "tool_name": event.tool_name,
                            "tool_args": str(event.tool_args)[:500],
                        }
                    },
                    metadata=EventMetadata(
                        hostname=socket.gethostname(),
                        ip_address=self._get_local_ip(),
                    ),
                )

                self.transport.send(monitor_event.to_dict())
            except Exception as e:
                logger.error(f"[工具使用] 处理失败: {e}", exc_info=True)

        @crewai_event_bus.on(ToolUsageFinishedEvent)
        def on_tool_finish(source, event):
            """Agent finishes using tool"""
            try:
                agent_id = event.agent_id or event.agent_role or "unknown"
                logger.info(f"[工具完成] {agent_id} 完成 {event.tool_name}")
                monitor_event = MonitorEvent(
                    source=EventSource(
                        server_id=self.server_id,
                        agent_id=agent_id,
                        framework="crewai",
                        language=Language.python,
                        process_id=os.getpid(),
                    ),
                    event={
                        "type": "tool_usage_finished",
                        "data": {
                            "tool_name": event.tool_name,
                            "result": str(event.output)[:500] if event.output else '',
                        }
                    },
                    metadata=EventMetadata(
                        hostname=socket.gethostname(),
                        ip_address=self._get_local_ip(),
                    ),
                )

                self.transport.send(monitor_event.to_dict())
            except Exception as e:
                logger.error(f"[工具完成] 处理失败: {e}", exc_info=True)

    def _setup_relationship_monitoring(self):
        """Monitor Agent relationships"""
        from crewai.events import crewai_event_bus
        from crewai.events.types.a2a_events import A2ADelegationStartedEvent

        @crewai_event_bus.on(A2ADelegationStartedEvent)
        def on_delegation(source, event):
            """Agent delegates task"""
            monitor_event = MonitorEvent(
                source=EventSource(
                    server_id=self.server_id,
                    agent_id=event.agent_id or "unknown",
                    framework="crewai",
                    language=Language.python,
                    process_id=os.getpid(),
                ),
                event={
                    "type": "agent_relationship",
                    "data": {
                        "relationship_type": "delegate",
                        "from_agent": event.agent_id or "unknown",
                        "to_agent": event.a2a_agent_name or "unknown",
                    }
                },
                metadata=EventMetadata(
                    hostname=socket.gethostname(),
                    ip_address=self._get_local_ip(),
                ),
            )

            self.transport.send(monitor_event.to_dict())

    def _get_server_id(self) -> str:
        """Get unique server identifier"""
        return os.getenv("AGENT_SERVER_ID", socket.gethostname())

    def _get_local_ip(self) -> Optional[str]:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None


# Auto-install if environment variables are set
# This is wrapped in try-except to prevent import errors
try:
    if os.getenv("AGENT_MONITOR_ENABLED"):
        monitor_url = os.getenv("AGENT_MONITOR_URL")
        if monitor_url:
            debug_mode = os.getenv("AGENT_MONITOR_DEBUG", "false").lower() == "true"
            plugin = CrewAIPlugin(monitor_url=monitor_url, debug=debug_mode)
            plugin.install()
            logger.info(f"CrewAI monitoring plugin auto-installed (debug={debug_mode})")
except Exception as e:
    logger.debug(f"Auto-install skipped: {e}")
