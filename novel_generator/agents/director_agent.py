"""总导演智能体 - 负责全局规划与协调"""
from typing import Dict, Any
from .base_agent import BaseAgent


class DirectorAgent(BaseAgent):
    """总导演 - 解析需求并制定创作计划"""
    
    def __init__(self, llm=None):
        super().__init__(llm, "Director")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析用户需求并制定创作计划
        
        Args:
            input_data: {
                "user_theme": "用户输入的主题",
                "target_length": 目标字数,
                "genre": "小说类型" (可选)
            }
            
        Returns:
            {
                "plan": "创作计划",
                "story_concept": "故事概念",
                "target_chapters": 目标章节数,
                "chapter_length": 每章字数
            }
        """
        self.log(f"📋 开始规划创作任务...")
        
        user_theme = input_data.get("user_theme", "未指定主题")
        target_length = input_data.get("target_length", 10000)
        genre = input_data.get("genre", "玄幻")
        
        # 制定创作计划
        planning_prompt = f"""
你是一位经验丰富的小说总导演,负责规划整个小说创作流程。

用户需求:
- 主题: {user_theme}
- 类型: {genre}
- 目标字数: {target_length}字

请制定详细的创作计划,包括:
1. 故事核心概念(简洁有力的一句话概括)
2. 建议的章节数量
3. 每章平均字数
4. 整体故事节奏规划(起承转合)
5. 关键创作要点

请以JSON格式输出(只输出JSON,不要其他内容):
{{
    "story_concept": "故事核心概念",
    "target_chapters": 章节数,
    "chapter_length": 每章字数,
    "story_rhythm": "节奏规划",
    "key_points": ["要点1", "要点2", "..."]
}}
"""
        
        self.log("🤔 正在分析需求并制定计划...")
        response = self.invoke_llm(planning_prompt)
        
        # 解析响应
        try:
            import json
            import re
            
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                # 如果解析失败,使用默认值
                self.log("⚠️ 计划解析失败,使用默认配置")
                plan_data = {
                    "story_concept": user_theme,
                    "target_chapters": max(3, target_length // 3000),
                    "chapter_length": 3000,
                    "story_rhythm": "起承转合",
                    "key_points": ["开局吸引读者", "中段冲突升级", "结尾圆满收官"]
                }
        except Exception as e:
            self.log(f"⚠️ 解析异常: {e},使用默认配置")
            plan_data = {
                "story_concept": user_theme,
                "target_chapters": max(3, target_length // 3000),
                "chapter_length": 3000,
                "story_rhythm": "起承转合",
                "key_points": ["开局吸引读者", "中段冲突升级", "结尾圆满收官"]
            }
        
        result = {
            "plan": response,
            "story_concept": plan_data.get("story_concept", user_theme),
            "target_chapters": plan_data.get("target_chapters", 3),
            "chapter_length": plan_data.get("chapter_length", 3000),
            "story_rhythm": plan_data.get("story_rhythm", "起承转合"),
            "key_points": plan_data.get("key_points", [])
        }
        
        self.log(f"✅ 创作计划已完成")
        self.log(f"   故事概念: {result['story_concept']}")
        self.log(f"   计划章节: {result['target_chapters']}章")
        self.log(f"   每章字数: {result['chapter_length']}字")
        
        return result
