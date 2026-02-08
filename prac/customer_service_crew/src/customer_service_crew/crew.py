"""
Customer Service Crew - 客服团队

这个模块定义了一个客户服务团队的 Crew、Agent 和 Task。
演示多 Agent 协作、任务委派和层级处理流程。
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class CustomerServiceCrew:
    """客户服务团队 Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # === 定义 Agents ===
    @agent
    def receptionist(self) -> Agent:
        """客服前台 Agent"""
        return Agent(
            config=self.agents_config['receptionist'],
            verbose=True,
            allow_delegation=True,  # 前台可以将问题委派给专家
        )

    @agent
    def specialist(self) -> Agent:
        """客户服务专家 Agent"""
        return Agent(
            config=self.agents_config['specialist'],
            verbose=True,
            allow_delegation=False,  # 专家直接解决问题
        )

    @agent
    def supervisor(self) -> Agent:
        """客服主管 Agent"""
        return Agent(
            config=self.agents_config['supervisor'],
            verbose=True,
            allow_delegation=False,
        )

    # === 定义 Tasks ===
    @task
    def initial_response(self) -> Task:
        """初步响应任务"""
        return Task(
            config=self.tasks_config['initial_response'],
        )

    @task
    def technical_support(self) -> Task:
        """技术支持任务"""
        return Task(
            config=self.tasks_config['technical_support'],
        )

    @task
    def quality_assurance(self) -> Task:
        """质量保证任务"""
        return Task(
            config=self.tasks_config['quality_assurance'],
        )

    # === 定义 Crew ===
    @crew
    def crew(self) -> Crew:
        """创建客户服务团队 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # 顺序执行
            verbose=True,
            memory=False,
            max_rpm=None,
            share_crew=False,
        )
