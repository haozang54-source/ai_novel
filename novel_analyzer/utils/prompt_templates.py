"""
Prompt模板库
"""


class PromptTemplates:
    """Prompt模板类"""
    
    # 单章分析Prompt
    CHAPTER_ANALYSIS = """分析以下小说章节，提取关键信息。

章节内容：
{chapter_text}

请严格按照以下JSON格式输出，不要添加任何其他文字说明：
{{
  "chapter_number": {chapter_number},
  "characters": [
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
  ],
  "locations": [
    {{
      "name": "地点名",
      "type": "地点类型",
      "first_appearance": true,
      "description": "地点描述"
    }}
  ],
  "events": [
    {{
      "type": "conflict/development/climax/turning_point",
      "description": "事件描述",
      "importance": "high/medium/low",
      "emotional_tone": "情感基调",
      "participants": ["参与角色"]
    }}
  ],
  "world_elements": [
    {{
      "type": "power_system/social_rule/special_item/organization",
      "element": "要素名称",
      "details": "详细信息"
    }}
  ],
  "writing_style_notes": {{
    "narrative_perspective": "叙事视角",
    "key_phrases": ["关键短语"],
    "emotional_intensity": "high/medium/low",
    "description_focus": ["描写重点"]
  }},
  "chapter_summary": {{
    "title": "章节标题或核心主题",
    "main_content": "详细概括本章主要内容，包括：1)主要角色的行动和对话 2)关键事件的发展过程 3)重要信息的揭示 4)情节的推进方向（150-300字）",
    "key_points": ["要点1", "要点2", "要点3"],
    "chapter_purpose": "本章在整体故事中的作用（如：引入新角色、推进主线、埋下伏笔、展现世界观等）"
  }}
}}

只输出JSON，不要其他文字。"""

    # 分段汇总Prompt
    SEGMENT_SUMMARY = """基于以下章节的分析结果，进行汇总概括。

章节分析数据：
{chapters_data}

请严格按照以下JSON格式输出，不要添加任何其他文字说明：
{{
  "segment_range": "{start_chapter}-{end_chapter}",
  "total_chapters": {total_chapters},
  "total_words": {total_words},
  "characters_summary": {{
    "main_characters": [
      {{
        "name": "角色名",
        "role": "角色定位",
        "development": "发展变化",
        "key_relationships": ["关系列表"],
        "power_growth": "实力成长"
      }}
    ],
    "new_characters": ["新角色名单"],
    "character_count": 0
  }},
  "locations_summary": {{
    "main_locations": ["主要地点"],
    "location_count": 0
  }},
  "plot_summary": {{
    "main_storyline": "主线剧情概述",
    "key_events": ["关键事件"],
    "conflicts": ["冲突列表"],
    "emotional_arc": "情感曲线"
  }},
  "world_building": {{
    "power_system_details": ["力量体系细节"],
    "social_structure": ["社会结构"],
    "special_items": ["特殊物品"]
  }},
  "style_patterns": {{
    "chapter_structure": "章节结构模式",
    "pacing": "节奏",
    "dialogue_ratio": "对话比例"
  }}
}}

只输出JSON，不要其他文字。"""

    # 世界观整合Prompt
    WORLD_INTEGRATION = """基于以下所有分段汇总，提取完整的世界观设定。

分段汇总数据：
{segments_data}

请严格按照以下JSON格式输出完整世界观，不要添加任何其他文字说明：
{{
  "basic_setting": {{
    "time_period": "时代背景",
    "world_type": "世界类型",
    "core_concept": "核心概念",
    "basic_rules": ["基本规则"]
  }},
  "power_system": {{
    "system_name": "力量体系名称",
    "levels": ["等级列表"],
    "advancement_method": "提升方式",
    "special_abilities": ["特殊能力"]
  }},
  "locations": [
    {{
      "name": "地点名称",
      "type": "地点类型",
      "importance": "high/medium/low",
      "description": "详细描述"
    }}
  ],
  "social_rules": {{
    "political_system": "政治体系",
    "class_structure": "阶级结构",
    "important_organizations": ["重要组织"]
  }},
  "special_items": [
    {{
      "name": "物品名称",
      "type": "物品类型",
      "function": "功能作用"
    }}
  ]
}}

只输出JSON，不要其他文字。"""

    # 角色模板整合Prompt
    CHARACTER_INTEGRATION = """基于以下所有分段汇总，提取角色模板。

分段汇总数据：
{segments_data}

请严格按照以下JSON格式输出角色模板，不要添加任何其他文字说明：
{{
  "protagonist": {{
    "name": "主角名字",
    "archetype": "角色原型",
    "initial_state": {{
      "background": "背景",
      "personality_traits": ["性格特征"],
      "abilities": ["初始能力"],
      "goals": ["目标"],
      "flaws": ["缺陷"]
    }},
    "growth_arc": {{
      "key_transformations": ["关键转变"],
      "power_progression": ["实力成长"],
      "personality_development": ["性格发展"]
    }},
    "relationships": {{
      "romance": "感情线",
      "friendship": "友情线",
      "rivalry": "对抗关系"
    }}
  }},
  "antagonist": {{
    "name": "反派名字",
    "motivation": "动机",
    "abilities": ["能力"],
    "conflict_with_protagonist": "与主角的冲突"
  }},
  "supporting_cast": [
    {{
      "name": "配角名字",
      "role": "角色定位",
      "relationship": "与主角关系",
      "key_traits": ["关键特征"]
    }}
  ]
}}

只输出JSON，不要其他文字。"""

    # 情节框架整合Prompt
    PLOT_INTEGRATION = """基于以下所有分段汇总，提取情节框架。

分段汇总数据：
{segments_data}

请严格按照以下JSON格式输出情节框架，不要添加任何其他文字说明：
{{
  "story_structure": {{
    "act1": {{
      "percentage": 25,
      "key_elements": ["开场钩子", "主角登场", "初始冲突"],
      "major_events": ["事件类型"],
      "ending_hook": "第一幕结尾方式"
    }},
    "act2": {{
      "percentage": 50,
      "midpoint": "中点转折",
      "conflict_escalation": ["冲突升级方式"],
      "subplots": ["支线类型"]
    }},
    "act3": {{
      "percentage": 25,
      "climax_pattern": "高潮模式",
      "resolution_style": "结局风格"
    }}
  }},
  "conflict_progression": {{
    "main_conflict": "主要冲突",
    "escalation_pattern": "升级模式",
    "key_turning_points": ["关键转折点"]
  }},
  "key_plot_points": [
    {{
      "chapter_range": "章节范围",
      "event": "事件描述",
      "significance": "重要性"
    }}
  ],
  "pacing_guide": {{
    "overall_rhythm": "整体节奏",
    "tension_curve": "张力曲线描述",
    "rest_points": "缓和节点"
  }},
  "chapter_templates": {{
    "average_length": 3000,
    "typical_structure": "典型章节结构",
    "ending_hooks": ["章节结尾钩子类型"]
  }}
}}

只输出JSON，不要其他文字。"""

    # 风格指导整合Prompt
    STYLE_INTEGRATION = """基于以下所有分段汇总，提取写作风格指导。

分段汇总数据：
{segments_data}

请严格按照以下JSON格式输出写作风格，不要添加任何其他文字说明：
{{
  "narrative_voice": {{
    "perspective": "叙事视角",
    "tense": "时态",
    "tone": "语调风格"
  }},
  "dialogue_style": {{
    "dialogue_ratio": "对话比例",
    "character_voice_differentiation": "角色语言区分度",
    "dialogue_tags": "对话标签使用",
    "typical_patterns": ["典型对话模式"]
  }},
  "description_templates": {{
    "environment": "环境描写风格",
    "character": "人物描写风格",
    "action": "动作描写风格",
    "emotion": "情感描写风格"
  }},
  "scene_transition": {{
    "methods": ["过渡方法"],
    "typical_phrases": ["典型过渡短语"]
  }},
  "emotional_beats": {{
    "intensity_pattern": "情感强度模式",
    "key_emotions": ["主要情感类型"],
    "expression_methods": ["情感表达方式"]
  }},
  "language_features": {{
    "vocabulary_level": "词汇水平",
    "sentence_structure": "句式特点",
    "rhetorical_devices": ["修辞手法"],
    "catchphrases": ["口头禅/经典语句"]
  }}
}}

只输出JSON，不要其他文字。"""

    # 整体分析Prompt
    GLOBAL_ANALYSIS = """基于以下所有分段汇总，进行整体分析，生成完整的小说模板基础。

分段汇总数据：
{segments_data}

请严格按照以下JSON格式输出整体分析结果，不要添加任何其他文字说明：
{{
  "world_setting": {{
    "type": "世界类型（如：玄幻、都市、科幻等）",
    "name": "世界名称",
    "time_period": "时代背景",
    "geography": {{
      "main_regions": ["主要区域"],
      "key_locations": ["关键地点"],
      "special_places": ["特殊场所"]
    }},
    "power_system": {{
      "name": "力量体系名称",
      "description": "体系描述",
      "levels": ["等级列表"],
      "mechanics": ["运作机制"]
    }},
    "social_structure": {{
      "organizations": ["组织势力"],
      "hierarchy": ["等级制度"],
      "relationships": ["关系网络"]
    }},
    "rules_and_laws": ["世界规则"],
    "unique_elements": ["独特要素"],
    "cultural_aspects": {{
      "customs": ["风俗"],
      "values": ["价值观"]
    }}
  }},
  "core_characters": [
    {{
      "name": "角色名",
      "role": "protagonist/antagonist/supporting",
      "archetype": "角色原型",
      "personality": {{
        "traits": ["性格特征"],
        "core_values": ["核心价值观"],
        "motivations": ["动机"]
      }},
      "background": {{
        "origin": "出身背景",
        "key_events": ["关键经历"]
      }},
      "abilities": ["能力特长"],
      "relationships": ["关系描述"],
      "character_arc": {{
        "starting_point": "起点",
        "transformations": ["转变过程"],
        "ending_state": "终点"
      }},
      "speech_patterns": ["语言习惯"],
      "distinctive_features": ["显著特征"]
    }}
  ],
  "plot_structure": {{
    "story_type": "故事类型",
    "narrative_style": "叙事风格",
    "main_plotline": {{
      "opening": {{
        "hook": "开篇钩子",
        "inciting_incident": "起始事件"
      }},
      "development": ["发展阶段"],
      "climax": {{
        "type": "高潮类型",
        "description": "高潮描述"
      }},
      "resolution": {{
        "style": "解决方式",
        "ending_tone": "结局基调"
      }}
    }},
    "subplots": ["支线情节"],
    "conflict_types": ["冲突类型"],
    "pacing_pattern": {{
      "rhythm": "节奏模式",
      "tension_curve": ["张力曲线"],
      "key_turning_points": ["关键转折点"]
    }},
    "plot_devices": ["情节手法"],
    "foreshadowing": ["伏笔设置"]
  }},
  "writing_style": {{
    "tone_and_mood": {{
      "overall_tone": "整体基调",
      "mood_variations": ["情绪变化"]
    }},
    "language_style": {{
      "formality_level": "正式程度",
      "vocabulary_characteristics": ["词汇特点"],
      "sentence_patterns": ["句式模式"]
    }},
    "narrative_techniques": {{
      "point_of_view": "叙事视角",
      "description_style": "描写风格",
      "dialogue_style": "对话风格",
      "special_techniques": ["特殊技巧"]
    }},
    "emotional_expression": {{
      "intensity": "情感强度",
      "methods": ["表达方法"]
    }},
    "descriptive_focus": ["描写重点"],
    "chapter_structure": {{
      "typical_length": "典型长度",
      "opening_patterns": ["开头模式"],
      "closing_patterns": ["结尾模式"]
    }}
  }},
  "themes": {{
    "main_themes": ["主要主题"],
    "theme_expression": ["主题表达方式"],
    "value_system": ["价值体系"]
  }},
  "originality_markers": ["原创性标记"],
  "success_factors": ["成功要素"],
  "character_interaction_patterns": ["角色互动模式"],
  "character_development": {{
    "growth_patterns": ["成长模式"],
    "relationship_evolution": ["关系演变"],
    "conflict_types": ["冲突类型"]
  }}
}}

只输出JSON，不要其他文字。"""
