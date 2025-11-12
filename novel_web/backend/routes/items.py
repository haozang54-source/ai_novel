from flask import Blueprint, request, jsonify
from ..models import db, Item
import json

bp = Blueprint('items', __name__, url_prefix='/api/items')

@bp.route('/project/<int:project_id>', methods=['GET'])
def get_project_items(project_id):
    """获取项目的所有物品"""
    category = request.args.get('category')
    query = Item.query.filter_by(project_id=project_id)
    
    if category:
        query = query.filter_by(category=category)
    
    items = query.all()
    return jsonify([item.to_dict() for item in items])

@bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """获取单个物品详情"""
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@bp.route('/', methods=['POST'])
def create_item():
    """创建物品"""
    data = request.json
    
    item = Item(
        project_id=data['project_id'],
        name=data['name'],
        category=data.get('category'),
        image_url=data.get('image_url'),
        description=data.get('description'),
        appearance=data.get('appearance'),
        abilities=data.get('abilities'),
        origin=data.get('origin'),
        level=data.get('level'),
        rarity=data.get('rarity'),
        attributes=json.dumps(data.get('attributes', {})),
        current_owner_id=data.get('current_owner_id'),
        ownership_history=json.dumps(data.get('ownership_history', [])),
        first_appearance=data.get('first_appearance'),
        appearance_chapters=json.dumps(data.get('appearance_chapters', [])),
        status=data.get('status', 'normal'),
        location_id=data.get('location_id'),
        tags=json.dumps(data.get('tags', [])),
        importance=data.get('importance', 3),
        ai_weight=data.get('ai_weight', 1.0)
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify(item.to_dict()), 201

@bp.route('/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """更新物品"""
    item = Item.query.get_or_404(item_id)
    data = request.json
    
    for key in ['name', 'category', 'image_url', 'description', 'appearance',
                'abilities', 'origin', 'level', 'rarity', 'current_owner_id',
                'first_appearance', 'status', 'location_id', 'importance', 'ai_weight']:
        if key in data:
            setattr(item, key, data[key])
    
    for key in ['attributes', 'ownership_history', 'appearance_chapters', 'tags']:
        if key in data:
            setattr(item, key, json.dumps(data[key]))
    
    db.session.commit()
    return jsonify(item.to_dict())

@bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """删除物品"""
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return '', 204
