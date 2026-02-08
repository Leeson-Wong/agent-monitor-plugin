"""
Data Analysis Crew - 数据分析团队

这个模块定义了一个数据分析团队的 Crew、Agent 和 Task。
演示层级代理关系、复杂协作和数据流转流程。
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class DataAnalysisCrew:
    """数据分析团队 Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # === 定义 Agents ===
    @agent
    def data_collector(self) -> Agent:
        """数据收集专员 Agent"""
        return Agent(
            config=self.agents_config['data_collector'],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def data_analyst(self) -> Agent:
        """资深数据分析师 Agent"""
        return Agent(
            config=self.agents_config['data_analyst'],
            verbose=True,
            allow_delegation=True,  # 可以委派部分分析任务
        )

    @agent
    def insight_generator(self) -> Agent:
        """洞察生成专家 Agent"""
        return Agent(
            config=self.agents_config['insight_generator'],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def report_specialist(self) -> Agent:
        """数据报告专家 Agent"""
        return Agent(
            config=self.agents_config['report_specialist'],
            verbose=True,
            allow_delegation=False,
        )

    # === 定义 Tasks ===
    @task
    def data_collection(self) -> Task:
        """数据收集任务"""
        return Task(
            config=self.tasks_config['data_collection'],
        )

    @task
    def statistical_analysis(self) -> Task:
        """统计分析任务"""
        return Task(
            config=self.tasks_config['statistical_analysis'],
        )

    @task
    def insight_generation(self) -> Task:
        """洞察生成任务"""
        return Task(
            config=self.tasks_config['insight_generation'],
        )

    @task
    def final_report(self) -> Task:
        """最终报告任务"""
        return Task(
            config=self.tasks_config['final_report'],
        )

    # === 定义 Crew ===
    @crew
    def crew(self) -> Crew:
        """创建数据分析团队 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # 顺序执行
            verbose=True,
            memory=False,
            max_rpm=None,
            share_crew=False,
        )
