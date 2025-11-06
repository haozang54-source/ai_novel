"""
模板生成器模块
"""
import os
import json
from typing import Dict, Optional
from datetime import datetime
from utils.file_utils import FileUtils


class TemplateGenerator:
    """最终模板生成器"""
    
    def __init__(self, config: dict, output_dir: str):
        """
        初始化模板生成器
        
        Args:
            config: 配置字典
            output_dir: 输出目录
        """
        self.config = config
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_all_templates(self, global_analysis: Dict) -> bool:
        """
        生成所有模板文件
        
        Args:
            global_analysis: 整体分析结果
            
        Returns:
            是否成功
        """
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"步骤 4: 生成最终模板")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        templates = [
            ('world_bible.json', self._generate_world_bible),
            ('plot_framework.json', self._generate_plot_framework),
            ('writing_guide.json', self._generate_writing_guide),
            ('character_templates.json', self._generate_character_templates),
            ('quality_criteria.json', self._generate_quality_criteria)
        ]
        
        success_count = 0
        for filename, generator_func in templates:
            print(f"📝 生成 {filename}...")
            try:
                template = generator_func(global_analysis)
                output_path = os.path.join(self.output_dir, filename)
                FileUtils.save_json(template, output_path)
                print(f"  ✓ 成功保存到 {output_path}")
                success_count += 1
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        print(f"\n💾 模板生成完成: {success_count}/{len(templates)} 个")
        return success_count == len(templates)
    
    def _generate_world_bible(self, analysis: Dict) -> Dict:
        """生成世界观圣经"""
        world_setting = analysis.get('world_setting', {})
        
        return {
            "metadata": {
                "template_name": "世界观圣经",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "source": "爆款小说分析系统"
            },
            "world_type": world_setting.get('type', '未知类型'),
            "world_name": world_setting.get('name', '待命名世界'),
            "time_period": world_setting.get('time_period', ''),
            "geography": {
                "main_regions": world_setting.get('geography', {}).get('main_regions', []),
                "key_locations": world_setting.get('geography', {}).get('key_locations', []),
                "special_places": world_setting.get('geography', {}).get('special_places', [])
            },
            "power_system": {
                "name": world_setting.get('power_system', {}).get('name', ''),
                "description": world_setting.get('power_system', {}).get('description', ''),
                "levels": world_setting.get('power_system', {}).get('levels', []),
                "mechanics": world_setting.get('power_system', {}).get('mechanics', [])
            },
            "social_structure": {
                "organizations": world_setting.get('social_structure', {}).get('organizations', []),
                "hierarchy": world_setting.get('social_structure', {}).get('hierarchy', []),
                "relationships": world_setting.get('social_structure', {}).get('relationships', [])
            },
            "rules_and_laws": world_setting.get('rules_and_laws', []),
            "unique_elements": world_setting.get('unique_elements', []),
            "cultural_aspects": world_setting.get('cultural_aspects', {})
        }
    
    def _generate_plot_framework(self, analysis: Dict) -> Dict:
        """生成情节框架"""
        plot_structure = analysis.get('plot_structure', {})
        
        return {
            "metadata": {
                "template_name": "情节框架",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "source": "爆款小说分析系统"
            },
            "story_type": plot_structure.get('story_type', ''),
            "narrative_style": plot_structure.get('narrative_style', ''),
            "main_plotline": {
                "opening": plot_structure.get('main_plotline', {}).get('opening', {}),
                "development": plot_structure.get('main_plotline', {}).get('development', []),
                "climax": plot_structure.get('main_plotline', {}).get('climax', {}),
                "resolution": plot_structure.get('main_plotline', {}).get('resolution', {})
            },
            "subplots": plot_structure.get('subplots', []),
            "conflict_types": plot_structure.get('conflict_types', []),
            "pacing_pattern": {
                "rhythm": plot_structure.get('pacing_pattern', {}).get('rhythm', ''),
                "tension_curve": plot_structure.get('pacing_pattern', {}).get('tension_curve', []),
                "key_turning_points": plot_structure.get('pacing_pattern', {}).get('key_turning_points', [])
            },
            "plot_devices": plot_structure.get('plot_devices', []),
            "foreshadowing": plot_structure.get('foreshadowing', [])
        }
    
    def _generate_writing_guide(self, analysis: Dict) -> Dict:
        """生成写作指南"""
        writing_style = analysis.get('writing_style', {})
        
        return {
            "metadata": {
                "template_name": "写作指南",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "source": "爆款小说分析系统"
            },
            "tone_and_mood": {
                "overall_tone": writing_style.get('tone_and_mood', {}).get('overall_tone', ''),
                "mood_variations": writing_style.get('tone_and_mood', {}).get('mood_variations', [])
            },
            "language_style": {
                "formality_level": writing_style.get('language_style', {}).get('formality_level', ''),
                "vocabulary_characteristics": writing_style.get('language_style', {}).get('vocabulary_characteristics', []),
                "sentence_patterns": writing_style.get('language_style', {}).get('sentence_patterns', [])
            },
            "narrative_techniques": {
                "point_of_view": writing_style.get('narrative_techniques', {}).get('point_of_view', ''),
                "description_style": writing_style.get('narrative_techniques', {}).get('description_style', ''),
                "dialogue_style": writing_style.get('narrative_techniques', {}).get('dialogue_style', ''),
                "special_techniques": writing_style.get('narrative_techniques', {}).get('special_techniques', [])
            },
            "emotional_expression": {
                "intensity": writing_style.get('emotional_expression', {}).get('intensity', ''),
                "methods": writing_style.get('emotional_expression', {}).get('methods', [])
            },
            "descriptive_focus": writing_style.get('descriptive_focus', []),
            "chapter_structure": {
                "typical_length": writing_style.get('chapter_structure', {}).get('typical_length', ''),
                "opening_patterns": writing_style.get('chapter_structure', {}).get('opening_patterns', []),
                "closing_patterns": writing_style.get('chapter_structure', {}).get('closing_patterns', [])
            }
        }
    
    def _generate_character_templates(self, analysis: Dict) -> Dict:
        """生成角色模板"""
        core_characters = analysis.get('core_characters', [])
        
        return {
            "metadata": {
                "template_name": "角色模板",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "source": "爆款小说分析系统"
            },
            "character_archetypes": self._extract_archetypes(core_characters),
            "main_characters": [
                {
                    "name": char.get('name', ''),
                    "role": char.get('role', ''),
                    "archetype": char.get('archetype', ''),
                    "personality": {
                        "traits": char.get('personality', {}).get('traits', []),
                        "core_values": char.get('personality', {}).get('core_values', []),
                        "motivations": char.get('personality', {}).get('motivations', [])
                    },
                    "background": char.get('background', {}),
                    "abilities": char.get('abilities', []),
                    "relationships": char.get('relationships', []),
                    "character_arc": char.get('character_arc', {}),
                    "speech_patterns": char.get('speech_patterns', []),
                    "distinctive_features": char.get('distinctive_features', [])
                }
                for char in core_characters
            ],
            "character_interaction_patterns": analysis.get('character_interaction_patterns', []),
            "character_development_guidelines": {
                "growth_patterns": analysis.get('character_development', {}).get('growth_patterns', []),
                "relationship_evolution": analysis.get('character_development', {}).get('relationship_evolution', []),
                "conflict_types": analysis.get('character_development', {}).get('conflict_types', [])
            }
        }
    
    def _generate_quality_criteria(self, analysis: Dict) -> Dict:
        """生成质量标准"""
        themes = analysis.get('themes', {})
        
        return {
            "metadata": {
                "template_name": "质量标准",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "source": "爆款小说分析系统"
            },
            "thematic_consistency": {
                "main_themes": themes.get('main_themes', []),
                "theme_expression": themes.get('theme_expression', []),
                "value_system": themes.get('value_system', [])
            },
            "plot_quality": {
                "logic_consistency": "检查情节发展是否合理，无明显漏洞",
                "conflict_intensity": "确保冲突足够吸引人，张力适中",
                "pacing_balance": "节奏要有快慢交替，避免单调",
                "surprise_factor": "情节需要适当的转折和惊喜"
            },
            "character_quality": {
                "consistency": "角色行为符合性格设定",
                "development": "主要角色需有成长弧线",
                "depth": "避免脸谱化，角色要有层次",
                "relatability": "读者能够共鸣或理解角色动机"
            },
            "writing_quality": {
                "language_fluency": "语言流畅，无明显语法错误",
                "description_vividness": "描写生动，能够唤起画面感",
                "dialogue_naturalness": "对话自然，符合角色身份",
                "emotional_resonance": "能够引发读者情感共鸣"
            },
            "world_building_quality": {
                "consistency": "世界观设定前后一致",
                "depth": "世界观有足够的细节支撑",
                "logic": "规则体系自洽合理",
                "uniqueness": "有独特的创新点"
            },
            "reader_engagement": {
                "hooks": "开篇和章节结尾要有吸引力",
                "suspense": "保持适度悬念",
                "emotional_investment": "让读者关心角色命运",
                "page_turner_quality": "让读者想继续阅读"
            },
            "originality_markers": analysis.get('originality_markers', []),
            "success_factors": analysis.get('success_factors', [])
        }
    
    def _extract_archetypes(self, characters: list) -> list:
        """提取角色原型"""
        archetypes = set()
        for char in characters:
            archetype = char.get('archetype', '')
            if archetype:
                archetypes.add(archetype)
        
        return [
            {
                "name": archetype,
                "description": f"{archetype}类型角色的典型特征"
            }
            for archetype in archetypes
        ]
