"""
创建示例数据库
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database_query", "sample.db")

def create_sample_database():
    """创建示例数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建表
    cursor.executescript("""
        -- 用户表
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            age INTEGER,
            city TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 产品表
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 订单表
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            total_price REAL,
            order_date TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    """)
    
    # 插入示例数据
    cursor.executescript("""
        -- 清空表
        DELETE FROM orders;
        DELETE FROM products;
        DELETE FROM users;
        
        -- 插入用户
        INSERT INTO users (name, email, age, city) VALUES
            ('张三', 'zhangsan@example.com', 28, '北京'),
            ('李四', 'lisi@example.com', 35, '上海'),
            ('王五', 'wangwu@example.com', 42, '广州'),
            ('赵六', 'zhaoliu@example.com', 31, '深圳'),
            ('钱七', 'qianqi@example.com', 25, '杭州');
        
        -- 插入产品
        INSERT INTO products (name, category, price, stock) VALUES
            ('iPhone 15', '电子产品', 6999, 100),
            ('MacBook Pro', '电子产品', 12999, 50),
            ('AirPods Pro', '电子产品', 1899, 200),
            ('Nike运动鞋', '服装', 599, 150),
            ('AdidasT恤', '服装', 299, 300),
            ('小米手环', '电子产品', 199, 500);
        
        -- 插入订单
        INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
            (1, 1, 1, 6999, 'completed'),
            (1, 3, 2, 3798, 'completed'),
            (2, 2, 1, 12999, 'completed'),
            (3, 4, 2, 1198, 'completed'),
            (4, 6, 3, 597, 'pending'),
            (5, 5, 1, 299, 'completed'),
            (2, 5, 2, 598, 'completed'),
            (1, 2, 1, 12999, 'pending');
    """)
    
    conn.commit()
    conn.close()
    print(f"示例数据库已创建: {DB_PATH}")

def get_db_schema():
    """获取数据库 Schema 描述"""
    return """
## 数据库表结构

### users (用户表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 用户ID (主键) |
| name | TEXT | 用户名 |
| email | TEXT | 邮箱 |
| age | INTEGER | 年龄 |
| city | TEXT | 城市 |
| created_at | TEXT | 创建时间 |

### products (产品表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 产品ID (主键) |
| name | TEXT | 产品名称 |
| category | TEXT | 分类 (电子产品/服装) |
| price | REAL | 价格 |
| stock | INTEGER | 库存数量 |
| created_at | TEXT | 创建时间 |

### orders (订单表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 订单ID (主键) |
| user_id | INTEGER | 用户ID (外键) |
| product_id | INTEGER | 产品ID (外键) |
| quantity | INTEGER | 数量 |
| total_price | REAL | 总价 |
| order_date | TEXT | 订单日期 |
| status | TEXT | 状态 (pending/completed/cancelled) |
"""

if __name__ == "__main__":
    create_sample_database()
    print(get_db_schema())
