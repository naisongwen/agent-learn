import sys
import os
from datetime import datetime

from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from llm.client import LLMClient
from utils.logger import setup_logging


load_dotenv()
logger = setup_logging(log_level="INFO", log_file="task_decomposer")


class TaskDecomposerAgent:
    def __init__(self, client: LLMClient):
        self.client = client

    def decompose(self, goal: str) -> str:
        system_prompt = (
            "你是一个任务分解助手。"
            "面向完全没有经验的开发者，用最简单的方式把目标拆成3-7个步骤。\n"
            "要求：\n"
            "1. 先用一句话重复理解到的目标。\n"
            "2. 然后输出\"步骤清单:\"，下面按顺序列出步骤：\n"
            "   - 每步一行，格式为：`数字. 步骤名称 — 一句话说明`。\n"
            "3. 最后输出\"思考提示:\"，给出1-2条下一步可以交给代理的子任务。"
        )

        content = self.client.chat_simple(
            user_message=goal,
            system_prompt=system_prompt,
        )
        return content


def demo_basic_decomposition():
    client = LLMClient(model="gpt-4-turbo")
    agent = TaskDecomposerAgent(client)

    print("🤖 Claude 任务分解演示")
    print("=" * 40)

    goal = "在一周内搭建一个可以发布文章的个人博客网站"
    print("用户目标:")
    print(goal)

    print("\nLLM 分解结果:\n")
    plan = agent.decompose(goal)
    print(plan)


def main():
    print("🚀 Claude Task Decomposer Demo")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        demo_basic_decomposition()

        print("\n" + "=" * 40)
        print("✅ 任务分解演示完成")
        print("\n💡 核心要点:")
        print("  • 只关心输入目标和输出步骤")
        print("  • 把复杂问题交给 LLM 负责拆解")
        print("  • 代码层面只做少量编排")
    except Exception as e:
        print("\n❌ 运行出错:", e)
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

