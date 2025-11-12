# AI小说创作Web系统

基于 Flask + React + Ant Design 的AI小说创作辅助系统。

## 快速启动

### 1. 安装依赖

**后端:**
```bash
cd /Users/zelaszang/Documents/UGit/ai_novel
pipenv install
```

**前端:**
```bash
cd novel_web/frontend
npm install
```

### 2. 初始化数据库

```bash
pipenv run python scripts/init_db.py
```

### 3. 启动服务

**后端 (Flask):**
```bash
cd novel_web/backend
pipenv run python app.py
```

**前端 (React):**
```bash
cd novel_web/frontend
npm run dev
```

### 4. 访问系统

- 前端: http://localhost:5173
- 后端: http://localhost:5000

## 项目结构

```
novel_web/
├── backend/           # Flask后端
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑
│   ├── routes/       # API路由
│   └── utils/        # 工具函数
│
├── frontend/         # React前端
│   └── src/
│       ├── types/    # TypeScript类型
│       ├── services/ # API调用
│       ├── store/    # Zustand状态管理
│       ├── pages/    # 页面组件
│       └── components/ # 通用组件
│
└── data/            # SQLite数据库
```

## 核心功能

- ✅ 项目管理 (CRUD)
- ✅ AI生成大纲 (Director + Outliner)
- ✅ 大纲可视化 (卡片视图)
- ✅ 章节编辑
- ✅ 实时进度推送 (WebSocket)
- ✅ 数据持久化 (SQLite)

## API文档

### Projects
- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/:id` - 获取项目详情
- `PUT /api/projects/:id` - 更新项目
- `DELETE /api/projects/:id` - 删除项目

### Outlines
- `GET /api/projects/:id/outline` - 获取大纲
- `POST /api/projects/:id/outline/generate` - 生成大纲
- `PUT /api/outline-chapters/:id` - 更新章节
- `POST /api/outlines/:id/chapters/reorder` - 章节排序

## 技术栈

- **后端**: Flask 3.0, SQLAlchemy, Flask-SocketIO
- **前端**: React 18, TypeScript, Ant Design 5, Zustand
- **AI**: novel_generator (Director + Outliner)
- **数据库**: SQLite
