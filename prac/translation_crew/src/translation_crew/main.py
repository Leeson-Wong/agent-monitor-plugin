#!/usr/bin/env python
"""
Translation Crew - 主程序入口

这个程序运行一个由多个 AI Agent 组成的翻译团队，
包括专业翻译员、质量编辑和最终审校编辑。

监控功能：
    - 启用后，会自动发送 Agent 事件到监控服务器
    - 设置环境变量：
        export AGENT_MONITOR_ENABLED=true
        export AGENT_MONITOR_URL=http://localhost:8080
"""
import sys
from translation_crew.crew import TranslationCrew

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
    """运行翻译 Crew"""
    # 设置监控
    setup_monitor()

    # 示例文本
    sample_text = '''
    人工智能技术正在快速发展，深度学习、自然语言处理和计算机视觉等领域的突破
    为各行各业带来了新的机遇。然而，我们也必须关注技术发展带来的挑战，
    包括数据隐私、算法偏见和就业影响等问题。只有在技术创新和社会责任之间
    找到平衡，我们才能真正实现人工智能的可持续发展。
    '''

    inputs = {
        'source_text': sample_text,
        'source_language': '中文',
        'target_language': '英文',
        'context': '这是一段关于人工智能发展的评论文章',
        'tone': '专业、正式'
    }

    print("=" * 60)
    print("🎬 启动翻译团队")
    print("=" * 60)
    print(f"📝 源语言：{inputs['source_language']}")
    print(f"📝 目标语言：{inputs['target_language']}")
    print(f"📋 上下文：{inputs['context']}")
    print(f"🎨 语调：{inputs['tone']}")
    print("=" * 60)
    print()

    try:
        # 创建 Crew 实例
        translation_crew = TranslationCrew()

        # 执行 Crew
        result = translation_crew.crew().kickoff(inputs=inputs)

        print()
        print("=" * 60)
        print("✅ 翻译完成！")
        print("=" * 60)
        print()

        # 显示最终输出
        if result:
            print("=" * 60)
            print("📄 最终翻译")
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


class TranslationCrewCLI:
    """命令行界面"""

    @staticmethod
    def run():
        """运行 Crew"""
        run()

    @staticmethod
    def repl():
        """
        REPL 模式 - 与翻译团队进行交互
        """
        # 设置监控
        setup_monitor()

        translation_crew = TranslationCrew()

        print("=" * 60)
        print("🎭 翻译团队 - REPL 模式")
        print("=" * 60)
        print("输入 'quit' 或 'exit' 退出")
        print()

        while True:
            try:
                source_lang = input("源语言（默认 中文）: ").strip() or "中文"
                target_lang = input("目标语言（默认 英文）: ").strip() or "英文"
                context = input("上下文说明（可选）: ").strip() or "通用翻译"

                print("\n请输入要翻译的文本（输入空行结束）:")
                lines = []
                while True:
                    line = input()
                    if line == '' and lines:
                        break
                    lines.append(line)

                text = '\n'.join(lines)

                if not text.strip():
                    print("⚠️  请输入文本")
                    continue

                inputs = {
                    'source_text': text,
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'context': context,
                    'tone': '自然流畅'
                }

                print(f"\n📝 正在翻译从 {source_lang} 到 {target_lang}...\n")

                result = translation_crew.crew().kickoff(inputs=inputs)

                print("\n✅ 翻译完成！\n")
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
            TranslationCrewCLI.repl()
        else:
            print("用法:")
            print("  python main.py          # 运行一次")
            print("  python main.py repl     # 交互模式")
    else:
        run()
