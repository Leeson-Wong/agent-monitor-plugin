"""
Research Analysis Crew - 研究分析团队

这个模块定义了一个研究分析团队的 Crew、Agent 和 Task。
演示顺序任务执行、LLM 调用监控和数据处理流程。
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class ResearchAnalysisCrew:
    """研究分析团队 Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # === 定义 Agents ===
    @agent
    def lead_researcher(self) -> Agent:
        """首席研究员 Agent"""
        return Agent(
            config=self.agents_config['lead_researcher'],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def data_collector(self) -> Agent:
        """数据收集专员 Agent"""
        return Agent(
            config=self.agents_config['data_collector'],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def analyst(self) -> Agent:
        """数据分析专家 Agent"""
        return Agent(
            config=self.agents_config['analyst'],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def report_writer(self) -> Agent:
        """报告撰写专家 Agent"""
        return Agent(
            config=self.agents_config['report_writer'],
            verbose=True,
            allow_delegation=False,
        )

    # === 定义 Tasks ===
    @task
    def research_planning(self) -> Task:
        """研究规划任务"""
        return Task(
            config=self.tasks_config['research_planning'],
        )

    @task
    def data_collection(self) -> Task:
        """数据收集任务"""
        return Task(
            config=self.tasks_config['data_collection'],
        )

    @task
    def data_analysis(self) -> Task:
        """数据分析任务"""
        return Task(
            config=self.tasks_config['data_analysis'],
        )

    @task
    def report_writing(self) -> Task:
        """报告撰写任务"""
        return Task(
            config=self.tasks_config['report_writing'],
        )

    # === 定义 Crew ===
    @crew
    def crew(self) -> Crew:
        """创建研究分析团队 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # 顺序执行
            verbose=True,
            memory=False,
            max_rpm=None,
            share_crew=False,
        )
