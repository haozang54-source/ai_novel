from flask import Blueprint, request, jsonify
from ..database import db
from ..models.character import Character
from ..models.worldview import Worldview
from ..models.location import Location
from ..models.item import Item
from ..models.foreshadowing import Foreshadowing
from ..models.writing_style import WritingStyle

# 导入AI Agent
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from novel_generator.agents import EditorAgent

ai_assistant_bp = Blueprint('ai_assistant', __name__, url_prefix='/api/ai-assistant')

# 创建AI编辑助手实例
editor_agent = EditorAgent()

@ai_assistant_bp.route('/analyze', methods=['POST'])
def analyze_text():
    """
    分析选中文本并根据用户指令生成修改建议
    
    请求体:
    {
        "selected_text": "选中的文本",
        "user_prompt": "用户的修改指令",
        "context": {
            "chapter_id": 1,
            "before_text": "前文",
            "after_text": "后文"
        },
        "knowledge_base": {
            "character_ids": [1, 2],
            "worldview_ids": [1],
            "location_ids": [],
            "item_ids": [],
            "foreshadowing_ids": [],
            "writing_style_id": 1
        }
    }
    """
    data = request.json
    selected_text = data.get('selected_text', '')
    user_prompt = data.get('user_prompt', '')
    context_data = data.get('context', {})
    knowledge_base = data.get('knowledge_base', {})
    
    # 获取知识库数据
    knowledge_context = _build_knowledge_context(
        data.get('project_id'),
        knowledge_base
    )
    
    # 使用AI Agent进行文本改写
    try:
        ai_input = {
            'selected_text': selected_text,
            'user_prompt': user_prompt,
            'context': {
                'before_text': context_data.get('before_text', ''),
                'after_text': context_data.get('after_text', '')
            },
            'knowledge_base': knowledge_context
        }
        
        ai_response = editor_agent.run(ai_input)
        return jsonify(ai_response)
        
    except Exception as e:
        # 如果AI调用失败，返回错误信息
        return jsonify({
            'original_text': selected_text,
            'suggested_text': selected_text,
            'explanation': f'AI分析失败: {str(e)}',
            'confidence': 0.0,
            'conversation_id': 'error'
        }), 500

@ai_assistant_bp.route('/knowledge-base/<int:project_id>', methods=['GET'])
def get_knowledge_base(project_id):
    """获取项目的所有知识库选项"""
    
    characters = Character.query.filter_by(project_id=project_id).all()
    worldviews = Worldview.query.filter_by(project_id=project_id).all()
    locations = Location.query.filter_by(project_id=project_id).all()
    items = Item.query.filter_by(project_id=project_id).all()
    foreshadowings = Foreshadowing.query.filter_by(project_id=project_id).all()
    writing_style = WritingStyle.query.filter_by(project_id=project_id).first()
    
    return jsonify({
        'characters': [{'id': c.id, 'name': c.name, 'role': c.role} for c in characters],
        'worldviews': [{'id': w.id, 'name': w.name, 'category': w.category} for w in worldviews],
        'locations': [{'id': l.id, 'name': l.name, 'type': l.location_type} for l in locations],
        'items': [{'id': i.id, 'name': i.name, 'category': i.category} for i in items],
        'foreshadowings': [{'id': f.id, 'title': f.title, 'status': f.status} for f in foreshadowings],
        'writing_style': writing_style.to_dict() if writing_style else None
    })

def _build_knowledge_context(project_id, knowledge_base):
    """构建知识库上下文"""
    context = {
        'characters': [],
        'worldviews': [],
        'locations': [],
        'items': [],
        'foreshadowings': [],
        'writing_style': None
    }
    
    # 获取角色信息
    if knowledge_base.get('character_ids'):
        characters = Character.query.filter(
            Character.id.in_(knowledge_base['character_ids'])
        ).all()
        context['characters'] = [c.to_dict() for c in characters]
    
    # 获取世界观信息
    if knowledge_base.get('worldview_ids'):
        worldviews = Worldview.query.filter(
            Worldview.id.in_(knowledge_base['worldview_ids'])
        ).all()
        context['worldviews'] = [w.to_dict() for w in worldviews]
    
    # 获取地点信息
    if knowledge_base.get('location_ids'):
        locations = Location.query.filter(
            Location.id.in_(knowledge_base['location_ids'])
        ).all()
        context['locations'] = [l.to_dict() for l in locations]
    
    # 获取物品信息
    if knowledge_base.get('item_ids'):
        items = Item.query.filter(
            Item.id.in_(knowledge_base['item_ids'])
        ).all()
        context['items'] = [i.to_dict() for i in items]
    
    # 获取伏笔信息
    if knowledge_base.get('foreshadowing_ids'):
        foreshadowings = Foreshadowing.query.filter(
            Foreshadowing.id.in_(knowledge_base['foreshadowing_ids'])
        ).all()
        context['foreshadowings'] = [f.to_dict() for f in foreshadowings]
    
    # 获取文风设定
    if knowledge_base.get('writing_style_id'):
        writing_style = WritingStyle.query.get(knowledge_base['writing_style_id'])
        if writing_style:
            context['writing_style'] = writing_style.to_dict()
    
    return context


