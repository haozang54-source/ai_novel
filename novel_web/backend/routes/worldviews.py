from flask import Blueprint, request, jsonify
from ..models import db, Worldview
import json

bp = Blueprint('worldviews', __name__, url_prefix='/api/worldviews')

@bp.route('/project/<int:project_id>', methods=['GET'])
def get_project_worldviews(project_id):
    """获取项目的世界观树形结构"""
    # 获取所有顶层节点
    root_nodes = Worldview.query.filter_by(
        project_id=project_id, 
        parent_id=None
    ).order_by(Worldview.order_index).all()
    
    return jsonify([node.to_dict(include_children=True) for node in root_nodes])

@bp.route('/<int:worldview_id>', methods=['GET'])
def get_worldview(worldview_id):
    """获取单个世界观节点"""
    worldview = Worldview.query.get_or_404(worldview_id)
    return jsonify(worldview.to_dict(include_children=True))

@bp.route('/', methods=['POST'])
def create_worldview():
    """创建世界观节点"""
    data = request.json
    
    # 计算层级
    level = 1
    if data.get('parent_id'):
        parent = Worldview.query.get(data['parent_id'])
        if parent:
            level = parent.level + 1
    
    worldview = Worldview(
        project_id=data['project_id'],
        parent_id=data.get('parent_id'),
        category=data['category'],
        title=data['title'],
        description=data.get('description'),
        tags=json.dumps(data.get('tags', [])),
        importance=data.get('importance', 3),
        ai_weight=data.get('ai_weight', 1.0),
        level=level,
        order_index=data.get('order_index', 0)
    )
    
    db.session.add(worldview)
    db.session.commit()
    
    return jsonify(worldview.to_dict()), 201

@bp.route('/<int:worldview_id>', methods=['PUT'])
def update_worldview(worldview_id):
    """更新世界观节点"""
    worldview = Worldview.query.get_or_404(worldview_id)
    data = request.json
    
    for key in ['category', 'title', 'description', 'importance', 'ai_weight', 'order_index']:
        if key in data:
            setattr(worldview, key, data[key])
    
    if 'tags' in data:
        worldview.tags = json.dumps(data['tags'])
    
    db.session.commit()
    return jsonify(worldview.to_dict())

@bp.route('/<int:worldview_id>', methods=['DELETE'])
def delete_worldview(worldview_id):
    """删除世界观节点(级联删除子节点)"""
    worldview = Worldview.query.get_or_404(worldview_id)
    db.session.delete(worldview)
    db.session.commit()
    return '', 204
