"""
Translation Crew - 翻译团队

这个模块定义了一个翻译团队的 Crew、Agent 和 Task。
演示简单工作流和质量保证流程。
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class TranslationCrew:
    """翻译团队 Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # === 定义 Agents ===
    @agent
    def translator(self) -> Agent:
        """专业翻译员 Agent"""
        return Agent(
            config=self.agents_config['translator'],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def quality_editor(self) -> Agent:
        """翻译质量编辑 Agent"""
        return Agent(
            config=self.agents_config['quality_editor'],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def final_editor(self) -> Agent:
        """最终审校编辑 Agent"""
        return Agent(
            config=self.agents_config['final_editor'],
            verbose=True,
            allow_delegation=False,
        )

    # === 定义 Tasks ===
    @task
    def translation_task(self) -> Task:
        """翻译任务"""
        return Task(
            config=self.tasks_config['translation_task'],
        )

    @task
    def quality_review(self) -> Task:
        """质量审查任务"""
        return Task(
            config=self.tasks_config['quality_review'],
        )

    @task
    def final_polish(self) -> Task:
        """最终润色任务"""
        return Task(
            config=self.tasks_config['final_polish'],
        )

    # === 定义 Crew ===
    @crew
    def crew(self) -> Crew:
        """创建翻译团队 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # 顺序执行
            verbose=True,
            memory=False,
            max_rpm=None,
            share_crew=False,
        )
