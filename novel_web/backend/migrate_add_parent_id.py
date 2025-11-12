"""
数据库迁移脚本：为 outline_chapters 表添加 parent_id 字段

运行方式：
cd novel_web/backend
python migrate_add_parent_id.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from novel_web.backend.app import app
from novel_web.backend.database import db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # 检查 parent_id 列是否已存在
            result = db.session.execute(text("PRAGMA table_info(outline_chapters)"))
            columns = [row[1] for row in result]
            
            if 'parent_id' in columns:
                print("✓ parent_id 字段已存在，无需迁移")
                return
            
            print("开始迁移：添加 parent_id 字段...")
            
            # SQLite 添加列
            db.session.execute(text(
                "ALTER TABLE outline_chapters ADD COLUMN parent_id INTEGER"
            ))
            
            db.session.commit()
            print("✓ 迁移成功：parent_id 字段已添加")
            
        except Exception as e:
            print(f"✗ 迁移失败: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate()
