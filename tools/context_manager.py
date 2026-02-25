"""
上下文管理工具
标准工具实现，遵循 agent-learn 项目规范
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from dataclasses import dataclass, asdict

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
    """上下文管理器 - 核心实现"""
    
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
        recent_non_user = non_user_messages[-5:] if len(non_user_messages) > 5 else non_user_messages
        
        # 重新组合并排序
        compressed_messages = user_messages + recent_non_user
        compressed_messages.sort(key=lambda x: x.timestamp)
        
        # 计算压缩效果
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
        return int(len(str(message.content)) * 0.3)
    
    def to_openai_format(self) -> List[Dict[str, Any]]:
        """转换为 OpenAI API 格式"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

class ContextManagerTool:
    """上下文管理工具 - 标准工具接口"""
    
    enabled = True
    name = "manage_context"
    description = "管理对话上下文，包括监控令牌使用、执行压缩和获取统计信息"
    
    def __init__(self):
        self.context_manager = ContextManager()
    
    def to_openai_format(self) -> Dict[str, Any]:
        """转换为 OpenAI 工具格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["monitor", "compress", "stats", "clear", "recent"],
                            "description": "要执行的操作类型"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "获取最近消息的数量（仅在action='recent'时使用）",
                            "default": 5
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    
    def execute(self, action: str, limit: int = 5) -> Dict[str, Any]:
        """执行上下文管理操作"""
        try:
            cm = self.context_manager
            
            if action == "monitor":
                stats = cm.get_context_stats()
                return {
                    "success": True,
                    "data": stats,
                    "message": f"当前上下文使用 {stats['total_tokens']}/{stats['max_tokens']} 令牌 "
                              f"({stats['utilization_rate']*100:.1f}%)"
                }
            elif action == "compress":
                if cm.should_compress():
                    result = cm.compress_context()
                    return {
                        "success": True,
                        "data": result,
                        "message": f"上下文压缩完成，节省了 {result['compression_ratio']*100:.1f}% 的令牌"
                    }
                else:
                    return {
                        "success": True,
                        "data": {"compressed": False, "reason": "上下文未达到压缩阈值"},
                        "message": "上下文使用率较低，无需压缩"
                    }
            elif action == "stats":
                return {
                    "success": True,
                    "data": cm.get_context_stats(),
                    "message": "上下文统计信息获取成功"
                }
            elif action == "clear":
                count = len(cm.messages)
                cm.clear_context()
                return {
                    "success": True,
                    "data": {"cleared_messages": count},
                    "message": f"已清空 {count} 条消息"
                }
            elif action == "recent":
                messages = cm.get_recent_messages(limit)
                return {
                    "success": True,
                    "data": {"messages": messages, "count": len(messages)},
                    "message": f"获取到最近 {len(messages)} 条消息"
                }
            else:
                return {"success": False, "error": f"未知操作: {action}"}
                
        except Exception as e:
            logger.error(f"上下文管理执行失败: {str(e)}")
            return {"success": False, "error": str(e)}

# 兼容性函数
def get_context_stats():
    """获取上下文统计信息"""
    tool = ContextManagerTool()
    return tool.execute("stats")

def monitor_context():
    """监控上下文状态"""
    tool = ContextManagerTool()
    return tool.execute("monitor")

def compress_context():
    """压缩上下文"""
    tool = ContextManagerTool()
    return tool.execute("compress")