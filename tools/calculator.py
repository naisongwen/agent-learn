"""
计算器工具
执行精确数学计算
"""

from typing import Dict, Any, Union
import logging
import ast
import operator
import sys

logger = logging.getLogger(__name__)

class CalculatorTool:
    """计算器工具"""
    
    enabled = True
    name = "calculate"
    description = "执行数学计算。支持加减乘除、幂运算、平方根等。当用户需要精确计算时使用，避免模型直接计算出错。"
    
    # 支持的运算符
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
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
                        "expression": {
                            "type": "string",
                            "description": "数学表达式，如'2+2'、'(3+5)*10'、'2**10'"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    
    def execute(self, expression: str) -> Dict[str, Any]:
        """执行计算"""
        try:
            # 安全验证表达式
            if not self._is_safe_expression(expression):
                return {
                    "success": False,
                    "error": "表达式包含不允许的字符或操作"
                }
            
            # 计算结果
            result = self._safe_eval(expression)
            
            logger.info(f"计算成功：{expression} = {result}")
            return {
                "success": True,
                "data": {
                    "expression": expression,
                    "result": result
                }
            }
            
        except ZeroDivisionError:
            return {
                "success": False,
                "error": "除数不能为零"
            }
        except Exception as e:
            logger.error(f"计算失败：{str(e)}")
            return {
                "success": False,
                "error": f"计算错误：{str(e)}"
            }
    
    def _is_safe_expression(self, expression: str) -> bool:
        """验证表达式安全性"""
        # 只允许数字、运算符和括号
        allowed_chars = set("0123456789+-*/%.() ")
        return all(c in allowed_chars for c in expression)
    
    def _safe_eval(self, expression: str) -> Union[int, float]:
        """安全计算表达式"""
        # 解析表达式
        node = ast.parse(expression, mode='eval')
        return self._eval_node(node.body)
    
    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        """递归计算AST节点"""
        # 处理不同Python版本的兼容性
        python_version = sys.version_info
        
        if python_version.major == 3 and python_version.minor <= 7:
            # Python 3.7及以下使用ast.Num
            if isinstance(node, ast.Num):
                return node.n
        else:
            # Python 3.8+使用ast.Constant
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("只支持数字常量")
        
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self.OPERATORS:
                return self.OPERATORS[op_type](left, right)
            raise ValueError(f"不支持的运算符：{op_type}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self.OPERATORS:
                return self.OPERATORS[op_type](operand)
            raise ValueError(f"不支持的一元运算符：{op_type}")
        else:
            # 如果是其他类型的节点，在Python 3.8+中可能是Constant
            if hasattr(ast, 'Constant') and isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("只支持数字常量")
            raise ValueError(f"不支持的表达式类型：{type(node)}")


if __name__ == "__main__":
    tool = CalculatorTool()
    test_cases = ["2+2", "(3+5)*10", "2**10", "100/3", "10%3"]
    for expr in test_cases:
        result = tool.execute(expr)
        print(f"{expr} = {result}")
