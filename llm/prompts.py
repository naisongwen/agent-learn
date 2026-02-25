"""
系统提示词定义
"""

class SystemPrompts:
    """系统提示词类"""
    
    @staticmethod
    def get_default_prompt():
        """获取默认系统提示词"""
        return "你是一个有用的AI助手。"
    
    @staticmethod 
    def get_tool_calling_prompt():
        """获取工具调用相关的系统提示词"""
        return """你是一个具有工具调用能力的AI助手。
你可以根据需要调用各种工具来完成任务。
请根据用户的需求选择合适的工具并正确使用。"""