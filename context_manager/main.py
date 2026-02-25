#!/usr/bin/env python3
"""
Claude Context Manager - 规范入口文件
引用 tools 目录中的标准工具实现
"""

import sys
import os
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 引用标准工具
from tools.context_manager import ContextManagerTool

def demo_core_concepts():
    """核心概念演示 - 使用标准工具"""
    print("🤖 Claude 上下文管理演示")
    print("=" * 40)
    
    # 使用标准工具
    context_tool = ContextManagerTool()
    
    print("🎯 演示1: 函数调用模拟")
    print("-" * 25)
    
    # 模拟工具调用场景
    test_messages = [
        {"role": "user", "content": "计算 (123+456)*789"},
        {"role": "assistant", "content": "正在计算...", "task_id": "calc_001"},
        {"role": "tool", "content": "计算结果：555435", "task_id": "calc_001"},
        {"role": "assistant", "content": "计算完成，结果是 555435"},
        {"role": "user", "content": "查询北京天气"},
        {"role": "assistant", "content": "正在查询天气...", "task_id": "weather_001"},
        {"role": "tool", "content": "北京天气：晴，15°C", "task_id": "weather_001"},
    ]
    
    # 通过工具接口添加消息
    cm = context_tool.context_manager
    for msg_dict in test_messages:
        cm.add_message_dict(msg_dict)
        print(f"  [{msg_dict['role']}] {msg_dict['content']}")
    
    # 监控上下文状态
    monitor_result = context_tool.execute("monitor")
    if monitor_result["success"]:
        data = monitor_result["data"]
        print(f"\n📊 上下文状态: {data['total_messages']} 消息, {data['total_tokens']} 令牌")
    
    print("\n🎯 演示2: 代理循环模拟")
    print("-" * 25)
    
    # 模拟完整代理循环
    conversation = [
        {"role": "user", "content": "帮我分析项目代码结构"},
        {"role": "assistant", "content": "正在分析项目结构..."},
        {"role": "tool", "content": "发现3个主要模块：auth, api, utils"},
        {"role": "assistant", "content": "分析完成。建议按模块分别重构"},
        {"role": "user", "content": "先重构认证模块"},
        {"role": "assistant", "content": "开始重构认证模块..."},
        {"role": "tool", "content": "认证模块重构完成，测试通过"},
        {"role": "assistant", "content": "认证模块重构完毕，主要改进：增加了JWT支持"},
    ]
    
    for msg_dict in conversation:
        cm.add_message_dict(msg_dict)
        print(f"  [{msg_dict['role']}] {msg_dict['content']}")
    
    # 获取详细统计
    stats_result = context_tool.execute("stats")
    if stats_result["success"]:
        data = stats_result["data"]
        print(f"\n📊 详细统计:")
        print(f"  总消息数: {data['total_messages']}")
        print(f"  总令牌数: {data['total_tokens']}")
        print(f"  使用率: {data['utilization_rate']*100:.1f}%")
        print(f"  角色分布: {data['role_distribution']}")
    
    # 检查并执行压缩
    if cm.should_compress():
        print("\n🔄 执行上下文压缩...")
        compress_result = context_tool.execute("compress")
        if compress_result["success"] and compress_result["data"].get("compressed"):
            data = compress_result["data"]
            print(f"  压缩前: {data['original_tokens']} tokens")
            print(f"  压缩后: {data['compressed_tokens']} tokens")
            print(f"  压缩率: {data['compression_ratio']*100:.1f}%")
    
    print("\n🎯 演示3: 工具接口功能")
    print("-" * 25)
    
    # 演示各种工具操作
    actions = [
        ("recent", "获取最近消息", {"limit": 3}),
        ("monitor", "监控上下文状态", {}),
        ("stats", "获取完整统计", {}),
    ]
    
    for action, description, kwargs in actions:
        print(f"  {description}:")
        result = context_tool.execute(action, **kwargs)
        if result["success"]:
            print(f"    ✅ {result['message']}")
            if "data" in result and isinstance(result["data"], dict):
                # 显示关键数据
                data = result["data"]
                if "utilization_rate" in data:
                    print(f"    使用率: {data['utilization_rate']*100:.1f}%")
                if "compression_count" in data:
                    print(f"    压缩次数: {data['compression_count']}")

def main():
    """主函数"""
    print(f"🚀 Claude Context Manager 规范入口")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"使用标准工具: ContextManagerTool")
    
    try:
        demo_core_concepts()
        
        print("\n" + "=" * 40)
        print("✅ 规范演示完成!")
        print("\n💡 核心要点:")
        print("  • 遵循标准分层架构规范")
        print("  • ContextManagerTool 位于 tools/ 目录")
        print("  • context_manager 作为规范入口引用工具")
        print("  • 保持接口一致性和向后兼容性")
        print("  • 函数调用 + 上下文管理核心概念完整演示")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()