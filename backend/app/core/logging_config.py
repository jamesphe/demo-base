import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.DEBUG,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    配置并返回一个logger实例
    
    Args:
        name: logger的名称
        level: 日志级别
        log_format: 日志格式，如果为None则使用默认格式
    
    Returns:
        配置好的logger实例
    """
    if log_format is None:
        log_format = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(message)s'
        )

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 如果logger还没有处理器，添加一个新的处理器
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger 