from flask import Blueprint, request, jsonify
from ..models import db, Character, CharacterRelation
import json

bp = Blueprint('characters', __name__, url_prefix='/api/characters')

@bp.route('/project/<int:project_id>', methods=['GET'])
def get_project_characters(project_id):
    """获取项目的所有人物"""
    characters = Character.query.filter_by(project_id=project_id).all()
    return jsonify([c.to_dict() for c in characters])

@bp.route('/<int:character_id>', methods=['GET'])
def get_character(character_id):
    """获取单个人物详情"""
    character = Character.query.get_or_404(character_id)
    return jsonify(character.to_dict(include_relations=True))

@bp.route('/', methods=['POST'])
def create_character():
    """创建人物"""
    data = request.json
    
    # 处理JSON字段
    character = Character(
        project_id=data['project_id'],
        name=data['name'],
        alias=json.dumps(data.get('alias', [])),
        avatar_url=data.get('avatar_url'),
        role_type=data.get('role_type'),
        gender=data.get('gender'),
        age=data.get('age'),
        appearance=data.get('appearance'),
        personality=data.get('personality'),
        background=data.get('background'),
        abilities=json.dumps(data.get('abilities', [])),
        goals=data.get('goals'),
        conflicts=data.get('conflicts'),
        character_arc=data.get('character_arc'),
        key_moments=json.dumps(data.get('key_moments', [])),
        tags=json.dumps(data.get('tags', [])),
        importance=data.get('importance', 3),
        ai_weight=data.get('ai_weight', 1.0),
        status=data.get('status', 'alive'),
        current_location_id=data.get('current_location_id')
    )
    
    db.session.add(character)
    db.session.commit()
    
    return jsonify(character.to_dict()), 201

@bp.route('/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    """更新人物"""
    character = Character.query.get_or_404(character_id)
    data = request.json
    
    # 更新字段
    for key in ['name', 'avatar_url', 'role_type', 'gender', 'age', 
                'appearance', 'personality', 'background', 'goals', 
                'conflicts', 'character_arc', 'importance', 'ai_weight', 
                'status', 'current_location_id']:
        if key in data:
            setattr(character, key, data[key])
    
    # 处理JSON字段
    for key in ['alias', 'abilities', 'key_moments', 'tags']:
        if key in data:
            setattr(character, key, json.dumps(data[key]))
    
    db.session.commit()
    return jsonify(character.to_dict())

@bp.route('/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    """删除人物"""
    character = Character.query.get_or_404(character_id)
    db.session.delete(character)
    db.session.commit()
    return '', 204

# 人物关系相关接口
@bp.route('/<int:character_id>/relations', methods=['GET'])
def get_character_relations(character_id):
    """获取人物的所有关系"""
    character = Character.query.get_or_404(character_id)
    relations = character.relations_from + character.relations_to
    return jsonify([r.to_dict() for r in relations])

@bp.route('/relations', methods=['POST'])
def create_relation():
    """创建人物关系"""
    data = request.json
    
    relation = CharacterRelation(
        from_character_id=data['from_character_id'],
        to_character_id=data['to_character_id'],
        relation_type=data.get('relation_type'),
        description=data.get('description'),
        intimacy=data.get('intimacy', 50),
        start_chapter=data.get('start_chapter'),
        end_chapter=data.get('end_chapter'),
        relation_changes=json.dumps(data.get('relation_changes', []))
    )
    
    db.session.add(relation)
    db.session.commit()
    
    return jsonify(relation.to_dict()), 201

@bp.route('/relations/<int:relation_id>', methods=['PUT'])
def update_relation(relation_id):
    """更新人物关系"""
    relation = CharacterRelation.query.get_or_404(relation_id)
    data = request.json
    
    for key in ['relation_type', 'description', 'intimacy', 'start_chapter', 'end_chapter']:
        if key in data:
            setattr(relation, key, data[key])
    
    if 'relation_changes' in data:
        relation.relation_changes = json.dumps(data['relation_changes'])
    
    db.session.commit()
    return jsonify(relation.to_dict())

@bp.route('/relations/<int:relation_id>', methods=['DELETE'])
def delete_relation(relation_id):
    """删除人物关系"""
    relation = CharacterRelation.query.get_or_404(relation_id)
    db.session.delete(relation)
    db.session.commit()
    return '', 204
