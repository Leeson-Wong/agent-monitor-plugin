"""
Agent Monitor Plugin - Python Agent 监控插件

安装:
    pip install -e .

使用:
    export AGENT_MONITOR_ENABLED=true
    export AGENT_MONITOR_URL=http://localhost:8080
    python your_agent_app.py
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-monitor-plugin",
    version="0.1.0",
    author="Agent Monitor Team",
    description="Universal monitoring plugin for AI Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/agent-monitor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "crewai": [
            "crewai>=0.1.0",
        ],
        "langgraph": [
            "langgraph>=0.0.20",
        ],
    },
    entry_points={
        "console_scripts": [
            "agent-monitor=agent_monitor.cli:main",
        ],
    },
)
