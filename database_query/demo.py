"""
数据库查询 Demo
使用 LLM 将自然语言转换为 SQL 查询
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.client import LLMClient
from tools.database import DatabaseTool, SCHEMA

DATABASE_PROMPT = f"""你是一个数据库查询专家。

## 数据库表结构
{SCHEMA}

## 工作流程（必须严格遵守）
1. 理解用户问题
2. 编写一条完整的 SQL 查询（用 JOIN 关联表，用聚合函数计算）
3. 调用 execute_sql 工具
4. **得到结果后，直接回答用户问题**
5. 不要再调用任何工具

## 回答要求
- 不要说"我将查询..."、"让我查询..."这类话
- 直接在回答中给出答案
- 如果结果为空，说"没有找到相关数据"
- 不要显示 SQL 代码"""


def create_database():
    """创建示例数据库"""
    from database_query.create_db import create_sample_database
    create_sample_database()


def demo_direct_sql():
    """直接执行 SQL 的演示"""
    print("\n" + "=" * 50)
    print("演示1: 直接执行 SQL")
    print("=" * 50)
    
    tool = DatabaseTool()
    
    queries = [
        ("查询所有用户", "SELECT * FROM users"),
        ("查询电子产品", "SELECT name, price FROM products WHERE category = '电子产品'"),
        ("查询已完成订单", "SELECT COUNT(*) as total FROM orders WHERE status = 'completed'"),
        ("查询每个用户的订单总数", """
            SELECT u.name, COUNT(o.id) as order_count 
            FROM users u 
            LEFT JOIN orders o ON u.id = o.user_id 
            GROUP BY u.id, u.name
        """),
        ("查询销售额最高的产品", """
            SELECT p.name, SUM(o.total_price) as total_sales 
            FROM products p 
            JOIN orders o ON p.id = o.product_id 
            GROUP BY p.id, p.name 
            ORDER BY total_sales DESC 
            LIMIT 3
        """)
    ]
    
    for desc, sql in queries:
        print(f"\n{desc}")
        print(f"SQL: {sql.strip()}")
        result = tool.execute(sql.strip())
        if result["success"]:
            data = result["data"]
            print(f"返回 {data['row_count']} 条记录")
            for row in data["results"][:3]:
                print(f"  {row}")
        else:
            print(f"错误: {result['error']}")


def demo_with_llm():
    """使用 LLM 进行自然语言查询"""
    print("\n" + "=" * 50)
    print("演示2: 使用 LLM 进行自然语言查询")
    print("=" * 50)
    
    # 确保数据库存在
    create_database()
    
    client = LLMClient()
    
    test_questions = [
        "查询所有在北京的用户",
        "查询价格超过 1000 元的产品有哪些？",
        "统计每个城市的用户数量",
        "查询所有未完成的订单",
        "找出订单总额最高的用户",
        "查询每种分类的产品数量和平均价格",
    ]
    
    for question in test_questions:
        print(f"\n问题: {question}")
        print("-" * 40)
        
        messages = [
            {"role": "system", "content": DATABASE_PROMPT},
            {"role": "user", "content": question}
        ]
        
        result = client.chat(messages, max_turns=3)
        
        if result["success"]:
            print(f"回答: {result['content']}")
        else:
            print(f"错误: {result.get('error', '未知错误')}")


def demo_interactive():
    """交互式查询"""
    print("\n" + "=" * 50)
    print("演示3: 交互式查询")
    print("=" * 50)
    print("输入问题进行查询，输入 'quit' 退出\n")
    
    # 确保数据库存在
    create_database()
    
    client = LLMClient()
    
    while True:
        question = input("请输入问题: ").strip()
        
        if question.lower() == 'quit':
            break
        
        if not question:
            continue
        
        messages = [
            {"role": "system", "content": DATABASE_PROMPT},
            {"role": "user", "content": question}
        ]
        
        result = client.chat(messages, max_turns=3)
        
        if result["success"]:
            print(f"\n回答: {result['content']}\n")
        else:
            print(f"\n错误: {result.get('error', '未知错误')}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库查询 Demo")
    parser.add_argument("--mode", choices=["direct", "llm", "interactive"], 
                        default="llm", help="运行模式")
    args = parser.parse_args()
    
    if args.mode == "direct":
        create_database()
        demo_direct_sql()
    elif args.mode == "llm":
        demo_with_llm()
    elif args.mode == "interactive":
        demo_interactive()
