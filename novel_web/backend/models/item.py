from datetime import datetime
from ..database import db
import json

class Item(db.Model):
    """物品/道具模型"""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # 武器/法宝/丹药/功法/宝物/消耗品
    image_url = db.Column(db.String(500))
    
    # 详细描述
    description = db.Column(db.Text)
    appearance = db.Column(db.Text)  # 外观描述
    abilities = db.Column(db.Text)  # 功能/能力
    origin = db.Column(db.Text)  # 来历/获得方式
    
    # 属性
    level = db.Column(db.String(50))  # 品阶/等级
    rarity = db.Column(db.String(50))  # 稀有度
    attributes = db.Column(db.Text)  # JSON object: 自定义属性
    
    # 持有者追踪
    current_owner_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=True)
    ownership_history = db.Column(db.Text)  # JSON: [{chapter, from, to, how}]
    
    # 出场追踪
    first_appearance = db.Column(db.Integer)
    appearance_chapters = db.Column(db.Text)  # JSON array
    
    # 状态
    status = db.Column(db.String(50), default='normal')  # normal/damaged/lost/destroyed
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    
    # 元数据
    tags = db.Column(db.Text)
    importance = db.Column(db.Integer, default=3)
    ai_weight = db.Column(db.Float, default=1.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    current_owner = db.relationship('Character', foreign_keys=[current_owner_id], backref='owned_items')
    location = db.relationship('Location', foreign_keys=[location_id], backref='items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'category': self.category,
            'image_url': self.image_url,
            'description': self.description,
            'appearance': self.appearance,
            'abilities': self.abilities,
            'origin': self.origin,
            'level': self.level,
            'rarity': self.rarity,
            'attributes': json.loads(self.attributes) if self.attributes else {},
            'current_owner_id': self.current_owner_id,
            'ownership_history': json.loads(self.ownership_history) if self.ownership_history else [],
            'first_appearance': self.first_appearance,
            'appearance_chapters': json.loads(self.appearance_chapters) if self.appearance_chapters else [],
            'status': self.status,
            'location_id': self.location_id,
            'tags': json.loads(self.tags) if self.tags else [],
            'importance': self.importance,
            'ai_weight': self.ai_weight,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
