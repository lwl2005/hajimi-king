# 🚀 Hajimi King 网页版快速开始

## 🎉 新功能亮点

✨ **全新网页配置界面** - 告别手动编辑配置文件的时代！
🔐 **密码保护访问** - 安全的Web管理界面
🐳 **完整Docker支持** - 一键容器化部署
⚡ **实时配置管理** - 在线修改所有参数

## 🏃‍♂️ 30秒快速开始

### 方式一：一键启动脚本

```bash
# 1. 克隆项目
git clone https://github.com/GakkiNoOne/hajimi-king.git
cd hajimi-king

# 2. 运行部署脚本（自动安装依赖和配置）
python deploy.py

# 3. 启动服务
python start.py
```

### 方式二：Docker一键部署

```bash
# 1. 克隆项目
git clone https://github.com/GakkiNoOne/hajimi-king.git
cd hajimi-king

# 2. 配置GitHub Token
cp env.example .env
# 编辑 .env 文件，设置 GITHUB_TOKENS=your_tokens_here

# 3. 启动Docker服务
docker-compose up -d
```

## 🌐 访问网页界面

- **地址**: http://localhost:5000
- **默认密码**: `hajimi123`
- **建议**: 首次登录后立即修改密码

## 📱 网页界面功能

### 🔐 登录页面
- 密码验证保护
- 安全会话管理
- 响应式设计

### ⚙️ 配置管理页面
- **GitHub配置**: Token管理和验证
- **基础设置**: 数据路径、扫描范围、模型选择
- **代理配置**: 多代理轮换设置
- **同步集成**: Gemini Balancer、GPT Load配置
- **高级选项**: 文件过滤、黑名单管理

### 📊 系统状态监控
- 实时配置验证状态
- GitHub Token数量显示
- 代理配置状态
- 数据目录检查

## 🔧 重要配置项

### 必填配置
```bash
# GitHub API访问令牌（必须配置）
GITHUB_TOKENS=ghp_token1,ghp_token2,ghp_token3
```

### 网页版配置
```bash
# 网页服务端口
WEB_PORT=5000

# 访问密码（强烈建议修改）
WEB_PASSWORD=your_secure_password

# 会话密钥（强烈建议修改）
WEB_SECRET_KEY=your_random_secret_key

# 启动模式：both(完整) / core(仅核心) / web(仅网页)
HAJIMI_MODE=both
```

### 推荐配置
```bash
# 代理配置（强烈推荐）
PROXY=http://proxy1:port,http://user:pass@proxy2:port

# 扫描范围（天数）
DATE_RANGE_DAYS=730

# 验证模型
HAJIMI_CHECK_MODEL=gemini-2.5-flash
```

## 🐳 Docker部署详解

### 完整docker-compose.yml
```yaml
version: '3.8'
services:
  hajimi-king:
    build: .
    container_name: hajimi-king
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - GITHUB_TOKENS=your_tokens_here
      - WEB_PASSWORD=your_secure_password
      - PROXY=your_proxy_if_needed
    volumes:
      - ./data:/app/data
      - ./queries.txt:/app/queries.txt
      - ./.env:/app/.env
```

### Docker管理命令
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 进入容器
docker exec -it hajimi-king bash
```

## 🔒 安全建议

### 1. 修改默认密码
```bash
# 在.env文件中设置强密码
WEB_PASSWORD=your_very_secure_password_123!
```

### 2. 修改会话密钥
```bash
# 生成随机密钥
WEB_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### 3. 使用HTTPS（生产环境）
```nginx
# Nginx反向代理配置
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🛠️ 故障排除

### 常见问题

1. **无法访问网页**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep 5000
   
   # 检查防火墙
   sudo ufw allow 5000
   ```

2. **配置保存失败**
   ```bash
   # 检查文件权限
   chmod 644 .env
   
   # 检查磁盘空间
   df -h
   ```

3. **Docker启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs
   
   # 重新构建镜像
   docker-compose build --no-cache
   ```

### 日志查看
```bash
# 本地部署日志
tail -f data/logs/*.log

# Docker部署日志
docker-compose logs -f hajimi-king
```

## 📚 进阶使用

### 启动模式控制
```bash
# 仅启动核心功能
export HAJIMI_MODE=core
python start.py

# 仅启动网页界面
export HAJIMI_MODE=web
python start.py

# 启动完整服务（默认）
export HAJIMI_MODE=both
python start.py
```

### API接口使用
```bash
# 获取系统状态
curl http://localhost:5000/api/status

# 获取配置信息
curl http://localhost:5000/api/config

# 更新配置（需要登录）
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"github_tokens": "new_tokens_here"}'
```

## 🎯 使用技巧

1. **批量配置**: 在网页界面一次性配置所有参数
2. **状态监控**: 定期检查系统状态页面
3. **安全访问**: 使用强密码并定期更换
4. **备份配置**: 定期备份.env和queries.txt文件
5. **代理轮换**: 配置多个代理提高成功率

## 🤝 获取帮助

- 📖 **详细文档**: [docs/WEB_SETUP.md](docs/WEB_SETUP.md)
- 🐛 **问题反馈**: GitHub Issues
- 💬 **讨论交流**: GitHub Discussions

---

💖 **享受使用 Hajimi King 网页版的便捷体验！** 🎉✨🎊
