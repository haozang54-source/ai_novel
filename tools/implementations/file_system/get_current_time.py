"""
LangChain Function Call工具 - 获取当前时间工具
用于代码生成时获取时间戳，确保文件名唯一性
"""

from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time(format: str = "YYYYMMDD_HHMMSS") -> str:
    """
    获取当前时间，返回格式化的时间字符串。

    Get current time and return formatted time string.

    Args:
        format: 时间格式，支持以下选项：
            - "YYYYMMDD_HHMMSS": 年月日_时分秒，如 20241029_143520（默认）
            - "YYYYMMDD": 年月日，如 20241029
            - "HHMMSS": 时分秒，如 143520
            - "ISO": ISO 8601 格式，如 2024-10-29T14:35:20
            - "READABLE": 可读格式，如 2024-10-29 14:35:20

    Returns:
        格式化的时间字符串

    """
    try:
        now = datetime.now()

        if format == "YYYYMMDD_HHMMSS":
            return now.strftime("%Y%m%d_%H%M%S")
        elif format == "YYYYMMDD":
            return now.strftime("%Y%m%d")
        elif format == "HHMMSS":
            return now.strftime("%H%M%S")
        elif format == "ISO":
            return now.isoformat()
        elif format == "READABLE":
            return now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # 默认格式
            return now.strftime("%Y%m%d_%H%M%S")

    except Exception as e:
        return f"错误: 获取时间失败: {str(e)}"
