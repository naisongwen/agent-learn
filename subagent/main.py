#!/usr/bin/env python3

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
logger = setup_logging(log_level="INFO", log_file="subagent")


class PlannerSubagent:
    def __init__(self, client: LLMClient):
        self.client = client

    def run(self, goal: str) -> str:
        system_prompt = (
            "你是项目规划子代理。"
            "负责把高层目标拆成 3-7 个小任务，按顺序列出。"
            "只输出任务列表，每行一个步骤。"
        )
        return self.client.chat_simple(
            user_message=goal,
            system_prompt=system_prompt,
        )


class ImplementSubagent:
    def __init__(self, client: LLMClient):
        self.client = client

    def run(self, task_description: str) -> str:
        system_prompt = (
            "你是实现子代理。"
            "针对给定的单个任务，输出一个非常具体的执行方案，"
            "包含 3-5 步的操作清单。"
        )
        return self.client.chat_simple(
            user_message=task_description,
            system_prompt=system_prompt,
        )


def run_main_agent(goal: str) -> None:
    client = LLMClient(model="gpt-4-turbo")
    planner = PlannerSubagent(client)
    implementer = ImplementSubagent(client)

    print("🤖 主代理: 接收到用户目标")
    print(goal)

    print("\n🧩 子代理1: 规划子代理开始工作...")
    plan_text = planner.run(goal)
    print(plan_text)

    first_task = plan_text.splitlines()[0].strip() if plan_text else ""
    if not first_task:
        print("\n⚠️ 无法从规划结果中提取第一个任务")
        return

    print("\n🛠️ 子代理2: 实现子代理针对第一个任务给出细化方案...")
    detailed_plan = implementer.run(first_task)
    print(detailed_plan)


def main():
    print("🚀 Subagent Demo")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        goal = "在一周内搭建一个可以发布文章的个人技术博客，并支持基本的访问统计。"
        run_main_agent(goal)
        print("\n✅ Subagent 演示完成")
        print("主代理只负责拆分角色，具体思考交给子代理完成。")
    except Exception as e:
        print("\n❌ 运行出错:", e)
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

