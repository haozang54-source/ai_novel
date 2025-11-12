from flask import Blueprint, request, jsonify
from ..models import db, Foreshadowing
import json

bp = Blueprint('foreshadowings', __name__, url_prefix='/api/foreshadowings')

@bp.route('/project/<int:project_id>', methods=['GET'])
def get_project_foreshadowings(project_id):
    """获取项目的所有伏笔"""
    status = request.args.get('status')  # planted/revealed/abandoned
    query = Foreshadowing.query.filter_by(project_id=project_id)
    
    if status:
        query = query.filter_by(status=status)
    
    foreshadowings = query.order_by(Foreshadowing.planted_chapter).all()
    return jsonify([f.to_dict() for f in foreshadowings])

@bp.route('/<int:foreshadowing_id>', methods=['GET'])
def get_foreshadowing(foreshadowing_id):
    """获取单个伏笔详情"""
    foreshadowing = Foreshadowing.query.get_or_404(foreshadowing_id)
    return jsonify(foreshadowing.to_dict())

@bp.route('/', methods=['POST'])
def create_foreshadowing():
    """创建伏笔"""
    data = request.json
    
    foreshadowing = Foreshadowing(
        project_id=data['project_id'],
        title=data['title'],
        description=data.get('description'),
        category=data.get('category'),
        planted_chapter=data.get('planted_chapter'),
        planted_content=data.get('planted_content'),
        planted_method=data.get('planted_method'),
        planned_reveal_chapter=data.get('planned_reveal_chapter'),
        actual_reveal_chapter=data.get('actual_reveal_chapter'),
        reveal_content=data.get('reveal_content'),
        status=data.get('status', 'planted'),
        related_characters=json.dumps(data.get('related_characters', [])),
        related_items=json.dumps(data.get('related_items', [])),
        related_locations=json.dumps(data.get('related_locations', [])),
        importance=data.get('importance', 3),
        urgency=data.get('urgency', 3),
        ai_reminder=data.get('ai_reminder'),
        notes=data.get('notes')
    )
    
    db.session.add(foreshadowing)
    db.session.commit()
    
    return jsonify(foreshadowing.to_dict()), 201

@bp.route('/<int:foreshadowing_id>', methods=['PUT'])
def update_foreshadowing(foreshadowing_id):
    """更新伏笔"""
    foreshadowing = Foreshadowing.query.get_or_404(foreshadowing_id)
    data = request.json
    
    for key in ['title', 'description', 'category', 'planted_chapter', 
                'planted_content', 'planted_method', 'planned_reveal_chapter',
                'actual_reveal_chapter', 'reveal_content', 'status',
                'importance', 'urgency', 'ai_reminder', 'notes']:
        if key in data:
            setattr(foreshadowing, key, data[key])
    
    for key in ['related_characters', 'related_items', 'related_locations']:
        if key in data:
            setattr(foreshadowing, key, json.dumps(data[key]))
    
    db.session.commit()
    return jsonify(foreshadowing.to_dict())

@bp.route('/<int:foreshadowing_id>', methods=['DELETE'])
def delete_foreshadowing(foreshadowing_id):
    """删除伏笔"""
    foreshadowing = Foreshadowing.query.get_or_404(foreshadowing_id)
    db.session.delete(foreshadowing)
    db.session.commit()
    return '', 204

@bp.route('/<int:foreshadowing_id>/reveal', methods=['POST'])
def reveal_foreshadowing(foreshadowing_id):
    """标记伏笔为已揭示"""
    foreshadowing = Foreshadowing.query.get_or_404(foreshadowing_id)
    data = request.json
    
    foreshadowing.status = 'revealed'
    foreshadowing.actual_reveal_chapter = data.get('actual_reveal_chapter')
    foreshadowing.reveal_content = data.get('reveal_content')
    
    db.session.commit()
    return jsonify(foreshadowing.to_dict())
