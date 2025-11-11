"""大纲师智能体 - 负责生成故事大纲"""
from typing import Dict, Any, List
from .base_agent import BaseAgent


class OutlinerAgent(BaseAgent):
    """大纲师 - 生成详细的章节大纲"""
    
    def __init__(self, llm=None):
        super().__init__(llm, "Outliner")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成故事大纲
        
        Args:
            input_data: {
                "story_concept": "故事概念",
                "target_chapters": 目标章节数,
                "chapter_length": 每章字数,
                "genre": "小说类型"
            }
            
        Returns:
            {
                "outline": [
                    {
                        "chapter_num": 1,
                        "title": "章节标题",
                        "summary": "章节摘要",
                        "key_events": ["事件1", "事件2"],
                        "conflicts": "主要冲突",
                        "emotional_beat": "情感节拍"
                    },
                    ...
                ]
            }
        """
        self.log(f"📝 开始生成故事大纲...")
        
        story_concept = input_data.get("story_concept", "未指定")
        target_chapters = input_data.get("target_chapters", 3)
        genre = input_data.get("genre", "玄幻")
        
        # 生成大纲
        outline_prompt = f"""
你是一位专业的小说大纲师,擅长构建引人入胜的故事框架。

任务: 为以下故事创作详细的章节大纲

故事信息:
- 核心概念: {story_concept}
- 小说类型: {genre}
- 章节数量: {target_chapters}章

要求:
1. 每章都要有明确的冲突和看点
2. 整体结构符合{genre}小说的特点
3. 节奏张弛有度,高潮迭起
4. 每章之间有清晰的承接关系

请为每一章生成:
- 章节标题 (吸引眼球)
- 章节摘要 (100字左右)
- 关键事件 (2-3个)
- 主要冲突
- 情感节拍 (紧张/舒缓/悬疑等)

请按以下格式输出每章:

第X章: [标题]
摘要: [章节摘要]
关键事件:
- [事件1]
- [事件2]
- [事件3]
冲突: [主要冲突]
情感: [情感节拍]

---
"""
        
        self.log(f"🎯 正在为 {target_chapters} 章节规划大纲...")
        response = self.invoke_llm(outline_prompt)
        
        # 解析大纲
        outline = self._parse_outline(response, target_chapters)
        
        self.log(f"✅ 大纲生成完成,共 {len(outline)} 章")
        for chapter in outline:
            self.log(f"   第{chapter['chapter_num']}章: {chapter['title']}")
        
        return {"outline": outline, "raw_outline": response}
    
    def _parse_outline(self, outline_text: str, expected_chapters: int) -> List[Dict[str, Any]]:
        """解析大纲文本为结构化数据"""
        chapters = []
        current_chapter = None
        
        lines = outline_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 检测章节标题
            if line.startswith('第') and '章' in line and ':' in line:
                # 保存上一章
                if current_chapter:
                    chapters.append(current_chapter)
                
                # 开始新章
                parts = line.split(':', 1)
                chapter_num = len(chapters) + 1
                title = parts[1].strip() if len(parts) > 1 else f"第{chapter_num}章"
                
                current_chapter = {
                    "chapter_num": chapter_num,
                    "title": title,
                    "summary": "",
                    "key_events": [],
                    "conflicts": "",
                    "emotional_beat": ""
                }
            
            elif current_chapter:
                # 解析章节内容
                if line.startswith('摘要:'):
                    current_chapter['summary'] = line.replace('摘要:', '').strip()
                elif line.startswith('- ') and not current_chapter.get('summary'):
                    # 关键事件
                    current_chapter['key_events'].append(line[2:].strip())
                elif line.startswith('冲突:'):
                    current_chapter['conflicts'] = line.replace('冲突:', '').strip()
                elif line.startswith('情感:'):
                    current_chapter['emotional_beat'] = line.replace('情感:', '').strip()
        
        # 添加最后一章
        if current_chapter:
            chapters.append(current_chapter)
        
        # 如果解析失败,生成默认大纲
        if len(chapters) == 0:
            self.log(f"⚠️ 大纲解析失败,生成默认大纲")
            for i in range(expected_chapters):
                chapters.append({
                    "chapter_num": i + 1,
                    "title": f"第{i+1}章",
                    "summary": "章节内容待生成",
                    "key_events": ["主要事件"],
                    "conflicts": "待定",
                    "emotional_beat": "正常"
                })
        
        return chapters
