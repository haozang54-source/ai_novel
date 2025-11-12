from datetime import datetime
from ..database import db
import json

class Character(db.Model):
    """人物角色模型"""
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # 基本信息
    name = db.Column(db.String(100), nullable=False)
    alias = db.Column(db.Text)  # JSON array: ["别名1", "别名2"]
    avatar_url = db.Column(db.String(500))
    
    # 角色档案
    role_type = db.Column(db.String(50))  # 主角/配角/反派/路人
    gender = db.Column(db.String(20))
    age = db.Column(db.String(50))
    appearance = db.Column(db.Text)  # 外貌描写
    personality = db.Column(db.Text)  # 性格特征
    background = db.Column(db.Text)  # 背景故事
    
    # 能力与目标
    abilities = db.Column(db.Text)  # JSON array
    goals = db.Column(db.Text)  # 人物目标
    conflicts = db.Column(db.Text)  # 内在冲突
    
    # 发展轨迹
    character_arc = db.Column(db.Text)  # 人物弧光/成长路线
    key_moments = db.Column(db.Text)  # JSON array: [{chapter, event, change}]
    
    # 元数据
    tags = db.Column(db.Text)  # JSON array
    importance = db.Column(db.Integer, default=3)  # 1-5星
    ai_weight = db.Column(db.Float, default=1.0)
    
    # 状态追踪
    status = db.Column(db.String(50), default='alive')  # alive/dead/unknown
    current_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    relations_from = db.relationship('CharacterRelation', 
                                     foreign_keys='CharacterRelation.from_character_id',
                                     backref='from_character',
                                     cascade='all, delete-orphan')
    relations_to = db.relationship('CharacterRelation',
                                   foreign_keys='CharacterRelation.to_character_id',
                                   backref='to_character',
                                   cascade='all, delete-orphan')
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'alias': json.loads(self.alias) if self.alias else [],
            'avatar_url': self.avatar_url,
            'role_type': self.role_type,
            'gender': self.gender,
            'age': self.age,
            'appearance': self.appearance,
            'personality': self.personality,
            'background': self.background,
            'abilities': json.loads(self.abilities) if self.abilities else [],
            'goals': self.goals,
            'conflicts': self.conflicts,
            'character_arc': self.character_arc,
            'key_moments': json.loads(self.key_moments) if self.key_moments else [],
            'tags': json.loads(self.tags) if self.tags else [],
            'importance': self.importance,
            'ai_weight': self.ai_weight,
            'status': self.status,
            'current_location_id': self.current_location_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_relations:
            data['relations'] = [r.to_dict() for r in self.relations_from]
        
        return data


class CharacterRelation(db.Model):
    """人物关系模型"""
    __tablename__ = 'character_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    from_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    to_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    
    # 关系描述
    relation_type = db.Column(db.String(50))  # 师徒/情侣/敌对/盟友/亲属
    description = db.Column(db.Text)
    intimacy = db.Column(db.Integer, default=50)  # 0-100 亲密度
    
    # 时间范围
    start_chapter = db.Column(db.Integer)
    end_chapter = db.Column(db.Integer)
    
    # 关系变化追踪
    relation_changes = db.Column(db.Text)  # JSON: [{chapter, event, before, after}]
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'from_character_id': self.from_character_id,
            'to_character_id': self.to_character_id,
            'relation_type': self.relation_type,
            'description': self.description,
            'intimacy': self.intimacy,
            'start_chapter': self.start_chapter,
            'end_chapter': self.end_chapter,
            'relation_changes': json.loads(self.relation_changes) if self.relation_changes else [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
