"""
单章分析器V2 - 分段输出版本（容错机制 + 增量更新）
"""
import os
import json
import time
from typing import Dict, Optional, List
from utils.file_utils import FileUtils
from utils.json_parser import JSONParser
from utils.time_checker import TimeChecker


class ChapterAnalyzerV2:
    """
    单章分析器V2 - 分段输出版本
    
    特点：
    1. 将大JSON拆分为6个小任务，每个任务单独调用LLM
    2. 每个任务完成后立即保存到临时文件
    3. 支持断点续传：已完成的部分不会重复执行
    4. 单个任务失败不影响其他任务
    5. 最终合并所有部分为完整JSON
    """
    
    # 定义分段任务
    TASKS = [
        'characters',
        'locations', 
        'events',
        'world_elements',
        'writing_style_notes',
        'chapter_summary'
    ]
    
    def __init__(self, llm, config: dict, output_dir: str, no_time_check: bool = False):
        """
        初始化单章分析器V2
        
        Args:
            llm: LangChain LLM实例
            config: 配置字典
            output_dir: 输出目录
            no_time_check: 是否跳过时间检查
        """
        self.llm = llm
        self.config = config
        self.output_dir = os.path.join(output_dir, 'chapter_summaries')
        self.temp_dir = os.path.join(output_dir, 'chapter_temp')
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.retry_times = config.get('extraction', {}).get('retry_times', 3)  # 单任务重试3次即可
        self.no_time_check = no_time_check
        
        # 如果禁用时间检查，传入空配置给TimeChecker
        time_check_config = {} if no_time_check else config
        self.time_checker = TimeChecker(time_check_config)
    
    def analyze_chapter(self, chapter: Dict) -> Optional[Dict]:
        """
        分析单个章节（分段执行）
        
        Args:
            chapter: 章节数据
            
        Returns:
            分析结果字典
        """
        chapter_number = chapter['number']
        
        # 检查是否已存在完整结果
        output_file = os.path.join(self.output_dir, f"chapter_{chapter_number:03d}.json")
        if os.path.exists(output_file):
            print(f"  章节 {chapter_number} 已分析，跳过")
            return FileUtils.load_json(output_file)
        
        # 准备章节内容（智能截断）
        content = chapter['content']
        max_length = 6000
        if len(content) > max_length:
            truncate_pos = max_length
            for i in range(max_length, max(0, max_length - 200), -1):
                if content[i] in '。！？…\n':
                    truncate_pos = i + 1
                    break
            content = content[:truncate_pos]
        
        # 创建章节临时目录
        chapter_temp_dir = os.path.join(self.temp_dir, f"chapter_{chapter_number:03d}")
        os.makedirs(chapter_temp_dir, exist_ok=True)
        
        # 执行分段提取
        result = {}
        success_count = 0
        
        for task_name in self.TASKS:
            print(f"    → 提取 {task_name}...")
            
            # 检查是否已有缓存
            temp_file = os.path.join(chapter_temp_dir, f"{task_name}.json")
            if os.path.exists(temp_file):
                try:
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        result[task_name] = json.load(f)
                    print(f"      ✓ 从缓存加载")
                    success_count += 1
                    continue
                except Exception as e:
                    print(f"      ⚠️  缓存文件损坏，重新提取: {e}")
            
            # 调用LLM提取该部分
            task_result = self._retry_extract(task_name, content, chapter_number)
            
            if task_result is not None:
                result[task_name] = task_result
                # 立即保存到临时文件
                try:
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(task_result, f, ensure_ascii=False, indent=2)
                    print(f"      ✓ 成功")
                    success_count += 1
                except Exception as e:
                    print(f"      ⚠️  保存失败: {e}")
            else:
                print(f"      ✗ 失败")
            
            # 避免请求过快
            time.sleep(0.5)
        
        # 检查是否所有任务都成功
        if success_count < len(self.TASKS):
            print(f"  ⚠️  章节 {chapter_number} 部分任务失败 ({success_count}/{len(self.TASKS)})")
            # 即使部分失败，也保存已有结果
        
        # 添加基本信息
        result['chapter_number'] = chapter_number
        result['chapter_title'] = chapter.get('title', '')
        result['word_count'] = chapter['word_count']
        
        # 保存最终结果
        FileUtils.save_json(result, output_file)
        
        # 清理临时文件（可选，如需调试可注释掉）
        # self._cleanup_temp_files(chapter_temp_dir)
        
        return result
    
    def _retry_extract(self, task_name: str, content: str, chapter_number: int) -> Optional[any]:
        """
        带重试机制的提取函数
        
        Args:
            task_name: 任务名称
            content: 章节内容
            chapter_number: 章节号
            
        Returns:
            提取结果
        """
        for attempt in range(self.retry_times):
            try:
                if task_name == 'characters':
                    result = self._extract_characters(content, chapter_number)
                elif task_name == 'locations':
                    result = self._extract_locations(content, chapter_number)
                elif task_name == 'events':
                    result = self._extract_events(content, chapter_number)
                elif task_name == 'world_elements':
                    result = self._extract_world_elements(content, chapter_number)
                elif task_name == 'writing_style_notes':
                    result = self._extract_writing_style(content, chapter_number)
                elif task_name == 'chapter_summary':
                    result = self._extract_chapter_summary(content, chapter_number)
                else:
                    return None
                
                if result is not None:
                    return result
                    
            except Exception as e:
                if attempt < self.retry_times - 1:
                    print(f"        ⚠️  重试 {attempt + 1}/{self.retry_times}: {e}")
                    time.sleep(1)
                else:
                    print(f"        ❌ 达到最大重试次数: {e}")
        
        return None
    
    def _extract_characters(self, content: str, chapter_number: int) -> Optional[List]:
        """提取角色信息"""
        prompt = f"""分析以下章节内容，只提取角色信息。

章节内容：
{content}

请严格按照以下JSON格式输出角色列表，不要添加其他文字：
[
  {{
    "name": "角色名",
    "role": "protagonist/antagonist/supporting",
    "first_appearance": true,
    "status_changes": ["变化描述"],
    "relationships": [
      {{
        "target": "相关角色名",
        "relation_type": "丈夫/妻子/父亲/母亲/兄弟/姐妹/师徒/朋友/敌人/恋人等",
        "description": "关系描述"
      }}
    ],
    "appearance_traits": ["外貌特征"],
    "personality_traits": ["性格特征"]
  }}
]

只输出JSON数组，不要其他文字。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_locations(self, content: str, chapter_number: int) -> Optional[List]:
        """提取地点信息"""
        prompt = f"""分析以下章节内容，只提取地点信息。

章节内容：
{content}

请严格按照以下JSON格式输出地点列表，不要添加其他文字：
[
  {{
    "name": "地点名",
    "type": "地点类型",
    "first_appearance": true,
    "description": "地点描述"
  }}
]

只输出JSON数组，不要其他文字。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_events(self, content: str, chapter_number: int) -> Optional[List]:
        """提取事件信息"""
        prompt = f"""分析以下章节内容，只提取关键事件。

章节内容：
{content}

请严格按照以下JSON格式输出事件列表，不要添加其他文字：
[
  {{
    "type": "conflict/development/climax/turning_point",
    "description": "事件描述",
    "importance": "high/medium/low",
    "emotional_tone": "情感基调",
    "participants": ["参与角色"]
  }}
]

只输出JSON数组，不要其他文字。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_world_elements(self, content: str, chapter_number: int) -> Optional[List]:
        """提取世界观元素"""
        prompt = f"""分析以下章节内容，只提取世界观相关元素。

章节内容：
{content}

请严格按照以下JSON格式输出世界观元素列表，不要添加其他文字：
[
  {{
    "type": "power_system/social_rule/special_item/organization",
    "element": "要素名称",
    "details": "详细信息"
  }}
]

只输出JSON数组，不要其他文字。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_writing_style(self, content: str, chapter_number: int) -> Optional[Dict]:
        """提取写作风格"""
        prompt = f"""分析以下章节内容，只提取写作风格信息。

章节内容：
{content}

请严格按照以下JSON格式输出写作风格，不要添加其他文字：
{{
  "narrative_perspective": "叙事视角",
  "key_phrases": ["关键短语"],
  "emotional_intensity": "high/medium/low",
  "description_focus": ["描写重点"]
}}

只输出JSON对象，不要其他文字。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_chapter_summary(self, content: str, chapter_number: int) -> Optional[Dict]:
        """提取章节摘要"""
        prompt = f"""分析以下章节内容，生成章节摘要。

章节内容：
{content}

请严格按照以下JSON格式输出章节摘要，不要添加其他文字：
{{
  "title": "章节标题或核心主题",
  "main_content": "详细概括本章主要内容，包括：1)主要角色的行动和对话 2)关键事件的发展过程 3)重要信息的揭示 4)情节的推进方向（150-300字）",
  "key_points": ["要点1", "要点2", "要点3"],
  "chapter_purpose": "本章在整体故事中的作用（如：引入新角色、推进主线、埋下伏笔、展现世界观等）"
}}

只输出JSON对象，不要其他文字。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _cleanup_temp_files(self, temp_dir: str):
        """清理临时文件"""
        try:
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"      ⚠️  清理临时文件失败: {e}")
    
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
        print(f"第一层：单章分析 (V2 - 分段输出版本)")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for idx, chapter in enumerate(chapters, 1):
            # 检查时间（每个章节前检查）
            self.time_checker.check_and_wait()
            
            print(f"📖 分析章节 {idx}/{total}: {chapter.get('title', chapter['filename'])}")
            
            result = self.analyze_chapter(chapter)
            if result:
                results.append(result)
                print(f"  ✓ 成功")
            else:
                print(f"  ✗ 失败")
        
        print(f"\n💾 已保存单章结果: {len(results)}/{total} 个JSON文件")
        print(f"📁 临时文件目录: {self.temp_dir}")
        return results
