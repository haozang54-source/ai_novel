from flask import Blueprint, request, jsonify
from ..database import db
from ..models.chapter import Chapter
from ..models.outline import OutlineChapter

chapters_bp = Blueprint('chapters', __name__, url_prefix='/api/chapters')

@chapters_bp.route('/outline-chapter/<int:outline_chapter_id>', methods=['GET'])
def get_chapter_by_outline(outline_chapter_id):
    """获取指定大纲章节对应的正文"""
    outline_chapter = OutlineChapter.query.get_or_404(outline_chapter_id)
    
    if outline_chapter.chapter:
        return jsonify(outline_chapter.chapter.to_dict())
    else:
        # 如果还没有章节内容,返回空结构
        return jsonify({
            'outline_chapter_id': outline_chapter_id,
            'content': '',
            'word_count': 0,
            'status': 'not_started'
        })

@chapters_bp.route('/outline-chapter/<int:outline_chapter_id>', methods=['POST'])
def create_or_update_chapter(outline_chapter_id):
    """创建或更新章节内容"""
    outline_chapter = OutlineChapter.query.get_or_404(outline_chapter_id)
    data = request.json
    
    if outline_chapter.chapter:
        # 更新现有章节
        chapter = outline_chapter.chapter
        if 'content' in data:
            chapter.content = data['content']
            chapter.word_count = len(data['content'].replace(' ', '').replace('\n', ''))
        if 'status' in data:
            chapter.status = data['status']
        if 'quality_score' in data:
            chapter.quality_score = data['quality_score']
    else:
        # 创建新章节
        chapter = Chapter(
            outline_chapter_id=outline_chapter_id,
            content=data.get('content', ''),
            word_count=len(data.get('content', '').replace(' ', '').replace('\n', '')),
            status=data.get('status', 'draft'),
            quality_score=data.get('quality_score')
        )
        db.session.add(chapter)
    
    db.session.commit()
    return jsonify(chapter.to_dict())

@chapters_bp.route('/<int:chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    """删除章节内容"""
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return jsonify({'message': 'Chapter deleted successfully'})

@chapters_bp.route('/project/<int:project_id>', methods=['GET'])
def get_project_chapters(project_id):
    """
    获取项目所有可编写的章节
    
    逻辑:
    1. 如果是章级大纲(chapter)，直接返回所有OutlineChapter
    2. 如果是卷级大纲(volume)，返回所有子章节（parent_id不为None的章节）
       如果没有子章节，提示需要先细化大纲
    """
    from ..models.outline import Outline
    
    outline = Outline.query.filter_by(project_id=project_id).first()
    
    if not outline:
        return jsonify({
            'message': '请先创建大纲',
            'outline_level': None,
            'chapters': []
        })
    
    chapters_data = []
    
    # 根据大纲类型处理
    if outline.outline_level == 'volume':
        # 卷级大纲：返回所有子章节（parent_id 不为 None）
        child_chapters = OutlineChapter.query.filter_by(
            outline_id=outline.id
        ).filter(
            OutlineChapter.parent_id.isnot(None)
        ).order_by(
            OutlineChapter.parent_id, OutlineChapter.order_index
        ).all()
        
        # 返回所有子章节供编写（可以为空，前端会提示用户添加章节）
        for oc in child_chapters:
            chapter_info = {
                'outline_chapter_id': oc.id,
                'chapter_num': oc.chapter_num,
                'title': oc.title,
                'summary': oc.summary,
                'parent_id': oc.parent_id,
            }
            
            if oc.chapter:
                chapter_info['chapter'] = oc.chapter.to_dict()
            else:
                chapter_info['chapter'] = None
                
            chapters_data.append(chapter_info)
        
        return jsonify({
            'message': '卷级大纲',
            'outline_level': 'volume',
            'chapters': chapters_data
        })
    else:
        # 章级大纲：返回所有章节
        outline_chapters = OutlineChapter.query.filter_by(
            outline_id=outline.id
        ).order_by(OutlineChapter.order_index).all()
        
        for oc in outline_chapters:
            chapter_info = {
                'outline_chapter_id': oc.id,
                'chapter_num': oc.chapter_num,
                'title': oc.title,
                'summary': oc.summary,
            }
            
            if oc.chapter:
                chapter_info['chapter'] = oc.chapter.to_dict()
            else:
                chapter_info['chapter'] = None
                
            chapters_data.append(chapter_info)
        
        return jsonify({
            'message': '章级大纲，可直接编写',
            'outline_level': 'chapter',
            'chapters': chapters_data
        })

@chapters_bp.route('/outline/<int:outline_id>/chapters', methods=['POST'])
def add_chapter_to_outline(outline_id):
    """在大纲中新增章节"""
    from ..models.outline import Outline
    
    outline = Outline.query.get_or_404(outline_id)
    data = request.json
    
    # 获取当前最大的order_index和chapter_num
    max_chapter = OutlineChapter.query.filter_by(
        outline_id=outline_id
    ).order_by(OutlineChapter.order_index.desc()).first()
    
    next_order = (max_chapter.order_index + 1) if max_chapter else 0
    next_num = (max_chapter.chapter_num + 1) if max_chapter else 1
    
    # 创建新的大纲章节
    new_outline_chapter = OutlineChapter(
        outline_id=outline_id,
        chapter_num=data.get('chapter_num', next_num),
        title=data.get('title', f'第{next_num}章'),
        summary=data.get('summary', ''),
        conflicts=data.get('conflicts', ''),
        emotional_beat=data.get('emotional_beat', ''),
        positioning=data.get('positioning', ''),
        character_growth=data.get('character_growth', ''),
        outline_type='chapter',
        review_status='pending',
        order_index=next_order
    )
    
    db.session.add(new_outline_chapter)
    db.session.commit()
    
    return jsonify(new_outline_chapter.to_dict()), 201

@chapters_bp.route('/outline-chapter/<int:outline_chapter_id>', methods=['PUT'])
def update_outline_chapter(outline_chapter_id):
    """更新大纲章节信息"""
    outline_chapter = OutlineChapter.query.get_or_404(outline_chapter_id)
    data = request.json
    
    # 更新字段
    if 'title' in data:
        outline_chapter.title = data['title']
    if 'summary' in data:
        outline_chapter.summary = data['summary']
    if 'conflicts' in data:
        outline_chapter.conflicts = data['conflicts']
    if 'emotional_beat' in data:
        outline_chapter.emotional_beat = data['emotional_beat']
    if 'positioning' in data:
        outline_chapter.positioning = data['positioning']
    if 'character_growth' in data:
        outline_chapter.character_growth = data['character_growth']
    if 'chapter_num' in data:
        outline_chapter.chapter_num = data['chapter_num']
    
    db.session.commit()
    return jsonify(outline_chapter.to_dict())

@chapters_bp.route('/outline-chapter/<int:outline_chapter_id>', methods=['DELETE'])
def delete_outline_chapter(outline_chapter_id):
    """删除大纲章节（会级联删除对应的正文章节）"""
    outline_chapter = OutlineChapter.query.get_or_404(outline_chapter_id)
    outline_id = outline_chapter.outline_id
    
    db.session.delete(outline_chapter)
    db.session.commit()
    
    # 重新排序剩余章节
    remaining_chapters = OutlineChapter.query.filter_by(
        outline_id=outline_id
    ).order_by(OutlineChapter.order_index).all()
    
    for idx, chapter in enumerate(remaining_chapters):
        chapter.order_index = idx
        chapter.chapter_num = idx + 1
    
    db.session.commit()
    
    return jsonify({'message': '章节删除成功'})
