import sys
import os
import logging
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from llm.client import LLMClient
from utils.logger import setup_logging

# 加载环境变量
load_dotenv()

# 配置日志
logger = setup_logging(log_level="INFO", log_file="app")

def main():
    # 创建LLM客户端
    client = LLMClient(model="gpt-4-turbo")
    
    # 演示场景1：天气查询
    print("\n📍 场景1：天气查询")
    print("-" * 40)
    messages = [{"role": "user", "content": "北京今天天气怎么样？"}]
    result = client.chat(messages)
    
    if result["success"]:
        print(f"AI回答：{result['content']}")
    else:
        print(f"错误：{result.get('error')}")
    # 演示场景2：计算
    print("\n🔢 场景2：数学计算")
    print("-" * 40)
    messages = [{"role": "user", "content": "帮我计算 (123+456)*789 等于多少"}]
    result = client.chat(messages)
    
    if result["success"]:
        print(f"AI回答：{result['content']}")
    
    # 演示场景3：多工具协作
    print("\n🔄 场景3：多工具协作")
    print("-" * 40)
    messages = [{
        "role": "user", 
        "content": "现在几点了？如果北京是下午，帮我查一下天气"
    }]
    result = client.chat(messages)
    
    if result["success"]:
        print(f"AI回答：{result['content']}")
        print(f"工具调用次数：{result.get('tool_calls_count', 0)}")
    
    # 演示场景4：简单对话
    print("\n💬 场景4：简单对话（无工具）")
    print("-" * 40)
    response = client.chat_simple("请用一句话介绍你自己")
    print(f"AI回答：{response}")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
