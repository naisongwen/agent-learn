"""
上下文管理器
处理对话历史、令牌计数和上下文压缩
"""

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Message:
    """消息数据类"""
    role: str
    content: str
    timestamp: datetime = None
    task_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            "metadata": self.metadata or {}
        }

class ContextManager:
    """上下文管理器"""
    
    def __init__(self, max_tokens: int = 4000, compression_threshold: float = 0.8):
        self.max_tokens = max_tokens
        self.compression_threshold = compression_threshold
        self.messages: List[Message] = []
        self.token_count = 0
        self.compression_count = 0
        
    def add_message(self, message: Message) -> None:
        """添加消息到上下文"""
        self.messages.append(message)
        self.token_count += self._count_tokens(message)
        logger.debug(f"添加消息: {message.role}, 当前令牌数: {self.token_count}")
    
    def add_message_dict(self, message_dict: Dict[str, Any]) -> None:
        """添加字典格式的消息"""
        message = Message(
            role=message_dict["role"],
            content=message_dict["content"],
            task_id=message_dict.get("task_id"),
            metadata=message_dict.get("metadata")
        )
        self.add_message(message)
    
    def should_compress(self) -> bool:
        """判断是否需要压缩上下文"""
        threshold_tokens = int(self.max_tokens * self.compression_threshold)
        needs_compression = self.token_count > threshold_tokens
        if needs_compression:
            logger.info(f"触发压缩: {self.token_count} > {threshold_tokens} tokens")
        return needs_compression
    
    def compress_context(self) -> Dict[str, Any]:
        """执行上下文压缩"""
        if not self.messages:
            return {"compressed": False, "reason": "无消息可压缩"}
        
        logger.info("开始执行上下文压缩...")
        
        # 保留策略：用户消息 + 最近N条非用户消息
        user_messages = [msg for msg in self.messages if msg.role == "user"]
        non_user_messages = [msg for msg in self.messages if msg.role != "user"]
        
        # 保留最近的5条非用户消息
        recent_non_user = non_user_messages[-5:] if len(non_user_messages) > 5 else non_user_messages
        
        # 重新组合消息列表
        compressed_messages = user_messages + recent_non_user
        
        # 按时间排序保持顺序
        compressed_messages.sort(key=lambda x: x.timestamp)
        
        # 计算压缩前后的令牌数
        old_token_count = self.token_count
        new_token_count = sum(self._count_tokens(msg) for msg in compressed_messages)
        
        # 更新状态
        self.messages = compressed_messages
        self.token_count = new_token_count
        self.compression_count += 1
        
        compression_stats = {
            "compressed": True,
            "original_tokens": old_token_count,
            "compressed_tokens": new_token_count,
            "compression_ratio": round((old_token_count - new_token_count) / old_token_count, 3),
            "messages_removed": len(non_user_messages) - len(recent_non_user),
            "compression_count": self.compression_count
        }
        
        logger.info(f"压缩完成: {old_token_count} → {new_token_count} tokens "
                   f"(压缩率: {compression_stats['compression_ratio']*100:.1f}%)")
        
        return compression_stats
    
    def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
        role_counts = {}
        task_counts = {}
        
        for msg in self.messages:
            role_counts[msg.role] = role_counts.get(msg.role, 0) + 1
            if msg.task_id:
                task_counts[msg.task_id] = task_counts.get(msg.task_id, 0) + 1
        
        return {
            "total_messages": len(self.messages),
            "total_tokens": self.token_count,
            "max_tokens": self.max_tokens,
            "compression_threshold": self.compression_threshold,
            "compression_count": self.compression_count,
            "role_distribution": role_counts,
            "task_distribution": task_counts,
            "utilization_rate": round(self.token_count / self.max_tokens, 3)
        }
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的消息"""
        recent = self.messages[-limit:] if len(self.messages) > limit else self.messages
        return [msg.to_dict() for msg in recent]
    
    def clear_context(self) -> None:
        """清空上下文"""
        self.messages.clear()
        self.token_count = 0
        logger.info("上下文已清空")
    
    def _count_tokens(self, message: Message) -> int:
        """估算消息的令牌数"""
        # 简化的令牌计算：每个字符约0.3个token
        text_content = str(message.content)
        return int(len(text_content) * 0.3)
    
    def to_openai_format(self) -> List[Dict[str, Any]]:
        """转换为 OpenAI API 格式"""
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in self.messages
        ]

# 便捷函数
def create_context_manager(max_tokens: int = 4000) -> ContextManager:
    """创建上下文管理器实例"""
    return ContextManager(max_tokens=max_tokens)

def demo_context_management():
    """演示上下文管理功能"""
    print("🤖 上下文管理器演示")
    print("=" * 40)
    
    # 创建管理器
    cm = ContextManager(max_tokens=1000, compression_threshold=0.7)
    
    # 添加测试消息
    test_messages = [
        {"role": "user", "content": "分析项目代码结构"},
        {"role": "assistant", "content": "正在分析...", "task_id": "task_001"},
        {"role": "tool", "content": "发现3个主要模块", "task_id": "task_001"},
        {"role": "assistant", "content": "分析完成，建议如下..."},
        {"role": "user", "content": "请详细说明第一个模块"},
        {"role": "assistant", "content": "第一个模块是认证系统..."},
        {"role": "user", "content": "帮我重构这个模块"},
        {"role": "assistant", "content": "开始重构...", "task_id": "task_002"},
        {"role": "tool", "content": "重构完成，测试通过", "task_id": "task_002"},
        {"role": "assistant", "content": "重构已完成，主要改进..."},
    ]
    
    print("📥 添加测试消息...")
    for i, msg_dict in enumerate(test_messages):
        cm.add_message_dict(msg_dict)
        print(f"  消息 {i+1}: {msg_dict['role']} - {len(msg_dict['content'])} 字符")
    
    # 显示统计信息
    stats = cm.get_context_stats()
    print(f"\n📊 上下文统计:")
    print(f"  总消息数: {stats['total_messages']}")
    print(f"  总令牌数: {stats['total_tokens']}")
    print(f"  利用率: {stats['utilization_rate']*100:.1f}%")
    print(f"  角色分布: {stats['role_distribution']}")
    
    # 检查压缩需求
    if cm.should_compress():
        compression_result = cm.compress_context()
        print(f"\n🔄 压缩结果:")
        print(f"  压缩前: {compression_result['original_tokens']} tokens")
        print(f"  压缩后: {compression_result['compressed_tokens']} tokens")
        print(f"  压缩率: {compression_result['compression_ratio']*100:.1f}%")
    
    # 显示最近消息
    print(f"\n📝 最近3条消息:")
    recent = cm.get_recent_messages(3)
    for msg in recent:
        print(f"  [{msg['role']}] {msg['content'][:50]}...")
    
    return cm

if __name__ == "__main__":
    demo_context_management()