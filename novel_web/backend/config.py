import os
from pathlib import Path

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # 数据库配置
    BASE_DIR = Path(__file__).parent.parent
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/data/database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:5173']
    
    # 服务端口
    PORT = 5001
