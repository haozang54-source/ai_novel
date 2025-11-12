"""
LangChain Function Call工具 - 搜索文件内容工具
参考gemini-cli的grep.ts实现
"""

import os
import re
from pathlib import Path
from typing import Optional, List
from langchain_core.tools import tool


@tool
def search_file_content(
    directory: str,
    pattern: str,
    file_pattern: Optional[str] = None,
    case_sensitive: bool = False,
    max_results: int = 50,
) -> str:
    """
    在指定目录中搜索匹配指定模式的文件内容。支持正则表达式搜索。

    Searches for file content matching a specified pattern in a directory.
    Supports regex pattern matching.

    Args:
        directory: 要搜索的目录的绝对路径
        pattern: 要搜索的文本模式（支持正则表达式）
        file_pattern: 文件名模式（如 "*.py", "*.js"），None表示搜索所有文件
        case_sensitive: 是否区分大小写，默认False
        max_results: 最大返回结果数，默认50

    Returns:
        格式化的搜索结果字符串，包含匹配的文件、行号和内容

    适用场景：
        - 查找特定字符串的使用位置
    """
    try:
        # 验证路径是否为绝对路径
        if not os.path.isabs(directory):
            return f"错误: 路径必须是绝对路径: {directory}"

        # 验证目录是否存在
        if not os.path.exists(directory):
            return f"错误: 目录不存在: {directory}"

        # 验证是否为目录
        if not os.path.isdir(directory):
            return f"错误: 路径不是目录: {directory}"

        # 编译正则表达式
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
        except re.error as e:
            return f"错误: 无效的正则表达式: {pattern}\n详情: {str(e)}"

        # 编译文件名模式
        file_regex = None
        if file_pattern:
            # 将glob模式转换为正则表达式
            file_pattern_regex = file_pattern.replace(".", r"\.")
            file_pattern_regex = file_pattern_regex.replace("*", ".*")
            file_pattern_regex = file_pattern_regex.replace("?", ".")
            file_pattern_regex = f"^{file_pattern_regex}$"
            try:
                file_regex = re.compile(file_pattern_regex)
            except re.error:
                return f"错误: 无效的文件模式: {file_pattern}"

        # 搜索结果
        results = []
        total_matches = 0
        searched_files = 0

        # 遍历目录
        for root, dirs, files in os.walk(directory):
            # 过滤掉常见的忽略目录
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    ".git",
                    "__pycache__",
                    "node_modules",
                    ".venv",
                    "venv",
                    ".pytest_cache",
                    ".mypy_cache",
                    "dist",
                    "build",
                ]
            ]

            for filename in files:
                # 检查文件名是否匹配
                if file_regex and not file_regex.match(filename):
                    continue

                # 跳过二进制文件
                if filename.endswith((".pyc", ".so", ".dll", ".exe", ".bin")):
                    continue

                file_path = os.path.join(root, filename)
                searched_files += 1

                try:
                    # 读取文件
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # 搜索匹配的行
                    for line_num, line in enumerate(lines, 1):
                        if regex.search(line):
                            total_matches += 1

                            if len(results) < max_results:
                                # 获取相对路径
                                rel_path = os.path.relpath(file_path, directory)

                                results.append(
                                    {
                                        "file": rel_path,
                                        "line": line_num,
                                        "content": line.rstrip(),
                                    }
                                )

                            if total_matches >= max_results:
                                break

                    if total_matches >= max_results:
                        break

                except (UnicodeDecodeError, PermissionError):
                    # 跳过无法读取的文件
                    continue
                except Exception:
                    # 跳过其他错误
                    continue

            if total_matches >= max_results:
                break

        # 格式化输出
        if not results:
            # 生成智能建议
            suggestions = []
            
            # 建议1: 尝试更宽泛的搜索词
            if "_" in pattern or len(pattern) > 15:
                # 如果是下划线分隔的长词，建议搜索部分关键词
                if "_" in pattern:
                    parts = pattern.split("_")
                    if len(parts) > 2:
                        base_pattern = "_".join(parts[:2])  # 取前两个部分
                        suggestions.append(f"尝试搜索更短的关键词: '{base_pattern}'")
                    else:
                        suggestions.append(f"尝试搜索单个关键词: '{parts[0]}' 或 '{parts[-1]}'")
                else:
                    # 长词建议搜索部分
                    suggestions.append(f"尝试搜索部分关键词，如: '{pattern[:10]}'")
            
            # 建议2: 尝试不同的文件类型
            if file_pattern == "*.py":
                suggestions.append("尝试搜索其他文件类型: 不指定 file_pattern 参数以搜索所有文件")
            elif file_pattern:
                suggestions.append("尝试不指定 file_pattern 参数以搜索所有文件类型")
            
            # 建议3: 使用 list_directory 探索目录结构
            suggestions.append("使用 'list_directory' 工具查看目录结构，确认搜索位置是否正确")
            
            # 建议4: 考虑功能可能不存在
            suggestions.append("如果多次搜索失败，该功能可能不存在，考虑查看相似功能的实现作为参考")
            
            # 格式化建议
            suggestion_text = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(suggestions))
            
            return (
                f"❌ 在目录 {directory} 中未找到匹配 '{pattern}' 的内容\n"
                f"   (已搜索 {searched_files} 个文件)\n\n"
                f"💡 建议下一步操作:\n{suggestion_text}\n\n"
                f"⚠️ 重要提示:\n"
                f"  - 请勿使用相同参数重复搜索\n"
                f"  - 如果连续搜索失败，应改变搜索策略或考虑从头实现功能"
            )

        output = f"搜索结果 (模式: '{pattern}', 目录: {directory}):\n"
        output += f"找到 {total_matches} 个匹配项"

        if total_matches > max_results:
            output += f" (仅显示前 {max_results} 个)"

        output += f", 已搜索 {searched_files} 个文件\n\n"

        # 按文件分组显示结果
        current_file = None
        for result in results:
            if result["file"] != current_file:
                current_file = result["file"]
                output += f"\n📄 {current_file}:\n"

            output += f"  {result['line']:4d} | {result['content']}\n"

        return output

    except Exception as e:
        return f"错误: 搜索文件内容时发生异常: {str(e)}"
