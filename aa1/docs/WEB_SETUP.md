# 🌐 Hajimi King 网页版配置指南

## 📋 概述

Hajimi King 现在支持网页版配置管理！通过直观的Web界面，您可以轻松配置所有参数，无需手动编辑配置文件。

## ✨ 新功能特性

- 🔐 **密码保护访问** - 安全的登录验证机制
- 🎨 **响应式界面** - 支持桌面和移动设备
- ⚡ **实时配置** - 即时保存和验证配置
- 📊 **状态监控** - 实时显示系统状态
- 🐳 **Docker支持** - 完整的容器化部署方案

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

```bash
# 克隆项目
git clone https://github.com/GakkiNoOne/hajimi-king.git
cd hajimi-king

# 安装依赖
pip install -r pyproject.toml

# 启动服务（核心功能 + 网页界面）
python start.py
```

访问 http://localhost:5000，默认密码：`hajimi123`

### 方式二：Docker部署

```bash
# 克隆项目
git clone https://github.com/GakkiNoOne/hajimi-king.git
cd hajimi-king

# 复制并编辑配置文件
cp env.example .env
# 编辑 .env 文件，至少配置 GITHUB_TOKENS

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问 http://localhost:5000

## 🔧 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `WEB_PORT` | `5000` | 网页服务端口 |
| `WEB_PASSWORD` | `hajimi123` | 网页访问密码 |
| `WEB_SECRET_KEY` | `hajimi-king-web-secret-key-change-me` | Flask会话密钥 |
| `WEB_DEBUG` | `false` | 是否启用调试模式 |
| `HAJIMI_MODE` | `both` | 启动模式：`core`/`web`/`both` |

### 安全建议

⚠️ **重要安全提示**：

1. **修改默认密码**：
   ```bash
   # 在 .env 文件中设置
   WEB_PASSWORD=your_secure_password_here
   ```

2. **修改会话密钥**：
   ```bash
   # 在 .env 文件中设置
   WEB_SECRET_KEY=your_random_secret_key_here
   ```

3. **使用HTTPS**：生产环境建议配置反向代理（如Nginx）启用HTTPS

## 📱 界面功能

### 登录页面
- 密码验证
- 会话管理
- 安全提示

### 配置管理页面
- **GitHub配置**：Token管理
- **基础配置**：数据路径、代理、模型选择等
- **同步配置**：Gemini Balancer、GPT Load集成
- **高级配置**：文件过滤、路径黑名单等

### 系统状态
- 配置验证状态
- GitHub Token数量
- 代理配置状态
- 数据目录状态

## 🐳 Docker部署详解

### 完整的docker-compose.yml示例

```yaml
version: '3.8'

services:
  hajimi-king:
    build: .
    image: hajimi-king:latest
    container_name: hajimi-king
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      # 必填：GitHub配置
      - GITHUB_TOKENS=ghp_your_token_1,ghp_your_token_2
      
      # 网页配置
      - WEB_PORT=5000
      - WEB_PASSWORD=your_secure_password
      - WEB_SECRET_KEY=your_random_secret_key
      
      # 可选：其他配置
      - PROXY=http://proxy1:port,http://proxy2:port
      - DATE_RANGE_DAYS=730
      - HAJIMI_CHECK_MODEL=gemini-2.5-flash
      
    volumes:
      - ./data:/app/data
      - ./queries.txt:/app/queries.txt
      - ./.env:/app/.env
```

### Docker命令

```bash
# 构建镜像
docker build -t hajimi-king:latest .

# 运行容器
docker run -d \
  --name hajimi-king \
  -p 5000:5000 \
  -e GITHUB_TOKENS="your_tokens_here" \
  -e WEB_PASSWORD="your_password" \
  -v $(pwd)/data:/app/data \
  hajimi-king:latest

# 查看日志
docker logs -f hajimi-king

# 停止容器
docker stop hajimi-king

# 重启容器
docker restart hajimi-king
```

## 🔧 高级配置

### 启动模式

通过 `HAJIMI_MODE` 环境变量控制启动模式：

```bash
# 仅启动核心功能（无网页界面）
export HAJIMI_MODE=core
python start.py

# 仅启动网页界面（用于配置管理）
export HAJIMI_MODE=web
python start.py

# 启动完整服务（默认）
export HAJIMI_MODE=both
python start.py
```

### 反向代理配置

使用Nginx作为反向代理的示例配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🛠️ 故障排除

### 常见问题

1. **无法访问网页界面**
   ```bash
   # 检查端口是否被占用
   netstat -tulpn | grep 5000
   
   # 检查防火墙设置
   sudo ufw allow 5000
   ```

2. **配置保存失败**
   - 检查文件权限
   - 确保.env文件可写
   - 查看应用日志

3. **Docker容器启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs hajimi-king
   
   # 检查配置文件
   docker-compose config
   ```

### 日志查看

```bash
# 本地部署
tail -f data/logs/*.log

# Docker部署
docker-compose logs -f

# 查看特定服务日志
docker exec hajimi-king tail -f /var/log/web-interface.out.log
docker exec hajimi-king tail -f /var/log/hajimi-king.out.log
```

## 📚 API文档

网页界面提供以下API端点：

- `GET /api/config` - 获取当前配置
- `POST /api/config` - 更新配置
- `GET /api/status` - 获取系统状态

## 🔄 升级指南

从旧版本升级到网页版：

1. 备份现有配置和数据
2. 拉取最新代码
3. 安装新依赖：`pip install flask`
4. 使用新的启动方式

## 💡 使用技巧

1. **批量配置**：可以在网页界面一次性配置所有参数
2. **状态监控**：定期检查系统状态页面
3. **安全访问**：建议使用强密码并定期更换
4. **备份配置**：定期备份.env文件

## 🤝 贡献

欢迎提交Issue和Pull Request来改进网页版功能！

---

💖 **享受使用 Hajimi King 网页版的便捷体验！** 🎉✨🎊
