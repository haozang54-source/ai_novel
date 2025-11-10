"""
智能分块器 - 根据文件大小限制和语义分组进行智能分块
"""
import json
from typing import List, Dict, Any, Optional


class SmartChunker:
    """智能分块器，按语义和大小限制进行分块"""
    
    # 不同LLM的上下文窗口限制（字节）
    SIZE_LIMITS = {
        'gpt4': 30 * 1024,      # 30KB
        'claude': 50 * 1024,    # 50KB
        'llama3': 10 * 1024,    # 10KB
        'default': 30 * 1024    # 默认30KB
    }
    
    def __init__(self, max_size: int = None, model_type: str = 'default'):
        """
        初始化分块器
        
        Args:
            max_size: 最大块大小（字节），如果提供则覆盖model_type
            model_type: 模型类型，用于选择默认大小限制
        """
        if max_size:
            self.max_size = max_size
        else:
            self.max_size = self.SIZE_LIMITS.get(model_type, self.SIZE_LIMITS['default'])
        
        # 保留10%的空间作为缓冲（JSON格式化、元数据等）
        self.effective_max_size = int(self.max_size * 0.9)
    
    def chunk_by_items(self, items: List[Dict], group_key: Optional[str] = None) -> List[List[Dict]]:
        """
        按项目列表分块，可选按某个键分组
        
        Args:
            items: 要分块的项目列表
            group_key: 用于分组的键名（可选）
            
        Returns:
            分块后的项目列表的列表
        """
        if not items:
            return []
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        # 如果有分组键，先按组分类
        if group_key:
            groups = self._group_by_key(items, group_key)
            for group_items in groups.values():
                chunk, remaining = self._fill_chunk(group_items, current_chunk, current_size)
                if chunk:
                    chunks.append(chunk)
                current_chunk = []
                current_size = 0
                
                # 处理剩余项目
                while remaining:
                    chunk, remaining = self._fill_chunk(remaining, [], 0)
                    if chunk:
                        chunks.append(chunk)
        else:
            # 简单顺序分块
            for item in items:
                item_size = len(json.dumps(item, ensure_ascii=False).encode('utf-8'))
                
                if current_size + item_size > self.effective_max_size:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = [item]
                    current_size = item_size
                else:
                    current_chunk.append(item)
                    current_size += item_size
            
            if current_chunk:
                chunks.append(current_chunk)
        
        return chunks
    
    def chunk_by_chapters(self, chapters: List[Dict], chapters_per_chunk: int = None) -> List[List[Dict]]:
        """
        按章节范围分块
        
        Args:
            chapters: 章节列表
            chapters_per_chunk: 每个块的章节数（可选，默认根据大小自动计算）
            
        Returns:
            分块后的章节列表
        """
        if not chapters:
            return []
        
        if chapters_per_chunk:
            # 固定章节数分块
            chunks = []
            for i in range(0, len(chapters), chapters_per_chunk):
                chunks.append(chapters[i:i + chapters_per_chunk])
            return chunks
        else:
            # 按大小自动分块
            return self.chunk_by_items(chapters)
    
    def chunk_dict_by_category(self, data: Dict[str, List[Dict]]) -> Dict[str, List[List[Dict]]]:
        """
        对字典中的每个类别分别分块
        
        Args:
            data: 按类别组织的数据字典
            
        Returns:
            按类别分块后的数据字典
        """
        result = {}
        for category, items in data.items():
            result[category] = self.chunk_by_items(items)
        return result
    
    def estimate_chunk_count(self, items: List[Dict]) -> int:
        """
        估算需要的块数量
        
        Args:
            items: 项目列表
            
        Returns:
            估算的块数量
        """
        total_size = len(json.dumps(items, ensure_ascii=False).encode('utf-8'))
        return max(1, (total_size + self.effective_max_size - 1) // self.effective_max_size)
    
    def get_chunk_info(self, chunk: List[Dict]) -> Dict[str, Any]:
        """
        获取块的信息
        
        Args:
            chunk: 数据块
            
        Returns:
            块信息（大小、项目数等）
        """
        chunk_json = json.dumps(chunk, ensure_ascii=False)
        size_bytes = len(chunk_json.encode('utf-8'))
        
        return {
            'item_count': len(chunk),
            'size_bytes': size_bytes,
            'size_kb': round(size_bytes / 1024, 2),
            'utilization': round(size_bytes / self.effective_max_size * 100, 2)
        }
    
    def _group_by_key(self, items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
        """按键值分组项目"""
        groups = {}
        for item in items:
            value = item.get(key)
            if value not in groups:
                groups[value] = []
            groups[value].append(item)
        return groups
    
    def _fill_chunk(self, items: List[Dict], current_chunk: List[Dict], 
                    current_size: int) -> tuple[List[Dict], List[Dict]]:
        """
        尽可能填充当前块
        
        Returns:
            (完成的块, 剩余项目)
        """
        chunk = current_chunk.copy()
        size = current_size
        remaining = []
        
        for item in items:
            item_size = len(json.dumps(item, ensure_ascii=False).encode('utf-8'))
            
            if size + item_size <= self.effective_max_size:
                chunk.append(item)
                size += item_size
            else:
                remaining.append(item)
        
        return chunk, remaining
