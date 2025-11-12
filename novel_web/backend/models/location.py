from datetime import datetime
from ..database import db
import json

class Location(db.Model):
    """地点/地图模型 - 层级式地理系统"""
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    
    # 基本信息
    name = db.Column(db.String(200), nullable=False)
    location_type = db.Column(db.String(50))  # 大陆/国家/城市/建筑/房间
    description = db.Column(db.Text)
    
    # 地图坐标
    map_image_url = db.Column(db.String(500))  # 地图图片
    coordinates = db.Column(db.String(100))  # JSON: {x, y} 在父级地图中的坐标
    
    # 环境特征
    climate = db.Column(db.String(100))  # 气候
    terrain = db.Column(db.String(100))  # 地形
    special_features = db.Column(db.Text)  # 特殊地貌/建筑特点
    
    # 元数据
    tags = db.Column(db.Text)  # JSON array
    importance = db.Column(db.Integer, default=3)
    ai_weight = db.Column(db.Float, default=1.0)
    
    # 层级
    level = db.Column(db.Integer, default=1)
    order_index = db.Column(db.Integer, default=0)
    
    # 出场追踪
    first_appearance = db.Column(db.Integer)  # 首次出现章节
    appearance_chapters = db.Column(db.Text)  # JSON array: [1, 3, 5]
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 自引用关系
    children = db.relationship('Location',
                               backref=db.backref('parent', remote_side=[id]),
                               cascade='all, delete-orphan')
    
    # 关联人物
    characters = db.relationship('Character', backref='current_location')
    
    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'parent_id': self.parent_id,
            'name': self.name,
            'location_type': self.location_type,
            'description': self.description,
            'map_image_url': self.map_image_url,
            'coordinates': json.loads(self.coordinates) if self.coordinates else None,
            'climate': self.climate,
            'terrain': self.terrain,
            'special_features': self.special_features,
            'tags': json.loads(self.tags) if self.tags else [],
            'importance': self.importance,
            'ai_weight': self.ai_weight,
            'level': self.level,
            'order_index': self.order_index,
            'first_appearance': self.first_appearance,
            'appearance_chapters': json.loads(self.appearance_chapters) if self.appearance_chapters else [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_children:
            data['children'] = [child.to_dict(include_children=True) for child in self.children]
        
        return data
