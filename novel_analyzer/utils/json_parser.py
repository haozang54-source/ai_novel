"""
JSON解析和修复工具
"""
import json
import re
from typing import Optional, Dict, Any


class JSONParser:
    """JSON解析工具类"""
    
    @staticmethod
    def parse(text: str, retry: int = 3) -> Optional[Dict[Any, Any]]:
        """
        解析JSON文本，支持自动修复
        
        Args:
            text: JSON文本
            retry: 重试次数
            
        Returns:
            解析后的字典，失败返回None
        """
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取JSON部分
        extracted = JSONParser._extract_json(text)
        if extracted:
            try:
                return json.loads(extracted)
            except json.JSONDecodeError:
                pass
        
        # 尝试修复常见问题
        for i in range(retry):
            fixed = JSONParser._fix_common_issues(text if i == 0 else extracted)
            if fixed:
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    @staticmethod
    def _extract_json(text: str) -> Optional[str]:
        """
        从文本中提取JSON部分
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            提取的JSON字符串
        """
        # 查找第一个 { 到最后一个 }
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        
        # 尝试查找数组格式
        start = text.find('[')
        end = text.rfind(']')
        
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        
        return None
    
    @staticmethod
    def _fix_common_issues(text: str) -> Optional[str]:
        """
        修复JSON中的常见问题
        
        Args:
            text: JSON文本
            
        Returns:
            修复后的JSON文本
        """
        if not text:
            return None
        
        # 移除注释
        text = re.sub(r'//.*?\n', '\n', text)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # 修复单引号
        text = text.replace("'", '"')
        
        # 修复尾部逗号
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # 修复缺失的引号（针对键）
        text = re.sub(r'(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)
        
        return text
    
    @staticmethod
    def validate_structure(data: dict, required_keys: list) -> bool:
        """
        验证JSON结构是否包含必需的键
        
        Args:
            data: JSON数据
            required_keys: 必需的键列表
            
        Returns:
            是否包含所有必需的键
        """
        if not isinstance(data, dict):
            return False
        
        for key in required_keys:
            if key not in data:
                return False
        
        return True
