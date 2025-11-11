"""场景作家智能体 - 负责具体内容生成"""
from typing import Dict, Any
from .base_agent import BaseAgent


class SceneWriterAgent(BaseAgent):
    """场景作家 - 生成具体的章节内容"""
    
    def __init__(self, llm=None):
        super().__init__(llm, "SceneWriter")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成章节内容
        
        Args:
            input_data: {
                "chapter_info": {
                    "chapter_num": 章节号,
                    "title": "章节标题",
                    "summary": "章节摘要",
                    "key_events": ["事件列表"],
                    "conflicts": "主要冲突",
                    "emotional_beat": "情感节拍"
                },
                "story_context": "整体故事背景",
                "target_length": 目标字数,
                "genre": "小说类型",
                "previous_content": "前文内容" (可选)
            }
            
        Returns:
            {
                "content": "生成的章节内容",
                "word_count": 实际字数
            }
        """
        chapter_info = input_data.get("chapter_info", {})
        story_context = input_data.get("story_context", "")
        target_length = input_data.get("target_length", 3000)
        genre = input_data.get("genre", "玄幻")
        previous_content = input_data.get("previous_content", "")
        
        chapter_num = chapter_info.get("chapter_num", 1)
        title = chapter_info.get("title", f"第{chapter_num}章")
        
        self.log(f"✍️ 开始创作: {title}")
        
        # 构建创作提示词
        writing_prompt = self._build_writing_prompt(
            chapter_info, story_context, target_length, genre, previous_content
        )
        
        # 生成内容
        self.log(f"🎨 正在生成约{target_length}字的内容...")
        content = self.invoke_llm(writing_prompt)
        
        # 统计字数
        word_count = len(content)
        
        self.log(f"✅ 创作完成,共{word_count}字")
        
        return {
            "content": content,
            "word_count": word_count,
            "chapter_num": chapter_num,
            "title": title
        }
    
    def _build_writing_prompt(self, chapter_info: Dict, story_context: str, 
                            target_length: int, genre: str, previous_content: str) -> str:
        """构建写作提示词"""
        
        chapter_num = chapter_info.get("chapter_num", 1)
        title = chapter_info.get("title", "")
        summary = chapter_info.get("summary", "")
        key_events = chapter_info.get("key_events", [])
        conflicts = chapter_info.get("conflicts", "")
        emotional_beat = chapter_info.get("emotional_beat", "")
        
        # 基础提示词
        prompt = f"""
你是一位专业的{genre}小说作家,擅长创作引人入胜的网络小说。

【整体背景】
{story_context}

【当前章节信息】
章节: 第{chapter_num}章 - {title}
章节摘要: {summary}
关键事件: {', '.join(key_events)}
主要冲突: {conflicts}
情感基调: {emotional_beat}

【写作要求】
1. 目标字数: {target_length}字左右
2. 符合{genre}小说特点,有代入感
3. 对话生动自然,符合人物性格
4. 场景描写细腻,画面感强
5. 节奏把控得当,有张有弛
6. 情节推进流畅,逻辑合理
7. 语言风格统一,符合网文读者喜好
"""
        
        # 如果有前文,添加衔接要求
        if previous_content:
            # 只取前文末尾部分作为参考
            prev_excerpt = previous_content[-500:] if len(previous_content) > 500 else previous_content
            prompt += f"""
【前文末尾】
...{prev_excerpt}

【衔接要求】
本章需要承接上文,保持情节连贯性和人物一致性。
"""
        
        # 添加具体创作指令
        prompt += f"""

【创作任务】
现在请创作第{chapter_num}章的完整内容,包括:
- 章节标题
- 正文内容(需包含所有关键事件,展现主要冲突,营造{emotional_beat}的情感氛围)

请直接开始创作,不要有任何多余的解释说明。

第{chapter_num}章 {title}

"""
        
        return prompt
