"""AI编辑助手智能体 - 负责文本改写和优化"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class EditorAgent(BaseAgent):
    """AI编辑助手 - 根据用户指令改写和优化文本"""
    
    def __init__(self, llm=None):
        super().__init__(llm, "Editor")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文本改写任务
        
        Args:
            input_data: {
                "selected_text": str,  # 选中的文本
                "user_prompt": str,    # 用户的修改指令
                "context": {           # 上下文信息
                    "before_text": str,
                    "after_text": str
                },
                "knowledge_base": {    # 知识库信息
                    "characters": List[Dict],
                    "worldviews": List[Dict],
                    "locations": List[Dict],
                    "items": List[Dict],
                    "foreshadowings": List[Dict],
                    "writing_style": Optional[Dict]
                }
            }
        
        Returns:
            {
                "original_text": str,      # 原文
                "suggested_text": str,     # 改写后的文本
                "explanation": str,        # 改写说明
                "confidence": float,       # 置信度 0-1
                "conversation_id": str     # 对话ID
            }
        """
        self.log("📝 开始分析文本改写任务...")
        
        selected_text = input_data.get("selected_text", "")
        user_prompt = input_data.get("user_prompt", "")
        context = input_data.get("context", {})
        knowledge_base = input_data.get("knowledge_base", {})
        
        if not selected_text or not user_prompt:
            return {
                "original_text": selected_text,
                "suggested_text": selected_text,
                "explanation": "缺少必要的输入参数",
                "confidence": 0.0,
                "conversation_id": "error"
            }
        
        # 构建知识库上下文
        kb_context = self._build_knowledge_context(knowledge_base)
        
        # 构建AI提示词
        prompt = self._build_editing_prompt(
            selected_text, 
            user_prompt, 
            context, 
            kb_context
        )
        
        self.log(f"🎯 用户指令: {user_prompt}")
        self.log(f"📊 知识库: {kb_context['summary']}")
        
        # 输出完整的 Prompt 到日志
        self.log("=" * 80)
        self.log("📄 完整 Prompt:")
        self.log("-" * 80)
        self.log(prompt)
        self.log("=" * 80)
        
        # 调用LLM
        response = self.invoke_llm(prompt)
        
        # 解析响应
        result = self._parse_response(response, selected_text)
        
        self.log(f"✅ 改写完成，置信度: {result['confidence']:.0%}")
        
        return result
    
    def _build_knowledge_context(self, knowledge_base: Dict) -> Dict[str, Any]:
        """构建知识库上下文摘要"""
        context_parts = []
        details = {}
        
        # 人物信息
        characters = knowledge_base.get("characters", [])
        if characters:
            char_names = [c.get("name", "") for c in characters]
            context_parts.append(f"相关人物: {', '.join(char_names)}")
            
            # 详细人物信息
            char_details = []
            for c in characters:
                char_info = f"- {c.get('name', '未知')}"
                if c.get('role'):
                    char_info += f" ({c.get('role')})"
                if c.get('personality'):
                    char_info += f": {c.get('personality')}"
                char_details.append(char_info)
            details['characters'] = '\n'.join(char_details)
        
        # 世界观信息
        worldviews = knowledge_base.get("worldviews", [])
        if worldviews:
            world_names = [w.get("name", "") for w in worldviews]
            context_parts.append(f"世界观设定: {', '.join(world_names)}")
            
            world_details = []
            for w in worldviews:
                world_info = f"- {w.get('name', '未知')}"
                if w.get('description'):
                    world_info += f": {w.get('description')}"
                world_details.append(world_info)
            details['worldviews'] = '\n'.join(world_details)
        
        # 地点信息
        locations = knowledge_base.get("locations", [])
        if locations:
            loc_names = [l.get("name", "") for l in locations]
            context_parts.append(f"场景地点: {', '.join(loc_names)}")
            
            loc_details = []
            for l in locations:
                loc_info = f"- {l.get('name', '未知')}"
                if l.get('description'):
                    loc_info += f": {l.get('description')}"
                loc_details.append(loc_info)
            details['locations'] = '\n'.join(loc_details)
        
        # 物品信息
        items = knowledge_base.get("items", [])
        if items:
            item_names = [i.get("name", "") for i in items]
            context_parts.append(f"相关道具: {', '.join(item_names)}")
            
            item_details = []
            for i in items:
                item_info = f"- {i.get('name', '未知')}"
                if i.get('description'):
                    item_info += f": {i.get('description')}"
                item_details.append(item_info)
            details['items'] = '\n'.join(item_details)
        
        # 伏笔信息
        foreshadowings = knowledge_base.get("foreshadowings", [])
        if foreshadowings:
            fh_titles = [f.get("title", "") for f in foreshadowings]
            context_parts.append(f"相关伏笔: {', '.join(fh_titles)}")
            
            fh_details = []
            for f in foreshadowings:
                fh_info = f"- {f.get('title', '未知')}"
                if f.get('content'):
                    fh_info += f": {f.get('content')}"
                fh_details.append(fh_info)
            details['foreshadowings'] = '\n'.join(fh_details)
        
        # 文风设定
        writing_style = knowledge_base.get("writing_style")
        if writing_style:
            context_parts.append("已应用文风设定")
            
            style_details = []
            if writing_style.get('narrative_perspective'):
                style_details.append(f"叙事视角: {writing_style['narrative_perspective']}")
            if writing_style.get('language_style'):
                style_details.append(f"语言风格: {writing_style['language_style']}")
            if writing_style.get('tone'):
                style_details.append(f"整体基调: {writing_style['tone']}")
            details['writing_style'] = '\n'.join(style_details)
        
        return {
            'summary': '\n'.join(context_parts) if context_parts else '无额外知识库',
            'details': details
        }
    
    def _build_editing_prompt(
        self, 
        selected_text: str, 
        user_prompt: str, 
        context: Dict, 
        kb_context: Dict
    ) -> str:
        """构建编辑提示词"""
        
        prompt_parts = [
            "你是一位专业的小说编辑，擅长根据作者的指令对文本进行精细化改写和优化。",
            "",
            "## 任务",
            f"作者选中了以下文本，并希望你根据指令进行修改：",
            "",
            "### 原文",
            f"```",
            selected_text,
            f"```",
            "",
            f"### 作者指令",
            f"{user_prompt}",
            ""
        ]
        
        # 添加上下文
        if context.get("before_text") or context.get("after_text"):
            prompt_parts.append("### 上下文")
            if context.get("before_text"):
                prompt_parts.append(f"**前文片段**: ...{context['before_text']}")
            if context.get("after_text"):
                prompt_parts.append(f"**后文片段**: {context['after_text']}...")
            prompt_parts.append("")
        
        # 添加知识库信息
        if kb_context['details']:
            prompt_parts.append("### 参考知识库")
            
            for key, detail in kb_context['details'].items():
                if key == 'characters':
                    prompt_parts.append("**人物设定**:")
                elif key == 'worldviews':
                    prompt_parts.append("**世界观设定**:")
                elif key == 'locations':
                    prompt_parts.append("**地点设定**:")
                elif key == 'items':
                    prompt_parts.append("**道具设定**:")
                elif key == 'foreshadowings':
                    prompt_parts.append("**伏笔设定**:")
                elif key == 'writing_style':
                    prompt_parts.append("**文风设定**:")
                
                prompt_parts.append(detail)
                prompt_parts.append("")
        
        # 添加要求
        prompt_parts.extend([
            "## 要求",
            "1. 严格按照作者的指令进行修改",
            "2. 保持故事的连贯性和逻辑性",
            "3. 参考知识库中的设定，确保人物性格、世界观、道具等细节一致",
            "4. 如果有文风设定，请严格遵循",
            "5. 保持原文的核心意图，只在必要时调整",
            "6. 改写后的文本应该流畅自然，富有感染力",
            "",
            "## 输出格式",
            "请按照以下格式输出：",
            "",
            "【改写文本】",
            "<改写后的完整文本>",
            "",
            "【改写说明】",
            "<简要说明你做了哪些修改，为什么这样改>",
            "",
            "现在请开始改写。"
        ])
        
        return '\n'.join(prompt_parts)
    
    def _parse_response(self, response: str, original_text: str) -> Dict[str, Any]:
        """解析AI响应"""
        
        # 提取改写文本
        suggested_text = ""
        explanation = ""
        
        # 尝试按标记分割
        if "【改写文本】" in response and "【改写说明】" in response:
            parts = response.split("【改写说明】")
            text_part = parts[0].replace("【改写文本】", "").strip()
            explanation = parts[1].strip() if len(parts) > 1 else ""
            suggested_text = text_part
        else:
            # 如果没有标记，整个响应作为改写文本
            suggested_text = response.strip()
            explanation = "AI已完成改写"
        
        # 计算置信度（简单启发式：根据长度变化和内容相似度）
        confidence = self._calculate_confidence(original_text, suggested_text)
        
        return {
            "original_text": original_text,
            "suggested_text": suggested_text,
            "explanation": explanation,
            "confidence": confidence,
            "conversation_id": f"conv_{hash(original_text + suggested_text)}"
        }
    
    def _calculate_confidence(self, original: str, suggested: str) -> float:
        """计算改写置信度"""
        # 简单启发式：
        # 1. 如果改写文本太短或太长，降低置信度
        # 2. 如果改写文本与原文完全相同，置信度为0
        # 3. 如果改写文本长度合理，置信度较高
        
        if suggested == original:
            return 0.3
        
        if not suggested or len(suggested) < 10:
            return 0.5
        
        len_ratio = len(suggested) / max(len(original), 1)
        
        if 0.5 <= len_ratio <= 2.0:
            return 0.85
        elif 0.3 <= len_ratio <= 3.0:
            return 0.7
        else:
            return 0.6
