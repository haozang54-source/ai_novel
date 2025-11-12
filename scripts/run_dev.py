#!/usr/bin/env python3
import subprocess
import sys
import time
from pathlib import Path

def start_backend():
    print("🚀 启动Flask后端...")
    backend_dir = Path(__file__).parent.parent / "novel_web/backend"
    return subprocess.Popen([sys.executable, "app.py"], cwd=backend_dir)

def start_frontend():
    print("🚀 启动React前端...")
    frontend_dir = Path(__file__).parent.parent / "novel_web/frontend"
    return subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)

if __name__ == "__main__":
    backend_process = start_backend()
    time.sleep(2)
    frontend_process = start_frontend()
    
    print("\n✅ 开发服务器已启动:")
    print("   - 后端: http://localhost:5001")
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
