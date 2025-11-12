from datetime import datetime
from ..database import db
import json

class Outline(db.Model):
    __tablename__ = 'outlines'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    story_concept = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='draft')
    ai_generated = db.Column(db.Boolean, default=True)
    outline_level = db.Column(db.String(20), default='chapter')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chapters = db.relationship('OutlineChapter', backref='outline', cascade='all, delete-orphan',
                               order_by='OutlineChapter.order_index')
    
    def to_dict(self, include_hierarchy=False):
        """
        include_hierarchy: 是否返回层级结构（卷包含章节）
        """
        if include_hierarchy and self.outline_level == 'volume':
            # 构建层级结构：只返回顶级卷（parent_id为None），卷包含其子章节
            volumes = [ch for ch in self.chapters if ch.parent_id is None]
            return {
                'id': self.id,
                'project_id': self.project_id,
                'story_concept': self.story_concept,
                'version': self.version,
                'status': self.status,
                'ai_generated': self.ai_generated,
                'outline_level': self.outline_level,
                'created_at': self.created_at.isoformat(),
                'chapters': [vol.to_dict(include_children=True) for vol in volumes]
            }
        else:
            # 平铺结构
            return {
                'id': self.id,
                'project_id': self.project_id,
                'story_concept': self.story_concept,
                'version': self.version,
                'status': self.status,
                'ai_generated': self.ai_generated,
                'outline_level': self.outline_level,
                'created_at': self.created_at.isoformat(),
                'chapters': [ch.to_dict(include_children=False) for ch in self.chapters]
            }

class OutlineChapter(db.Model):
    __tablename__ = 'outline_chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    outline_id = db.Column(db.Integer, db.ForeignKey('outlines.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('outline_chapters.id'), nullable=True)  # 父节点ID（用于卷-章节关系）
    chapter_num = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text)
    key_events = db.Column(db.Text)
    conflicts = db.Column(db.Text)
    emotional_beat = db.Column(db.String(100))
    positioning = db.Column(db.String(200))
    length = db.Column(db.String(100))
    core_tasks = db.Column(db.Text)
    key_turns = db.Column(db.Text)
    character_growth = db.Column(db.Text)
    outline_type = db.Column(db.String(20), default='chapter')
    review_status = db.Column(db.String(20), default='pending')
    order_index = db.Column(db.Integer, nullable=False)
    
    chapter = db.relationship('Chapter', backref='outline_chapter', uselist=False, cascade='all, delete-orphan')
    
    # 子章节关系
    children = db.relationship('OutlineChapter',
                               backref=db.backref('parent', remote_side=[id]),
                               cascade='all, delete-orphan',
                               order_by='OutlineChapter.order_index')
    
    def to_dict(self, include_children=False):
        result = {
            'id': self.id,
            'outline_id': self.outline_id,
            'parent_id': self.parent_id,
            'chapter_num': self.chapter_num,
            'title': self.title,
            'summary': self.summary,
            'key_events': json.loads(self.key_events) if self.key_events else [],
            'conflicts': self.conflicts,
            'emotional_beat': self.emotional_beat,
            'positioning': self.positioning,
            'length': self.length,
            'core_tasks': json.loads(self.core_tasks) if self.core_tasks else [],
            'key_turns': json.loads(self.key_turns) if self.key_turns else [],
            'character_growth': self.character_growth,
            'outline_type': self.outline_type,
            'review_status': self.review_status,
            'order_index': self.order_index
        }
        
        if include_children:
            result['children'] = [child.to_dict(include_children=False) for child in self.children]
        
        return result
