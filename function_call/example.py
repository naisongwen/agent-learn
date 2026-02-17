#!/usr/bin/env python3
"""
Agent-Learn 简化示例
展示核心功能使用方法
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def demo_basic_tools():
    """演示基础工具使用"""
    print("🔧 基础工具演示")
    print("=" * 40)
    
    # 导入工具
    from tools import get_tool_by_name
    
    # 1. 天气工具
    print("\n🌤️  天气查询:")
    weather_tool = get_tool_by_name("get_weather")
    result = weather_tool.execute("北京")
    if result["success"]:
        data = result["data"]
        print(f"  城市: {data['location']}")
        print(f"  温度: {data['temperature']}°C")
        print(f"  天气: {data['condition']}")
    
    # 2. 计算器工具
    print("\n🧮 数学计算:")
    calc_tool = get_tool_by_name("calculate")
    result = calc_tool.execute("(123 + 456) * 789")
    if result["success"]:
        data = result["data"]
        print(f"  表达式: {data['expression']}")
        print(f"  结果: {data['result']}")
    
    # 3. 时间工具
    print("\n⏰ 时间查询:")
    time_tool = get_tool_by_name("get_current_time")
    result = time_tool.execute()
    if result["success"]:
        data = result["data"]
        print(f"  当前时间: {data['datetime']}")
        print(f"  星期: {data['weekday']}")

def demo_tool_registration():
    """演示工具注册机制"""
    print("\n📋 工具注册信息")
    print("=" * 40)
    
    from tools import get_enabled_tool_names, get_all_tools
    
    # 显示启用的工具
    enabled_tools = get_enabled_tool_names()
    print(f"启用的工具 ({len(enabled_tools)}个):")
    for tool_name in enabled_tools:
        print(f"  - {tool_name}")
    
    # 显示工具定义
    print(f"\n工具定义数量: {len(get_all_tools())}")

def demo_validation():
    """演示参数验证功能"""
    print("\n🛡️  参数验证演示")
    print("=" * 40)
    
    from utils.validators import validate_tool_call
    
    # 合法调用
    print("\n✅ 合法调用:")
    result = validate_tool_call("calculate", {"expression": "2+2"})
    print(f"  计算 '2+2': {result}")
    
    # 非法调用
    print("\n❌ 非法调用:")
    result = validate_tool_call("calculate", {"expression": "import os"})  
    print(f"  计算 'import os': {result}")

def demo_rate_limiting():
    """演示速率限制功能"""
    print("\n⏱️  速率限制演示")
    print("=" * 40)
    
    from utils.rate_limiter import RateLimiter
    import time
    
    limiter = RateLimiter(limit_per_minute=5)  # 限制每分钟5次
    
    print("执行5次快速调用...")
    start_time = time.time()
    
    for i in range(5):
        limiter.acquire()
        print(f"  第{i+1}次调用: {time.time() - start_time:.2f}秒")
    
    print("速率限制生效!")

def main():
    """主函数"""
    print("🤖 Agent-Learn 功能演示")
    print("=" * 50)
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your-api-key-here":
        print("⚠️  注意: 请在 .env 文件中设置有效的 OPENAI_API_KEY")
        print("   当前演示仅展示本地工具功能\n")
    
    try:
        demo_basic_tools()
        demo_tool_registration()
        demo_validation()
        demo_rate_limiting()
        
        print("\n" + "=" * 50)
        print("🎉 演示完成!")
        print("\n💡 完整功能体验:")
        print("   运行: python -m function_call.main")
        print("   健康检查: python test_project.py")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        print("请检查项目配置和依赖安装")

if __name__ == "__main__":
    main()
