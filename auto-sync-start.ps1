# 自动密码登录、代码同步和启动服务脚本
param(
    [string]$ServerIP = "192.168.1.215",
    [string]$Username = "dev",
    [string]$Password = "123"
)

Write-Host "🚀 开始自动部署流程..." -ForegroundColor Green

# 创建SSH密钥认证文件
$sshKeyFile = "$env:USERPROFILE\.ssh\id_rsa"
$sshConfigFile = "$env:USERPROFILE\.ssh\config"

# 确保SSH目录存在
if (!(Test-Path "$env:USERPROFILE\.ssh")) {
    New-Item -ItemType Directory -Path "$env:USERPROFILE\.ssh" -Force
}

# 创建SSH配置
$sshConfig = @"
Host $ServerIP
    HostName $ServerIP
    User $Username
    IdentityFile $sshKeyFile
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
"@

Set-Content -Path $sshConfigFile -Value $sshConfig -Force

# 生成SSH密钥（如果不存在）
if (!(Test-Path $sshKeyFile)) {
    Write-Host "🔑 生成SSH密钥..." -ForegroundColor Yellow
    ssh-keygen -t rsa -b 4096 -f $sshKeyFile -N '""' -q
}

# 复制公钥到服务器
Write-Host "📤 复制SSH公钥到服务器..." -ForegroundColor Yellow
$pubKey = Get-Content "$sshKeyFile.pub"
$pubKeyContent = $pubKey -join "`n"

# 使用expect脚本自动输入密码
$expectScript = @"
#!/usr/bin/expect -f
set timeout 30
spawn ssh-copy-id -i $sshKeyFile.pub $Username@$ServerIP
expect {
    "password:" {
        send "$Password\r"
        expect eof
    }
    eof
}
"@

# 保存expect脚本
$expectScriptPath = "ssh-copy-id.expect"
Set-Content -Path $expectScriptPath -Value $expectScript -Force

# 执行expect脚本
Write-Host "🔐 配置SSH密钥认证..." -ForegroundColor Yellow
& expect $expectScriptPath

# 清理expect脚本
Remove-Item $expectScriptPath -Force

# 测试SSH连接
Write-Host "🔍 测试SSH连接..." -ForegroundColor Yellow
try {
    $testResult = ssh -o ConnectTimeout=10 $Username@$ServerIP "echo 'SSH连接成功'"
    if ($testResult -eq "SSH连接成功") {
        Write-Host "✅ SSH连接成功" -ForegroundColor Green
    } else {
        throw "SSH连接失败"
    }
} catch {
    Write-Host "❌ SSH连接失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 同步代码到服务器
Write-Host "📁 同步代码到服务器..." -ForegroundColor Yellow
try {
    # 创建远程目录
    ssh $Username@$ServerIP "mkdir -p /home/dev/project"
    
    # 同步后端代码
    Write-Host "📦 同步后端代码..." -ForegroundColor Yellow
    scp -r backend/* $Username@$ServerIP:/home/dev/project/
    
    # 同步启动脚本
    Write-Host "📜 同步启动脚本..." -ForegroundColor Yellow
    scp scripts/start-backend.sh $Username@$ServerIP:/home/dev/project/
    
    Write-Host "✅ 代码同步完成" -ForegroundColor Green
} catch {
    Write-Host "❌ 代码同步失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 启动后端服务
Write-Host "🚀 启动后端服务..." -ForegroundColor Yellow
try {
    ssh $Username@$ServerIP "cd /home/dev/project && chmod +x start-backend.sh && ./start-backend.sh"
    Write-Host "✅ 后端服务启动完成" -ForegroundColor Green
} catch {
    Write-Host "❌ 后端服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 等待服务启动
Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host "🔍 检查服务状态..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://$ServerIP:8000/docs" -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 后端服务运行正常!" -ForegroundColor Green
        Write-Host "🌐 服务地址: http://${ServerIP}:8000" -ForegroundColor Green
        Write-Host "📚 API文档: http://${ServerIP}:8000/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 后端服务检查失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎯 自动部署流程完成" -ForegroundColor Green
