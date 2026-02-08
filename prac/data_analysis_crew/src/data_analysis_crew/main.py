#!/usr/bin/env python
"""
Data Analysis Crew - 主程序入口

这个程序运行一个由多个 AI Agent 组成的数据分析团队，
包括数据收集专员、数据分析师、洞察生成专家和报告专家。

监控功能：
    - 启用后，会自动发送 Agent 事件到监控服务器
    - 设置环境变量：
        export AGENT_MONITOR_ENABLED=true
        export AGENT_MONITOR_URL=http://localhost:8080
"""
import sys
from data_analysis_crew.crew import DataAnalysisCrew

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
    """运行数据分析 Crew"""
    # 设置监控
    setup_monitor()

    # 示例分析需求
    sample_data = '''
    以下是某电商平台过去一年的销售数据摘要：

    月度销售额（万元）：
    Q1: 1200, 1350, 1100
    Q2: 1400, 1550, 1600
    Q3: 1750, 1800, 1950
    Q4: 2100, 2400, 2800

    产品类别销售额占比：
    - 电子产品：35%
    - 服装：28%
    - 家居用品：18%
    - 食品：12%
    - 其他：7%

    客户数据：
    - 新客户增长率：平均每月15%
    - 客户留存率：72%
    - 平均客单价：450元
    - 复购率：45%
    '''

    inputs = {
        'analysis_goal': '分析销售趋势，识别增长机会，提供Q1战略建议',
        'data_description': sample_data,
        'business_context': '电商零售业务，关注增长和客户价值',
        'focus_areas': '销售趋势、产品表现、客户行为、增长机会'
    }

    print("=" * 60)
    print("🎬 启动数据分析团队")
    print("=" * 60)
    print(f"📊 分析目标：{inputs['analysis_goal']}")
    print(f"📋 业务背景：{inputs['business_context']}")
    print(f"🎯 关注领域：{inputs['focus_areas']}")
    print("=" * 60)
    print()

    try:
        # 创建 Crew 实例
        analysis_crew = DataAnalysisCrew()

        # 执行 Crew
        result = analysis_crew.crew().kickoff(inputs=inputs)

        print()
        print("=" * 60)
        print("✅ 数据分析完成！")
        print("=" * 60)
        print()

        # 显示最终输出
        if result:
            print("=" * 60)
            print("📄 分析报告")
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


class DataAnalysisCrewCLI:
    """命令行界面"""

    @staticmethod
    def run():
        """运行 Crew"""
        run()

    @staticmethod
    def repl():
        """
        REPL 模式 - 与数据分析团队进行交互
        """
        # 设置监控
        setup_monitor()

        analysis_crew = DataAnalysisCrew()

        print("=" * 60)
        print("🎭 数据分析团队 - REPL 模式")
        print("=" * 60)
        print("输入 'quit' 或 'exit' 退出")
        print()

        while True:
            try:
                goal = input("📊 分析目标（或 quit 退出）: ").strip()

                if goal.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 再见！")
                    break

                if not goal:
                    print("⚠️  请输入分析目标")
                    continue

                context = input("📋 业务背景（可选）: ").strip() or "通用业务分析"
                focus = input("🎯 关注领域（可选）: ").strip() or "整体分析"

                print("\n请输入数据描述（输入空行结束）:")
                lines = []
                while True:
                    line = input()
                    if line == '' and lines:
                        break
                    lines.append(line)

                data = '\n'.join(lines)

                if not data.strip():
                    print("⚠️  请输入数据描述")
                    continue

                inputs = {
                    'analysis_goal': goal,
                    'data_description': data,
                    'business_context': context,
                    'focus_areas': focus
                }

                print(f"\n📝 正在分析数据...\n")

                result = analysis_crew.crew().kickoff(inputs=inputs)

                print("\n✅ 分析完成！\n")
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
            DataAnalysisCrewCLI.repl()
        else:
            print("用法:")
            print("  python main.py          # 运行一次")
            print("  python main.py repl     # 交互模式")
    else:
        run()
