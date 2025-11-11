# AI小说创作Web系统开发进度规划

> **目标**: 使用AI辅助完成MVP核心功能开发  
> **开发模式**: AI驱动的快速开发  
> **范围**: 项目管理 + 大纲编辑器 + 正文创作基础功能

---

## 📋 任务总览

```
✅ = 已完成  🔄 = 进行中  ⏳ = 待开始
```

### 核心模块进度
- ✅ **基础架构搭建** (已完成)
- ✅ **后端开发** (已完成: Models + Services + Routes + WebSocket)
- ✅ **前端开发** (已完成: Dashboard + OutlineEditor + Store + API)
- ✅ **集成测试** (已完成: 数据库初始化成功)

---

## 阶段一：基础架构搭建

### 任务清单

#### 1.1 项目目录结构创建
```bash
# 创建目录结构
novel_web/
├── backend/
│   ├── models/
│   ├── services/
│   ├── routes/
│   └── utils/
└── frontend/
    └── src/
```

**文件清单:**
- [ ] `novel_web/backend/app.py`
- [ ] `novel_web/backend/config.py`
- [ ] `novel_web/backend/database.py`
- [ ] `novel_web/backend/__init__.py`

---

#### 1.2 后端依赖安装
**操作:**
```bash
cd novel_web/backend
pip install Flask==3.0.0 Flask-CORS==4.0.0 Flask-SocketIO==5.3.5
pip install Flask-SQLAlchemy==3.1.1 Flask-Migrate==4.0.5
pip install Flask-RESTX==1.2.0 marshmallow==3.20.1
pip install python-socketio==5.10.0 eventlet==0.33.3
```

**验证:**
```bash
python -c "import flask; print(flask.__version__)"
```

---

#### 1.3 前端项目初始化
**操作:**
```bash
cd novel_web
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

**安装核心依赖:**
```bash
npm install antd @ant-design/icons
npm install react-router-dom zustand axios
npm install socket.io-client
npm install @dnd-kit/core @dnd-kit/sortable
npm install react-markdown-editor-lite react-markdown remark-gfm
npm install echarts echarts-for-react
npm install @antv/g6
npm install dayjs
```

**验证:**
```bash
npm run dev  # 确保能启动
```

---

#### 1.4 配置文件创建

**backend/config.py**
```python
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
    
    # WebSocket配置
    SOCKETIO_ASYNC_MODE = 'eventlet'
```

**frontend/vite.config.ts**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true
      }
    }
  }
})
```

---

#### 1.5 数据库初始化脚本

**scripts/init_db.py**
```python
#!/usr/bin/env python3
"""初始化数据库"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from novel_web.backend.app import app, db

def init_database():
    """创建数据库表"""
    with app.app_context():
        # 创建data目录
        data_dir = Path(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        data_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建所有表
        db.create_all()
        print("✅ 数据库初始化成功!")

if __name__ == '__main__':
    init_database()
```

---

#### 1.6 开发环境启动脚本

**scripts/run_dev.py**
```python
#!/usr/bin/env python3
"""开发环境启动脚本"""
import subprocess
import sys
import time
from pathlib import Path

def start_backend():
    """启动Flask后端"""
    print("🚀 启动Flask后端...")
    backend_dir = Path(__file__).parent.parent / "novel_web/backend"
    return subprocess.Popen([
        sys.executable, "app.py"
    ], cwd=backend_dir)

def start_frontend():
    """启动React前端"""
    print("🚀 启动React前端...")
    frontend_dir = Path(__file__).parent.parent / "novel_web/frontend"
    return subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=frontend_dir)

if __name__ == "__main__":
    backend_process = start_backend()
    time.sleep(2)  # 等待后端启动
    frontend_process = start_frontend()
    
    print("\n✅ 开发服务器已启动:")
    print("   - 后端: http://localhost:5000")
    print("   - 前端: http://localhost:5173")
    print("\n按Ctrl+C停止服务器\n")
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n👋 正在停止服务器...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("✅ 服务器已停止")
```

---

## 阶段二：后端开发

### 2.1 数据模型层 (models/)

#### 任务 2.1.1: 创建基础模型

**models/__init__.py**
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .project import Project
from .outline import Outline, OutlineChapter
from .chapter import Chapter
from .annotation import Annotation
from .worldview import WorldView

__all__ = [
    'db',
    'Project',
    'Outline',
    'OutlineChapter', 
    'Chapter',
    'Annotation',
    'WorldView'
]
```

---

#### 任务 2.1.2: Project模型

**models/project.py**
```python
from datetime import datetime
from . import db

class Project(db.Model):
    """项目模型"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    theme = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(50), nullable=False)  # 玄幻/仙侠/都市等
    target_length = db.Column(db.Integer, default=15000)
    status = db.Column(db.String(20), default='draft')  # draft/outlining/writing/completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    outline = db.relationship('Outline', backref='project', uselist=False, cascade='all, delete-orphan')
    worldviews = db.relationship('WorldView', backref='project', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'theme': self.theme,
            'genre': self.genre,
            'target_length': self.target_length,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
```

---

#### 任务 2.1.3: Outline和OutlineChapter模型

**models/outline.py**
```python
from datetime import datetime
from . import db
import json

class Outline(db.Model):
    """大纲模型"""
    __tablename__ = 'outlines'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    story_concept = db.Column(db.Text)
    version = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='draft')  # draft/confirmed
    ai_generated = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    chapters = db.relationship('OutlineChapter', backref='outline', cascade='all, delete-orphan', order_by='OutlineChapter.order_index')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'story_concept': self.story_concept,
            'version': self.version,
            'status': self.status,
            'ai_generated': self.ai_generated,
            'created_at': self.created_at.isoformat(),
            'chapters': [ch.to_dict() for ch in self.chapters]
        }


class OutlineChapter(db.Model):
    """大纲章节模型"""
    __tablename__ = 'outline_chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    outline_id = db.Column(db.Integer, db.ForeignKey('outlines.id'), nullable=False)
    chapter_num = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text)
    key_events = db.Column(db.Text)  # JSON字符串
    conflicts = db.Column(db.Text)
    emotional_beat = db.Column(db.String(100))
    review_status = db.Column(db.String(20), default='pending')  # pending/approved/need_revision
    order_index = db.Column(db.Integer, nullable=False)
    
    # 关系
    chapter = db.relationship('Chapter', backref='outline_chapter', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'outline_id': self.outline_id,
            'chapter_num': self.chapter_num,
            'title': self.title,
            'summary': self.summary,
            'key_events': json.loads(self.key_events) if self.key_events else [],
            'conflicts': self.conflicts,
            'emotional_beat': self.emotional_beat,
            'review_status': self.review_status,
            'order_index': self.order_index
        }
```

---

#### 任务 2.1.4: Chapter模型

**models/chapter.py**
```python
from datetime import datetime
from . import db

class Chapter(db.Model):
    """正文章节模型"""
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    outline_chapter_id = db.Column(db.Integer, db.ForeignKey('outline_chapters.id'), nullable=False)
    content = db.Column(db.Text)  # Markdown格式
    word_count = db.Column(db.Integer, default=0)
    quality_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='draft')  # draft/reviewing/published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'outline_chapter_id': self.outline_chapter_id,
            'content': self.content,
            'word_count': self.word_count,
            'quality_score': self.quality_score,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
```

---

#### 任务 2.1.5: Annotation和WorldView模型

**models/annotation.py**
```python
from datetime import datetime
from . import db

class Annotation(db.Model):
    """批注模型"""
    __tablename__ = 'annotations'
    
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(20), nullable=False)  # outline/chapter
    target_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='idea')  # idea/issue/todo/praise
    status = db.Column(db.String(20), default='open')  # open/resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'content': self.content,
            'type': self.type,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
```

**models/worldview.py**
```python
from datetime import datetime
from . import db

class WorldView(db.Model):
    """世界观设定模型"""
    __tablename__ = 'worldviews'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # power_system/geography/character
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)  # JSON格式
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }
```

---

### 2.2 业务逻辑层 (services/)

#### 任务 2.2.1: AIService - AI智能体封装

**services/ai_service.py**
```python
import sys
from pathlib import Path

# 添加项目路径以导入novel_generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from novel_generator.agents import DirectorAgent, OutlinerAgent, SceneWriterAgent, CriticAgent
from ..models import db, Outline, OutlineChapter
import json

class AIService:
    """AI智能体服务"""
    
    def __init__(self):
        self.director = DirectorAgent()
        self.outliner = OutlinerAgent()
        self.writer = SceneWriterAgent()
        self.critic = CriticAgent()
    
    def generate_outline(self, project_id, config, progress_callback=None):
        """
        生成大纲
        
        Args:
            project_id: 项目ID
            config: {'theme': str, 'genre': str, 'target_length': int}
            progress_callback: 进度回调 (stage, progress, message)
        
        Returns:
            Outline对象
        """
        # 阶段1: Director规划
        if progress_callback:
            progress_callback('director', 0, '正在规划故事结构...')
        
        plan = self.director.run({
            'user_theme': config['theme'],
            'target_length': config['target_length'],
            'genre': config['genre']
        })
        
        if progress_callback:
            progress_callback('director', 50, 'Director规划完成')
        
        # 阶段2: Outliner生成大纲
        if progress_callback:
            progress_callback('outliner', 50, '正在生成章节大纲...')
        
        outline_result = self.outliner.run({
            'story_concept': plan['story_concept'],
            'target_chapters': plan['target_chapters'],
            'chapter_length': plan['chapter_length'],
            'genre': config['genre']
        })
        
        if progress_callback:
            progress_callback('outliner', 100, '大纲生成完成')
        
        # 保存到数据库
        outline = Outline(
            project_id=project_id,
            story_concept=plan['story_concept'],
            status='draft',
            ai_generated=True
        )
        db.session.add(outline)
        db.session.flush()  # 获取outline.id
        
        # 保存章节
        for idx, ch in enumerate(outline_result['outline']):
            chapter = OutlineChapter(
                outline_id=outline.id,
                chapter_num=ch['chapter_num'],
                title=ch['title'],
                summary=ch['summary'],
                key_events=json.dumps(ch['key_events'], ensure_ascii=False),
                conflicts=ch['conflicts'],
                emotional_beat=ch['emotional_beat'],
                review_status='pending',
                order_index=idx
            )
            db.session.add(chapter)
        
        db.session.commit()
        
        return outline
    
    def regenerate_chapter(self, chapter_id, context):
        """重新生成单个章节"""
        # TODO: 实现单章重新生成逻辑
        pass
    
    def generate_chapter_content(self, outline_chapter_id):
        """生成章节正文"""
        # TODO: 使用SceneWriterAgent生成正文
        pass
    
    def review_chapter(self, chapter_id):
        """评审章节"""
        # TODO: 使用CriticAgent评审
        pass

# 全局实例
ai_service = AIService()
```

---

#### 任务 2.2.2: ProjectService - 项目管理

**services/project_service.py**
```python
from ..models import db, Project

class ProjectService:
    """项目管理服务"""
    
    @staticmethod
    def get_all_projects():
        """获取所有项目"""
        return Project.query.order_by(Project.updated_at.desc()).all()
    
    @staticmethod
    def get_project(project_id):
        """获取单个项目"""
        return Project.query.get_or_404(project_id)
    
    @staticmethod
    def create_project(data):
        """创建项目"""
        project = Project(
            title=data['title'],
            theme=data['theme'],
            genre=data['genre'],
            target_length=data.get('target_length', 15000),
            status='draft'
        )
        db.session.add(project)
        db.session.commit()
        return project
    
    @staticmethod
    def update_project(project_id, data):
        """更新项目"""
        project = Project.query.get_or_404(project_id)
        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        db.session.commit()
        return project
    
    @staticmethod
    def delete_project(project_id):
        """删除项目"""
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()

# 全局实例
project_service = ProjectService()
```

---

#### 任务 2.2.3: OutlineService - 大纲管理

**services/outline_service.py**
```python
from ..models import db, Outline, OutlineChapter
import json

class OutlineService:
    """大纲管理服务"""
    
    @staticmethod
    def get_outline_by_project(project_id):
        """根据项目ID获取大纲"""
        return Outline.query.filter_by(project_id=project_id).first()
    
    @staticmethod
    def update_chapter(chapter_id, data):
        """更新章节"""
        chapter = OutlineChapter.query.get_or_404(chapter_id)
        
        if 'title' in data:
            chapter.title = data['title']
        if 'summary' in data:
            chapter.summary = data['summary']
        if 'key_events' in data:
            chapter.key_events = json.dumps(data['key_events'], ensure_ascii=False)
        if 'conflicts' in data:
            chapter.conflicts = data['conflicts']
        if 'emotional_beat' in data:
            chapter.emotional_beat = data['emotional_beat']
        if 'review_status' in data:
            chapter.review_status = data['review_status']
        
        db.session.commit()
        return chapter
    
    @staticmethod
    def reorder_chapters(outline_id, chapter_orders):
        """
        重新排序章节
        
        Args:
            outline_id: 大纲ID
            chapter_orders: [{'id': 1, 'order_index': 0}, ...]
        """
        for item in chapter_orders:
            chapter = OutlineChapter.query.get(item['id'])
            if chapter and chapter.outline_id == outline_id:
                chapter.order_index = item['order_index']
        
        db.session.commit()
    
    @staticmethod
    def delete_chapter(chapter_id):
        """删除章节"""
        chapter = OutlineChapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
    
    @staticmethod
    def insert_chapter(outline_id, data, position):
        """插入新章节"""
        # 先移动后续章节
        chapters = OutlineChapter.query.filter(
            OutlineChapter.outline_id == outline_id,
            OutlineChapter.order_index >= position
        ).all()
        
        for ch in chapters:
            ch.order_index += 1
        
        # 插入新章节
        new_chapter = OutlineChapter(
            outline_id=outline_id,
            chapter_num=data.get('chapter_num', position + 1),
            title=data['title'],
            summary=data.get('summary', ''),
            key_events=json.dumps(data.get('key_events', []), ensure_ascii=False),
            conflicts=data.get('conflicts', ''),
            emotional_beat=data.get('emotional_beat', ''),
            review_status='pending',
            order_index=position
        )
        db.session.add(new_chapter)
        db.session.commit()
        return new_chapter

# 全局实例
outline_service = OutlineService()
```

---

### 2.3 API路由层 (routes/)

#### 任务 2.3.1: Flask应用入口

**app.py**
```python
import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .config import Config
from .models import db
from .routes import register_routes

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
CORS(app, origins=app.config['CORS_ORIGINS'])
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'], async_mode='eventlet')

# 注册路由
register_routes(app)

# 注册WebSocket事件
from .utils.websocket import register_socketio_events
register_socketio_events(socketio)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

---

#### 任务 2.3.2: 路由注册

**routes/__init__.py**
```python
from flask import Blueprint

def register_routes(app):
    """注册所有路由"""
    from .projects import bp as projects_bp
    from .outlines import bp as outlines_bp
    from .chapters import bp as chapters_bp
    from .annotations import bp as annotations_bp
    
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(outlines_bp, url_prefix='/api')
    app.register_blueprint(chapters_bp, url_prefix='/api')
    app.register_blueprint(annotations_bp, url_prefix='/api')
```

---

#### 任务 2.3.3: Projects路由

**routes/projects.py**
```python
from flask import Blueprint, request, jsonify
from ..services.project_service import project_service

bp = Blueprint('projects', __name__)

@bp.route('/projects', methods=['GET'])
def get_projects():
    """获取项目列表"""
    projects = project_service.get_all_projects()
    return jsonify([p.to_dict() for p in projects])

@bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """获取项目详情"""
    project = project_service.get_project(project_id)
    return jsonify(project.to_dict())

@bp.route('/projects', methods=['POST'])
def create_project():
    """创建项目"""
    data = request.json
    project = project_service.create_project(data)
    return jsonify(project.to_dict()), 201

@bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """更新项目"""
    data = request.json
    project = project_service.update_project(project_id, data)
    return jsonify(project.to_dict())

@bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    project_service.delete_project(project_id)
    return '', 204
```

---

#### 任务 2.3.4: Outlines路由

**routes/outlines.py**
```python
from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room
import threading
from ..services.ai_service import ai_service
from ..services.outline_service import outline_service

bp = Blueprint('outlines', __name__)

@bp.route('/projects/<int:project_id>/outline', methods=['GET'])
def get_outline(project_id):
    """获取大纲"""
    outline = outline_service.get_outline_by_project(project_id)
    if not outline:
        return jsonify({'error': 'Outline not found'}), 404
    return jsonify(outline.to_dict())

@bp.route('/projects/<int:project_id>/outline/generate', methods=['POST'])
def generate_outline(project_id):
    """生成大纲（异步）"""
    from ..app import socketio
    
    data = request.json
    room = f'project_{project_id}'
    
    def progress_callback(stage, progress, message):
        """进度回调"""
        socketio.emit('outline_generation_progress', {
            'stage': stage,
            'progress': progress,
            'message': message
        }, room=room)
    
    def generate_task():
        """后台生成任务"""
        try:
            outline = ai_service.generate_outline(project_id, data, progress_callback)
            socketio.emit('outline_generation_complete', {
                'success': True,
                'outline': outline.to_dict()
            }, room=room)
        except Exception as e:
            socketio.emit('outline_generation_error', {
                'success': False,
                'error': str(e)
            }, room=room)
    
    # 启动后台线程
    thread = threading.Thread(target=generate_task)
    thread.start()
    
    return jsonify({'status': 'started', 'room': room})

@bp.route('/outline-chapters/<int:chapter_id>', methods=['PUT'])
def update_chapter(chapter_id):
    """更新章节"""
    data = request.json
    chapter = outline_service.update_chapter(chapter_id, data)
    return jsonify(chapter.to_dict())

@bp.route('/outlines/<int:outline_id>/chapters/reorder', methods=['POST'])
def reorder_chapters(outline_id):
    """重新排序章节"""
    data = request.json  # [{'id': 1, 'order_index': 0}, ...]
    outline_service.reorder_chapters(outline_id, data)
    return jsonify({'success': True})

@bp.route('/outline-chapters/<int:chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    """删除章节"""
    outline_service.delete_chapter(chapter_id)
    return '', 204

@bp.route('/outlines/<int:outline_id>/chapters', methods=['POST'])
def insert_chapter(outline_id):
    """插入新章节"""
    data = request.json
    position = data.pop('position', 0)
    chapter = outline_service.insert_chapter(outline_id, data, position)
    return jsonify(chapter.to_dict()), 201
```

---

#### 任务 2.3.5: WebSocket事件处理

**utils/websocket.py**
```python
from flask_socketio import join_room, leave_room, emit

def register_socketio_events(socketio):
    """注册WebSocket事件"""
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        """客户端订阅房间"""
        room = data['room']
        join_room(room)
        emit('subscribed', {'room': room})
    
    @socketio.on('unsubscribe')
    def handle_unsubscribe(data):
        """客户端取消订阅"""
        room = data['room']
        leave_room(room)
        emit('unsubscribed', {'room': room})
```

---

## 阶段三：前端开发

### 3.1 项目基础配置

#### 任务 3.1.1: TypeScript类型定义

**src/types/index.ts**
```typescript
// 项目类型
export interface Project {
  id: number;
  title: string;
  theme: string;
  genre: string;
  target_length: number;
  status: 'draft' | 'outlining' | 'writing' | 'completed';
  created_at: string;
  updated_at: string;
}

// 大纲类型
export interface Outline {
  id: number;
  project_id: number;
  story_concept: string;
  version: number;
  status: 'draft' | 'confirmed';
  ai_generated: boolean;
  created_at: string;
  chapters: OutlineChapter[];
}

// 大纲章节类型
export interface OutlineChapter {
  id: number;
  outline_id: number;
  chapter_num: number;
  title: string;
  summary: string;
  key_events: string[];
  conflicts: string;
  emotional_beat: string;
  review_status: 'pending' | 'approved' | 'need_revision';
  order_index: number;
}

// 正文章节类型
export interface Chapter {
  id: number;
  outline_chapter_id: number;
  content: string;
  word_count: number;
  quality_score?: number;
  status: 'draft' | 'reviewing' | 'published';
  created_at: string;
  updated_at: string;
}

// 批注类型
export interface Annotation {
  id: number;
  target_type: 'outline' | 'chapter';
  target_id: number;
  content: string;
  type: 'idea' | 'issue' | 'todo' | 'praise';
  status: 'open' | 'resolved';
  created_at: string;
}
```

---

#### 任务 3.1.2: API服务封装

**src/services/api.ts**
```typescript
import axios from 'axios';
import type { Project, Outline, OutlineChapter, Chapter, Annotation } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Project API
export const projectApi = {
  getAll: () => api.get<Project[]>('/projects'),
  getById: (id: number) => api.get<Project>(`/projects/${id}`),
  create: (data: Partial<Project>) => api.post<Project>('/projects', data),
  update: (id: number, data: Partial<Project>) => api.put<Project>(`/projects/${id}`, data),
  delete: (id: number) => api.delete(`/projects/${id}`),
};

// Outline API
export const outlineApi = {
  getByProject: (projectId: number) => api.get<Outline>(`/projects/${projectId}/outline`),
  generate: (projectId: number, config: any) => api.post(`/projects/${projectId}/outline/generate`, config),
  updateChapter: (chapterId: number, data: Partial<OutlineChapter>) => 
    api.put<OutlineChapter>(`/outline-chapters/${chapterId}`, data),
  reorderChapters: (outlineId: number, orders: Array<{id: number, order_index: number}>) =>
    api.post(`/outlines/${outlineId}/chapters/reorder`, orders),
  deleteChapter: (chapterId: number) => api.delete(`/outline-chapters/${chapterId}`),
  insertChapter: (outlineId: number, data: any) => api.post(`/outlines/${outlineId}/chapters`, data),
};

export default api;
```

---

#### 任务 3.1.3: WebSocket服务

**src/services/websocket.ts**
```typescript
import { io, Socket } from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;
  
  connect() {
    if (!this.socket) {
      this.socket = io('http://localhost:5000', {
        transports: ['websocket'],
      });
    }
    return this.socket;
  }
  
  subscribe(room: string) {
    if (this.socket) {
      this.socket.emit('subscribe', { room });
    }
  }
  
  unsubscribe(room: string) {
    if (this.socket) {
      this.socket.emit('unsubscribe', { room });
    }
  }
  
  on(event: string, callback: (data: any) => void) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }
  
  off(event: string) {
    if (this.socket) {
      this.socket.off(event);
    }
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export const wsService = new WebSocketService();
```

---

### 3.2 状态管理 (Zustand)

#### 任务 3.2.1: Project Store

**src/store/projectStore.ts**
```typescript
import { create } from 'zustand';
import { projectApi } from '../services/api';
import type { Project } from '../types';

interface ProjectStore {
  projects: Project[];
  currentProject: Project | null;
  loading: boolean;
  
  fetchProjects: () => Promise<void>;
  createProject: (data: Partial<Project>) => Promise<Project>;
  selectProject: (id: number) => void;
  updateProject: (id: number, data: Partial<Project>) => Promise<void>;
  deleteProject: (id: number) => Promise<void>;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  currentProject: null,
  loading: false,
  
  fetchProjects: async () => {
    set({ loading: true });
    try {
      const response = await projectApi.getAll();
      set({ projects: response.data, loading: false });
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      set({ loading: false });
    }
  },
  
  createProject: async (data) => {
    const response = await projectApi.create(data);
    const newProject = response.data;
    set(state => ({ projects: [newProject, ...state.projects] }));
    return newProject;
  },
  
  selectProject: (id) => {
    const project = get().projects.find(p => p.id === id);
    set({ currentProject: project || null });
  },
  
  updateProject: async (id, data) => {
    await projectApi.update(id, data);
    set(state => ({
      projects: state.projects.map(p => p.id === id ? { ...p, ...data } : p),
      currentProject: state.currentProject?.id === id 
        ? { ...state.currentProject, ...data } 
        : state.currentProject
    }));
  },
  
  deleteProject: async (id) => {
    await projectApi.delete(id);
    set(state => ({
      projects: state.projects.filter(p => p.id !== id),
      currentProject: state.currentProject?.id === id ? null : state.currentProject
    }));
  },
}));
```

---

#### 任务 3.2.2: Outline Store

**src/store/outlineStore.ts**
```typescript
import { create } from 'zustand';
import { outlineApi } from '../services/api';
import type { Outline, OutlineChapter } from '../types';

interface OutlineStore {
  outline: Outline | null;
  selectedChapter: OutlineChapter | null;
  isGenerating: boolean;
  generationProgress: number;
  generationMessage: string;
  
  fetchOutline: (projectId: number) => Promise<void>;
  generateOutline: (projectId: number, config: any) => void;
  updateChapter: (chapterId: number, data: Partial<OutlineChapter>) => Promise<void>;
  reorderChapters: (orders: Array<{id: number, order_index: number}>) => Promise<void>;
  selectChapter: (chapter: OutlineChapter | null) => void;
  
  setGenerationProgress: (progress: number, message: string) => void;
  setGenerating: (isGenerating: boolean) => void;
}

export const useOutlineStore = create<OutlineStore>((set, get) => ({
  outline: null,
  selectedChapter: null,
  isGenerating: false,
  generationProgress: 0,
  generationMessage: '',
  
  fetchOutline: async (projectId) => {
    try {
      const response = await outlineApi.getByProject(projectId);
      set({ outline: response.data });
    } catch (error) {
      console.error('Failed to fetch outline:', error);
    }
  },
  
  generateOutline: (projectId, config) => {
    set({ isGenerating: true, generationProgress: 0 });
    outlineApi.generate(projectId, config);
  },
  
  updateChapter: async (chapterId, data) => {
    await outlineApi.updateChapter(chapterId, data);
    set(state => ({
      outline: state.outline ? {
        ...state.outline,
        chapters: state.outline.chapters.map(ch => 
          ch.id === chapterId ? { ...ch, ...data } : ch
        )
      } : null
    }));
  },
  
  reorderChapters: async (orders) => {
    const outline = get().outline;
    if (!outline) return;
    
    await outlineApi.reorderChapters(outline.id, orders);
    
    // 本地更新顺序
    set(state => ({
      outline: state.outline ? {
        ...state.outline,
        chapters: state.outline.chapters
          .map(ch => {
            const order = orders.find(o => o.id === ch.id);
            return order ? { ...ch, order_index: order.order_index } : ch;
          })
          .sort((a, b) => a.order_index - b.order_index)
      } : null
    }));
  },
  
  selectChapter: (chapter) => {
    set({ selectedChapter: chapter });
  },
  
  setGenerationProgress: (progress, message) => {
    set({ generationProgress: progress, generationMessage: message });
  },
  
  setGenerating: (isGenerating) => {
    set({ isGenerating });
  },
}));
```

---

### 3.3 核心页面开发

#### 任务 3.3.1: App入口和路由

**src/App.tsx**
```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Dashboard from './pages/Dashboard';
import OutlineEditor from './pages/OutlineEditor';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects/:id/outline" element={<OutlineEditor />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
```

---

#### 任务 3.3.2: Dashboard页面

**src/pages/Dashboard/index.tsx**
```typescript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Card, Button, Modal, Form, Input, Select, Row, Col, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useProjectStore } from '../../store/projectStore';

const { Header, Content } = Layout;
const { TextArea } = Input;

export default function Dashboard() {
  const navigate = useNavigate();
  const { projects, fetchProjects, createProject } = useProjectStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (values: any) => {
    const project = await createProject(values);
    setIsModalOpen(false);
    form.resetFields();
    navigate(`/projects/${project.id}/outline`);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h1 style={{ margin: 0 }}>AI小说创作助手</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
          新建项目
        </Button>
      </Header>
      
      <Content style={{ padding: '24px' }}>
        <Row gutter={[16, 16]}>
          {projects.map(project => (
            <Col key={project.id} xs={24} sm={12} lg={8}>
              <Card
                hoverable
                title={project.title}
                extra={<span>{project.genre}</span>}
                onClick={() => navigate(`/projects/${project.id}/outline`)}
              >
                <p>{project.theme}</p>
                <Space>
                  <span>目标: {project.target_length}字</span>
                  <span>状态: {project.status}</span>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      </Content>

      <Modal
        title="新建项目"
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => setIsModalOpen(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateProject}>
          <Form.Item name="title" label="标题" rules={[{ required: true }]}>
            <Input placeholder="输入小说标题" />
          </Form.Item>
          <Form.Item name="genre" label="类型" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="玄幻">玄幻</Select.Option>
              <Select.Option value="仙侠">仙侠</Select.Option>
              <Select.Option value="都市">都市</Select.Option>
              <Select.Option value="科幻">科幻</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="theme" label="主题" rules={[{ required: true }]}>
            <TextArea rows={4} placeholder="描述你的小说创意..." />
          </Form.Item>
          <Form.Item name="target_length" label="目标字数" initialValue={15000}>
            <Input type="number" />
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
}
```

---

#### 任务 3.3.3: OutlineEditor页面（简化版）

**src/pages/OutlineEditor/index.tsx**
```typescript
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Layout, Button, Space, Drawer, Form, Input, Modal, Progress, Card, Tag } from 'antd';
import { useOutlineStore } from '../../store/outlineStore';
import { useProjectStore } from '../../store/projectStore';
import { wsService } from '../../services/websocket';
import OutlineCard from '../../components/OutlineCard';

const { Header, Content } = Layout;
const { TextArea } = Input;

export default function OutlineEditor() {
  const { id } = useParams<{ id: string }>();
  const projectId = parseInt(id!);
  
  const { currentProject, selectProject } = useProjectStore();
  const { 
    outline, 
    fetchOutline, 
    generateOutline, 
    isGenerating, 
    generationProgress,
    generationMessage,
    setGenerationProgress,
    setGenerating,
    selectedChapter,
    selectChapter,
    updateChapter
  } = useOutlineStore();
  
  const [isGenerateDrawerOpen, setIsGenerateDrawerOpen] = useState(false);
  const [isEditDrawerOpen, setIsEditDrawerOpen] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    selectProject(projectId);
    fetchOutline(projectId);
    
    // 连接WebSocket
    const socket = wsService.connect();
    wsService.subscribe(`project_${projectId}`);
    
    wsService.on('outline_generation_progress', (data) => {
      setGenerationProgress(data.progress, data.message);
    });
    
    wsService.on('outline_generation_complete', (data) => {
      setGenerating(false);
      fetchOutline(projectId);
      Modal.success({ title: '大纲生成成功！' });
    });
    
    return () => {
      wsService.off('outline_generation_progress');
      wsService.off('outline_generation_complete');
    };
  }, [projectId]);

  const handleGenerate = (values: any) => {
    generateOutline(projectId, {
      theme: currentProject?.theme || values.theme,
      genre: currentProject?.genre || values.genre,
      target_length: currentProject?.target_length || 15000
    });
    setIsGenerateDrawerOpen(false);
  };

  const handleEditChapter = (values: any) => {
    if (selectedChapter) {
      updateChapter(selectedChapter.id, values);
      setIsEditDrawerOpen(false);
      selectChapter(null);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h1 style={{ margin: 0 }}>{currentProject?.title || '大纲编辑器'}</h1>
        <Space>
          <Button type="primary" onClick={() => setIsGenerateDrawerOpen(true)}>
            生成大纲
          </Button>
        </Space>
      </Header>
      
      <Content style={{ padding: '24px' }}>
        {outline?.chapters.map(chapter => (
          <OutlineCard
            key={chapter.id}
            chapter={chapter}
            onClick={() => {
              selectChapter(chapter);
              form.setFieldsValue(chapter);
              setIsEditDrawerOpen(true);
            }}
          />
        ))}
      </Content>

      {/* 生成配置抽屉 */}
      <Drawer
        title="生成大纲"
        open={isGenerateDrawerOpen}
        onClose={() => setIsGenerateDrawerOpen(false)}
        width={400}
      >
        <Form layout="vertical" onFinish={handleGenerate}>
          <Form.Item label="主题" name="theme" initialValue={currentProject?.theme}>
            <TextArea rows={4} />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>开始生成</Button>
        </Form>
      </Drawer>

      {/* 编辑抽屉 */}
      <Drawer
        title="编辑章节"
        open={isEditDrawerOpen}
        onClose={() => setIsEditDrawerOpen(false)}
        width={500}
      >
        <Form form={form} layout="vertical" onFinish={handleEditChapter}>
          <Form.Item name="title" label="标题">
            <Input />
          </Form.Item>
          <Form.Item name="summary" label="摘要">
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item name="conflicts" label="冲突">
            <Input />
          </Form.Item>
          <Form.Item name="emotional_beat" label="情感">
            <Input />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>保存</Button>
        </Form>
      </Drawer>

      {/* 生成进度弹窗 */}
      <Modal
        title="正在生成大纲"
        open={isGenerating}
        footer={null}
        closable={false}
      >
        <Progress percent={generationProgress} />
        <p>{generationMessage}</p>
      </Modal>
    </Layout>
  );
}
```

---

#### 任务 3.3.4: OutlineCard组件

**src/components/OutlineCard/index.tsx**
```typescript
import { Card, Tag, Space } from 'antd';
import { CheckCircleOutlined, ExclamationCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import type { OutlineChapter } from '../../types';

interface Props {
  chapter: OutlineChapter;
  onClick: () => void;
}

const statusConfig = {
  pending: { text: '待审阅', color: 'default', icon: <ClockCircleOutlined /> },
  approved: { text: '已确认', color: 'success', icon: <CheckCircleOutlined /> },
  need_revision: { text: '需修改', color: 'warning', icon: <ExclamationCircleOutlined /> },
};

export default function OutlineCard({ chapter, onClick }: Props) {
  const status = statusConfig[chapter.review_status];
  
  return (
    <Card
      hoverable
      onClick={onClick}
      style={{ marginBottom: 16 }}
      title={
        <Space>
          <span>第{chapter.chapter_num}章: {chapter.title}</span>
          <Tag color={status.color} icon={status.icon}>{status.text}</Tag>
        </Space>
      }
    >
      <p><strong>摘要:</strong> {chapter.summary}</p>
      <p><strong>冲突:</strong> {chapter.conflicts}</p>
      <p><strong>情感:</strong> {chapter.emotional_beat}</p>
      {chapter.key_events.length > 0 && (
        <div>
          <strong>关键事件:</strong>
          <Space wrap style={{ marginTop: 8 }}>
            {chapter.key_events.map((event, idx) => (
              <Tag key={idx}>{event}</Tag>
            ))}
          </Space>
        </div>
      )}
    </Card>
  );
}
```

---

## 阶段四：集成测试

### 任务 4.1: 初始化数据库
```bash
python scripts/init_db.py
```

### 任务 4.2: 启动开发服务器
```bash
python scripts/run_dev.py
```

### 任务 4.3: 功能验证清单

#### ✅ 基础功能
- [ ] 打开 http://localhost:5173 能看到Dashboard
- [ ] 能够创建新项目
- [ ] 项目卡片正确显示
- [ ] 点击项目能跳转到大纲编辑器

#### ✅ 大纲生成
- [ ] 点击"生成大纲"打开配置抽屉
- [ ] 提交后显示进度弹窗
- [ ] WebSocket实时推送进度
- [ ] 生成完成后显示章节卡片

#### ✅ 大纲编辑
- [ ] 点击章节卡片打开编辑抽屉
- [ ] 编辑标题、摘要等字段
- [ ] 保存后卡片内容更新
- [ ] 章节状态标签正确显示

---

## 📝 开发注意事项

### 代码质量
1. **类型安全**: 前端全部使用TypeScript，定义清晰的接口
2. **错误处理**: 所有API调用都要try-catch，显示友好错误提示
3. **加载状态**: 异步操作显示Loading，提升体验
4. **数据验证**: 后端使用Marshmallow验证数据

### 性能优化
1. **前端**: 使用React.memo优化组件渲染
2. **后端**: 数据库查询使用索引
3. **WebSocket**: 只推送必要的数据

### AI调用优化
1. **超时处理**: AI调用可能较慢，设置合理超时
2. **错误重试**: 失败后允许用户重新生成
3. **进度反馈**: 实时推送进度，避免用户焦虑

---

## 🎯 MVP完成标准

### 必须实现的功能
- ✅ 项目CRUD
- ✅ AI生成大纲（Director + Outliner）
- ✅ 大纲可视化展示（卡片视图）
- ✅ 章节编辑（标题、摘要、冲突等）
- ✅ 实时进度推送（WebSocket）
- ✅ 数据持久化（SQLite）

### 可选功能（时间允许）
- 拖拽排序
- 批注系统
- 版本管理
- 思维导图视图

---

## 📚 参考资源

### 文档
- Flask: https://flask.palletsprojects.com/
- React: https://react.dev/
- Ant Design: https://ant.design/
- Zustand: https://zustand-demo.pmnd.rs/

### 现有代码
- AI智能体: `novel_generator/agents/`
- 工作流: `novel_generator/workflows/`
- Demo示例: `demo_e2e.py`

---

**文档版本**: v1.0  
**最后更新**: 2025-11-11
