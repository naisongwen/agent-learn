"""
LLM客户端封装
处理与OpenAI API的交互
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# 确保能够导入项目模块
import sys
import os as os_path
project_root = os_path.path.dirname(os_path.path.dirname(os_path.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools import get_all_tools, get_tool_by_name
from utils.validators import validate_tool_call
from utils.rate_limiter import RateLimiter

load_dotenv()
logger = logging.getLogger(__name__)

class LLMClient:
    """LLM客户端"""
    
    def __init__(self, model: str = None):
        self.model = model or os.getenv("DEFAULT_MODEL", "gpt-4-turbo")
        self.max_conversation_history = int(os.getenv("MAX_CONVERSATION_HISTORY", 20))
        self.max_tool_call_retries = int(os.getenv("MAX_TOOL_CALL_RETRIES", 3))
        self.enable_logging = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # 配置日志
        if self.enable_logging:
            logging.basicConfig(
                level=getattr(logging, self.log_level),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.tools = get_all_tools()
        self.rate_limiter = RateLimiter(
            limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
        )
        self.max_retries = int(os.getenv("MAX_RETRIES", 3))
    
    def chat(self, messages: List[Dict[str, Any]], 
             tool_choice: str = "auto",
             max_turns: int = 5) -> Dict[str, Any]:
        """
        执行对话，支持多轮工具调用
        
        Args:
            messages: 对话历史
            tool_choice: 工具选择策略 (auto/required/none)
            max_turns: 最大工具调用轮数
        
        Returns:
            最终响应
        """
        current_messages = messages.copy()
        
        # 直接使用tools参数，让LLM自主判断是否需要调用工具
        
        for turn in range(max_turns):
            logger.info(f"对话轮次：{turn + 1}")
            
            try:
                # 速率限制检查
                self.rate_limiter.acquire()
                
                # 调用API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=current_messages,
                    tools=self.tools,
                    tool_choice=tool_choice,
                    temperature=0.7,
                )
                
                assistant_message = response.choices[0].message
                current_messages.append(assistant_message)
                
                # 检查是否有工具调用
                if not assistant_message.tool_calls:
                    # 没有工具调用，返回最终回答
                    return {
                        "success": True,
                        "content": assistant_message.content,
                        "tool_calls_count": turn + 1,
                        "messages": current_messages
                    }
                
                # 处理工具调用
                for tool_call in assistant_message.tool_calls:
                    result = self._execute_tool_call(tool_call)
                    
                    # 添加工具响应到消息历史
                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                    
                    logger.info(f"工具调用完成：{tool_call.function.name}")
                
            except Exception as e:
                logger.error(f"对话失败：{str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "messages": current_messages
                }
        
        # 达到最大轮数，调用 LLM 生成最终答案
        logger.warning("达到最大工具调用轮数，生成最终答案")
        try:
            self.rate_limiter.acquire()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                temperature=0.7,
            )
            final_answer = response.choices[0].message.content
            return {
                "success": True,
                "content": final_answer,
                "tool_calls_count": max_turns,
                "messages": current_messages
            }
        except Exception as e:
            return {
                "success": True,
                "content": "抱歉，处理过程过于复杂，未能完成所有操作。",
                "tool_calls_count": max_turns,
                "messages": current_messages
            }
    
    def _execute_tool_call(self, tool_call) -> Dict[str, Any]:
        """执行单个工具调用"""
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # 安全验证
        validation_result = validate_tool_call(function_name, function_args)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"]
            }
        
        # 获取工具实例
        tool = get_tool_by_name(function_name)
        if not tool:
            return {
                "success": False,
                "error": f"未找到工具：{function_name}"
            }
        
        # 执行工具
        try:
            result = tool.execute(**function_args)
            return result
        except Exception as e:
            logger.error(f"工具执行失败：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def chat_simple(self, user_message: str, 
                    system_prompt: Optional[str] = None) -> str:
        """
        简单对话（不使用工具）
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
        
        Returns:
            AI响应
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"聊天失败: {str(e)}")
            return f"聊天失败: {str(e)}"

# 使用示例
if __name__ == "__main__":
    client = LLMClient()
    
    # 简单对话
    response = client.chat_simple("你好，请介绍一下自己")
    print(response)
    
    # 带工具调用的对话
    messages = [{"role": "user", "content": "北京今天天气怎么样？"}]
    result = client.chat(messages)
    print(result["content"])