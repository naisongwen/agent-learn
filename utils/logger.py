"""
日志配置
"""

import logging
import os
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """配置日志"""
    
    # 创建logs目录
    if log_file:
        os.makedirs("logs", exist_ok=True)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 配置根日志
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(f"logs/{log_file}_{timestamp}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
