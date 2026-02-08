#!/usr/bin/env python
"""
Research Analysis Crew - 主程序入口

这个程序运行一个由多个 AI Agent 组成的研究分析团队，
包括首席研究员、数据收集专员、数据分析师和报告撰写专家。

监控功能：
    - 启用后，会自动发送 Agent 事件到监控服务器
    - 设置环境变量：
        export AGENT_MONITOR_ENABLED=true
        export AGENT_MONITOR_URL=http://localhost:8080
"""
import sys
from research_analysis_crew.crew import ResearchAnalysisCrew

# ==================== 监控插件导入 ====================
try:
    from agent_monitor import CrewAIPlugin
    MONITOR_AVAILABLE = True
    print("[INFO] Agent Monitor Plugin 已加载")
except ImportError:
    MONITOR_AVAILABLE = False
    print("[INFO] Agent Monitor Plugin 未安装，监控功能不可用")
# ===========================================================


def setup_monitor():
    """设置监控插件"""
    if not MONITOR_AVAILABLE:
        return

    import os

    if not os.getenv("AGENT_MONITOR_ENABLED"):
        print("[INFO] 监控未启用 (设置 AGENT_MONITOR_ENABLED=true 来启用)")
        return

    monitor_url = os.getenv("AGENT_MONITOR_URL")
    if not monitor_url:
        print("[WARN] AGENT_MONITOR_URL 未设置，监控功能无法使用")
        return

    try:
        plugin = CrewAIPlugin(monitor_url=monitor_url)
        plugin.install()
        print(f"[INFO] 监控已启用 -> {monitor_url}")
    except Exception as e:
        print(f"[ERROR] 监控插件安装失败: {e}")


def run():
    """运行研究分析 Crew"""
    # 设置监控
    setup_monitor()

    # 定义输入参数
    inputs = {
        'research_topic': '人工智能在医疗诊断中的应用现状和发展趋势'
    }

    print("=" * 60)
    print("🎬 启动研究分析团队")
    print("=" * 60)
    print(f"📚 研究主题：{inputs['research_topic']}")
    print("=" * 60)
    print()

    try:
        # 创建 Crew 实例
        research_crew = ResearchAnalysisCrew()

        # 执行 Crew
        result = research_crew.crew().kickoff(inputs=inputs)

        print()
        print("=" * 60)
        print("✅ 研究分析完成！")
        print("=" * 60)
        print()

        # 显示最终输出
        if result:
            print("=" * 60)
            print("📊 研究报告")
            print("=" * 60)
            print(str(result.raw))
            print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ 执行过程中出现错误")
        print("=" * 60)
        print(f"错误信息：{str(e)}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


class ResearchAnalysisCrewCLI:
    """命令行界面"""

    @staticmethod
    def run():
        """运行 Crew"""
        run()

    @staticmethod
    def repl():
        """
        REPL 模式 - 与研究分析团队进行交互
        """
        # 设置监控
        setup_monitor()

        research_crew = ResearchAnalysisCrew()

        print("=" * 60)
        print("🎭 研究分析团队 - REPL 模式")
        print("=" * 60)
        print("输入 'quit' 或 'exit' 退出")
        print()

        while True:
            try:
                topic = input("📚 请输入研究主题（或 quit 退出）: ").strip()

                if topic.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 再见！")
                    break

                if not topic:
                    print("⚠️  请输入一个研究主题")
                    continue

                inputs = {'research_topic': topic}

                print(f"\n📝 正在研究主题：{topic}...\n")

                result = research_crew.crew().kickoff(inputs=inputs)

                print("\n✅ 研究完成！\n")
                print("=" * 60)
                print(str(result.raw))
                print("=" * 60)
                print()

            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 错误：{str(e)}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "repl":
            ResearchAnalysisCrewCLI.repl()
        else:
            print("用法:")
            print("  python main.py          # 运行一次")
            print("  python main.py repl     # 交互模式")
    else:
        run()
