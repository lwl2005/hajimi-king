import os
import sys
import json
import hashlib
import glob
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import Config
from common.Logger import logger
from utils.file_manager import file_manager

app = Flask(__name__)
app.secret_key = os.getenv('WEB_SECRET_KEY', 'hajimi-king-web-secret-key-change-me')

# 网页访问密码配置
WEB_PASSWORD = os.getenv('WEB_PASSWORD', 'hajimi123')
WEB_PASSWORD_HASH = hashlib.sha256(WEB_PASSWORD.encode()).hexdigest()

def require_auth(f):
    """装饰器：要求用户登录"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """首页重定向到控制面板"""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@require_auth
def dashboard():
    """控制面板页面"""
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if password_hash == WEB_PASSWORD_HASH:
            session['authenticated'] = True
            session['login_time'] = datetime.now().isoformat()
            flash('登录成功！', 'success')
            return redirect(url_for('config'))
        else:
            flash('密码错误！', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('login'))

@app.route('/config')
@require_auth
def config():
    """配置页面"""
    # 读取当前配置
    current_config = {
        'github_tokens': ','.join(Config.GITHUB_TOKENS),
        'data_path': Config.DATA_PATH,
        'proxy': ','.join(Config.PROXY_LIST) if Config.PROXY_LIST else '',
        'date_range_days': Config.DATE_RANGE_DAYS,
        'queries_file': Config.QUERIES_FILE,
        'hajimi_check_model': Config.HAJIMI_CHECK_MODEL,
        'gemini_balancer_sync_enabled': Config.parse_bool(Config.GEMINI_BALANCER_SYNC_ENABLED),
        'gemini_balancer_url': Config.GEMINI_BALANCER_URL,
        'gemini_balancer_auth': Config.GEMINI_BALANCER_AUTH,
        'gpt_load_sync_enabled': Config.parse_bool(Config.GPT_LOAD_SYNC_ENABLED),
        'gpt_load_url': Config.GPT_LOAD_URL,
        'gpt_load_auth': Config.GPT_LOAD_AUTH,
        'gpt_load_group_name': Config.GPT_LOAD_GROUP_NAME,
        'file_path_blacklist': ','.join(Config.FILE_PATH_BLACKLIST)
    }

    return render_template('config.html', config=current_config)

@app.route('/keys')
@require_auth
def keys():
    """密钥管理页面"""
    return render_template('keys.html')

@app.route('/logs')
@require_auth
def logs():
    """日志查看页面"""
    return render_template('logs.html')

@app.route('/api/config', methods=['GET'])
@require_auth
def get_config():
    """获取当前配置API"""
    config_data = {
        'github_tokens_count': len(Config.GITHUB_TOKENS),
        'data_path': Config.DATA_PATH,
        'proxy_count': len(Config.PROXY_LIST),
        'date_range_days': Config.DATE_RANGE_DAYS,
        'queries_file': Config.QUERIES_FILE,
        'hajimi_check_model': Config.HAJIMI_CHECK_MODEL,
        'gemini_balancer_sync_enabled': Config.parse_bool(Config.GEMINI_BALANCER_SYNC_ENABLED),
        'gemini_balancer_url': Config.GEMINI_BALANCER_URL,
        'gpt_load_sync_enabled': Config.parse_bool(Config.GPT_LOAD_SYNC_ENABLED),
        'gpt_load_url': Config.GPT_LOAD_URL,
        'gpt_load_group_name': Config.GPT_LOAD_GROUP_NAME,
        'file_path_blacklist_count': len(Config.FILE_PATH_BLACKLIST)
    }
    return jsonify(config_data)

@app.route('/api/config', methods=['POST'])
@require_auth
def update_config():
    """更新配置API"""
    try:
        data = request.get_json()
        
        # 构建新的环境变量字典
        env_updates = {}
        
        # 处理各种配置项
        if 'github_tokens' in data:
            env_updates['GITHUB_TOKENS'] = data['github_tokens']
        
        if 'data_path' in data:
            env_updates['DATA_PATH'] = data['data_path']
            
        if 'proxy' in data:
            env_updates['PROXY'] = data['proxy']
            
        if 'date_range_days' in data:
            env_updates['DATE_RANGE_DAYS'] = str(data['date_range_days'])
            
        if 'queries_file' in data:
            env_updates['QUERIES_FILE'] = data['queries_file']
            
        if 'hajimi_check_model' in data:
            env_updates['HAJIMI_CHECK_MODEL'] = data['hajimi_check_model']
            
        if 'gemini_balancer_sync_enabled' in data:
            env_updates['GEMINI_BALANCER_SYNC_ENABLED'] = str(data['gemini_balancer_sync_enabled']).lower()
            
        if 'gemini_balancer_url' in data:
            env_updates['GEMINI_BALANCER_URL'] = data['gemini_balancer_url']
            
        if 'gemini_balancer_auth' in data:
            env_updates['GEMINI_BALANCER_AUTH'] = data['gemini_balancer_auth']
            
        if 'gpt_load_sync_enabled' in data:
            env_updates['GPT_LOAD_SYNC_ENABLED'] = str(data['gpt_load_sync_enabled']).lower()
            
        if 'gpt_load_url' in data:
            env_updates['GPT_LOAD_URL'] = data['gpt_load_url']
            
        if 'gpt_load_auth' in data:
            env_updates['GPT_LOAD_AUTH'] = data['gpt_load_auth']
            
        if 'gpt_load_group_name' in data:
            env_updates['GPT_LOAD_GROUP_NAME'] = data['gpt_load_group_name']
            
        if 'file_path_blacklist' in data:
            env_updates['FILE_PATH_BLACKLIST'] = data['file_path_blacklist']
        
        # 更新.env文件
        update_env_file(env_updates)
        
        logger.info(f"配置已通过网页更新: {list(env_updates.keys())}")
        
        return jsonify({
            'success': True,
            'message': '配置更新成功！重启应用后生效。',
            'updated_keys': list(env_updates.keys())
        })
        
    except Exception as e:
        logger.error(f"配置更新失败: {e}")
        return jsonify({
            'success': False,
            'message': f'配置更新失败: {str(e)}'
        }), 500

def update_env_file(updates):
    """更新.env文件"""
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    # 读取现有的.env文件
    env_vars = {}
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # 更新变量
    env_vars.update(updates)
    
    # 写回文件
    with open(env_file_path, 'w', encoding='utf-8') as f:
        f.write("# Hajimi King Configuration\n")
        f.write(f"# Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 按类别组织配置项
        categories = {
            'GitHub配置': ['GITHUB_TOKENS'],
            '基础配置': ['DATA_PATH', 'PROXY', 'DATE_RANGE_DAYS', 'QUERIES_FILE', 'HAJIMI_CHECK_MODEL'],
            'Gemini Balancer配置': ['GEMINI_BALANCER_SYNC_ENABLED', 'GEMINI_BALANCER_URL', 'GEMINI_BALANCER_AUTH'],
            'GPT Load配置': ['GPT_LOAD_SYNC_ENABLED', 'GPT_LOAD_URL', 'GPT_LOAD_AUTH', 'GPT_LOAD_GROUP_NAME'],
            '高级配置': ['FILE_PATH_BLACKLIST', 'VALID_KEY_PREFIX', 'RATE_LIMITED_KEY_PREFIX', 'KEYS_SEND_PREFIX']
        }
        
        for category, keys in categories.items():
            f.write(f"# {category}\n")
            for key in keys:
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
            f.write("\n")
        
        # 写入其他未分类的配置项
        written_keys = set()
        for keys in categories.values():
            written_keys.update(keys)
        
        other_keys = set(env_vars.keys()) - written_keys
        if other_keys:
            f.write("# 其他配置\n")
            for key in sorted(other_keys):
                f.write(f"{key}={env_vars[key]}\n")

@app.route('/api/status')
@require_auth
def get_status():
    """获取系统状态API"""
    try:
        # 检查数据目录
        data_dir = Config.DATA_PATH
        data_dir_exists = os.path.exists(data_dir)

        # 检查查询文件
        queries_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), Config.QUERIES_FILE)
        queries_file_exists = os.path.exists(queries_file)

        # 检查.env文件
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        env_file_exists = os.path.exists(env_file)

        # 获取密钥统计信息
        key_stats = get_key_statistics()

        status = {
            'config_valid': Config.check(),
            'data_directory': {
                'path': data_dir,
                'exists': data_dir_exists
            },
            'queries_file': {
                'path': queries_file,
                'exists': queries_file_exists
            },
            'env_file': {
                'path': env_file,
                'exists': env_file_exists
            },
            'github_tokens_count': len(Config.GITHUB_TOKENS),
            'proxy_count': len(Config.PROXY_LIST),
            'key_statistics': key_stats,
            'last_check': datetime.now().isoformat()
        }

        return jsonify(status)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'last_check': datetime.now().isoformat()
        }), 500

@app.route('/api/keys')
@require_auth
def get_keys():
    """获取密钥列表API"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        key_type = request.args.get('type', 'valid')  # valid, rate_limited, sent
        search = request.args.get('search', '')

        keys_data = get_keys_data(key_type, search, page, per_page)

        return jsonify(keys_data)

    except Exception as e:
        logger.error(f"获取密钥列表失败: {e}")
        return jsonify({
            'error': str(e),
            'keys': [],
            'total': 0,
            'page': 1,
            'per_page': 50,
            'total_pages': 0
        }), 500

@app.route('/api/keys/statistics')
@require_auth
def get_key_statistics_api():
    """获取密钥统计信息API"""
    try:
        stats = get_key_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取密钥统计失败: {e}")
        return jsonify({
            'error': str(e),
            'valid_keys': 0,
            'rate_limited_keys': 0,
            'sent_keys': 0,
            'total_files_scanned': 0
        }), 500

@app.route('/api/keys/export')
@require_auth
def export_keys():
    """导出密钥API"""
    try:
        key_type = request.args.get('type', 'valid')
        format_type = request.args.get('format', 'txt')  # txt, json, csv

        keys_data = get_all_keys_data(key_type)

        if format_type == 'json':
            return jsonify(keys_data)
        elif format_type == 'csv':
            # 生成CSV格式
            import io
            import csv
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Key', 'Source', 'Found Time', 'Status'])

            for key_info in keys_data:
                writer.writerow([
                    key_info.get('key', ''),
                    key_info.get('source', ''),
                    key_info.get('found_time', ''),
                    key_info.get('status', '')
                ])

            response = app.response_class(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=hajimi_keys_{key_type}_{datetime.now().strftime("%Y%m%d")}.csv'}
            )
            return response
        else:
            # 默认TXT格式
            keys_text = '\n'.join([key_info.get('key', '') for key_info in keys_data])
            response = app.response_class(
                keys_text,
                mimetype='text/plain',
                headers={'Content-Disposition': f'attachment; filename=hajimi_keys_{key_type}_{datetime.now().strftime("%Y%m%d")}.txt'}
            )
            return response

    except Exception as e:
        logger.error(f"导出密钥失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
@require_auth
def get_logs():
    """获取日志API"""
    try:
        log_type = request.args.get('type', 'scan')  # scan, error, system
        lines = int(request.args.get('lines', 100))

        logs_data = get_logs_data(log_type, lines)

        return jsonify(logs_data)

    except Exception as e:
        logger.error(f"获取日志失败: {e}")
        return jsonify({
            'error': str(e),
            'logs': [],
            'total_lines': 0
        }), 500

def get_key_statistics():
    """获取密钥统计信息"""
    try:
        stats = {
            'valid_keys': 0,
            'rate_limited_keys': 0,
            'sent_keys': 0,
            'total_files_scanned': 0,
            'last_scan_time': None
        }

        # 统计有效密钥
        valid_files = glob.glob(os.path.join(Config.DATA_PATH, f"{Config.VALID_KEY_PREFIX}*.txt"))
        for file_path in valid_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    stats['valid_keys'] += len([line for line in f if line.strip()])
            except Exception as e:
                logger.error(f"读取有效密钥文件失败 {file_path}: {e}")

        # 统计限流密钥
        rate_limited_files = glob.glob(os.path.join(Config.DATA_PATH, f"{Config.RATE_LIMITED_KEY_PREFIX}*.txt"))
        for file_path in rate_limited_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    stats['rate_limited_keys'] += len([line for line in f if line.strip()])
            except Exception as e:
                logger.error(f"读取限流密钥文件失败 {file_path}: {e}")

        # 统计已发送密钥
        sent_files = glob.glob(os.path.join(Config.DATA_PATH, f"{Config.KEYS_SEND_PREFIX}*.txt"))
        for file_path in sent_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    stats['sent_keys'] += len([line for line in f if line.strip()])
            except Exception as e:
                logger.error(f"读取已发送密钥文件失败 {file_path}: {e}")

        # 获取扫描文件数量
        scanned_shas_file = os.path.join(Config.DATA_PATH, Config.SCANNED_SHAS_FILE)
        if os.path.exists(scanned_shas_file):
            try:
                with open(scanned_shas_file, 'r', encoding='utf-8') as f:
                    stats['total_files_scanned'] = len([line for line in f if line.strip() and not line.startswith('#')])
            except Exception as e:
                logger.error(f"读取扫描文件统计失败: {e}")

        # 获取最后扫描时间
        checkpoint_file = os.path.join(Config.DATA_PATH, "checkpoint.json")
        if os.path.exists(checkpoint_file):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                    stats['last_scan_time'] = checkpoint_data.get('last_scan_time')
            except Exception as e:
                logger.error(f"读取检查点文件失败: {e}")

        return stats

    except Exception as e:
        logger.error(f"获取密钥统计失败: {e}")
        return {
            'valid_keys': 0,
            'rate_limited_keys': 0,
            'sent_keys': 0,
            'total_files_scanned': 0,
            'last_scan_time': None
        }

def get_keys_data(key_type, search='', page=1, per_page=50):
    """获取密钥数据"""
    try:
        all_keys = []

        if key_type == 'valid':
            prefix = Config.VALID_KEY_PREFIX
            detail_prefix = Config.VALID_KEY_DETAIL_PREFIX
        elif key_type == 'rate_limited':
            prefix = Config.RATE_LIMITED_KEY_PREFIX
            detail_prefix = Config.RATE_LIMITED_KEY_DETAIL_PREFIX
        elif key_type == 'sent':
            prefix = Config.KEYS_SEND_PREFIX
            detail_prefix = Config.KEYS_SEND_DETAIL_PREFIX
        else:
            raise ValueError(f"不支持的密钥类型: {key_type}")

        # 获取密钥文件
        key_files = glob.glob(os.path.join(Config.DATA_PATH, f"{prefix}*.txt"))
        detail_files = glob.glob(os.path.join(Config.DATA_PATH, f"{detail_prefix}*.log"))

        # 解析详细信息文件
        key_details = {}
        for detail_file in detail_files:
            try:
                with open(detail_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    parse_detail_file(content, key_details)
            except Exception as e:
                logger.error(f"解析详细文件失败 {detail_file}: {e}")

        # 读取密钥文件
        for key_file in key_files:
            try:
                with open(key_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        key = line.strip()
                        if key and not key.startswith('#'):
                            # 搜索过滤
                            if search and search.lower() not in key.lower():
                                continue

                            key_info = {
                                'key': key,
                                'file': os.path.basename(key_file),
                                'line': line_num,
                                'type': key_type,
                                'found_time': key_details.get(key, {}).get('time', ''),
                                'source': key_details.get(key, {}).get('url', ''),
                                'status': 'active' if key_type == 'valid' else key_type
                            }
                            all_keys.append(key_info)
            except Exception as e:
                logger.error(f"读取密钥文件失败 {key_file}: {e}")

        # 排序（按发现时间倒序）
        all_keys.sort(key=lambda x: x.get('found_time', ''), reverse=True)

        # 分页
        total = len(all_keys)
        start = (page - 1) * per_page
        end = start + per_page
        keys = all_keys[start:end]

        return {
            'keys': keys,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
            'search': search,
            'type': key_type
        }

    except Exception as e:
        logger.error(f"获取密钥数据失败: {e}")
        return {
            'keys': [],
            'total': 0,
            'page': page,
            'per_page': per_page,
            'total_pages': 0,
            'search': search,
            'type': key_type,
            'error': str(e)
        }

def parse_detail_file(content, key_details):
    """解析详细信息文件"""
    try:
        blocks = content.split('-' * 80)
        for block in blocks:
            if not block.strip():
                continue

            lines = block.strip().split('\n')
            time_info = ''
            url_info = ''
            keys = []

            for line in lines:
                line = line.strip()
                if line.startswith('TIME:'):
                    time_info = line[5:].strip()
                elif line.startswith('URL:'):
                    url_info = line[4:].strip()
                elif line.startswith('KEY:'):
                    key = line[4:].strip()
                    if '|' in key:  # 处理发送结果格式
                        key = key.split('|')[0].strip()
                    keys.append(key)
                elif line and not line.startswith('TIME:') and not line.startswith('URL:'):
                    # 处理没有KEY:前缀的密钥行
                    if re.match(r'^AIzaSy[A-Za-z0-9\-_]{33}', line):
                        keys.append(line)

            # 保存密钥详细信息
            for key in keys:
                if key not in key_details:
                    key_details[key] = {
                        'time': time_info,
                        'url': url_info
                    }
    except Exception as e:
        logger.error(f"解析详细文件内容失败: {e}")

def get_all_keys_data(key_type):
    """获取所有密钥数据（用于导出）"""
    try:
        keys_data = get_keys_data(key_type, '', 1, 999999)  # 获取所有数据
        return keys_data.get('keys', [])
    except Exception as e:
        logger.error(f"获取所有密钥数据失败: {e}")
        return []

def get_logs_data(log_type, lines=100):
    """获取日志数据"""
    try:
        logs = []

        if log_type == 'scan':
            # 扫描日志
            log_files = glob.glob(os.path.join(Config.DATA_PATH, f"{Config.VALID_KEY_DETAIL_PREFIX}*.log"))
        elif log_type == 'error':
            # 错误日志
            log_files = glob.glob(os.path.join(Config.DATA_PATH, "logs", "*.log"))
        else:
            # 系统日志
            log_files = []

        # 读取最新的日志文件
        if log_files:
            log_files.sort(key=os.path.getmtime, reverse=True)
            latest_log = log_files[0]

            try:
                with open(latest_log, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    # 获取最后N行
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

                    for line in recent_lines:
                        line = line.strip()
                        if line:
                            logs.append({
                                'timestamp': datetime.now().isoformat(),
                                'level': 'INFO',
                                'message': line
                            })
            except Exception as e:
                logger.error(f"读取日志文件失败 {latest_log}: {e}")

        return {
            'logs': logs,
            'total_lines': len(logs),
            'log_type': log_type,
            'file_count': len(log_files)
        }

    except Exception as e:
        logger.error(f"获取日志数据失败: {e}")
        return {
            'logs': [],
            'total_lines': 0,
            'log_type': log_type,
            'error': str(e)
        }

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(Config.DATA_PATH, exist_ok=True)

    # 启动Flask应用
    port = int(os.getenv('WEB_PORT', 5000))
    debug = os.getenv('WEB_DEBUG', 'false').lower() == 'true'

    logger.info(f"🌐 启动Hajimi King网页配置界面")
    logger.info(f"🌐 访问地址: http://localhost:{port}")
    logger.info(f"🔐 访问密码: {WEB_PASSWORD}")

    app.run(host='0.0.0.0', port=port, debug=debug)
