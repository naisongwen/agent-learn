"""
参数验证工具
"""

import re
from typing import Dict, Any

def validate_tool_call(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证工具调用参数
    
    Returns:
        {"valid": True/False, "error": "错误信息"}
    """
    # 白名单检查
    allowed_functions = ["get_weather", "send_email", "calculate", "get_current_time"]
    if function_name not in allowed_functions:
        return {
            "valid": False,
            "error": f"未授权的函数调用：{function_name}"
        }
    
    # 特定函数验证
    if function_name == "send_email":
        return _validate_email_params(arguments)
    
    if function_name == "calculate":
        return _validate_calculate_params(arguments)
    
    if function_name == "get_weather":
        return _validate_weather_params(arguments)
    
    return {"valid": True, "error": None}


def _validate_email_params(args: Dict[str, Any]) -> Dict[str, Any]:
    """验证邮件参数"""
    to = args.get("to", "")
    subject = args.get("subject", "")
    body = args.get("body", "")
    
    # 邮箱格式验证
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, to):
        return {"valid": False, "error": f"无效的邮箱地址：{to}"}
    
    # 主题长度
    if len(subject) > 100:
        return {"valid": False, "error": "邮件主题过长"}
    
    # 正文长度
    if len(body) > 50000:
        return {"valid": False, "error": "邮件正文过长"}
    
    # 敏感词检查
    sensitive_words = ["密码", "银行卡", "身份证"]
    for word in sensitive_words:
        if word in body:
            return {"valid": False, "error": "内容包含敏感信息"}
    
    return {"valid": True, "error": None}


def _validate_calculate_params(args: Dict[str, Any]) -> Dict[str, Any]:
    """验证计算参数"""
    expression = args.get("expression", "")
    
    # 只允许数字和运算符
    allowed_chars = set("0123456789+-*/%.() ")
    if not all(c in allowed_chars for c in expression):
        return {"valid": False, "error": "表达式包含非法字符"}
    
    # 长度限制
    if len(expression) > 1000:
        return {"valid": False, "error": "表达式过长"}
    
    return {"valid": True, "error": None}


def _validate_weather_params(args: Dict[str, Any]) -> Dict[str, Any]:
    """验证天气查询参数"""
    location = args.get("location", "")
    
    if not location or len(location) > 50:
        return {"valid": False, "error": "无效的城市名称"}
    
    return {"valid": True, "error": None}
