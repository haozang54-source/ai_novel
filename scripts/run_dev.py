#!/usr/bin/env python3
import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    print("🚀 启动Flask后端...")
    backend_dir = Path(__file__).parent.parent / "novel_web/backend"
    print(f"📁 后端工作目录: {backend_dir}")
    # 确保工作目录存在
    if not backend_dir.exists():
        print(f"❌ 错误: 后端目录不存在: {backend_dir}")
        sys.exit(1)
    
    # 检查是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    # 检查Pipfile是否存在，确定是否使用pipenv
    project_root = Path(__file__).parent.parent
    pipfile = project_root / "Pipfile"
    
    try:
        if in_venv:
            print("🔧 检测到虚拟环境，使用当前Python环境启动后端")
            cmd = [sys.executable, "app.py"]
        elif pipfile.exists():
            print("🔧 检测到Pipfile，使用pipenv启动后端")
            cmd = ["pipenv", "run", "python", "app.py"]
        else:
            print("🔧 未检测到虚拟环境和Pipfile，使用系统Python启动后端")
            cmd = [sys.executable, "app.py"]
            
        return subprocess.Popen(
            cmd, 
            cwd=backend_dir,
            stdout=None,  # 直接输出到控制台，便于查看错误
            stderr=None,  # 直接输出到控制台，便于查看错误
            text=True
        )
    except Exception as e:
        print(f"❌ 启动后端时出错: {str(e)}")
        sys.exit(1)

def start_frontend():
    print("🚀 启动React前端...")
    frontend_dir = Path(__file__).parent.parent / "novel_web/frontend"
    print(f"📁 前端工作目录: {frontend_dir}")
    
    # 确保工作目录存在
    if not frontend_dir.exists():
        print(f"❌ 错误: 前端目录不存在: {frontend_dir}")
        sys.exit(1)
    
    # 检查package.json是否存在
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print(f"❌ 错误: package.json不存在: {package_json}")
        sys.exit(1)
    
    # 在Windows系统上使用cmd /c执行npm命令
    if sys.platform.startswith('win'):
        print("🔧 Windows系统: 使用cmd /c执行npm命令")
        cmd = ["cmd", "/c", "npm", "run", "dev"]
    else:
        print("🔧 Unix系统: 直接执行npm命令")
        cmd = ["npm", "run", "dev"]
    
    try:
        # 直接输出到控制台，便于查看npm的日志
        return subprocess.Popen(
            cmd, 
            cwd=frontend_dir,
            stdout=None,  # 直接输出到控制台
            stderr=None,  # 直接输出到控制台
            env=os.environ.copy()  # 传递当前环境变量
        )
    except Exception as e:
        print(f"❌ 启动前端时出错: {str(e)}")
        sys.exit(1)

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
