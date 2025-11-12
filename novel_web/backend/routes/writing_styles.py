from flask import Blueprint, request, jsonify
from ..models import db, WritingStyle
import json

bp = Blueprint('writing_styles', __name__, url_prefix='/api/writing-styles')

@bp.route('/project/<int:project_id>', methods=['GET', 'POST'])
def handle_project_writing_style(project_id):
    """获取或创建/更新项目的文风设定(一般每个项目只有一个)"""
    if request.method == 'GET':
        writing_style = WritingStyle.query.filter_by(
            project_id=project_id,
            is_active=True
        ).first()
        
        if not writing_style:
            return jsonify(None)
        
        return jsonify(writing_style.to_dict())
    
    elif request.method == 'POST':
        # 创建或更新文风设定
        data = request.json
        
        # 查找已有的文风设定
        existing_style = WritingStyle.query.filter_by(
            project_id=project_id,
            is_active=True
        ).first()
        
        if existing_style:
            # 更新现有设定
            for key in ['narrative_perspective', 'language_style', 'dialogue_style',
                        'description_density', 'custom_notes', 'ai_weight']:
                if key in data:
                    setattr(existing_style, key, data[key])
            
            if 'style_samples' in data:
                existing_style.style_samples = json.dumps(data['style_samples'])
            
            db.session.commit()
            return jsonify(existing_style.to_dict())
        else:
            # 创建新设定
            style = WritingStyle(
                project_id=project_id,
                narrative_perspective=data.get('narrative_perspective'),
                language_style=data.get('language_style'),
                dialogue_style=data.get('dialogue_style'),
                description_density=data.get('description_density'),
                custom_notes=data.get('custom_notes'),
                style_samples=json.dumps(data.get('style_samples', [])),
                ai_weight=data.get('ai_weight', 1.0),
                is_active=True
            )
            
            db.session.add(style)
            db.session.commit()
            
            return jsonify(style.to_dict()), 201

@bp.route('/<int:style_id>', methods=['GET'])
def get_writing_style(style_id):
    """获取文风设定详情"""
    style = WritingStyle.query.get_or_404(style_id)
    return jsonify(style.to_dict())

@bp.route('/', methods=['POST'])
def create_writing_style():
    """创建文风设定"""
    data = request.json
    
    # 将同项目的其他文风设为非活跃
    WritingStyle.query.filter_by(
        project_id=data['project_id'],
        is_active=True
    ).update({'is_active': False})
    
    style = WritingStyle(
        project_id=data['project_id'],
        narrative_perspective=data.get('narrative_perspective'),
        language_style=data.get('language_style'),
        dialogue_style=data.get('dialogue_style'),
        description_density=data.get('description_density'),
        custom_notes=data.get('custom_notes'),
        style_samples=json.dumps(data.get('style_samples', [])),
        ai_weight=data.get('ai_weight', 1.0),
        is_active=True
    )
    
    db.session.add(style)
    db.session.commit()
    
    return jsonify(style.to_dict()), 201

@bp.route('/<int:style_id>', methods=['PUT'])
def update_writing_style(style_id):
    """更新文风设定"""
    style = WritingStyle.query.get_or_404(style_id)
    data = request.json
    
    for key in ['narrative_perspective', 'language_style', 'dialogue_style',
                'description_density', 'custom_notes', 'ai_weight', 'is_active']:
        if key in data:
            setattr(style, key, data[key])
    
    if 'style_samples' in data:
        style.style_samples = json.dumps(data['style_samples'])
    
    db.session.commit()
    return jsonify(style.to_dict())

@bp.route('/<int:style_id>', methods=['DELETE'])
def delete_writing_style(style_id):
    """删除文风设定"""
    style = WritingStyle.query.get_or_404(style_id)
    db.session.delete(style)
    db.session.commit()
    return '', 204
