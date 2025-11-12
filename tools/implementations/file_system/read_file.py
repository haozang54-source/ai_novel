"""
LangChain Function Call工具 - 读取文件工具
参考gemini-cli的read.ts实现
"""

import os
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool


@tool
def read_file(
    path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    max_lines: int = 500,
    allow_large_file: Optional[bool] = None,
) -> str:
    """
    读取指定文件的内容。可以选择性地指定起始和结束行号来读取文件的一部分。
    为避免上下文溢出，代码文件默认最多读取500行，文档文件（doc/*.md）可读取完整内容。

    Reads the contents of a specified file. Optionally specify start and end
    line numbers to read a portion of the file. Defaults to max 500 lines for code files,
    but allows full content for documentation files (doc/*.md).

    Args:
        path: 要读取的文件的绝对路径 (必须是绝对路径)
        start_line: 起始行号（从1开始，包含），None表示从文件开头
        end_line: 结束行号（包含），None表示到文件末尾
        max_lines: 最大读取行数，默认500行（防止上下文溢出）
        allow_large_file: 是否允许读取大文件（不限制行数）。
                         None时自动判断：doc目录下的.md文件自动允许
                         True时强制允许，False时强制限制

    Returns:
        文件内容字符串，如果指定了行号范围则返回该范围的内容
        如果文件超过max_lines，会截断并提示使用search_file_content

    适用场景：
        - 查看文件内容

    注意：
        - 对于大型文件（>500行），建议使用 search_file_content 搜索特定内容

    """
    try:
        # 验证路径是否为绝对路径
        if not os.path.isabs(path):
            return f"错误: 路径必须是绝对路径: {path}"

        # 验证文件是否存在
        if not os.path.exists(path):
            return f"错误: 文件不存在: {path}"

        # 验证是否为文件
        if not os.path.isfile(path):
            return f"错误: 路径不是文件: {path}"

        # 读取文件
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(path, "r", encoding="gbk") as f:
                    lines = f.readlines()
            except Exception:
                return f"错误: 无法读取文件（编码问题）: {path}"
        except PermissionError:
            return f"错误: 没有权限读取文件: {path}"

        # 如果文件为空
        if len(lines) == 0:
            return f"文件 {path} 为空。"

        # 处理行号范围
        total_lines = len(lines)

        # 判断是否允许读取大文件（混合方案）
        if allow_large_file is not None:
            # 1. 如果显式指定了 allow_large_file，使用该值
            is_large_file_allowed = allow_large_file
        else:
            # 2. 否则自动判断：doc 目录下的 .md 文件
            normalized_path = path.replace("\\", "/")
            is_large_file_allowed = (
                "/doc/" in normalized_path and normalized_path.endswith(".md")
            )

        # 设置有效的最大行数
        if is_large_file_allowed:
            effective_max_lines = float("inf")  # 不限制行数
        else:
            effective_max_lines = max_lines  # 使用默认限制

        if start_line is not None:
            if start_line < 1:
                return f"错误: 起始行号必须大于等于1，当前值: {start_line}"
            if start_line > total_lines:
                return f"错误: 起始行号 {start_line} 超出文件总行数 {total_lines}"

        if end_line is not None:
            if end_line < 1:
                return f"错误: 结束行号必须大于等于1，当前值: {end_line}"
            if end_line > total_lines:
                return f"错误: 结束行号 {end_line} 超出文件总行数 {total_lines}"

        if start_line is not None and end_line is not None:
            if start_line > end_line:
                return f"错误: 起始行号 {start_line} 不能大于结束行号 {end_line}"

        # 提取指定范围的行
        if start_line is None and end_line is None:
            # 读取整个文件，但限制最大行数（除非是允许的大文件）
            if total_lines > effective_max_lines:
                truncate_lines = int(effective_max_lines)
                content = "".join(lines[:truncate_lines])
                line_info = f"(共 {total_lines} 行，已截断至前 {truncate_lines} 行)"
                warning = f"\n\n⚠️ 警告: 文件过大（{total_lines} 行），已截断至前 {truncate_lines} 行。\n建议使用 search_file_content 工具搜索特定内容，例如：\n  - 搜索函数定义: pattern=\"def function_name\"\n  - 搜索类定义: pattern=\"class ClassName\"\n  - 搜索导入语句: pattern=\"import|from\""
                content = content + warning
            else:
                content = "".join(lines)
                line_info = f"(共 {total_lines} 行)"
        else:
            start_idx = (start_line - 1) if start_line else 0
            end_idx = end_line if end_line else total_lines

            # 检查读取范围是否超过effective_max_lines
            read_lines = end_idx - start_idx
            if read_lines > effective_max_lines:
                truncate_lines = int(effective_max_lines)
                end_idx = start_idx + truncate_lines
                content = "".join(lines[start_idx:end_idx])
                line_info = f"(第 {start_line or 1}-{start_idx + truncate_lines} 行，共 {total_lines} 行，已截断至 {truncate_lines} 行)"
                warning = f"\n\n⚠️ 警告: 请求范围过大，已截断至 {truncate_lines} 行。"
                content = content + warning
            else:
                content = "".join(lines[start_idx:end_idx])
                line_info = f"(第 {start_line or 1}-{end_line or total_lines} 行，共 {total_lines} 行)"

        # 格式化输出
        result = f"文件: {path} {line_info}\n\n{content}"

        return result

    except Exception as e:
        return f"错误: 读取文件时发生异常: {str(e)}"
