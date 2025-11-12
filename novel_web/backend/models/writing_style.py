from datetime import datetime
from ..database import db
import json

class WritingStyle(db.Model):
    """文风设定模型"""
    __tablename__ = 'writing_styles'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # 快速配置
    narrative_perspective = db.Column(db.String(50))  # 第一人称/第三人称全知/第三人称限知
    language_style = db.Column(db.String(50))  # 现代口语化/古典文雅/网文爽文
    dialogue_style = db.Column(db.String(50))  # 简洁/生动/幽默
    description_density = db.Column(db.String(50))  # 简练/适中/细腻
    
    # 自定义说明
    custom_notes = db.Column(db.Text)  # 其他风格说明
    
    # 样本库(JSON array)
    style_samples = db.Column(db.Text)  # [{"scene_type": "战斗", "sample": "..."}]
    
    # AI权重设置
    ai_weight = db.Column(db.Float, default=1.0)  # AI参考此设定的权重
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'narrative_perspective': self.narrative_perspective,
            'language_style': self.language_style,
            'dialogue_style': self.dialogue_style,
            'description_density': self.description_density,
            'custom_notes': self.custom_notes,
            'style_samples': json.loads(self.style_samples) if self.style_samples else [],
            'ai_weight': self.ai_weight,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
