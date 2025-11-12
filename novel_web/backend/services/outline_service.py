from ..models import db, Outline, OutlineChapter
import json

class OutlineService:
    @staticmethod
    def get_by_project(project_id):
        return Outline.query.filter_by(project_id=project_id).first()
    
    @staticmethod
    def update_chapter(chapter_id, data):
        chapter = OutlineChapter.query.get_or_404(chapter_id)

        if 'key_events' in data and isinstance(data['key_events'], list):
            data['key_events'] = json.dumps(data['key_events'], ensure_ascii=False)
        if 'core_tasks' in data and isinstance(data['core_tasks'], list):
            data['core_tasks'] = json.dumps(data['core_tasks'], ensure_ascii=False)
        if 'key_turns' in data and isinstance(data['key_turns'], list):
            data['key_turns'] = json.dumps(data['key_turns'], ensure_ascii=False)

        for key, value in data.items():
            if hasattr(chapter, key):
                setattr(chapter, key, value)

        db.session.commit()
        return chapter
    
    @staticmethod
    def reorder_chapters(outline_id, orders):
        for item in orders:
            chapter = OutlineChapter.query.get(item['id'])
            if chapter and chapter.outline_id == outline_id:
                chapter.order_index = item['order_index']
        db.session.commit()
    
    @staticmethod
    def add_child_chapter(parent_id, data):
        """为指定卷添加子章节"""
        parent = OutlineChapter.query.get_or_404(parent_id)
        
        # 从 data 中移除会被覆盖的字段
        data_copy = data.copy()
        data_copy.pop('outline_id', None)
        data_copy.pop('parent_id', None)
        data_copy.pop('outline_type', None)
        data_copy.pop('order_index', None)
        data_copy.pop('chapter_num', None)  # 移除chapter_num，我们会自动计算
        
        # 处理 JSON 字段
        if 'key_events' in data_copy and isinstance(data_copy['key_events'], list):
            data_copy['key_events'] = json.dumps(data_copy['key_events'], ensure_ascii=False)
        if 'core_tasks' in data_copy and isinstance(data_copy['core_tasks'], list):
            data_copy['core_tasks'] = json.dumps(data_copy['core_tasks'], ensure_ascii=False)
        if 'key_turns' in data_copy and isinstance(data_copy['key_turns'], list):
            data_copy['key_turns'] = json.dumps(data_copy['key_turns'], ensure_ascii=False)
        
        # 获取当前卷下已有章节的最大 order_index
        max_order = db.session.query(db.func.max(OutlineChapter.order_index))\
            .filter_by(parent_id=parent_id).scalar() or 0
        
        # 获取当前卷下已有章节的最大 chapter_num
        max_chapter_num = db.session.query(db.func.max(OutlineChapter.chapter_num))\
            .filter_by(parent_id=parent_id).scalar() or 0
        
        chapter = OutlineChapter(
            outline_id=parent.outline_id,
            parent_id=parent_id,
            outline_type='chapter',
            order_index=max_order + 1,
            chapter_num=max_chapter_num + 1,  # 自动分配章节号
            **data_copy
        )
        
        db.session.add(chapter)
        db.session.commit()
        return chapter
    
    @staticmethod
    def create_chapter(data):
        """创建章节（可以是顶级卷或子章节）"""
        # 处理 JSON 字段
        if 'key_events' in data and isinstance(data['key_events'], list):
            data['key_events'] = json.dumps(data['key_events'], ensure_ascii=False)
        if 'core_tasks' in data and isinstance(data['core_tasks'], list):
            data['core_tasks'] = json.dumps(data['core_tasks'], ensure_ascii=False)
        if 'key_turns' in data and isinstance(data['key_turns'], list):
            data['key_turns'] = json.dumps(data['key_turns'], ensure_ascii=False)
        
        chapter = OutlineChapter(**data)
        db.session.add(chapter)
        db.session.commit()
        return chapter

outline_service = OutlineService()
