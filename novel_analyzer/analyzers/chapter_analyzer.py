"""
单章分析器模块
"""
import os
import time
from typing import Dict, Optional
from langchain_community.llms import Ollama
from utils.file_utils import FileUtils
from utils.json_parser import JSONParser
from utils.prompt_templates import PromptTemplates


class ChapterAnalyzer:
    """单章分析器"""
    
    def __init__(self, llm, config: dict, output_dir: str):
        """
        初始化单章分析器
        
        Args:
            llm: LangChain LLM实例
            config: 配置字典
            output_dir: 输出目录
        """
        self.llm = llm
        self.config = config
        self.output_dir = os.path.join(output_dir, 'chapter_summaries')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.retry_times = config.get('extraction', {}).get('retry_times', 3)
    
    def analyze_chapter(self, chapter: Dict) -> Optional[Dict]:
        """
        分析单个章节
        
        Args:
            chapter: 章节数据
            
        Returns:
            分析结果字典
        """
        chapter_number = chapter['number']
        
        # 检查是否已存在结果
        output_file = os.path.join(self.output_dir, f"chapter_{chapter_number:03d}.json")
        if os.path.exists(output_file):
            print(f"  章节 {chapter_number} 已分析，跳过")
            return FileUtils.load_json(output_file)
        
        # 构建prompt（智能截断，保留完整句子）
        content = chapter['content']
        max_length = 6000  # 增加上下文长度
        if len(content) > max_length:
            # 在max_length附近找到句号、问号、感叹号等标点
            truncate_pos = max_length
            for i in range(max_length, max(0, max_length - 200), -1):
                if content[i] in '。！？…\n':
                    truncate_pos = i + 1
                    break
            content = content[:truncate_pos]
        
        prompt = PromptTemplates.CHAPTER_ANALYSIS.format(
            chapter_text=content,
            chapter_number=chapter_number
        )
        
        # 调用LLM（带重试）
        for attempt in range(self.retry_times):
            try:
                # 每次都重新调用LLM
                response = self.llm.invoke(prompt)
                
                # 提取响应文本（兼容不同LLM返回格式）
                if hasattr(response, 'content'):
                    # ChatOpenAI等返回AIMessage对象
                    response_text = response.content
                else:
                    # Ollama等返回字符串
                    response_text = str(response)
                
                # 解析JSON
                result = JSONParser.parse(response_text)
                
                if result and self._validate_chapter_result(result):
                    # 添加基本信息
                    result['chapter_number'] = chapter_number
                    result['chapter_title'] = chapter.get('title', '')
                    result['word_count'] = chapter['word_count']
                    
                    # 保存结果
                    FileUtils.save_json(result, output_file)
                    return result
                else:
                    # JSON解析失败，打印调试信息
                    if attempt < self.retry_times - 1:
                        print(f"  ⚠️  章节 {chapter_number} JSON解析失败，重新调用LLM重试 {attempt + 1}/{self.retry_times}")
                        # 打印部分响应用于调试
                        if response_text:
                            preview = response_text[:200] if len(response_text) > 200 else response_text
                            print(f"  📝 响应预览: {preview}...")
                        time.sleep(2)  # 等待后重新调用
                        continue
                    else:
                        print(f"  ⚠️  章节 {chapter_number} JSON解析失败，已达到最大重试次数")
                        # 打印完整响应用于调试
                        if response_text:
                            print(f"  📝 最后一次响应: {response_text[:500]}...")
                    
            except Exception as e:
                print(f"  ❌ 章节 {chapter_number} 调用LLM出错: {e}")
                if attempt < self.retry_times - 1:
                    print(f"  🔄 等待2秒后重试...")
                    time.sleep(2)
                    continue
        
        print(f"  ❌ 章节 {chapter_number} 分析失败，已达到最大重试次数")
        return None
    
    def _validate_chapter_result(self, result: dict) -> bool:
        """
        验证章节分析结果
        
        Args:
            result: 分析结果
            
        Returns:
            是否有效
        """
        required_keys = ['characters', 'locations', 'events', 'world_elements', 'writing_style_notes', 'chapter_summary']
        if not JSONParser.validate_structure(result, required_keys):
            return False
        
        # 验证characters中必须有relationships字段（即使为空列表）
        if 'characters' in result:
            for char in result['characters']:
                if 'relationships' not in char:
                    char['relationships'] = []
        
        # 验证chapter_summary结构
        if 'chapter_summary' in result:
            summary = result['chapter_summary']
            # 如果是旧版本的字符串格式，转换为新格式
            if isinstance(summary, str):
                result['chapter_summary'] = {
                    "title": "待补充",
                    "main_content": summary,
                    "key_points": [],
                    "chapter_purpose": "待补充"
                }
            # 验证新格式必要字段
            elif isinstance(summary, dict):
                if 'main_content' not in summary:
                    return False
        
        return True
    
    def batch_analyze(self, chapters: list) -> list:
        """
        批量分析章节
        
        Args:
            chapters: 章节列表
            
        Returns:
            分析结果列表
        """
        results = []
        total = len(chapters)
        
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"第一层：单章分析")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for idx, chapter in enumerate(chapters, 1):
            print(f"📖 分析章节 {idx}/{total}: {chapter.get('title', chapter['filename'])}")
            
            result = self.analyze_chapter(chapter)
            if result:
                results.append(result)
                print(f"  ✓ 成功")
            else:
                print(f"  ✗ 失败")
            
            # 避免请求过快
            time.sleep(0.5)
        
        print(f"\n💾 已保存单章结果: {len(results)}/{total} 个JSON文件")
        return results
