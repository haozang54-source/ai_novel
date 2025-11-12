"""
LangChain Function Call工具 - 写入文件工具
参考gemini-cli的write.ts实现
"""

import os
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool


@tool
def write_file(
    path: str,
    content: str,
    create_directories: bool = True,
) -> str:
    """
    将内容写入指定文件。如果文件已存在则覆盖，如果不存在则创建新文件。

    Writes content to a specified file. Overwrites if file exists, creates new if not.

    Args:
        path: 要写入的文件的绝对路径 (必须是绝对路径)
        content: 要写入的内容
        create_directories: 是否自动创建父目录，默认为True

    Returns:
        操作结果消息

    适用场景：
        - 创建新文件
        - 修改现有文件
        - 保存配置文件

    注意事项：
        - 此操作会覆盖现有文件内容
        - 确保有足够的权限写入目标位置
        - 建议在写入前先读取文件确认内容
    """
    try:
        # 验证路径是否为绝对路径
        if not os.path.isabs(path):
            return f"错误: 路径必须是绝对路径: {path}"

        # 获取父目录
        parent_dir = os.path.dirname(path)

        # 检查父目录是否存在
        if not os.path.exists(parent_dir):
            if create_directories:
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                except PermissionError:
                    return f"错误: 没有权限创建目录: {parent_dir}"
                except Exception as e:
                    return f"错误: 创建目录失败: {str(e)}"
            else:
                return f"错误: 父目录不存在: {parent_dir}"

        # 检查是否为目录
        if os.path.exists(path) and os.path.isdir(path):
            return f"错误: 路径是一个目录，不能写入: {path}"

        # 记录是创建还是覆盖
        is_new_file = not os.path.exists(path)

        # 写入文件
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except PermissionError:
            return f"错误: 没有权限写入文件: {path}"
        except Exception as e:
            return f"错误: 写入文件失败: {str(e)}"

        # 获取文件信息
        file_size = os.path.getsize(path)
        line_count = content.count("\n") + 1 if content else 0

        # 格式化输出
        action = "创建" if is_new_file else "覆盖"
        result = f"✅ 成功{action}文件: {path}\n"
        result += f"   - 文件大小: {file_size} 字节\n"
        result += f"   - 行数: {line_count} 行"

        return result

    except Exception as e:
        return f"错误: 写入文件时发生异常: {str(e)}"
