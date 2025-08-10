# 🌐 Hajimi King - Claw.cloud 快速部署

## 🎯 5分钟快速部署到claw.cloud

### 📋 准备工作

1. **claw.cloud账户** - 注册并创建Kubernetes集群
2. **GitHub Tokens** - 至少1个有效的GitHub API Token
3. **kubectl工具** - 本地安装kubectl并配置连接

### 🚀 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/GakkiNoOne/hajimi-king.git
cd hajimi-king

# 2. 配置claw.cloud连接
# 从claw.cloud控制台下载kubeconfig文件
export KUBECONFIG=/path/to/your/kubeconfig

# 3. 运行一键部署脚本
./cloud/deploy-to-claw.sh
```

**脚本会提示输入：**
- GitHub Tokens（必填）
- 网页访问密码（可选，默认hajimi123）
- 域名（可选，默认使用claw.cloud子域名）
- 代理配置（可选但推荐）

### 🎉 部署完成

部署成功后，您将看到：

```
============================================================
🎉 部署完成！
============================================================
🌐 访问地址: https://your-domain.claw.cloud
🔐 登录密码: your_password
📊 监控命令:
   kubectl logs -f deployment/hajimi-king
   kubectl get pods -l app=hajimi-king
============================================================
```

## 🔧 快速配置

### 必填配置

```bash
# GitHub API Tokens（必须配置）
GITHUB_TOKENS=ghp_your_token_1,ghp_your_token_2
```

### 推荐配置

```bash
# 网页访问密码（强烈建议修改）
WEB_PASSWORD=your_secure_password

# 代理配置（提高成功率）
PROXY=http://proxy1:port,http://proxy2:port

# 域名配置
DOMAIN=hajimi.your-domain.com
```

## 📱 访问网页界面

1. **打开浏览器** - 访问部署完成后显示的URL
2. **输入密码** - 使用配置的密码登录
3. **开始配置** - 在网页界面管理所有配置项

### 网页功能

- 🔐 **安全登录** - 密码保护的访问控制
- ⚙️ **配置管理** - 在线修改所有参数
- 📊 **状态监控** - 实时查看系统状态
- 💾 **一键保存** - 配置即时生效

## 🐳 Docker Compose 部署（备选方案）

如果您更喜欢使用Docker Compose：

```bash
# 1. 使用云端配置
cp cloud/env.cloud.example .env

# 2. 编辑配置文件
nano .env
# 至少配置 GITHUB_TOKENS

# 3. 启动服务
docker-compose -f cloud/docker-compose.cloud.yml up -d

# 4. 访问服务
open http://localhost:5000
```

## 🛠️ 常用管理命令

### 查看状态

```bash
# 查看Pod状态
kubectl get pods -l app=hajimi-king

# 查看服务状态
kubectl get svc hajimi-king-service

# 查看访问地址
kubectl get ingress hajimi-king-ingress
```

### 查看日志

```bash
# 查看应用日志
kubectl logs -f deployment/hajimi-king

# 查看特定容器日志
kubectl logs -f deployment/hajimi-king -c hajimi-core
kubectl logs -f deployment/hajimi-king -c web-interface
```

### 更新配置

```bash
# 更新GitHub Tokens
kubectl patch secret hajimi-king-secrets -p '{"stringData":{"GITHUB_TOKENS":"new_tokens_here"}}'

# 重启应用使配置生效
kubectl rollout restart deployment/hajimi-king
```

### 扩缩容

```bash
# 手动扩容
kubectl scale deployment hajimi-king --replicas=3

# 查看扩容状态
kubectl get pods -l app=hajimi-king
```

## 🔒 安全建议

### 1. 修改默认密码

```bash
# 生成强密码
NEW_PASSWORD=$(openssl rand -base64 32)

# 更新密码
kubectl patch secret hajimi-king-secrets -p "{\"stringData\":{\"WEB_PASSWORD\":\"$NEW_PASSWORD\"}}"

echo "新密码: $NEW_PASSWORD"
```

### 2. 配置HTTPS

```bash
# 如果您有自己的域名，更新Ingress配置
kubectl patch ingress hajimi-king-ingress -p '{"spec":{"tls":[{"hosts":["your-domain.com"],"secretName":"your-tls-secret"}]}}'
```

### 3. 网络安全

```bash
# 限制访问来源（可选）
kubectl annotate ingress hajimi-king-ingress nginx.ingress.kubernetes.io/whitelist-source-range="your-ip/32"
```

## 🆘 故障排除

### 常见问题

1. **Pod启动失败**
   ```bash
   kubectl describe pod -l app=hajimi-king
   ```

2. **无法访问网页**
   ```bash
   # 端口转发测试
   kubectl port-forward svc/hajimi-king-service 5000:5000
   # 然后访问 http://localhost:5000
   ```

3. **配置不生效**
   ```bash
   # 检查配置
   kubectl get configmap hajimi-king-config -o yaml
   kubectl get secret hajimi-king-secrets -o yaml
   
   # 重启应用
   kubectl rollout restart deployment/hajimi-king
   ```

### 获取帮助

- 📖 **详细文档**: [完整部署指南](docs/CLAW_CLOUD_DEPLOYMENT.md)
- 🐛 **问题反馈**: GitHub Issues
- 💬 **社区支持**: GitHub Discussions

## 🎯 下一步

部署成功后，您可以：

1. **配置GitHub Tokens** - 在网页界面添加更多tokens
2. **设置代理** - 配置代理服务器提高成功率
3. **自定义查询** - 编辑搜索查询表达式
4. **监控运行** - 查看扫描结果和日志
5. **集成外部服务** - 配置Gemini Balancer或GPT Load同步

---

💖 **享受在claw.cloud上使用Hajimi King的云端体验！** 🎉✨🎊

## 📞 技术支持

遇到问题？我们来帮您：

- 📧 **邮件支持**: support@hajimi-king.com
- 💬 **在线聊天**: [claw.cloud支持中心](https://claw.cloud/support)
- 📱 **社区群组**: [加入Telegram群](https://t.me/hajimi_king)

**部署愉快！** 🚀
