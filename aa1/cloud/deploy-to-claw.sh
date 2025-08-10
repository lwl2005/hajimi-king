#!/bin/bash

# Hajimi King - Claw.cloud 部署脚本
# 自动化部署到 claw.cloud 平台

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_banner() {
    echo "============================================================"
    echo "🎪 Hajimi King - Claw.cloud 部署脚本"
    echo "🌐 网页版配置 + 云端部署"
    echo "============================================================"
}

# 检查必要工具
check_prerequisites() {
    print_info "检查部署环境..."
    
    # 检查kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl 未安装，请先安装 kubectl"
        exit 1
    fi
    
    # 检查docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查集群连接
    if ! kubectl cluster-info &> /dev/null; then
        print_error "无法连接到 Kubernetes 集群，请检查 kubeconfig"
        exit 1
    fi
    
    print_success "环境检查通过"
}

# 配置部署参数
configure_deployment() {
    print_info "配置部署参数..."
    
    # 读取配置
    echo "请输入以下配置信息："
    
    # GitHub Tokens
    while [[ -z "$GITHUB_TOKENS" ]]; do
        read -p "GitHub Tokens (必填，多个用逗号分隔): " GITHUB_TOKENS
        if [[ -z "$GITHUB_TOKENS" ]]; then
            print_warning "GitHub Tokens 不能为空"
        fi
    done
    
    # 网页密码
    read -p "网页访问密码 (默认: hajimi123): " WEB_PASSWORD
    WEB_PASSWORD=${WEB_PASSWORD:-hajimi123}
    
    # 域名
    read -p "域名 (例如: hajimi.your-domain.com): " DOMAIN
    if [[ -z "$DOMAIN" ]]; then
        DOMAIN="hajimi-king.claw.cloud"
        print_warning "使用默认域名: $DOMAIN"
    fi
    
    # 代理配置（可选）
    read -p "代理配置 (可选，多个用逗号分隔): " PROXY
    
    # 生成随机密钥
    WEB_SECRET_KEY=$(openssl rand -hex 32)
    
    print_success "配置完成"
}

# 构建Docker镜像
build_image() {
    print_info "构建Docker镜像..."
    
    # 镜像标签
    IMAGE_TAG="hajimi-king:cloud-$(date +%Y%m%d-%H%M%S)"
    
    # 构建镜像
    docker build -f cloud/Dockerfile.cloud -t $IMAGE_TAG .
    
    # 如果有容器注册表，推送镜像
    if [[ ! -z "$CONTAINER_REGISTRY" ]]; then
        print_info "推送镜像到注册表..."
        docker tag $IMAGE_TAG $CONTAINER_REGISTRY/$IMAGE_TAG
        docker push $CONTAINER_REGISTRY/$IMAGE_TAG
        IMAGE_TAG="$CONTAINER_REGISTRY/$IMAGE_TAG"
    fi
    
    print_success "镜像构建完成: $IMAGE_TAG"
}

# 更新部署配置
update_deployment_config() {
    print_info "更新部署配置..."
    
    # 创建临时配置文件
    TEMP_CONFIG="/tmp/hajimi-king-deploy.yml"
    cp cloud/claw-cloud-deploy.yml $TEMP_CONFIG
    
    # 替换配置值
    sed -i "s|hajimi-king:latest|$IMAGE_TAG|g" $TEMP_CONFIG
    sed -i "s|your-domain.claw.cloud|$DOMAIN|g" $TEMP_CONFIG
    
    # 更新Secret中的敏感信息
    kubectl create secret generic hajimi-king-secrets \
        --from-literal=GITHUB_TOKENS="$GITHUB_TOKENS" \
        --from-literal=WEB_PASSWORD="$WEB_PASSWORD" \
        --from-literal=WEB_SECRET_KEY="$WEB_SECRET_KEY" \
        --from-literal=PROXY="$PROXY" \
        --from-literal=GEMINI_BALANCER_URL="" \
        --from-literal=GEMINI_BALANCER_AUTH="" \
        --from-literal=GPT_LOAD_URL="" \
        --from-literal=GPT_LOAD_AUTH="" \
        --from-literal=GPT_LOAD_GROUP_NAME="" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "配置更新完成"
}

# 部署到Kubernetes
deploy_to_kubernetes() {
    print_info "部署到 Kubernetes..."
    
    # 应用配置
    kubectl apply -f $TEMP_CONFIG
    
    # 等待部署完成
    print_info "等待部署完成..."
    kubectl rollout status deployment/hajimi-king --timeout=300s
    
    print_success "部署完成"
}

# 检查部署状态
check_deployment_status() {
    print_info "检查部署状态..."
    
    # 检查Pod状态
    kubectl get pods -l app=hajimi-king
    
    # 检查Service状态
    kubectl get service hajimi-king-service
    
    # 检查Ingress状态
    kubectl get ingress hajimi-king-ingress
    
    # 获取访问地址
    EXTERNAL_IP=$(kubectl get ingress hajimi-king-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [[ -z "$EXTERNAL_IP" ]]; then
        EXTERNAL_IP=$(kubectl get ingress hajimi-king-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    fi
    
    print_success "部署状态检查完成"
    
    echo ""
    echo "============================================================"
    echo "🎉 部署完成！"
    echo "============================================================"
    echo "🌐 访问地址: https://$DOMAIN"
    echo "🔐 登录密码: $WEB_PASSWORD"
    echo "📊 监控命令:"
    echo "   kubectl logs -f deployment/hajimi-king"
    echo "   kubectl get pods -l app=hajimi-king"
    echo "============================================================"
}

# 清理临时文件
cleanup() {
    if [[ -f "$TEMP_CONFIG" ]]; then
        rm -f $TEMP_CONFIG
    fi
}

# 主函数
main() {
    print_banner
    
    # 设置清理陷阱
    trap cleanup EXIT
    
    # 执行部署步骤
    check_prerequisites
    configure_deployment
    build_image
    update_deployment_config
    deploy_to_kubernetes
    check_deployment_status
    
    print_success "Hajimi King 已成功部署到 claw.cloud！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
