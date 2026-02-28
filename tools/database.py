"""
数据库查询工具
使用 LLM 将自然语言转换为 SQL 查询
"""

import sqlite3
import re
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    "database_query", 
    "sample.db"
)

SCHEMA = """
## 数据库表结构

### users (用户表)
- id: INTEGER (主键)
- name: TEXT (用户名)
- email: TEXT (邮箱)
- age: INTEGER (年龄)
- city: TEXT (城市)
- created_at: TEXT (创建时间)

### products (产品表)
- id: INTEGER (主键)
- name: TEXT (产品名称)
- category: TEXT (分类: 电子产品/服装)
- price: REAL (价格)
- stock: INTEGER (库存数量)
- created_at: TEXT (创建时间)

### orders (订单表)
- id: INTEGER (主键)
- user_id: INTEGER (用户ID，外键)
- product_id: INTEGER (产品ID，外键)
- quantity: INTEGER (数量)
- total_price: REAL (总价)
- order_date: TEXT (订单日期)
- status: TEXT (状态: pending/completed/cancelled)
"""


class DatabaseTool:
    """数据库查询工具"""
    
    enabled = True
    name = "execute_sql"
    description = "执行 SQL 查询数据库。只支持 SELECT 查询，用于回答用户关于数据库数据的问题。"
    
    ALLOWED_KEYWORDS = [
        "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IN", "LIKE",
        "ORDER BY", "ASC", "DESC", "LIMIT", "OFFSET", "GROUP BY",
        "HAVING", "COUNT", "SUM", "AVG", "MAX", "MIN", "AS", "ON",
        "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN",
        "DISTINCT", "BETWEEN", "IS NULL", "IS NOT NULL", "CASE", "WHEN",
        "THEN", "ELSE", "END", "UNION", "EXISTS"
    ]
    
    FORBIDDEN_PATTERNS = [
        r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b",
        r"\bCREATE\b", r"\bALTER\b", r"\bTRUNCATE\b", r"\bGRANT\b",
        r"\bREVOKE\b", r"\bEXEC\b", r"\bEXECUTE\b", r"\b--", r";.*;"
    ]
    
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
                        "sql": {
                            "type": "string",
                            "description": "要执行的 SQL 查询语句（只支持 SELECT）"
                        }
                    },
                    "required": ["sql"]
                }
            }
        }
    
    def execute(self, sql: str) -> Dict[str, Any]:
        """
        执行 SQL 查询
        
        Args:
            sql: SQL 查询语句
        
        Returns:
            查询结果或错误信息
        """
        sql = sql.strip()
        
        # 安全验证
        validation_result = self._validate_sql(sql)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"]
            }
        
        # 规范化 SQL（移除多余空格转为小写用于检查）
        sql_lower = sql.lower()
        
        # 执行查询
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            # 转换为字典列表
            results = []
            for row in rows:
                results.append(dict(row))
            
            conn.close()
            
            logger.info(f"SQL 查询成功，返回 {len(results)} 条记录")
            
            return {
                "success": True,
                "data": {
                    "row_count": len(results),
                    "results": results
                }
            }
            
        except sqlite3.Error as e:
            logger.error(f"SQL 执行错误: {str(e)}")
            return {
                "success": False,
                "error": f"SQL 执行错误: {str(e)}"
            }
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            return {
                "success": False,
                "error": f"查询失败: {str(e)}"
            }
    
    def _validate_sql(self, sql: str) -> Dict[str, Any]:
        """验证 SQL 安全性"""
        sql_upper = sql.upper()
        
        # 检查禁止的模式
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, sql_upper):
                return {
                    "valid": False,
                    "error": f"不支持的 SQL 操作: 检测到禁止的关键词"
                }
        
        # 确保是 SELECT 语句
        if not sql_upper.strip().startswith("SELECT"):
            return {
                "valid": False,
                "error": "只支持 SELECT 查询语句"
            }
        
        return {"valid": True}
    
    def get_schema(self) -> str:
        """获取数据库 Schema"""
        return SCHEMA


if __name__ == "__main__":
    tool = DatabaseTool()
    
    # 测试查询
    test_queries = [
        "SELECT * FROM users LIMIT 5",
        "SELECT name, price FROM products WHERE category = '电子产品'",
        "SELECT COUNT(*) as total FROM orders WHERE status = 'completed'"
    ]
    
    for sql in test_queries:
        print(f"\n执行: {sql}")
        result = tool.execute(sql)
        print(f"结果: {result}")
