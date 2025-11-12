#!/usr/bin/env python3
"""数据库迁移脚本 - 添加卷级大纲支持字段"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from novel_web.backend.app import app, db

def migrate_database():
    with app.app_context():
        # 获取数据库连接
        connection = db.engine.connect()
        
        print("开始数据库迁移...")
        
        # 添加 outlines 表的新字段
        try:
            connection.execute(db.text("""
                ALTER TABLE outlines ADD COLUMN outline_level VARCHAR(20) DEFAULT 'chapter'
            """))
            print("✅ outlines.outline_level 字段添加成功")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("⚠️  outlines.outline_level 字段已存在，跳过")
            else:
                print(f"❌ 添加 outlines.outline_level 失败: {e}")
        
        # 添加 outline_chapters 表的新字段
        new_columns = [
            ("positioning", "VARCHAR(200)"),
            ("length", "VARCHAR(100)"),
            ("core_tasks", "TEXT"),
            ("key_turns", "TEXT"),
            ("character_growth", "TEXT"),
            ("outline_type", "VARCHAR(20) DEFAULT 'chapter'")
        ]
        
        for column_name, column_type in new_columns:
            try:
                connection.execute(db.text(f"""
                    ALTER TABLE outline_chapters ADD COLUMN {column_name} {column_type}
                """))
                print(f"✅ outline_chapters.{column_name} 字段添加成功")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"⚠️  outline_chapters.{column_name} 字段已存在，跳过")
                else:
                    print(f"❌ 添加 outline_chapters.{column_name} 失败: {e}")
        
        connection.commit()
        connection.close()
        
        print("\n🎉 数据库迁移完成！")
        print("提示：如果出现问题，可以删除数据库文件重新初始化：")
        print("  rm novel_web/data/novel.db")
        print("  pipenv run python scripts/init_db.py")

if __name__ == '__main__':
    migrate_database()
