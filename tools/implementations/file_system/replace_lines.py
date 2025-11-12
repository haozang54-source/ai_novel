"""
文件行替换工具
支持对指定行范围进行替换
"""
from langchain.tools import tool
from typing import Optional


@tool
def replace_lines(
    file_path: str,
    start_line: int,
    end_line: int,
    new_content: str
) -> str:
    """
    替换文件中指定行范围的内容
    
    Args:
        file_path: 文件路径（相对于项目根目录或绝对路径）
        start_line: 起始行号（从1开始）
        end_line: 结束行号（包含，从1开始）
        new_content: 新的内容（多行用\\n分隔）
    
    Returns:
        操作结果描述
        
    Examples:
        # 替换第10-12行
        replace_lines("test.py", 10, 12, "new line 1\\nnew line 2\\nnew line 3")
        
        # 替换单行
        replace_lines("test.py", 5, 5, "new single line")
    """
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        
        # 验证行号
        if start_line < 1 or end_line < 1:
            return f"错误：行号必须从1开始，当前start_line={start_line}, end_line={end_line}"
        
        if start_line > total_lines or end_line > total_lines:
            return f"错误：行号超出范围，文件共{total_lines}行，请求范围{start_line}-{end_line}"
        
        if start_line > end_line:
            return f"错误：起始行号({start_line})不能大于结束行号({end_line})"
        
        # 转换为0-based索引
        start_idx = start_line - 1
        end_idx = end_line  # end_line是包含的，所以不需要-1
        
        # 处理新内容（确保每行都有换行符）
        new_lines = new_content.split('\n')
        new_lines_with_newline = [line + '\n' if not line.endswith('\n') else line 
                                   for line in new_lines]
        
        # 如果最后一行是空的（因为split产生的），去掉
        if new_lines_with_newline and new_lines_with_newline[-1] == '\n':
            new_lines_with_newline = new_lines_with_newline[:-1]
        
        # 替换内容
        new_file_lines = lines[:start_idx] + new_lines_with_newline + lines[end_idx:]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_file_lines)
        
        replaced_count = end_line - start_line + 1
        new_count = len(new_lines_with_newline)
        
        return (f"✅ 替换成功\n"
                f"文件：{file_path}\n"
                f"原始：第{start_line}-{end_line}行（共{replaced_count}行）\n"
                f"新增：{new_count}行\n"
                f"文件总行数：{total_lines} → {len(new_file_lines)}")
        
    except FileNotFoundError:
        return f"错误：文件不存在 - {file_path}"
    except PermissionError:
        return f"错误：没有权限访问文件 - {file_path}"
    except Exception as e:
        return f"错误：{str(e)}"
