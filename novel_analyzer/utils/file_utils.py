"""
文件操作工具模块
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def _natural_sort_key(text: str) -> List:
        """
        自然排序的key函数，支持数字正确排序
        例如：第1章、第2章、第10章 而不是 第1章、第10章、第2章
        
        Args:
            text: 文件名
            
        Returns:
            排序用的key列表
        """
        def atoi(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [atoi(c) for c in re.split(r'(\d+)', text)]
    
    @staticmethod
    def load_novel_files(novel_folder: str, encoding: str = "utf-8") -> List[Dict]:
        """
        加载小说文件夹中的所有txt文件
        
        Args:
            novel_folder: 小说文件夹路径
            encoding: 文件编码
            
        Returns:
            章节列表，每个元素包含文件名、内容、字数等信息
        """
        if not os.path.exists(novel_folder):
            raise FileNotFoundError(f"文件夹不存在: {novel_folder}")
        
        # 获取所有txt文件
        txt_files = [f for f in os.listdir(novel_folder) if f.endswith('.txt')]
        
        if not txt_files:
            raise ValueError(f"文件夹中没有找到txt文件: {novel_folder}")
        
        # 按文件名自然排序（支持数字排序）
        txt_files.sort(key=FileUtils._natural_sort_key)
        
        chapters = []
        for idx, filename in enumerate(txt_files, 1):
            file_path = os.path.join(novel_folder, filename)
            
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # 提取章节标题（如果有）
                title = FileUtils._extract_chapter_title(content, filename)
                
                chapters.append({
                    'number': idx,
                    'filename': filename,
                    'title': title,
                    'content': content,
                    'word_count': len(content)
                })
            except Exception as e:
                print(f"警告: 读取文件 {filename} 失败: {e}")
                continue
        
        return chapters
    
    @staticmethod
    def _extract_chapter_title(content: str, filename: str) -> str:
        """
        从章节内容或文件名中提取标题
        
        Args:
            content: 章节内容
            filename: 文件名
            
        Returns:
            章节标题
        """
        # 尝试从内容第一行提取
        lines = content.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            # 匹配常见的章节标题格式
            if re.match(r'^第.{1,5}[章节]', first_line) or re.match(r'^Chapter', first_line, re.I):
                return first_line
        
        # 从文件名提取
        title = os.path.splitext(filename)[0]
        return title
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        # 去除多余的空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 去除行首行尾空白
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # 去除特殊的控制字符（保留中文标点）
        # text = re.sub(r'[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\s，。！？；：""''（）【】《》\n]', '', text)
        
        return text.strip()
    
    @staticmethod
    def save_json(data: dict, filepath: str, pretty: bool = True):
        """
        保存JSON文件
        
        Args:
            data: 要保存的数据
            filepath: 文件路径
            pretty: 是否格式化输出
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(data, f, ensure_ascii=False)
    
    @staticmethod
    def load_json(filepath: str) -> dict:
        """
        加载JSON文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            JSON数据
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def get_chapter_files(intermediate_dir: str, pattern: str = "chapter_*.json") -> List[str]:
        """
        获取所有章节分析文件
        
        Args:
            intermediate_dir: 中间结果目录
            pattern: 文件匹配模式
            
        Returns:
            文件路径列表
        """
        chapter_dir = os.path.join(intermediate_dir, 'chapter_summaries')
        if not os.path.exists(chapter_dir):
            return []
        
        files = []
        for filename in os.listdir(chapter_dir):
            if filename.endswith('.json'):
                files.append(os.path.join(chapter_dir, filename))
        
        return sorted(files)
    
    @staticmethod
    def get_segment_files(intermediate_dir: str) -> List[str]:
        """
        获取所有分段汇总文件
        
        Args:
            intermediate_dir: 中间结果目录
            
        Returns:
            文件路径列表
        """
        segment_dir = os.path.join(intermediate_dir, 'segment_summaries')
        if not os.path.exists(segment_dir):
            return []
        
        files = []
        for filename in os.listdir(segment_dir):
            if filename.endswith('.json'):
                files.append(os.path.join(segment_dir, filename))
        
        return sorted(files)
