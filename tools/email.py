"""
邮件发送工具
用于发送通知、提醒等邮件
"""

from typing import Dict, Any, Optional
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailTool:
    """邮件发送工具"""
    
    enabled = True
    name = "send_email"
    description = "发送邮件到指定邮箱地址。用于发送通知、提醒、报告等。需要收件人邮箱、主题和正文。"
    require_confirmation = True  # 敏感操作需要确认
    
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
                        "to": {
                            "type": "string",
                            "description": "收件人邮箱地址"
                        },
                        "subject": {
                            "type": "string",
                            "description": "邮件主题，不超过100字符"
                        },
                        "body": {
                            "type": "string",
                            "description": "邮件正文内容"
                        },
                        "cc": {
                            "type": "string",
                            "description": "抄送邮箱地址，可选"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        }
    
    def execute(self, to: str, subject: str, body: str, cc: Optional[str] = None) -> Dict[str, Any]:
        """执行邮件发送"""
        try:
            # 验证邮箱格式
            if not self._is_valid_email(to):
                return {
                    "success": False,
                    "error": f"无效的收件人邮箱地址：{to}"
                }
            
            if cc and not self._is_valid_email(cc):
                return {
                    "success": False,
                    "error": f"无效的抄送邮箱地址：{cc}"
                }
            
            # 验证主题长度
            if len(subject) > 100:
                return {
                    "success": False,
                    "error": "邮件主题过长，不超过100字符"
                }
            
            # 验证正文长度
            if len(body) > 50000:
                return {
                    "success": False,
                    "error": "邮件正文过长，不超过50000字符"
                }
            
            # 敏感内容检查
            if self._contains_sensitive_content(body):
                logger.warning(f"邮件包含敏感内容，已拦截：{to}")
                return {
                    "success": False,
                    "error": "邮件内容包含敏感信息，发送失败"
                }
            
            # 模拟发送（实际项目替换为真实SMTP或邮件API）
            email_id = self._send_email_mock(to, subject, body, cc)
            
            logger.info(f"邮件发送成功：{to}, 主题：{subject}")
            return {
                "success": True,
                "data": {
                    "email_id": email_id,
                    "sent_at": datetime.now().isoformat(),
                    "to": to,
                    "subject": subject
                }
            }
            
        except Exception as e:
            logger.error(f"邮件发送失败：{str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _is_valid_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _contains_sensitive_content(self, content: str) -> bool:
        """检查敏感内容"""
        sensitive_keywords = ["密码", "银行卡", "身份证", "信用卡", "cvv"]
        return any(keyword in content for keyword in sensitive_keywords)
    
    def _send_email_mock(self, to: str, subject: str, body: str, cc: Optional[str] = None) -> str:
        """模拟邮件发送"""
        import uuid
        # 实际项目中使用 smtplib 或 SendGrid/Mailgun 等API
        return str(uuid.uuid4())


if __name__ == "__main__":
    tool = EmailTool()
    result = tool.execute(
        to="test@example.com",
        subject="测试邮件",
        body="这是一封测试邮件"
    )
    print(result)
