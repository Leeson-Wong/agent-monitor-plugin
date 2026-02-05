"""
CrewAI Monitoring Plugin

Listens to CrewAI events and sends them to monitoring server
"""

import os
import socket
from typing import Optional
import logging

from agent_monitor.transports.direct import DirectTransport
from agent_monitor.protocol.unified_event import (
    MonitorEvent,
    EventSource,
    EventMetadata,
    Language,
)

logger = logging.getLogger(__name__)


class CrewAIPlugin:
    """
    CrewAI Framework Monitoring Plugin

    Captures CrewAI events and sends them to monitoring server
    """

    def __init__(
        self,
        monitor_url: Optional[str] = None,
        transport: Optional[DirectTransport] = None
    ):
        """
        Initialize CrewAI Plugin

        Args:
            monitor_url: Monitoring server URL
            transport: Transport instance (optional)
        """
        self.server_id = self._get_server_id()
        self.transport = transport or DirectTransport(
            monitor_url or os.getenv("AGENT_MONITOR_URL")
        )
        self._installed = False

        logger.info(f"CrewAI Plugin initialized (server_id: {self.server_id})")

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
        self._setup_agent_monitoring()
        self._setup_task_monitoring()
        self._setup_tool_monitoring()
        self._setup_relationship_monitoring()

        self._installed = True
        logger.info("CrewAI monitoring plugin installed successfully")

    def _setup_agent_monitoring(self):
        """Monitor Agent lifecycle"""
        from crewai.events import (
            crewai_event_bus,
            AgentExecutionStartedEvent,
            AgentExecutionCompletedEvent,
            AgentExecutionErrorEvent,
        )

        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_start(source, event):
            """Agent comes online"""
            monitor_event = MonitorEvent(
                source=EventSource(
                    server_id=self.server_id,
                    agent_id=event.agent.id,
                    framework="crewai",
                    language=Language.python,
                    process_id=os.getpid(),
                ),
                event={
                    "type": "agent_online",
                    "data": {
                        "role": event.agent.role,
                        "goal": event.agent.goal,
                        "backstory": event.agent.backstory,
                    }
                },
                metadata=EventMetadata(
                    hostname=socket.gethostname(),
                    ip_address=self._get_local_ip(),
                ),
            )

            self.transport.send(monitor_event.to_dict())

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

    def _setup_task_monitoring(self):
        """Monitor task execution"""
        from crewai.events import crewai_event_bus, TaskStartedEvent

        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_start(source, event):
            """Agent starts working"""
            monitor_event = MonitorEvent(
                source=EventSource(
                    server_id=self.server_id,
                    agent_id=event.task.agent.id,
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
                ),
            )

            self.transport.send(monitor_event.to_dict())

    def _setup_tool_monitoring(self):
        """Monitor tool usage"""
        from crewai.events import crewai_event_bus, ToolUsageStartedEvent

        @crewai_event_bus.on(ToolUsageStartedEvent)
        def on_tool_start(source, event):
            """Agent uses tool"""
            monitor_event = MonitorEvent(
                source=EventSource(
                    server_id=self.server_id,
                    agent_id=event.agent_key,
                    framework="crewai",
                    language=Language.python,
                    process_id=os.getpid(),
                ),
                event={
                    "type": "agent_using_tool",
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
                    agent_id=event.source_agent_id,
                    framework="crewai",
                    language=Language.python,
                    process_id=os.getpid(),
                ),
                event={
                    "type": "agent_relationship",
                    "data": {
                        "relationship_type": "delegate",
                        "from_agent": event.source_agent_id,
                        "to_agent": event.a2a_agent_name,
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
            plugin = CrewAIPlugin(monitor_url=monitor_url)
            plugin.install()
            logger.info("CrewAI monitoring plugin auto-installed")
except Exception as e:
    logger.debug(f"Auto-install skipped: {e}")
