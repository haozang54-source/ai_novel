"""
分段汇总器模块
"""
import os
import json
import time
from typing import List, Dict, Optional
from utils.file_utils import FileUtils
from utils.json_parser import JSONParser
from utils.prompt_templates import PromptTemplates


class SegmentSummarizer:
    """分段汇总器"""
    
    def __init__(self, llm, config: dict, output_dir: str):
        """
        初始化分段汇总器
        
        Args:
            llm: LangChain LLM实例
            config: 配置字典
            output_dir: 输出目录
        """
        self.llm = llm
        self.config = config
        self.output_dir = os.path.join(output_dir, 'segment_summaries')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.segment_size = config.get('processing', {}).get('segment_size', 20)
        self.retry_times = config.get('extraction', {}).get('retry_times', 3)
    
    def summarize_segments(self, chapter_results: List[Dict]) -> List[Dict]:
        """
        对所有章节进行分段汇总
        
        Args:
            chapter_results: 章节分析结果列表
            
        Returns:
            分段汇总结果列表
        """
        segment_summaries = []
        total_chapters = len(chapter_results)
        num_segments = (total_chapters + self.segment_size - 1) // self.segment_size
        
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"第二层：分段汇总（每{self.segment_size}章）")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"总共需要汇总 {num_segments} 个分段\n")
        
        for i in range(0, total_chapters, self.segment_size):
            segment_chapters = chapter_results[i:i + self.segment_size]
            start_num = segment_chapters[0]['chapter_number']
            end_num = segment_chapters[-1]['chapter_number']
            
            print(f"📝 汇总分段 {start_num:03d}-{end_num:03d} ({len(segment_chapters)}章)")
            
            summary = self.summarize_segment(segment_chapters, start_num, end_num)
            if summary:
                segment_summaries.append(summary)
                print(f"  ✓ 成功")
            else:
                print(f"  ✗ 失败")
            
            time.sleep(1)
        
        print(f"\n💾 已保存分段汇总: {len(segment_summaries)} 个JSON文件")
        return segment_summaries
    
    def summarize_segment(self, chapters: List[Dict], start_num: int, end_num: int) -> Optional[Dict]:
        """
        汇总单个分段
        
        Args:
            chapters: 章节分析结果列表
            start_num: 起始章节号
            end_num: 结束章节号
            
        Returns:
            汇总结果字典
        """
        # 检查是否已存在
        output_file = os.path.join(self.output_dir, f"segment_{start_num:03d}-{end_num:03d}.json")
        if os.path.exists(output_file):
            print(f"  分段 {start_num:03d}-{end_num:03d} 已汇总，跳过")
            return FileUtils.load_json(output_file)
        
        # 准备章节数据（精简版）
        chapters_data = self._prepare_chapters_data(chapters)
        total_words = sum(ch.get('word_count', 0) for ch in chapters)
        
        # 构建prompt
        prompt = PromptTemplates.SEGMENT_SUMMARY.format(
            chapters_data=json.dumps(chapters_data, ensure_ascii=False, indent=2),
            start_chapter=start_num,
            end_chapter=end_num,
            total_chapters=len(chapters),
            total_words=total_words
        )
        
        # 调用LLM（带重试）
        for attempt in range(self.retry_times):
            try:
                # 每次都重新调用LLM
                response = self.llm.invoke(prompt)
                
                # 提取响应文本（兼容不同LLM返回格式）
                if hasattr(response, 'content'):
                    response_text = response.content
                else:
                    response_text = str(response)
                
                # 解析JSON
                result = JSONParser.parse(response_text)
                
                if result and self._validate_segment_result(result):
                    # 添加基本信息
                    result['segment_range'] = f"{start_num:03d}-{end_num:03d}"
                    result['total_chapters'] = len(chapters)
                    result['total_words'] = total_words
                    
                    # 保存结果
                    FileUtils.save_json(result, output_file)
                    return result
                else:
                    if attempt < self.retry_times - 1:
                        print(f"  ⚠️  分段 {start_num:03d}-{end_num:03d} JSON解析失败，重新调用LLM重试 {attempt + 1}/{self.retry_times}")
                        time.sleep(2)
                        continue
                    else:
                        print(f"  ⚠️  分段 {start_num:03d}-{end_num:03d} JSON解析失败")
                    
            except Exception as e:
                print(f"  ❌ 分段汇总调用LLM出错: {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(2)
                    continue
        
        print(f"  ❌ 分段 {start_num:03d}-{end_num:03d} 汇总失败")
        return None
    
    def _prepare_chapters_data(self, chapters: List[Dict]) -> List[Dict]:
        """
        准备章节数据（精简版，避免prompt过长）
        
        Args:
            chapters: 章节分析结果列表
            
        Returns:
            精简的章节数据列表
        """
        simplified = []
        for ch in chapters:
            simplified.append({
                'chapter_number': ch.get('chapter_number'),
                'title': ch.get('chapter_title', ''),
                'characters': ch.get('characters', []),
                'locations': ch.get('locations', []),
                'events': [
                    {
                        'type': e.get('type'),
                        'description': e.get('description', '')[:100]  # 限制长度
                    } for e in ch.get('events', [])
                ],
                'world_elements': ch.get('world_elements', [])
            })
        return simplified
    
    def _validate_segment_result(self, result: dict) -> bool:
        """
        验证分段汇总结果
        
        Args:
            result: 汇总结果
            
        Returns:
            是否有效
        """
        required_keys = ['characters_summary', 'locations_summary', 'plot_summary', 
                        'world_building', 'style_patterns']
        return JSONParser.validate_structure(result, required_keys)
