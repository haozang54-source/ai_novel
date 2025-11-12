from flask import Blueprint, request, jsonify
from ..models import db, Location
import json

bp = Blueprint('locations', __name__, url_prefix='/api/locations')

@bp.route('/project/<int:project_id>', methods=['GET'])
def get_project_locations(project_id):
    """获取项目的地点树形结构"""
    root_nodes = Location.query.filter_by(
        project_id=project_id,
        parent_id=None
    ).order_by(Location.order_index).all()
    
    return jsonify([node.to_dict(include_children=True) for node in root_nodes])

@bp.route('/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """获取单个地点详情"""
    location = Location.query.get_or_404(location_id)
    return jsonify(location.to_dict(include_children=True))

@bp.route('/', methods=['POST'])
def create_location():
    """创建地点"""
    data = request.json
    
    level = 1
    if data.get('parent_id'):
        parent = Location.query.get(data['parent_id'])
        if parent:
            level = parent.level + 1
    
    location = Location(
        project_id=data['project_id'],
        parent_id=data.get('parent_id'),
        name=data['name'],
        location_type=data.get('location_type'),
        description=data.get('description'),
        map_image_url=data.get('map_image_url'),
        coordinates=json.dumps(data.get('coordinates')) if data.get('coordinates') else None,
        climate=data.get('climate'),
        terrain=data.get('terrain'),
        special_features=data.get('special_features'),
        tags=json.dumps(data.get('tags', [])),
        importance=data.get('importance', 3),
        ai_weight=data.get('ai_weight', 1.0),
        level=level,
        order_index=data.get('order_index', 0),
        first_appearance=data.get('first_appearance'),
        appearance_chapters=json.dumps(data.get('appearance_chapters', []))
    )
    
    db.session.add(location)
    db.session.commit()
    
    return jsonify(location.to_dict()), 201

@bp.route('/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    """更新地点"""
    location = Location.query.get_or_404(location_id)
    data = request.json
    
    for key in ['name', 'location_type', 'description', 'map_image_url', 
                'climate', 'terrain', 'special_features', 'importance', 
                'ai_weight', 'order_index', 'first_appearance']:
        if key in data:
            setattr(location, key, data[key])
    
    for key in ['coordinates', 'tags', 'appearance_chapters']:
        if key in data:
            setattr(location, key, json.dumps(data[key]))
    
    db.session.commit()
    return jsonify(location.to_dict())

@bp.route('/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    """删除地点"""
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    return '', 204
