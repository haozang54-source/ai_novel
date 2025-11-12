import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from novel_generator.agents import DirectorAgent, OutlinerAgent
from ..models import db, Outline, OutlineChapter
import json

class AIService:
    def __init__(self):
        self.director = DirectorAgent()
        self.outliner = OutlinerAgent()
    
    def generate_outline(self, project_id, config):
        """生成大纲"""
        # 阶段1: Director规划
        plan = self.director.run({
            'user_theme': config['theme'],
            'target_length': config['target_length'],
            'genre': config['genre']
        })
        
        # 阶段2: Outliner生成大纲
        outline_level = config.get('outline_level', 'chapter')
        
        # 准备 outliner 输入参数
        outliner_input = {
            'story_concept': plan['story_concept'],
            'target_chapters': plan['target_chapters'],
            'chapter_length': plan['chapter_length'],
            'genre': config['genre'],
            'outline_level': outline_level,
            'key_points': plan.get('key_points', []),
            'story_rhythm': plan.get('story_rhythm', '起承转合')
        }
        
        # 如果是卷级大纲，添加 target_volumes 参数
        if outline_level == 'volume':
            outliner_input['target_volumes'] = config.get('target_volumes', 4)
        
        outline_result = self.outliner.run(outliner_input)
        
        generated_nodes = outline_result['outline']
        unit_label = '卷' if outline_result.get('outline_level') == 'volume' or outline_level == 'volume' else '章'
        
        outline = Outline(
            project_id=project_id,
            story_concept=plan['story_concept'],
            status='draft',
            ai_generated=True,
            outline_level=outline_result.get('outline_level', outline_level)
        )
        db.session.add(outline)
        db.session.flush()
        
        for idx, node in enumerate(generated_nodes):
            chapter = OutlineChapter(
                outline_id=outline.id,
                chapter_num=node['chapter_num'],
                title=node['title'],
                summary=node.get('summary', ''),
                key_events=json.dumps(node.get('key_events', []), ensure_ascii=False),
                conflicts=node.get('conflicts', ''),
                emotional_beat=node.get('emotional_beat', ''),
                review_status='pending',
                order_index=idx,
                positioning=node.get('positioning'),
                length=node.get('length'),
                core_tasks=json.dumps(node.get('core_tasks', []), ensure_ascii=False),
                key_turns=json.dumps(node.get('key_turns', []), ensure_ascii=False),
                character_growth=node.get('character_growth'),
                outline_type=outline_result.get('outline_level', outline_level)
            )
            db.session.add(chapter)
        
        db.session.commit()
        
        return outline

ai_service = AIService()
