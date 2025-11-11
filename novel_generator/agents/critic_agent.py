"""评审员智能体 - 负责内容质量评估"""
from typing import Dict, Any
from .base_agent import BaseAgent


class CriticAgent(BaseAgent):
    """评审员 - 评估生成内容的质量"""
    
    def __init__(self, llm=None):
        super().__init__(llm, "Critic")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估章节内容质量
        
        Args:
            input_data: {
                "content": "待评估的内容",
                "chapter_info": 章节信息,
                "story_context": 故事背景
            }
            
        Returns:
            {
                "overall_score": 总分(0-10),
                "readability": 可读性评分,
                "plot_consistency": 情节连贯性评分,
                "character_consistency": 角色一致性评分,
                "writing_quality": 文笔质量评分,
                "suggestions": ["改进建议"],
                "highlights": ["亮点"],
                "issues": ["问题"]
            }
        """
        content = input_data.get("content", "")
        chapter_info = input_data.get("chapter_info", {})
        
        self.log(f"🔍 开始评审章节内容...")
        
        # 构建评审提示词
        evaluation_prompt = f"""
你是一位经验丰富的小说编辑,负责评估网络小说章节的质量。

【待评审章节】
{content[:1500]}...  (前1500字)

【章节要求】
标题: {chapter_info.get('title', '')}
摘要: {chapter_info.get('summary', '')}
关键事件: {', '.join(chapter_info.get('key_events', []))}

【评审维度】
请从以下5个维度评分(0-10分):
1. 可读性 - 语言流畅度、易读性
2. 情节连贯性 - 逻辑是否通顺、前后是否呼应
3. 文笔质量 - 描写是否生动、语言是否优美
4. 情节吸引力 - 是否有吸引读者的亮点
5. 符合大纲 - 是否包含所需的关键事件

请按以下JSON格式输出(只输出JSON):
{{
    "readability": 评分,
    "plot_consistency": 评分,
    "writing_quality": 评分,
    "plot_appeal": 评分,
    "outline_match": 评分,
    "overall_score": 总体评分,
    "highlights": ["亮点1", "亮点2"],
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
}}
"""
        
        self.log("📊 正在分析内容质量...")
        response = self.invoke_llm(evaluation_prompt)
        
        # 解析评估结果
        evaluation = self._parse_evaluation(response)
        
        # 显示评审结果
        self.log(f"✅ 评审完成 - 总分: {evaluation['overall_score']}/10")
        self.log(f"   可读性: {evaluation['readability']}/10")
        self.log(f"   情节连贯性: {evaluation['plot_consistency']}/10")
        self.log(f"   文笔质量: {evaluation['writing_quality']}/10")
        
        if evaluation['highlights']:
            self.log(f"   ✨ 亮点: {', '.join(evaluation['highlights'][:2])}")
        if evaluation['issues']:
            self.log(f"   ⚠️ 问题: {', '.join(evaluation['issues'][:2])}")
        
        return evaluation
    
    def _parse_evaluation(self, response: str) -> Dict[str, Any]:
        """解析评估结果"""
        try:
            import json
            import re
            
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                eval_data = json.loads(json_match.group())
            else:
                eval_data = {}
        except Exception as e:
            self.log(f"⚠️ 评估结果解析失败: {e}")
            eval_data = {}
        
        # 确保所有字段都存在
        return {
            "overall_score": eval_data.get("overall_score", 7.0),
            "readability": eval_data.get("readability", 7.0),
            "plot_consistency": eval_data.get("plot_consistency", 7.0),
            "writing_quality": eval_data.get("writing_quality", 7.0),
            "plot_appeal": eval_data.get("plot_appeal", 7.0),
            "outline_match": eval_data.get("outline_match", 7.0),
            "highlights": eval_data.get("highlights", ["内容生动"]),
            "issues": eval_data.get("issues", []),
            "suggestions": eval_data.get("suggestions", ["继续保持"])
        }
