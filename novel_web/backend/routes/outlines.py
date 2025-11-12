from flask import Blueprint, request, jsonify

bp = Blueprint('outlines', __name__)

@bp.route('/projects/<int:project_id>/outline', methods=['GET'])
def get_outline(project_id):
    from ..services import outline_service
    outline = outline_service.get_by_project(project_id)
    if not outline:
        return jsonify({'error': 'Outline not found'}), 404
    
    # 如果是卷级大纲，返回层级结构
    include_hierarchy = request.args.get('hierarchy', 'false').lower() == 'true'
    return jsonify(outline.to_dict(include_hierarchy=include_hierarchy))

@bp.route('/projects/<int:project_id>/outline/generate', methods=['POST'])
def generate_outline(project_id):
    from ..services import ai_service
    
    data = request.json
    
    try:
        outline = ai_service.generate_outline(project_id, data)
        return jsonify({
            'success': True,
            'outline': outline.to_dict()
        })
    except Exception as e:
        import traceback
        print(f'[Error] {str(e)}')
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/outline-chapters/<int:chapter_id>', methods=['PUT'])
def update_chapter(chapter_id):
    from ..services import outline_service
    data = request.json
    chapter = outline_service.update_chapter(chapter_id, data)
    return jsonify(chapter.to_dict())

@bp.route('/outlines/<int:outline_id>/chapters/reorder', methods=['POST'])
def reorder_chapters(outline_id):
    from ..services import outline_service
    data = request.json
    outline_service.reorder_chapters(outline_id, data)
    return jsonify({'success': True})

@bp.route('/outline-chapters/<int:parent_id>/add-child', methods=['POST'])
def add_child_chapter(parent_id):
    """为指定卷添加子章节"""
    from ..services import outline_service
    data = request.json
    chapter = outline_service.add_child_chapter(parent_id, data)
    return jsonify(chapter.to_dict())

@bp.route('/outline-chapters', methods=['POST'])
def create_chapter():
    """创建章节（可以是顶级卷或子章节）"""
    from ..services import outline_service
    data = request.json
    chapter = outline_service.create_chapter(data)
    return jsonify(chapter.to_dict())
