#!/usr/bin/env python3
"""
Hajimi King 快速部署脚本
自动化设置和部署流程
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🎪 Hajimi King 快速部署向导")
    print("🌐 网页版配置 + Docker支持")
    print("=" * 60)

def check_requirements():
    """检查系统要求"""
    print("🔍 检查系统要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 11):
        print("❌ 需要Python 3.11或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    
    # 检查Docker（可选）
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
        else:
            print("⚠️ Docker未安装（可选）")
    except FileNotFoundError:
        print("⚠️ Docker未安装（可选）")
    
    # 检查docker-compose（可选）
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose: {result.stdout.strip()}")
        else:
            print("⚠️ Docker Compose未安装（可选）")
    except FileNotFoundError:
        print("⚠️ Docker Compose未安装（可选）")
    
    return True

def setup_environment():
    """设置环境"""
    print("\n🔧 设置环境...")
    
    # 创建数据目录
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ 创建数据目录: {data_dir.absolute()}")
    
    # 复制配置文件
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path("env.example")
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ 创建 .env 配置文件")
        else:
            print("❌ env.example 文件不存在")
            return False
    else:
        print("ℹ️ .env 文件已存在")
    
    # 复制查询文件
    queries_file = Path("queries.txt")
    if not queries_file.exists():
        queries_example = Path("queries.example")
        if queries_example.exists():
            shutil.copy(queries_example, queries_file)
            print("✅ 创建 queries.txt 查询文件")
        else:
            # 创建默认查询文件
            with open(queries_file, 'w', encoding='utf-8') as f:
                f.write("# GitHub搜索查询配置文件\n")
                f.write("# 每行一个查询语句，支持GitHub搜索语法\n")
                f.write("# 以#开头的行为注释，空行会被忽略\n\n")
                f.write("AIzaSy in:file\n")
                f.write("AizaSy in:file filename:.env\n")
            print("✅ 创建默认 queries.txt 文件")
    else:
        print("ℹ️ queries.txt 文件已存在")
    
    return True

def install_dependencies():
    """安装依赖"""
    print("\n📦 安装Python依赖...")
    
    try:
        # 尝试使用uv
        result = subprocess.run(['uv', '--version'], capture_output=True)
        if result.returncode == 0:
            print("✅ 使用uv安装依赖...")
            subprocess.run(['uv', 'pip', 'install', '-r', 'pyproject.toml'], check=True)
        else:
            # 回退到pip
            print("✅ 使用pip安装依赖...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask', 'google-generativeai', 'python-dotenv', 'requests'], check=True)
        
        print("✅ 依赖安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 包管理器未找到")
        return False

def configure_github_tokens():
    """配置GitHub Tokens"""
    print("\n🔑 配置GitHub Tokens...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env文件不存在")
        return False
    
    # 读取当前配置
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已配置
    if 'GITHUB_TOKENS=' in content and not content.split('GITHUB_TOKENS=')[1].split('\n')[0].strip() == '':
        print("ℹ️ GitHub Tokens已配置")
        return True
    
    print("⚠️ 需要配置GitHub Tokens")
    print("📖 获取方式: https://github.com/settings/tokens")
    print("🔐 权限要求: public_repo")
    
    while True:
        tokens = input("请输入GitHub Tokens（多个用逗号分隔）: ").strip()
        if tokens:
            # 更新.env文件
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('GITHUB_TOKENS='):
                    lines[i] = f'GITHUB_TOKENS={tokens}'
                    break
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print("✅ GitHub Tokens配置完成")
            return True
        else:
            print("❌ GitHub Tokens不能为空")

def configure_web_password():
    """配置网页密码"""
    print("\n🔐 配置网页访问密码...")
    
    env_file = Path(".env")
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_password = "hajimi123"  # 默认密码
    
    print(f"当前密码: {current_password}")
    new_password = input("输入新密码（回车保持默认）: ").strip()
    
    if new_password:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('WEB_PASSWORD='):
                lines[i] = f'WEB_PASSWORD={new_password}'
                break
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ 网页密码已更新为: {new_password}")
    else:
        print(f"ℹ️ 使用默认密码: {current_password}")
    
    return True

def choose_deployment_method():
    """选择部署方式"""
    print("\n🚀 选择部署方式:")
    print("1. 本地运行（推荐新手）")
    print("2. Docker部署（推荐生产）")
    
    while True:
        choice = input("请选择 (1/2): ").strip()
        if choice in ['1', '2']:
            return int(choice)
        print("❌ 请输入1或2")

def deploy_local():
    """本地部署"""
    print("\n🏠 本地部署...")
    
    print("✅ 本地部署配置完成！")
    print("\n🚀 启动命令:")
    print("   python start.py")
    print("\n🌐 访问地址:")
    print("   http://localhost:5000")
    print("\n📖 更多信息:")
    print("   查看 docs/WEB_SETUP.md")

def deploy_docker():
    """Docker部署"""
    print("\n🐳 Docker部署...")
    
    try:
        # 检查Docker
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
        subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
        
        print("✅ Docker环境检查通过")
        
        # 构建镜像
        print("🔨 构建Docker镜像...")
        subprocess.run(['docker-compose', 'build'], check=True)
        
        print("✅ Docker部署配置完成！")
        print("\n🚀 启动命令:")
        print("   docker-compose up -d")
        print("\n🌐 访问地址:")
        print("   http://localhost:5000")
        print("\n📊 管理命令:")
        print("   docker-compose logs -f    # 查看日志")
        print("   docker-compose stop       # 停止服务")
        print("   docker-compose restart    # 重启服务")
        
    except subprocess.CalledProcessError:
        print("❌ Docker命令执行失败")
        return False
    except FileNotFoundError:
        print("❌ Docker或Docker Compose未安装")
        return False
    
    return True

def main():
    """主函数"""
    print_banner()
    
    # 检查系统要求
    if not check_requirements():
        sys.exit(1)
    
    # 设置环境
    if not setup_environment():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 配置GitHub Tokens
    if not configure_github_tokens():
        sys.exit(1)
    
    # 配置网页密码
    configure_web_password()
    
    # 选择部署方式
    deployment_method = choose_deployment_method()
    
    if deployment_method == 1:
        deploy_local()
    else:
        deploy_docker()
    
    print("\n" + "=" * 60)
    print("🎉 部署完成！")
    print("💖 享受使用 Hajimi King 的快乐时光！")
    print("=" * 60)

if __name__ == "__main__":
    main()
