#!/usr/bin/env python3
"""
Hajimi King 启动脚本
支持同时运行核心功能和网页配置界面
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n🛑 收到停止信号，正在关闭服务...")
    sys.exit(0)

def run_core_service():
    """运行核心服务"""
    print("🚀 启动 Hajimi King 核心服务...")
    try:
        subprocess.run([sys.executable, "app/hajimi_king.py"], check=True)
    except KeyboardInterrupt:
        print("⛔ 核心服务被用户中断")
    except Exception as e:
        print(f"❌ 核心服务异常: {e}")

def run_web_service():
    """运行网页服务"""
    print("🌐 启动网页配置界面...")
    try:
        subprocess.run([sys.executable, "web/app.py"], check=True)
    except KeyboardInterrupt:
        print("⛔ 网页服务被用户中断")
    except Exception as e:
        print(f"❌ 网页服务异常: {e}")

def check_dependencies():
    """检查依赖"""
    try:
        import flask
        import google.generativeai
        import requests
        from dotenv import load_dotenv
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r pyproject.toml")
        return False

def setup_environment():
    """设置环境"""
    # 确保数据目录存在
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ 数据目录: {data_dir.absolute()}")
    
    # 检查.env文件
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env文件不存在，从示例文件复制...")
        example_file = Path("env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ 已创建.env文件，请编辑配置")
        else:
            print("❌ env.example文件不存在")
            return False
    
    # 检查queries.txt文件
    queries_file = Path("queries.txt")
    if not queries_file.exists():
        print("⚠️ queries.txt文件不存在，从示例文件复制...")
        example_file = Path("queries.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, queries_file)
            print("✅ 已创建queries.txt文件")
        else:
            # 创建默认查询文件
            with open(queries_file, 'w', encoding='utf-8') as f:
                f.write("# GitHub搜索查询配置文件\n")
                f.write("# 每行一个查询语句，支持GitHub搜索语法\n")
                f.write("# 以#开头的行为注释，空行会被忽略\n\n")
                f.write("AIzaSy in:file\n")
                f.write("AizaSy in:file filename:.env\n")
            print("✅ 已创建默认queries.txt文件")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🎪 Hajimi King - 人人都是哈基米大王 👑")
    print("=" * 60)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置环境
    if not setup_environment():
        sys.exit(1)
    
    # 获取启动模式
    mode = os.getenv('HAJIMI_MODE', 'both').lower()
    
    if mode == 'core':
        print("🔧 仅启动核心服务模式")
        run_core_service()
    elif mode == 'web':
        print("🌐 仅启动网页服务模式")
        run_web_service()
    else:
        print("🚀 启动完整服务模式（核心 + 网页）")
        
        # 创建线程运行两个服务
        core_thread = threading.Thread(target=run_core_service, daemon=True)
        web_thread = threading.Thread(target=run_web_service, daemon=True)
        
        # 启动线程
        core_thread.start()
        time.sleep(2)  # 等待核心服务启动
        web_thread.start()
        
        print("\n" + "=" * 60)
        print("✅ 服务启动完成！")
        print("🔍 核心服务: 正在后台运行")
        print("🌐 网页配置: http://localhost:5000")
        print("🔐 默认密码: hajimi123")
        print("⛔ 按 Ctrl+C 停止服务")
        print("=" * 60)
        
        try:
            # 保持主线程运行
            while True:
                time.sleep(1)
                if not core_thread.is_alive() and not web_thread.is_alive():
                    break
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务...")

if __name__ == "__main__":
    main()
