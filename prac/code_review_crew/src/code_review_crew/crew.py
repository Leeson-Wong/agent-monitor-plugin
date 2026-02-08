"""
Code Review Crew - 代码审查团队

这个模块定义了一个代码审查团队的 Crew、Agent 和 Task。
演示工具使用监控和专业的代码审查流程。
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent

# 导入自定义工具
from code_review_crew.tools import CodeComplexityTool, SecurityScanTool, CodeSmellDetector


@CrewBase
class CodeReviewCrew:
    """代码审查团队 Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # === 定义 Agents ===
    @agent
    def code_reviewer(self) -> Agent:
        """代码审查专家 Agent"""
        return Agent(
            config=self.agents_config['code_reviewer'],
            verbose=True,
            allow_delegation=False,
            tools=[
                CodeComplexityTool(),
                CodeSmellDetector(),
            ],
        )

    @agent
    def security_specialist(self) -> Agent:
        """安全审查专家 Agent"""
        return Agent(
            config=self.agents_config['security_specialist'],
            verbose=True,
            allow_delegation=False,
            tools=[
                SecurityScanTool(),
            ],
        )

    @agent
    def report_generator(self) -> Agent:
        """报告生成专家 Agent"""
        return Agent(
            config=self.agents_config['report_generator'],
            verbose=True,
            allow_delegation=False,
        )

    # === 定义 Tasks ===
    @task
    def code_quality_review(self) -> Task:
        """代码质量审查任务"""
        return Task(
            config=self.tasks_config['code_quality_review'],
        )

    @task
    def security_review(self) -> Task:
        """安全审查任务"""
        return Task(
            config=self.tasks_config['security_review'],
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
        """创建代码审查团队 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # 顺序执行
            verbose=True,
            memory=False,
            max_rpm=None,
            share_crew=False,
        )
