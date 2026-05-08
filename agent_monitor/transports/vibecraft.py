"""
Vibecraft 专用传输器

适配 agent-monitor 协议到 Vibecraft API
"""

import threading
import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class VibecraftTransport:
    """
    Vibecraft 专用传输器

    将 agent-monitor 协议转换为 Vibecraft 事件格式
    """

    def __init__(
        self,
        vibecraft_url: str,
        timeout: float = 2.0,
        silent_fail: bool = True
    ):
        """
        初始化 Vibecraft 传输器

        Args:
            vibecraft_url: Vibecraft 服务器 URL (e.g., http://localhost:4003)
            timeout: 请求超时时间（秒）
            silent_fail: 是否静默失败
        """
        self.vibecraft_url = vibecraft_url.rstrip("/")
        self.timeout = timeout
        self.silent_fail = silent_fail
        self.session = requests.Session()

        self.stats = {
            "sent": 0,
            "failed": 0
        }

    def send(self, event: Dict[str, Any]) -> bool:
        """
        发送事件到 Vibecraft（非阻塞）

        Args:
            event: agent-monitor 协议事件

        Returns:
            bool: 是否成功
        """
        def send_async():
            try:
                self._send_sync(event)
            except Exception as e:
                if not self.silent_fail:
                    logger.error(f"发送事件失败: {e}")

        thread = threading.Thread(target=send_async, daemon=True)
        thread.start()
        return True

    def send_sync(self, event: Dict[str, Any]) -> bool:
        """
        同步发送事件（用于测试）

        Args:
            event: agent-monitor 协议事件

        Returns:
            bool: 是否成功
        """
        return self._send_sync(event)

    def _send_sync(self, event: Dict[str, Any]) -> bool:
        """
        转换并发送事件到 Vibecraft

        将 agent-monitor 协议转换为 Vibecraft 格式
        """
        # 转换协议
        vibecraft_event = self._convert_to_vibecraft_format(event)

        url = f"{self.vibecraft_url}/event"

        try:
            response = self.session.post(
                url,
                json=vibecraft_event,
                timeout=self.timeout
            )

            if response.status_code == 200:
                self.stats["sent"] += 1
                event_type = event.get("event", {}).get("type", "unknown")
                logger.debug(f"[Vibecraft] 事件发送成功: {event_type}")
                return True
            else:
                self.stats["failed"] += 1
                logger.warning(
                    f"[Vibecraft] 事件发送失败: {response.status_code}"
                )
                return False

        except requests.exceptions.Timeout:
            self.stats["failed"] += 1
            logger.warning("[Vibecraft] 事件发送超时")
            return False

        except requests.exceptions.ConnectionError:
            self.stats["failed"] += 1
            logger.warning("[Vibecraft] 无法连接到服务器")
            return False

        except Exception as e:
            self.stats["failed"] += 1
            if not self.silent_fail:
                logger.error(f"[Vibecraft] 事件发送异常: {e}")
            return False

    def _convert_to_vibecraft_format(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换 agent-monitor 协议到 Vibecraft 格式

        agent-monitor 格式:
        {
            "protocol": "agent-monitor",
            "version": "1.0",
            "timestamp": "2024-01-01T00:00:00",
            "source": {...},
            "event": {"type": "agent_online", "data": {...}},
            "metadata": {...}
        }

        Vibecraft 格式:
        {
            "id": "...",
            "sessionId": "...",
            "type": "pre_tool_use",
            "timestamp": 1234567890,
            "tool": "Agent",
            "input": "...",
            "cwd": "..."
        }
        """
        from datetime import datetime

        source = event.get("source", {})
        event_data = event.get("event", {})
        event_type = event_data.get("type", "unknown")
        data = event_data.get("data", {})

        # 生成唯一 ID
        import uuid
        event_id = f"{event_type}-{uuid.uuid4().hex[:8]}"

        # 解析时间戳
        timestamp_str = event.get("timestamp")
        if isinstance(timestamp_str, datetime):
            timestamp_ms = int(timestamp_str.timestamp() * 1000)
        elif isinstance(timestamp_str, str):
            from dateutil import parser
            dt = parser.parse(timestamp_str)
            timestamp_ms = int(dt.timestamp() * 1000)
        else:
            timestamp_ms = 0

        # 根据 event_type 映射到 Vibecraft 格式
        vibecraft_event = {
            "id": event_id,
            "sessionId": source.get("server_id", "unknown"),
            "type": self._map_event_type(event_type),
            "timestamp": timestamp_ms,
        }

        # 添加类型特定的字段
        if event_type == "agent_online":
            vibecraft_event.update({
                "tool": "Agent",
                "input": f"{data.get('role', '')}: {data.get('goal', '')}",
                "cwd": f"/crewai/{source.get('framework', 'unknown')}"
            })
        elif event_type == "agent_offline":
            vibecraft_event.update({
                "tool": "Agent",
                "success": True,
                "output": str(data.get("result", ""))[:500]
            })
        elif event_type == "agent_working":
            vibecraft_event.update({
                "tool": "Task",
                "input": str(data.get("task", ""))[:200]
            })
        elif event_type == "agent_using_tool":
            vibecraft_event.update({
                "tool": data.get("tool_name", "Unknown"),
                "input": str(data.get("tool_args", ""))[:200]
            })
        elif event_type == "agent_error":
            vibecraft_event.update({
                "tool": "Agent",
                "success": False,
                "error": str(data.get("error", ""))[:200]
            })
        else:
            # 通用事件映射
            vibecraft_event.update({
                "tool": "Agent",
                "input": str(event_type)
            })

        return vibecraft_event

    def _map_event_type(self, event_type: str) -> str:
        """
        映射事件类型到 Vibecraft 格式

        agent_monitor -> Vibecraft:
        - agent_online -> pre_tool_use
        - agent_offline -> post_tool_use
        - agent_working -> pre_tool_use
        - agent_using_tool -> pre_tool_use
        - agent_error -> post_tool_use
        """
        mapping = {
            "agent_online": "pre_tool_use",
            "agent_offline": "post_tool_use",
            "agent_working": "pre_tool_use",
            "agent_using_tool": "pre_tool_use",
            "agent_error": "post_tool_use",
        }
        return mapping.get(event_type, "pre_tool_use")

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self.stats.copy()

    def close(self):
        """关闭 session"""
        self.session.close()
