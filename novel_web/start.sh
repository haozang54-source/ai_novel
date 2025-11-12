#!/bin/bash

# AI小说创作系统启动脚本

echo "========================================="
echo "AI小说创作系统 - 启动中..."
echo "========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查Node环境
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm"
    exit 1
fi

# 启动后端
echo ""
echo "1. 启动后端服务..."
cd backend
python3 migrate.py  # 首次运行需要创建数据库表
python3 app.py &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID) - http://localhost:5001"

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "2. 启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID)"

echo ""
echo "========================================="
echo "系统已启动！"
echo "前端地址: http://localhost:5173"
echo "后端地址: http://localhost:5001"
echo "========================================="
echo ""
echo "按 Ctrl+C 停止服务"

# 等待中断信号
trap "echo '正在关闭服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait
