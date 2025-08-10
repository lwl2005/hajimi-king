#!/usr/bin/env python3
"""
创建演示数据脚本
为Hajimi King网页版创建示例密钥和日志数据
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

def create_demo_data():
    """创建演示数据"""
    print("🎭 创建Hajimi King演示数据...")
    
    # 确保数据目录存在
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    keys_dir = data_dir / "keys"
    keys_dir.mkdir(exist_ok=True)
    
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # 创建示例有效密钥
    create_valid_keys(keys_dir, logs_dir)
    
    # 创建示例限流密钥
    create_rate_limited_keys(keys_dir, logs_dir)
    
    # 创建示例已发送密钥
    create_sent_keys(keys_dir, logs_dir)
    
    # 创建扫描统计文件
    create_scan_stats(data_dir)
    
    print("✅ 演示数据创建完成！")
    print("🌐 现在可以启动网页版查看效果：python start.py")

def create_valid_keys(keys_dir, logs_dir):
    """创建有效密钥示例"""
    print("📝 创建有效密钥示例...")
    
    # 示例密钥数据
    valid_keys = [
        "AIzaSyDemoKey1234567890abcdefghijklmnop",
        "AIzaSyDemoKey2345678901bcdefghijklmnopq",
        "AIzaSyDemoKey3456789012cdefghijklmnopqr",
        "AIzaSyDemoKey4567890123defghijklmnopqrs",
        "AIzaSyDemoKey5678901234efghijklmnopqrst"
    ]
    
    # 创建密钥文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    key_file = keys_dir / f"keys_valid_{timestamp}.txt"
    
    with open(key_file, 'w', encoding='utf-8') as f:
        f.write("# Hajimi King 有效密钥文件\n")
        f.write(f"# 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# 这是演示数据，请勿在生产环境使用\n\n")
        
        for key in valid_keys:
            f.write(f"{key}\n")
    
    # 创建详细日志文件
    detail_file = logs_dir / f"keys_valid_detail_{timestamp}.log"
    
    with open(detail_file, 'w', encoding='utf-8') as f:
        for i, key in enumerate(valid_keys):
            time_offset = timedelta(hours=i)
            scan_time = (datetime.now() - time_offset).strftime('%Y-%m-%d %H:%M:%S')
            
            f.write("-" * 80 + "\n")
            f.write(f"TIME: {scan_time}\n")
            f.write(f"URL: https://github.com/demo-user/demo-repo-{i+1}/blob/main/.env\n")
            f.write(f"KEY: {key}\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"✅ 创建了 {len(valid_keys)} 个有效密钥示例")

def create_rate_limited_keys(keys_dir, logs_dir):
    """创建限流密钥示例"""
    print("📝 创建限流密钥示例...")
    
    # 示例限流密钥
    rate_limited_keys = [
        "AIzaSyRateLimit1234567890abcdefghijklmn",
        "AIzaSyRateLimit2345678901bcdefghijklmno",
        "AIzaSyRateLimit3456789012cdefghijklmnop"
    ]
    
    # 创建密钥文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    key_file = keys_dir / f"key_429_{timestamp}.txt"
    
    with open(key_file, 'w', encoding='utf-8') as f:
        f.write("# Hajimi King 限流密钥文件\n")
        f.write(f"# 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# 这些密钥暂时被限流，稍后可能恢复\n\n")
        
        for key in rate_limited_keys:
            f.write(f"{key}\n")
    
    # 创建详细日志文件
    detail_file = logs_dir / f"key_429_detail_{timestamp}.log"
    
    with open(detail_file, 'w', encoding='utf-8') as f:
        for i, key in enumerate(rate_limited_keys):
            time_offset = timedelta(hours=i+2)
            scan_time = (datetime.now() - time_offset).strftime('%Y-%m-%d %H:%M:%S')
            
            f.write("-" * 80 + "\n")
            f.write(f"TIME: {scan_time}\n")
            f.write(f"URL: https://github.com/demo-user/rate-limited-repo-{i+1}/blob/main/config.py\n")
            f.write(f"KEY: {key}\n")
            f.write("STATUS: Rate Limited (429)\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"✅ 创建了 {len(rate_limited_keys)} 个限流密钥示例")

def create_sent_keys(keys_dir, logs_dir):
    """创建已发送密钥示例"""
    print("📝 创建已发送密钥示例...")
    
    # 示例已发送密钥
    sent_keys = [
        "AIzaSySentKey1234567890abcdefghijklmnop",
        "AIzaSySentKey2345678901bcdefghijklmnopq"
    ]
    
    # 创建密钥文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    key_file = keys_dir / f"keys_send_{timestamp}.txt"
    
    with open(key_file, 'w', encoding='utf-8') as f:
        f.write("# Hajimi King 已发送密钥文件\n")
        f.write(f"# 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# 这些密钥已同步到外部服务\n\n")
        
        for key in sent_keys:
            f.write(f"{key}\n")
    
    # 创建详细日志文件
    detail_file = logs_dir / f"keys_send_detail_{timestamp}.log"
    
    with open(detail_file, 'w', encoding='utf-8') as f:
        for i, key in enumerate(sent_keys):
            time_offset = timedelta(hours=i+1)
            scan_time = (datetime.now() - time_offset).strftime('%Y-%m-%d %H:%M:%S')
            send_time = (datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
            
            f.write("-" * 80 + "\n")
            f.write(f"TIME: {scan_time}\n")
            f.write(f"URL: https://github.com/demo-user/sent-repo-{i+1}/blob/main/secrets.json\n")
            f.write(f"KEY: {key} | 发送成功 | {send_time}\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"✅ 创建了 {len(sent_keys)} 个已发送密钥示例")

def create_scan_stats(data_dir):
    """创建扫描统计文件"""
    print("📝 创建扫描统计文件...")
    
    # 创建扫描SHA文件
    scanned_shas_file = data_dir / "scanned_shas.txt"
    
    with open(scanned_shas_file, 'w', encoding='utf-8') as f:
        f.write("# Hajimi King 已扫描文件SHA记录\n")
        f.write(f"# 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# 每行一个SHA值，用于避免重复扫描\n\n")
        
        # 生成一些示例SHA
        import hashlib
        for i in range(150):
            demo_content = f"demo-file-content-{i}"
            sha = hashlib.sha256(demo_content.encode()).hexdigest()
            f.write(f"{sha}\n")
    
    # 创建检查点文件
    checkpoint_file = data_dir / "checkpoint.json"
    
    checkpoint_data = {
        "last_scan_time": (datetime.now() - timedelta(hours=2)).isoformat(),
        "total_files_scanned": 150,
        "total_repos_scanned": 25,
        "scan_progress": 75.5,
        "current_query": "AIzaSy in:file",
        "scan_status": "completed"
    }
    
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
    
    print("✅ 创建了扫描统计文件")

def create_demo_logs():
    """创建演示日志"""
    print("📝 创建演示日志...")
    
    logs_dir = Path("data/logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 创建扫描日志
    scan_log = logs_dir / f"scan_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(scan_log, 'w', encoding='utf-8') as f:
        # 生成一些示例日志
        log_entries = [
            "开始扫描GitHub仓库...",
            "正在搜索查询: AIzaSy in:file",
            "找到 25 个匹配的仓库",
            "开始扫描仓库: demo-user/demo-repo-1",
            "发现可疑文件: .env",
            "提取到密钥: AIzaSyDemoKey1234567890abcdefghijklmnop",
            "验证密钥有效性...",
            "密钥验证成功，添加到有效列表",
            "继续扫描下一个文件...",
            "扫描完成，共发现 5 个有效密钥"
        ]
        
        for i, entry in enumerate(log_entries):
            timestamp = (datetime.now() - timedelta(minutes=len(log_entries)-i)).strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] INFO: {entry}\n")
    
    print("✅ 创建了演示日志文件")

if __name__ == "__main__":
    create_demo_data()
    create_demo_logs()
    
    print("\n" + "="*60)
    print("🎉 演示数据创建完成！")
    print("="*60)
    print("📊 数据统计:")
    print("   - 有效密钥: 5 个")
    print("   - 限流密钥: 3 个") 
    print("   - 已发送密钥: 2 个")
    print("   - 扫描文件: 150 个")
    print("\n🚀 启动建议:")
    print("   1. 运行: python start.py")
    print("   2. 访问: http://localhost:5000")
    print("   3. 密码: hajimi123")
    print("   4. 查看控制面板和密钥管理功能")
    print("="*60)
