"""
工具模块初始化
注册所有可用工具
"""

# 修复相对导入问题
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.weather import WeatherTool
from tools.email import EmailTool  
from tools.calculator import CalculatorTool
from tools.get_time import TimeTool

# 工具注册表
TOOL_REGISTRY = {
    "get_weather": WeatherTool(),
    "send_email": EmailTool(),
    "calculate": CalculatorTool(),
    "get_current_time": TimeTool(),
}

def get_all_tools():
    """获取所有工具的 OpenAI 格式定义"""
    return [tool.to_openai_format() for tool in TOOL_REGISTRY.values() if tool.enabled]

def get_tool_by_name(name: str):
    """根据名称获取工具实例"""
    return TOOL_REGISTRY.get(name)

def get_enabled_tool_names():
    """获取所有启用的工具名称"""
    return [name for name, tool in TOOL_REGISTRY.items() if tool.enabled]
