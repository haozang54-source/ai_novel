from datetime import datetime
from ..database import db
import json

class Foreshadowing(db.Model):
    """伏笔管理模型"""
    __tablename__ = 'foreshadowings'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # 基本信息
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # 人物/剧情/物品/世界观
    
    # 埋设信息
    planted_chapter = db.Column(db.Integer)  # 埋下的章节
    planted_content = db.Column(db.Text)  # 埋设时的具体内容/描述
    planted_method = db.Column(db.String(100))  # 明示/暗示/道具/对话
    
    # 揭示信息
    planned_reveal_chapter = db.Column(db.Integer)  # 计划揭晓章节
    actual_reveal_chapter = db.Column(db.Integer)  # 实际揭晓章节
    reveal_content = db.Column(db.Text)  # 揭晓时的内容
    
    # 状态
    status = db.Column(db.String(20), default='planted')  # planted/revealed/abandoned
    
    # 关联要素
    related_characters = db.Column(db.Text)  # JSON array: character IDs
    related_items = db.Column(db.Text)  # JSON array: item IDs
    related_locations = db.Column(db.Text)  # JSON array: location IDs
    
    # 重要性
    importance = db.Column(db.Integer, default=3)  # 1-5星
    urgency = db.Column(db.Integer, default=3)  # 紧迫度，影响AI提醒
    
    # AI提醒
    ai_reminder = db.Column(db.Text)  # AI生成的填坑提醒/建议
    
    # 笔记
    notes = db.Column(db.Text)  # 创作者备注
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'planted_chapter': self.planted_chapter,
            'planted_content': self.planted_content,
            'planted_method': self.planted_method,
            'planned_reveal_chapter': self.planned_reveal_chapter,
            'actual_reveal_chapter': self.actual_reveal_chapter,
            'reveal_content': self.reveal_content,
            'status': self.status,
            'related_characters': json.loads(self.related_characters) if self.related_characters else [],
            'related_items': json.loads(self.related_items) if self.related_items else [],
            'related_locations': json.loads(self.related_locations) if self.related_locations else [],
            'importance': self.importance,
            'urgency': self.urgency,
            'ai_reminder': self.ai_reminder,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
