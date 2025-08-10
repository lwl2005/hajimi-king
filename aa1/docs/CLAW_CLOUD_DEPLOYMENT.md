# 🌐 Hajimi King - Claw.cloud 部署指南

## 📋 概述

本指南详细介绍如何将 Hajimi King 部署到 claw.cloud 云平台。claw.cloud 是一个现代化的容器云平台，支持 Kubernetes 和 Docker 部署。

## ✨ 云端部署优势

- 🚀 **高可用性** - 自动故障恢复和负载均衡
- 🔒 **安全性** - 内置安全策略和网络隔离
- 📈 **可扩展性** - 自动水平扩缩容
- 💰 **成本优化** - 按需付费，资源弹性调整
- 🌍 **全球访问** - CDN加速和多地域部署

## 🚀 快速开始

### 方式一：一键部署脚本（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/GakkiNoOne/hajimi-king.git
cd hajimi-king

# 2. 配置claw.cloud访问
# 登录claw.cloud控制台，下载kubeconfig文件
export KUBECONFIG=/path/to/your/kubeconfig

# 3. 运行部署脚本
# Linux/macOS
chmod +x cloud/deploy-to-claw.sh
./cloud/deploy-to-claw.sh

# Windows PowerShell
PowerShell -ExecutionPolicy Bypass -File cloud/deploy-to-claw.ps1
```

**脚本会自动完成：**
- ✅ 环境检查和依赖验证
- ✅ 交互式配置GitHub Tokens和密码
- ✅ Docker镜像构建和推送
- ✅ Kubernetes资源创建和部署
- ✅ 服务状态检查和访问信息显示

### 方式二：Docker Compose部署

```bash
# 1. 使用云端优化的compose文件
cp cloud/env.cloud.example .env
# 编辑 .env 文件，配置必要参数

# 2. 启动服务
docker-compose -f cloud/docker-compose.cloud.yml up -d

# 3. 查看状态
docker-compose -f cloud/docker-compose.cloud.yml ps
```

### 方式三：手动Kubernetes部署

```bash
# 1. 配置kubectl连接到claw.cloud
kubectl config use-context claw-cloud

# 2. 创建命名空间（可选）
kubectl create namespace hajimi-king

# 3. 配置敏感信息
kubectl create secret generic hajimi-king-secrets \
  --from-literal=GITHUB_TOKENS="your_tokens_here" \
  --from-literal=WEB_PASSWORD="your_password" \
  --from-literal=WEB_SECRET_KEY="$(openssl rand -hex 32)"

# 4. 构建并推送镜像（如果使用私有注册表）
docker build -f cloud/Dockerfile.cloud -t your-registry/hajimi-king:latest .
docker push your-registry/hajimi-king:latest

# 5. 更新部署配置中的镜像地址
sed -i 's|hajimi-king:latest|your-registry/hajimi-king:latest|g' cloud/claw-cloud-deploy.yml

# 6. 部署到Kubernetes
kubectl apply -f cloud/claw-cloud-deploy.yml

# 7. 检查部署状态
kubectl get pods -l app=hajimi-king
kubectl get svc hajimi-king-service
kubectl get ingress hajimi-king-ingress
```

## 🔧 部署前准备

### 1. 账户和权限

- ✅ 注册 claw.cloud 账户
- ✅ 创建 Kubernetes 集群
- ✅ 配置 kubectl 访问权限
- ✅ 准备容器注册表（可选）

### 2. 必要信息

| 配置项 | 说明 | 示例 |
|--------|------|------|
| GitHub Tokens | API访问令牌 | `ghp_xxx,ghp_yyy` |
| 域名 | 访问域名 | `hajimi.your-domain.com` |
| 密码 | 网页访问密码 | `your_secure_password` |
| 代理 | 代理服务器（推荐） | `http://proxy:port` |

### 3. 资源规划

| 资源类型 | 最小配置 | 推荐配置 | 说明 |
|----------|----------|----------|------|
| CPU | 0.25 核 | 0.5 核 | 核心服务 + 网页界面 |
| 内存 | 512MB | 1GB | 包含缓存和日志 |
| 存储 | 5GB | 20GB | 数据和日志存储 |
| 网络 | 1Mbps | 10Mbps | API请求和数据传输 |

## 📁 云端部署文件结构

```
cloud/
├── claw-cloud-deploy.yml      # Kubernetes部署配置
├── Dockerfile.cloud           # 云端优化Dockerfile
├── docker-compose.cloud.yml   # 云端Docker Compose
├── deploy-to-claw.sh          # Linux/macOS部署脚本
├── deploy-to-claw.ps1         # Windows部署脚本
└── env.cloud.example          # 云端环境配置示例
```

## 🔐 安全配置

### 1. 密码和密钥

```bash
# 生成强密码
WEB_PASSWORD=$(openssl rand -base64 32)

# 生成随机密钥
WEB_SECRET_KEY=$(openssl rand -hex 32)

# 更新Kubernetes Secret
kubectl create secret generic hajimi-king-secrets \
  --from-literal=WEB_PASSWORD="$WEB_PASSWORD" \
  --from-literal=WEB_SECRET_KEY="$WEB_SECRET_KEY" \
  --from-literal=GITHUB_TOKENS="your_tokens_here"
```

### 2. 网络安全

```yaml
# 网络策略示例
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hajimi-king-netpol
spec:
  podSelector:
    matchLabels:
      app: hajimi-king
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 5000
```

### 3. RBAC权限

```yaml
# 服务账户和权限
apiVersion: v1
kind: ServiceAccount
metadata:
  name: hajimi-king-sa
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: hajimi-king-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: hajimi-king-binding
subjects:
- kind: ServiceAccount
  name: hajimi-king-sa
roleRef:
  kind: Role
  name: hajimi-king-role
  apiGroup: rbac.authorization.k8s.io
```

## 🌍 域名和SSL配置

### 1. 域名解析

```bash
# 添加DNS记录
# A记录: hajimi.your-domain.com -> cluster-ip
# CNAME记录: www.hajimi.your-domain.com -> hajimi.your-domain.com
```

### 2. SSL证书

```yaml
# Let's Encrypt自动证书
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: hajimi-king-tls
spec:
  secretName: hajimi-king-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - hajimi.your-domain.com
  - www.hajimi.your-domain.com
```

## 📊 监控和日志

### 1. 应用监控

```yaml
# Prometheus监控配置
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: hajimi-king-monitor
spec:
  selector:
    matchLabels:
      app: hajimi-king
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### 2. 日志收集

```bash
# 查看应用日志
kubectl logs -f deployment/hajimi-king

# 查看特定容器日志
kubectl logs -f deployment/hajimi-king -c hajimi-core
kubectl logs -f deployment/hajimi-king -c web-interface

# 导出日志
kubectl logs deployment/hajimi-king --since=1h > hajimi-logs.txt
```

### 3. 性能监控

```bash
# 查看资源使用情况
kubectl top pods -l app=hajimi-king
kubectl top nodes

# 查看事件
kubectl get events --sort-by=.metadata.creationTimestamp
```

## 🔄 自动扩缩容

### 1. 水平Pod自动扩缩容 (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hajimi-king-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hajimi-king
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. 垂直Pod自动扩缩容 (VPA)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: hajimi-king-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hajimi-king
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: hajimi-king
      maxAllowed:
        cpu: 1
        memory: 2Gi
      minAllowed:
        cpu: 100m
        memory: 256Mi
```

## 💾 数据备份和恢复

### 1. 数据备份

```bash
# 创建备份任务
kubectl create job hajimi-backup-$(date +%Y%m%d) \
  --from=cronjob/hajimi-king-backup

# 手动备份数据
kubectl exec deployment/hajimi-king -- tar -czf /tmp/backup.tar.gz /app/data
kubectl cp hajimi-king-pod:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
```

### 2. 定时备份

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hajimi-king-backup
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: alpine:latest
            command:
            - /bin/sh
            - -c
            - |
              apk add --no-cache tar gzip
              tar -czf /backup/hajimi-$(date +%Y%m%d).tar.gz /app/data
              find /backup -name "hajimi-*.tar.gz" -mtime +7 -delete
            volumeMounts:
            - name: data-volume
              mountPath: /app/data
            - name: backup-volume
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: data-volume
            persistentVolumeClaim:
              claimName: hajimi-king-data
          - name: backup-volume
            persistentVolumeClaim:
              claimName: hajimi-king-backup
```

## 🛠️ 故障排除

### 常见问题

1. **Pod启动失败**
   ```bash
   # 查看Pod状态
   kubectl describe pod -l app=hajimi-king
   
   # 查看事件
   kubectl get events --field-selector involvedObject.name=hajimi-king-xxx
   ```

2. **网页无法访问**
   ```bash
   # 检查Service
   kubectl get svc hajimi-king-service
   
   # 检查Ingress
   kubectl describe ingress hajimi-king-ingress
   
   # 端口转发测试
   kubectl port-forward svc/hajimi-king-service 5000:5000
   ```

3. **配置问题**
   ```bash
   # 检查ConfigMap
   kubectl get configmap hajimi-king-config -o yaml
   
   # 检查Secret
   kubectl get secret hajimi-king-secrets -o yaml
   ```

### 调试命令

```bash
# 进入容器调试
kubectl exec -it deployment/hajimi-king -- /bin/bash

# 查看容器日志
kubectl logs -f deployment/hajimi-king --all-containers=true

# 检查资源使用
kubectl top pod -l app=hajimi-king

# 查看网络连接
kubectl exec deployment/hajimi-king -- netstat -tlnp
```

## 📈 性能优化

### 1. 资源优化

```yaml
# 优化资源配置
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### 2. 缓存优化

```bash
# 启用Redis缓存
REDIS_URL=redis://hajimi-redis:6379/0
CACHE_TTL=3600
```

### 3. 网络优化

```yaml
# 启用网络策略
networkPolicy:
  enabled: true
  ingress:
    - from:
      - podSelector:
          matchLabels:
            app: nginx-ingress
```

## 🔄 更新和维护

### 1. 滚动更新

```bash
# 更新镜像
kubectl set image deployment/hajimi-king hajimi-king=new-image:tag

# 查看更新状态
kubectl rollout status deployment/hajimi-king

# 回滚更新
kubectl rollout undo deployment/hajimi-king
```

### 2. 配置更新

```bash
# 更新ConfigMap
kubectl patch configmap hajimi-king-config -p '{"data":{"KEY":"new-value"}}'

# 重启Pod应用新配置
kubectl rollout restart deployment/hajimi-king
```

## 💰 成本优化

### 1. 资源调优

- 使用合适的资源请求和限制
- 启用自动扩缩容
- 使用Spot实例（如果支持）

### 2. 存储优化

- 定期清理旧日志和数据
- 使用压缩存储
- 配置数据生命周期策略

## 📞 技术支持

- 📖 **文档**: [完整文档](../README.md)
- 🐛 **问题反馈**: GitHub Issues
- 💬 **社区讨论**: GitHub Discussions
- 📧 **技术支持**: support@hajimi-king.com

---

💖 **享受在 claw.cloud 上使用 Hajimi King 的云端体验！** 🎉✨🎊
