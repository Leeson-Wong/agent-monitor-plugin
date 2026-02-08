#!/usr/bin/env python
"""
Customer Service Crew - 主程序入口

这个程序运行一个由多个 AI Agent 组成的客户服务团队，
包括前台接待、专家处理和主管监督三个角色。

监控功能：
    - 启用后，会自动发送 Agent 事件到监控服务器
    - 设置环境变量：
        export AGENT_MONITOR_ENABLED=true
        export AGENT_MONITOR_URL=http://localhost:8080
"""
import sys
from customer_service_crew.crew import CustomerServiceCrew

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
    """运行客服 Crew"""
    # 设置监控
    setup_monitor()

    # 定义输入参数
    inputs = {
        'customer_inquiry': '''
        尊敬的客服团队，

        我最近购买了你们的云服务产品，但在使用过程中遇到了一些问题：

        1. 我无法上传超过100MB的文件，系统总是提示超时错误
        2. 我的账户显示的存储空间与实际使用不符
        3. 我希望能升级到企业版，但不确定具体流程

        请帮我解决这些问题，谢谢！

        客户：张先生
        '''
    }

    print("=" * 60)
    print("🎬 启动客户服务团队")
    print("=" * 60)
    print(f"📧 收到客户咨询")
    print("=" * 60)
    print()

    try:
        # 创建 Crew 实例
        service_crew = CustomerServiceCrew()

        # 执行 Crew
        result = service_crew.crew().kickoff(inputs=inputs)

        print()
        print("=" * 60)
        print("✅ 客户服务完成！")
        print("=" * 60)
        print()

        # 显示最终输出
        if result:
            print("=" * 60)
            print("📋 服务报告")
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


class CustomerServiceCrewCLI:
    """命令行界面"""

    @staticmethod
    def run():
        """运行 Crew"""
        run()

    @staticmethod
    def repl():
        """
        REPL 模式 - 与客服团队进行交互
        """
        # 设置监控
        setup_monitor()

        service_crew = CustomerServiceCrew()

        print("=" * 60)
        print("🎭 客户服务团队 - REPL 模式")
        print("=" * 60)
        print("输入 'quit' 或 'exit' 退出")
        print()

        while True:
            try:
                print("\n请输入客户咨询内容（或 quit 退出）:")
                print("(多行输入，输入空行结束)")
                lines = []
                while True:
                    line = input()
                    if line == '' and lines:
                        break
                    lines.append(line)

                inquiry = '\n'.join(lines)

                if inquiry.strip().lower() in ['quit', 'exit', 'q']:
                    print("\n👋 再见！")
                    break

                inputs = {'customer_inquiry': inquiry}

                print(f"\n📝 正在处理客户咨询...\n")

                result = service_crew.crew().kickoff(inputs=inputs)

                print("\n✅ 处理完成！\n")
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
            CustomerServiceCrewCLI.repl()
        else:
            print("用法:")
            print("  python main.py          # 运行一次")
            print("  python main.py repl     # 交互模式")
    else:
        run()
