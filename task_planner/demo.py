#!/usr/bin/env python3
"""
Claude Task Planner Demo - 任务规划演示
展示 Claude 的计划与推理核心能力
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict

from dotenv import load_dotenv

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from llm.client import LLMClient
from utils.logger import setup_logging


load_dotenv()
logger = setup_logging(log_level="INFO", log_file="task_planner")


class TaskPlanningAgent:
    def __init__(self, client: LLMClient):
        self.client = client

    def plan(self, goal: str) -> Dict[str, Any]:
        system_prompt = (
            "你是一个项目任务规划助手。"
            "面向第一次接触 AI 代理的开发者，用分步骤的方式规划任务。\n"
            "请严格只输出一个 JSON 对象，不要任何解释或额外文本。\n"
            "JSON 结构示例:\n"
            "{\n"
            '  "goal_summary": "你理解到的目标摘要",\n'
            '  "tasks": [\n'
            '    {\n'
            '      "id": "task_1",\n'
            '      "title": "步骤名称",\n'
            '      "description": "一句话说明",\n'
            '      "priority": 1,\n'
            '      "estimated_hours": 2.0\n'
            "    }\n"
            "  ],\n"
            '  "execution_notes": "用一两句话解释推荐的执行顺序"\n'
            "}"
        )

        content = self.client.chat_simple(
            user_message=goal,
            system_prompt=system_prompt,
        )
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("LLM 输出中未找到 JSON 对象")
        json_text = content[start : end + 1]
        return json.loads(json_text)


def demo_llm_planning():
    client = LLMClient(model="gpt-4-turbo")
    agent = TaskPlanningAgent(client)

    print("🤖 Claude 任务规划演示（LLM 核心流程）")
    print("=" * 40)

    goal = "在一个月内上线一个简单的电商着陆页，用来测试市场反馈"
    print("用户目标:")
    print(goal)

    print("\nLLM 规划结果(JSON):\n")
    plan = agent.plan(goal)
    print(json.dumps(plan, ensure_ascii=False, indent=2))

    tasks_data = plan.get("tasks", [])
    tasks: List[Task] = []
    for index, item in enumerate(tasks_data, start=1):
        title = (item.get("title") or "").strip()
        description = (item.get("description") or "").strip()
        priority_value = item.get("priority")
        estimated_value = item.get("estimated_hours")
        if not isinstance(priority_value, int):
            priority_value = max(1, 5 - (index - 1))
        if not isinstance(estimated_value, (int, float)):
            estimated_value = 2.0
        task = Task(
            id=item.get("id") or f"llm_task_{index}",
            title=title or f"步骤{index}",
            description=description or title or f"步骤{index}",
            priority=priority_value,
            estimated_hours=float(estimated_value),
        )
        tasks.append(task)

    planner = TaskPlanner()
    for task in tasks:
        planner.add_task(task)

    print("\n解析为 Task 对象后的任务列表:")
    for task in planner.get_ready_tasks():
        print(f"  • [{task.priority}级] {task.id} - {task.title} ({task.estimated_hours}小时)")


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"

@dataclass
class Task:
    """任务数据类"""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1  # 1-5, 5为最高优先级
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    dependencies: List[str] = None
    assigned_to: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def can_start(self, completed_tasks: List[str]) -> bool:
        """检查任务是否可以开始（依赖是否满足）"""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def start_task(self) -> None:
        """开始任务"""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.IN_PROGRESS
            self.started_at = datetime.now()
    
    def complete_task(self) -> None:
        """完成任务"""
        if self.status == TaskStatus.IN_PROGRESS:
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.now()
            if self.started_at:
                self.actual_hours = (self.completed_at - self.started_at).total_seconds() / 3600
    
    def block_task(self, reason: str) -> None:
        """阻塞任务"""
        self.status = TaskStatus.BLOCKED
        self.metadata["blocking_reason"] = reason
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result["status"] = self.status.value
        result["created_at"] = self.created_at.isoformat() if self.created_at else None
        result["started_at"] = self.started_at.isoformat() if self.started_at else None
        result["completed_at"] = self.completed_at.isoformat() if self.completed_at else None
        return result

class TaskPlanner:
    """任务规划器"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.project_name = "Claude Task Planning Demo"
        self.start_date = datetime.now()
    
    def add_task(self, task: Task) -> None:
        """添加任务"""
        self.tasks[task.id] = task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def get_ready_tasks(self) -> List[Task]:
        """获取可以开始的任务（依赖已满足）"""
        completed_task_ids = [
            task_id for task_id, task in self.tasks.items() 
            if task.status == TaskStatus.COMPLETED
        ]
        
        ready_tasks = [
            task for task in self.tasks.values()
            if task.status == TaskStatus.PENDING and task.can_start(completed_task_ids)
        ]
        
        # 按优先级排序
        return sorted(ready_tasks, key=lambda x: x.priority, reverse=True)
    
    def get_blocked_tasks(self) -> List[Task]:
        """获取被阻塞的任务"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.BLOCKED]
    
    def get_in_progress_tasks(self) -> List[Task]:
        """获取进行中的任务"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.IN_PROGRESS]
    
    def get_completed_tasks(self) -> List[Task]:
        """获取已完成的任务"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.COMPLETED]
    
    def plan_project_timeline(self) -> Dict[str, Any]:
        """规划项目时间线"""
        total_estimated_hours = sum(task.estimated_hours for task in self.tasks.values())
        total_actual_hours = sum(task.actual_hours for task in self.tasks.values())
        
        # 简单的串行估算（实际项目中应该考虑并行执行）
        earliest_completion = self.start_date + timedelta(hours=total_estimated_hours)
        
        return {
            "project_name": self.project_name,
            "start_date": self.start_date.isoformat(),
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.get_completed_tasks()),
            "in_progress_tasks": len(self.get_in_progress_tasks()),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "blocked_tasks": len(self.get_blocked_tasks()),
            "total_estimated_hours": round(total_estimated_hours, 2),
            "total_actual_hours": round(total_actual_hours, 2),
            "earliest_completion_date": earliest_completion.isoformat(),
            "completion_percentage": round(len(self.get_completed_tasks()) / len(self.tasks) * 100, 1) if self.tasks else 0
        }
    
    def visualize_plan(self) -> str:
        """可视化任务计划"""
        timeline = self.plan_project_timeline()
        
        visualization = f"""
📋 项目计划可视化 - {self.project_name}
{'='*50}

📅 项目概览:
  开始日期: {timeline['start_date'][:10]}
  预计完成: {timeline['earliest_completion_date'][:10]}
  总任务数: {timeline['total_tasks']}
  完成进度: {timeline['completion_percentage']}%

📊 任务状态分布:
  ✅ 已完成: {timeline['completed_tasks']} 个任务
  🔄 进行中: {timeline['in_progress_tasks']} 个任务
  ⏳ 待开始: {timeline['pending_tasks']} 个任务
  ⛔ 已阻塞: {timeline['blocked_tasks']} 个任务

⏱️  工时统计:
  预估工时: {timeline['total_estimated_hours']} 小时
  实际工时: {timeline['total_actual_hours']} 小时
  效率比率: {round(timeline['total_actual_hours']/timeline['total_estimated_hours']*100, 1) if timeline['total_estimated_hours'] > 0 else 0}%

🎯 可以立即开始的任务:
"""
        
        ready_tasks = self.get_ready_tasks()
        if ready_tasks:
            for i, task in enumerate(ready_tasks[:5], 1):  # 显示前5个
                visualization += f"  {i}. [{task.priority}级] {task.title}\n"
                visualization += f"     预估: {task.estimated_hours}小时\n"
        else:
            visualization += "  暂无可以开始的任务\n"
        
        blocked_tasks = self.get_blocked_tasks()
        if blocked_tasks:
            visualization += "\n🚧 阻塞的任务:\n"
            for task in blocked_tasks[:3]:  # 显示前3个
                reason = task.metadata.get("blocking_reason", "未知原因")
                visualization += f"  • {task.title} - 阻塞原因: {reason}\n"
        
        return visualization


def demo_task_planning():
    print("此函数预留给进阶演示，目前未启用")

def main():
    """主函数"""
    print(f"🚀 Claude Task Planner Demo")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        print("🎯 演示1: 使用 LLM 规划并自动生成 Task 列表")
        print("-" * 30)
        demo_llm_planning()

        print("\n" + "=" * 40)
        print("✅ 任务规划演示完成!")
        print("\n💡 核心要点:")
        print("  • 把自然语言目标交给 LLM 做高层规划")
        print("  • 使用简单的数据结构在本地表达计划")
        print("  • TaskPlanner 专注于管理状态和依赖，执行由外部代理触发")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
