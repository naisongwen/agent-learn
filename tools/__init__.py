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
from tools.context_manager import ContextManagerTool
from tools.database import DatabaseTool

# 工具注册表
TOOL_REGISTRY = {
    "get_weather": WeatherTool(),
    "send_email": EmailTool(),
    "calculate": CalculatorTool(),
    "get_current_time": TimeTool(),
    "manage_context": ContextManagerTool(),
    "execute_sql": DatabaseTool(),
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

# 便捷函数
def demo_all_tools():
    """演示所有工具功能"""
    print("🔧 所有工具演示")
    print("=" * 40)
    
    enabled_tools = get_enabled_tool_names()
    print(f"启用的工具 ({len(enabled_tools)}个):")
    for tool_name in enabled_tools:
        print(f"  - {tool_name}")
    
    print(f"\n工具定义数量: {len(get_all_tools())}")

if __name__ == "__main__":
    demo_all_tools()