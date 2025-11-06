"""
整体分析器模块
"""
import os
import json
import time
from typing import List, Dict, Optional
from utils.file_utils import FileUtils
from utils.json_parser import JSONParser
from utils.prompt_templates import PromptTemplates


class GlobalAnalyzer:
    """整体分析器（第三层）"""
    
    def __init__(self, llm, config: dict, output_dir: str):
        """
        初始化整体分析器
        
        Args:
            llm: LangChain LLM实例
            config: 配置字典
            output_dir: 输出目录
        """
        self.llm = llm
        self.config = config
        self.output_dir = output_dir
        self.retry_times = config.get('extraction', {}).get('retry_times', 3)
    
    def analyze_global(self, segment_summaries: List[Dict]) -> Optional[Dict]:
        """
        基于分段汇总进行整体分析
        
        Args:
            segment_summaries: 分段汇总结果列表
            
        Returns:
            整体分析结果
        """
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"第三层：整体分析")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"基于 {len(segment_summaries)} 个分段进行整体分析\n")
        
        # 检查是否已存在
        output_file = os.path.join(self.output_dir, 'global_analysis.json')
        if os.path.exists(output_file):
            print(f"✓ 整体分析已存在，跳过")
            return FileUtils.load_json(output_file)
        
        # 准备分段汇总数据
        segments_data = self._prepare_segments_data(segment_summaries)
        
        # 构建prompt
        prompt = PromptTemplates.GLOBAL_ANALYSIS.format(
            segments_data=json.dumps(segments_data, ensure_ascii=False, indent=2),
            total_segments=len(segment_summaries)
        )
        
        # 调用LLM（带重试）
        print(f"🤖 开始整体分析...")
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
                
                if result and self._validate_global_result(result):
                    # 保存结果
                    FileUtils.save_json(result, output_file)
                    print(f"✓ 整体分析成功")
                    return result
                else:
                    if attempt < self.retry_times - 1:
                        print(f"⚠️  JSON解析失败，重新调用LLM重试 {attempt + 1}/{self.retry_times}")
                        time.sleep(2)
                        continue
                    else:
                        print(f"⚠️  JSON解析失败")
                    
            except Exception as e:
                print(f"❌ 整体分析调用LLM出错: {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(2)
                    continue
        
        print(f"❌ 整体分析失败")
        return None
    
    def _prepare_segments_data(self, segments: List[Dict]) -> List[Dict]:
        """
        准备分段数据（精简版）
        
        Args:
            segments: 分段汇总结果列表
            
        Returns:
            精简的分段数据
        """
        simplified = []
        for seg in segments:
            simplified.append({
                'segment_range': seg.get('segment_range'),
                'characters': seg.get('characters_summary', {}),
                'locations': seg.get('locations_summary', []),
                'plot': seg.get('plot_summary', {}),
                'world_building': seg.get('world_building', {}),
                'style': seg.get('style_patterns', {})
            })
        return simplified
    
    def _validate_global_result(self, result: dict) -> bool:
        """
        验证整体分析结果
        
        Args:
            result: 分析结果
            
        Returns:
            是否有效
        """
        required_keys = [
            'world_setting',
            'core_characters',
            'plot_structure',
            'writing_style',
            'themes'
        ]
        return JSONParser.validate_structure(result, required_keys)
