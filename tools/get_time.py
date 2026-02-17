"""
时间查询工具
获取当前时间和日期
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TimeTool:
    """时间查询工具"""
    
    enabled = True
    name = "get_current_time"
    description = "获取当前时间和日期。支持指定时区。当用户询问时间、日期、时区转换时使用。"
    
    # 常用时区映射
    TIMEZONES = {
        "北京": "Asia/Shanghai",
        "上海": "Asia/Shanghai",
        "东京": "Asia/Tokyo",
        "纽约": "America/New_York",
        "伦敦": "Europe/London",
        "巴黎": "Europe/Paris",
        "悉尼": "Australia/Sydney",
        "洛杉矶": "America/Los_Angeles",
    }
    
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
                        "timezone": {
                            "type": "string",
                            "description": "时区名称，如'Asia/Shanghai'、'America/New_York'，或城市名如'北京'、'纽约'"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["full", "date_only", "time_only"],
                            "description": "返回格式，默认full"
                        }
                    }
                }
            }
        }
    
    def execute(self, timezone: Optional[str] = None, format: str = "full") -> Dict[str, Any]:
        """获取当前时间"""
        try:
            # 解析时区
            tz_string = self._resolve_timezone(timezone)
            
            # 获取时间
            now = datetime.now()
            
            # 格式化输出
            if format == "date_only":
                time_str = now.strftime("%Y年%m月%d日")
            elif format == "time_only":
                time_str = now.strftime("%H:%M:%S")
            else:
                time_str = now.strftime("%Y年%m月%d日 %H:%M:%S")
            
            return {
                "success": True,
                "data": {
                    "datetime": time_str,
                    "timezone": tz_string,
                    "timestamp": now.timestamp(),
                    "weekday": now.strftime("%A")
                }
            }
            
        except Exception as e:
            logger.error(f"时间查询失败：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _resolve_timezone(self, timezone: Optional[str]) -> str:
        """解析时区字符串"""
        if not timezone:
            return "Asia/Shanghai"
        
        # 检查是否是城市名
        if timezone in self.TIMEZONES:
            return self.TIMEZONES[timezone]
        
        # 直接返回（假设是标准时区名）
        return timezone


if __name__ == "__main__":
    tool = TimeTool()
    result = tool.execute()
    print(result)
