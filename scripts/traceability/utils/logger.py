"""
Logging utility for traceability checker
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


def get_logger(name: str = "traceability") -> logging.Logger:
    """获取配置好的日志记录器"""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件输出
    log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'traceability.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


def log_check_result(logger: logging.Logger, check_name: str, 
                     errors: list, warnings: list, info: list = None):
    """记录检查结果"""
    logger.info(f"=== {check_name} ===")
    
    if errors:
        logger.error(f"  Errors: {len(errors)}")
        for error in errors:
            logger.error(f"    ❌ {error}")
    
    if warnings:
        logger.warning(f"  Warnings: {len(warnings)}")
        for warning in warnings:
            logger.warning(f"    ⚠️  {warning}")
    
    if info:
        for item in info:
            logger.info(f"    ℹ️  {item}")
    
    if not errors and not warnings:
        logger.info("  ✅ All checks passed")
