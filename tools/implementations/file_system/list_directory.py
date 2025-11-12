"""
LangChain Function Call工具 - 目录列表工具
参考gemini-cli的ls.ts实现
"""

import os
import re
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from langchain_core.tools import tool


@tool
def list_directory(
    path: str,
    ignore: Optional[List[str]] = None,
    respect_git_ignore: bool = True,
) -> str:
    """
    列出指定目录中的文件和子目录名称，显示文件大小和行数信息。可选择性地忽略匹配提供的glob模式的条目。

    Lists the names of files and subdirectories directly within a specified
    directory path with file size and line count information. Can optionally ignore entries matching provided glob patterns.

    Args:
        path: 要列出的目录的绝对路径 (必须是绝对路径，不能是相对路径)
        ignore: 要忽略的glob模式列表，例如 ["*.log", ".git", "__pycache__"]
        respect_git_ignore: 是否遵守.gitignore模式，默认为True

    Returns:
        格式化的目录列表字符串，包含文件和目录信息（文件大小、行数）

    适用场景：
        - 浏览项目目录结构
        - 查找特定文件或目录
        - 了解目录内容组织
        - 判断文件大小以决定读取策略（大文件使用 search_file_content 而非 read_file）
    """
    try:
        # 验证路径是否为绝对路径
        if not os.path.isabs(path):
            return f"错误: 路径必须是绝对路径: {path}"

        # 验证路径是否存在
        if not os.path.exists(path):
            return f"错误: 目录不存在或无法访问: {path}"

        # 验证是否为目录
        if not os.path.isdir(path):
            return f"错误: 路径不是目录: {path}"

        # 读取目录内容
        entries = []
        try:
            items = os.listdir(path)
        except PermissionError:
            return f"错误: 没有权限访问目录: {path}"

        if len(items) == 0:
            return f"目录 {path} 为空。"

        # 加载.gitignore规则（如果需要）
        gitignore_patterns = []
        if respect_git_ignore:
            gitignore_patterns = _load_gitignore_patterns(path)

        # 处理每个条目
        ignored_count = 0
        for item in items:
            full_path = os.path.join(path, item)

            # 检查是否应该忽略
            if _should_ignore(item, ignore):
                ignored_count += 1
                continue

            # 检查gitignore
            if respect_git_ignore and _matches_gitignore(item, gitignore_patterns):
                ignored_count += 1
                continue

            try:
                stat_info = os.stat(full_path)
                is_dir = os.path.isdir(full_path)

                # 计算文件行数（仅对文本文件）
                line_count = 0
                if not is_dir:
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            line_count = sum(1 for _ in f)
                    except (UnicodeDecodeError, PermissionError, OSError):
                        # 非文本文件或无法读取，行数为0
                        line_count = 0

                entries.append(
                    {
                        "name": item,
                        "path": full_path,
                        "is_directory": is_dir,
                        "size": 0 if is_dir else stat_info.st_size,
                        "line_count": line_count,
                        "modified_time": datetime.fromtimestamp(stat_info.st_mtime),
                    }
                )
            except Exception as e:
                # 记录错误但不中断整个列表
                print(f"访问 {full_path} 时出错: {e}")
                continue

        # 排序：目录优先，然后按字母顺序
        entries.sort(key=lambda x: (not x["is_directory"], x["name"].lower()))

        # 格式化输出
        def format_size(size_bytes: int) -> str:
            """格式化文件大小"""
            if size_bytes < 1024:
                return f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f}KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f}MB"

        directory_content = "\n".join(
            [
                f"{'[DIR]  ' if entry['is_directory'] else '[FILE] '}{entry['name']}"
                + (f" ({format_size(entry['size'])}, {entry['line_count']} 行)"
                   if not entry['is_directory'] and entry['line_count'] > 0
                   else f" ({format_size(entry['size'])})" if not entry['is_directory']
                   else "")
                + (" ⚠️ 大文件" if not entry['is_directory'] and entry['size'] > 100 * 1024 else "")
                for entry in entries
            ]
        )

        result_message = f"目录列表 {path}:\n{directory_content}"

        if ignored_count > 0:
            result_message += f"\n\n(已忽略 {ignored_count} 个项目)"

        return result_message

    except Exception as e:
        return f"错误: 列出目录时发生异常: {str(e)}"


def _should_ignore(filename: str, patterns: Optional[List[str]]) -> bool:
    """
    检查文件名是否匹配任何忽略模式

    Args:
        filename: 要检查的文件名
        patterns: glob模式数组

    Returns:
        如果应该忽略该文件名则返回True
    """
    if not patterns:
        return False

    for pattern in patterns:
        # 将glob模式转换为正则表达式
        regex_pattern = pattern.replace(".", r"\.")
        regex_pattern = regex_pattern.replace("*", ".*")
        regex_pattern = regex_pattern.replace("?", ".")
        regex_pattern = f"^{regex_pattern}$"

        if re.match(regex_pattern, filename):
            return True

    return False


def _load_gitignore_patterns(directory: str) -> List[str]:
    """
    加载.gitignore文件中的模式

    Args:
        directory: 目录路径

    Returns:
        gitignore模式列表
    """
    patterns = []
    gitignore_path = os.path.join(directory, ".gitignore")

    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 忽略空行和注释
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception as e:
            print(f"读取.gitignore失败: {e}")

    return patterns


def _matches_gitignore(filename: str, patterns: List[str]) -> bool:
    """
    检查文件名是否匹配gitignore模式

    Args:
        filename: 文件名
        patterns: gitignore模式列表

    Returns:
        如果匹配则返回True
    """
    for pattern in patterns:
        # 简化的gitignore匹配逻辑
        if pattern.endswith("/"):
            # 目录模式
            if filename == pattern[:-1]:
                return True
        else:
            # 文件模式
            regex_pattern = pattern.replace(".", r"\.")
            regex_pattern = regex_pattern.replace("*", ".*")
            regex_pattern = f"^{regex_pattern}$"

            if re.match(regex_pattern, filename):
                return True

    return False
