"""
直连传输器 - 直接发送到监控服务器（MVP）

最简单的方案，插件直接 HTTP POST 到监控服务器
"""

import threading
import socket
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DirectTransport:
    """
    直连传输器

    直接发送事件到监控服务器，无批量、无缓存
    适合 MVP 验证和小规模部署
    """

    def __init__(
        self,
        monitor_url: str,
        timeout: float = 1.0,
        silent_fail: bool = True
    ):
        """
        初始化直连传输器

        Args:
            monitor_url: 监控服务器 URL (e.g., http://localhost:8080)
            timeout: 请求超时时间（秒），默认 1 秒
            silent_fail: 是否静默失败，True 时失败不抛异常
        """
        self.monitor_url = monitor_url.rstrip("/")
        self.timeout = timeout
        self.silent_fail = silent_fail
        self.session = requests.Session()

        # 统计
        self.stats = {
            "sent": 0,
            "failed": 0
        }

    def send(self, event: Dict[str, Any]) -> bool:
        """
        发送事件到监控服务器（非阻塞）

        Args:
            event: 事件字典

        Returns:
            bool: 是否成功
        """
        # 在独立线程中发送，不阻塞 Agent
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
        同步发送事件（阻塞，用于测试）

        Args:
            event: 事件字典

        Returns:
            bool: 是否成功
        """
        return self._send_sync(event)

    def _send_sync(self, event: Dict[str, Any]) -> bool:
        """
        内部同步发送实现

        Args:
            event: 事件字典

        Returns:
            bool: 是否成功
        """
        url = f"{self.monitor_url}/api/events"

        try:
            response = self.session.post(
                url,
                json=event,
                timeout=self.timeout
            )

            if response.status_code == 200:
                self.stats["sent"] += 1
                logger.debug(f"事件发送成功: {event.get('event', {}).get('type')}")
                return True
            else:
                self.stats["failed"] += 1
                logger.warning(
                    f"事件发送失败: {response.status_code} - {response.text}"
                )
                return False

        except requests.exceptions.Timeout:
            self.stats["failed"] += 1
            logger.warning("事件发送超时")
            return False

        except requests.exceptions.ConnectionError:
            self.stats["failed"] += 1
            logger.warning("无法连接到监控服务器")
            return False

        except Exception as e:
            self.stats["failed"] += 1
            if not self.silent_fail:
                logger.error(f"事件发送异常: {e}")
            return False

    def send_batch(self, events: list) -> bool:
        """
        批量发送事件

        Args:
            events: 事件列表

        Returns:
            bool: 是否成功
        """
        if not events:
            return True

        url = f"{self.monitor_url}/api/events/batch"

        try:
            response = self.session.post(
                url,
                json=events,
                timeout=self.timeout * 2  # 批量发送超时加倍
            )

            if response.status_code == 200:
                self.stats["sent"] += len(events)
                logger.debug(f"批量发送成功: {len(events)} 个事件")
                return True
            else:
                self.stats["failed"] += len(events)
                logger.warning(
                    f"批量发送失败: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            self.stats["failed"] += len(events)
            if not self.silent_fail:
                logger.error(f"批量发送异常: {e}")
            return False

    def health_check(self) -> bool:
        """
        健康检查 - 测试监控服务器是否可达

        Returns:
            bool: 是否可达
        """
        try:
            url = f"{self.monitor_url}/api/health"
            response = self.session.get(url, timeout=2.0)
            return response.status_code == 200
        except:
            return False

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self.stats.copy()

    def close(self):
        """关闭 session"""
        self.session.close()


def create_transport(
    monitor_url: Optional[str] = None,
    transport_type: str = "direct"
) -> DirectTransport:
    """
    创建传输器实例

    Args:
        monitor_url: 监控服务器 URL，默认从环境变量读取
        transport_type: 传输器类型，当前只支持 "direct"

    Returns:
        传输器实例
    """
    import os

    if monitor_url is None:
        monitor_url = os.getenv("AGENT_MONITOR_URL")

    if not monitor_url:
        raise ValueError(
            "未设置监控服务器 URL，请设置 AGENT_MONITOR_URL 环境变量"
        )

    if transport_type == "direct":
        return DirectTransport(monitor_url)
    else:
        raise ValueError(f"不支持的传输器类型: {transport_type}")
