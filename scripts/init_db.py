#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from novel_web.backend.app import app, db

def init_database():
    with app.app_context():
        data_dir = Path(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        data_dir.parent.mkdir(parents=True, exist_ok=True)
        db.create_all()
        print("✅ 数据库初始化成功!")

if __name__ == '__main__':
    init_database()
