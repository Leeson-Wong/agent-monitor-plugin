#!/usr/bin/env python
"""
Code Review Crew - 主程序入口

这个程序运行一个由多个 AI Agent 组成的代码审查团队，
包括代码审查专家、安全审查专家和报告生成专家。

监控功能：
    - 启用后，会自动发送 Agent 事件到监控服务器
    - 设置环境变量：
        export AGENT_MONITOR_ENABLED=true
        export AGENT_MONITOR_URL=http://localhost:8080
"""
import sys
from code_review_crew.crew import CodeReviewCrew

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
    """运行代码审查 Crew"""
    # 设置监控
    setup_monitor()

    # 示例代码
    sample_code = '''
def process_user_data(user_id):
    # 获取用户数据
    import sqlite3
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 不安全的查询
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    user = cursor.fetchone()

    # 硬编码密钥
    api_key = "sk-1234567890abcdef"

    # 复杂的嵌套逻辑
    if user:
        if user[2] == "active":
            for item in user[3]:
                if item:
                    for detail in item:
                        if detail:
                            # 更多嵌套处理
                            result = process(detail)
                            if result:
                                if result.status == "ok":
                                    return result.data
    conn.close()
    return None

def process(item):
    class Result:
        def __init__(self):
            self.status = "ok"
            self.data = "processed"
    return Result()
'''

    inputs = {
        'code_to_review': sample_code,
        'language': 'Python',
        'context': '这是一个用户数据处理函数，需要审查代码质量和安全性'
    }

    print("=" * 60)
    print("🎬 启动代码审查团队")
    print("=" * 60)
    print(f"📝 语言：{inputs['language']}")
    print(f"📋 上下文：{inputs['context']}")
    print("=" * 60)
    print()

    try:
        # 创建 Crew 实例
        review_crew = CodeReviewCrew()

        # 执行 Crew
        result = review_crew.crew().kickoff(inputs=inputs)

        print()
        print("=" * 60)
        print("✅ 代码审查完成！")
        print("=" * 60)
        print()

        # 显示最终输出
        if result:
            print("=" * 60)
            print("📊 审查报告")
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


class CodeReviewCrewCLI:
    """命令行界面"""

    @staticmethod
    def run():
        """运行 Crew"""
        run()

    @staticmethod
    def repl():
        """
        REPL 模式 - 与代码审查团队进行交互
        """
        # 设置监控
        setup_monitor()

        review_crew = CodeReviewCrew()

        print("=" * 60)
        print("🎭 代码审查团队 - REPL 模式")
        print("=" * 60)
        print("输入 'quit' 或 'exit' 退出")
        print()

        while True:
            try:
                print("\n请输入要审查的代码（输入空行结束）:")
                print("(或输入 'quit' 退出)")

                lines = []
                while True:
                    line = input()
                    if line == 'quit' or line == 'exit' or line == 'q':
                        print("\n👋 再见！")
                        return
                    if line == '' and lines:
                        break
                    lines.append(line)

                code = '\n'.join(lines)

                if not code.strip():
                    print("⚠️  请输入代码")
                    continue

                language = input("编程语言（默认 Python）: ").strip() or "Python"
                context = input("上下文说明（可选）: ").strip() or "代码审查"

                inputs = {
                    'code_to_review': code,
                    'language': language,
                    'context': context
                }

                print(f"\n📝 正在审查代码...\n")

                result = review_crew.crew().kickoff(inputs=inputs)

                print("\n✅ 审查完成！\n")
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
            CodeReviewCrewCLI.repl()
        else:
            print("用法:")
            print("  python main.py          # 运行一次")
            print("  python main.py repl     # 交互模式")
    else:
        run()
