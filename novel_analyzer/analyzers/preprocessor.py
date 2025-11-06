"""
文件预处理模块
"""
import os
from typing import List, Dict
from utils.file_utils import FileUtils


class NovelPreprocessor:
    """小说预处理器"""
    
    def __init__(self, novel_folder: str, config: dict):
        """
        初始化预处理器
        
        Args:
            novel_folder: 小说文件夹路径
            config: 配置字典
        """
        self.novel_folder = novel_folder
        self.config = config
        self.chapters = []
        self.statistics = {}
    
    def load_and_process(self) -> List[Dict]:
        """
        加载并处理所有章节
        
        Returns:
            章节列表
        """
        print(f"📁 正在加载小说文件: {self.novel_folder}")
        
        # 加载所有章节
        encoding = self.config.get('preprocessing', {}).get('encoding', 'utf-8')
        self.chapters = FileUtils.load_novel_files(self.novel_folder, encoding)
        
        print(f"✓ 成功加载 {len(self.chapters)} 个章节")
        
        # 清洗文本
        self._clean_chapters()
        
        # 过滤章节
        self._filter_chapters()
        
        # 生成统计信息
        self._generate_statistics()
        
        return self.chapters
    
    def _clean_chapters(self):
        """清洗所有章节文本"""
        print("🧹 正在清洗文本...")
        for chapter in self.chapters:
            chapter['content'] = FileUtils.clean_text(chapter['content'])
            chapter['word_count'] = len(chapter['content'])
    
    def _filter_chapters(self):
        """过滤不符合要求的章节"""
        min_length = self.config.get('preprocessing', {}).get('min_chapter_length', 500)
        max_length = self.config.get('preprocessing', {}).get('max_chapter_length', 20000)
        
        filtered = []
        for chapter in self.chapters:
            if min_length <= chapter['word_count'] <= max_length:
                filtered.append(chapter)
            else:
                print(f"  跳过章节 {chapter['number']} (字数: {chapter['word_count']})")
        
        if len(filtered) < len(self.chapters):
            print(f"⚠️  过滤掉 {len(self.chapters) - len(filtered)} 个章节")
        
        self.chapters = filtered
    
    def _generate_statistics(self):
        """生成统计信息"""
        total_words = sum(ch['word_count'] for ch in self.chapters)
        avg_words = total_words // len(self.chapters) if self.chapters else 0
        
        self.statistics = {
            'total_chapters': len(self.chapters),
            'total_words': total_words,
            'average_chapter_length': avg_words,
            'min_chapter_length': min(ch['word_count'] for ch in self.chapters) if self.chapters else 0,
            'max_chapter_length': max(ch['word_count'] for ch in self.chapters) if self.chapters else 0
        }
        
        print("\n📊 统计信息:")
        print(f"  总章节数: {self.statistics['total_chapters']}")
        print(f"  总字数: {self.statistics['total_words']:,}")
        print(f"  平均章节长度: {self.statistics['average_chapter_length']:,} 字")
        print(f"  章节长度范围: {self.statistics['min_chapter_length']:,} - {self.statistics['max_chapter_length']:,} 字\n")
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return self.statistics
