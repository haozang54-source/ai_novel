from datetime import datetime
from ..database import db
import json

class Worldview(db.Model):
    """世界观设定模型 - 树形层级结构"""
    __tablename__ = 'worldviews'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('worldviews.id'), nullable=True)  # 支持树形结构
    
    # 基本信息
    category = db.Column(db.String(50), nullable=False)  # 时代背景/地理环境/社会结构/力量体系/规则设定
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # 元数据
    tags = db.Column(db.Text)  # JSON array: ["修仙", "等级制度"]
    importance = db.Column(db.Integer, default=3)  # 1-5星重要程度
    ai_weight = db.Column(db.Float, default=1.0)
    
    # 层级与排序
    level = db.Column(db.Integer, default=1)  # 层级深度
    order_index = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 自引用关系
    children = db.relationship('Worldview', 
                               backref=db.backref('parent', remote_side=[id]),
                               cascade='all, delete-orphan')
    
    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'parent_id': self.parent_id,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'tags': json.loads(self.tags) if self.tags else [],
            'importance': self.importance,
            'ai_weight': self.ai_weight,
            'level': self.level,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_children:
            data['children'] = [child.to_dict(include_children=True) for child in self.children]
        
        return data
