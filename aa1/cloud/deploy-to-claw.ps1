# Hajimi King - Claw.cloud 部署脚本 (PowerShell版本)
# 自动化部署到 claw.cloud 平台

param(
    [string]$GitHubTokens = "",
    [string]$WebPassword = "hajimi123",
    [string]$Domain = "",
    [string]$Proxy = "",
    [string]$ContainerRegistry = ""
)

# 颜色函数
function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Banner {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "🎪 Hajimi King - Claw.cloud 部署脚本" -ForegroundColor Cyan
    Write-Host "🌐 网页版配置 + 云端部署" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

# 检查必要工具
function Test-Prerequisites {
    Write-Info "检查部署环境..."
    
    # 检查kubectl
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-Error "kubectl 未安装，请先安装 kubectl"
        exit 1
    }
    
    # 检查docker
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker 未安装，请先安装 Docker"
        exit 1
    }
    
    # 检查集群连接
    try {
        kubectl cluster-info | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "kubectl cluster-info failed"
        }
    }
    catch {
        Write-Error "无法连接到 Kubernetes 集群，请检查 kubeconfig"
        exit 1
    }
    
    Write-Success "环境检查通过"
}

# 配置部署参数
function Set-DeploymentConfig {
    Write-Info "配置部署参数..."
    
    # GitHub Tokens
    if (-not $GitHubTokens) {
        do {
            $GitHubTokens = Read-Host "GitHub Tokens (必填，多个用逗号分隔)"
        } while (-not $GitHubTokens)
    }
    
    # 网页密码
    if (-not $WebPassword) {
        $WebPassword = Read-Host "网页访问密码 (默认: hajimi123)"
        if (-not $WebPassword) { $WebPassword = "hajimi123" }
    }
    
    # 域名
    if (-not $Domain) {
        $Domain = Read-Host "域名 (例如: hajimi.your-domain.com)"
        if (-not $Domain) {
            $Domain = "hajimi-king.claw.cloud"
            Write-Warning "使用默认域名: $Domain"
        }
    }
    
    # 代理配置（可选）
    if (-not $Proxy) {
        $Proxy = Read-Host "代理配置 (可选，多个用逗号分隔)"
    }
    
    # 生成随机密钥
    $WebSecretKey = [System.Web.Security.Membership]::GeneratePassword(64, 0)
    
    Write-Success "配置完成"
    
    return @{
        GitHubTokens = $GitHubTokens
        WebPassword = $WebPassword
        Domain = $Domain
        Proxy = $Proxy
        WebSecretKey = $WebSecretKey
    }
}

# 构建Docker镜像
function Build-DockerImage {
    param([string]$ContainerRegistry)
    
    Write-Info "构建Docker镜像..."
    
    # 镜像标签
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $imageTag = "hajimi-king:cloud-$timestamp"
    
    # 构建镜像
    docker build -f cloud/Dockerfile.cloud -t $imageTag .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker镜像构建失败"
        exit 1
    }
    
    # 如果有容器注册表，推送镜像
    if ($ContainerRegistry) {
        Write-Info "推送镜像到注册表..."
        $fullImageTag = "$ContainerRegistry/$imageTag"
        docker tag $imageTag $fullImageTag
        docker push $fullImageTag
        if ($LASTEXITCODE -ne 0) {
            Write-Error "镜像推送失败"
            exit 1
        }
        $imageTag = $fullImageTag
    }
    
    Write-Success "镜像构建完成: $imageTag"
    return $imageTag
}

# 更新部署配置
function Update-DeploymentConfig {
    param(
        [hashtable]$Config,
        [string]$ImageTag
    )
    
    Write-Info "更新部署配置..."
    
    # 创建临时配置文件
    $tempConfig = "$env:TEMP\hajimi-king-deploy.yml"
    Copy-Item "cloud/claw-cloud-deploy.yml" $tempConfig
    
    # 替换配置值
    (Get-Content $tempConfig) -replace "hajimi-king:latest", $ImageTag -replace "your-domain.claw.cloud", $Config.Domain | Set-Content $tempConfig
    
    # 更新Secret
    $secretYaml = @"
apiVersion: v1
kind: Secret
metadata:
  name: hajimi-king-secrets
  namespace: default
type: Opaque
stringData:
  GITHUB_TOKENS: "$($Config.GitHubTokens)"
  WEB_PASSWORD: "$($Config.WebPassword)"
  WEB_SECRET_KEY: "$($Config.WebSecretKey)"
  PROXY: "$($Config.Proxy)"
  GEMINI_BALANCER_URL: ""
  GEMINI_BALANCER_AUTH: ""
  GPT_LOAD_URL: ""
  GPT_LOAD_AUTH: ""
  GPT_LOAD_GROUP_NAME: ""
"@
    
    $secretYaml | kubectl apply -f -
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Secret创建失败"
        exit 1
    }
    
    Write-Success "配置更新完成"
    return $tempConfig
}

# 部署到Kubernetes
function Deploy-ToKubernetes {
    param([string]$ConfigFile)
    
    Write-Info "部署到 Kubernetes..."
    
    # 应用配置
    kubectl apply -f $ConfigFile
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Kubernetes部署失败"
        exit 1
    }
    
    # 等待部署完成
    Write-Info "等待部署完成..."
    kubectl rollout status deployment/hajimi-king --timeout=300s
    if ($LASTEXITCODE -ne 0) {
        Write-Error "部署超时或失败"
        exit 1
    }
    
    Write-Success "部署完成"
}

# 检查部署状态
function Test-DeploymentStatus {
    param([string]$Domain)
    
    Write-Info "检查部署状态..."
    
    # 检查Pod状态
    Write-Host "Pod状态:" -ForegroundColor Yellow
    kubectl get pods -l app=hajimi-king
    
    # 检查Service状态
    Write-Host "Service状态:" -ForegroundColor Yellow
    kubectl get service hajimi-king-service
    
    # 检查Ingress状态
    Write-Host "Ingress状态:" -ForegroundColor Yellow
    kubectl get ingress hajimi-king-ingress
    
    Write-Success "部署状态检查完成"
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "🎉 部署完成！" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "🌐 访问地址: https://$Domain" -ForegroundColor Green
    Write-Host "🔐 登录密码: $($Config.WebPassword)" -ForegroundColor Green
    Write-Host "📊 监控命令:" -ForegroundColor Yellow
    Write-Host "   kubectl logs -f deployment/hajimi-king" -ForegroundColor White
    Write-Host "   kubectl get pods -l app=hajimi-king" -ForegroundColor White
    Write-Host "============================================================" -ForegroundColor Cyan
}

# 主函数
function Main {
    Write-Banner
    
    try {
        # 执行部署步骤
        Test-Prerequisites
        $config = Set-DeploymentConfig
        $imageTag = Build-DockerImage -ContainerRegistry $ContainerRegistry
        $configFile = Update-DeploymentConfig -Config $config -ImageTag $imageTag
        Deploy-ToKubernetes -ConfigFile $configFile
        Test-DeploymentStatus -Domain $config.Domain
        
        Write-Success "Hajimi King 已成功部署到 claw.cloud！"
    }
    catch {
        Write-Error "部署过程中发生错误: $($_.Exception.Message)"
        exit 1
    }
    finally {
        # 清理临时文件
        if (Test-Path "$env:TEMP\hajimi-king-deploy.yml") {
            Remove-Item "$env:TEMP\hajimi-king-deploy.yml" -Force
        }
    }
}

# 脚本入口
if ($MyInvocation.InvocationName -ne '.') {
    Main
}
