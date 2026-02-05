#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试插件导入"""

from agent_monitor import DirectTransport, CrewAIPlugin
from agent_monitor.protocol.unified_event import MonitorEvent

print("[OK] DirectTransport: available")
print("[OK] CrewAIPlugin: available")
print("[OK] MonitorEvent: available")
print("\nPlugin is ready!")
