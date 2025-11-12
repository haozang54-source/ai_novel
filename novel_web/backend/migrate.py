"""
数据库迁移脚本 - 添加创作设定相关表
运行: pipenv run python migrate.py
或: python migrate.py (在虚拟环境中)
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from novel_web.backend.app import app
from novel_web.backend.database import db
from novel_web.backend.models import (
    WritingStyle, Worldview, Character, CharacterRelation,
    Location, Item, Foreshadowing, Chapter
)

def migrate():
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("\n✅ 数据库表创建成功！")
        print("\n已创建的新表:")
        print("- writing_styles (文风设定)")
        print("- worldviews (世界观)")
        print("- characters (人物)")
        print("- character_relations (人物关系)")
        print("- locations (地点/地图)")
        print("- items (物品/道具)")
        print("- foreshadowings (伏笔)")
        print("- chapters (章节内容) - 新增")
        print("\n✅ 迁移完成！现在可以重启后端服务了。\n")

if __name__ == '__main__':
    migrate()
