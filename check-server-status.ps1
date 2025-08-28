# 检查远程服务器状态脚本
Write-Host "🔍 检查远程服务器状态..." -ForegroundColor Green

# 检查后端服务状态
Write-Host "🔄 检查后端服务状态..." -ForegroundColor Yellow
try {
    $backendStatus = Invoke-WebRequest -Uri "http://192.168.1.215:8000/docs" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($backendStatus.StatusCode -eq 200) {
        Write-Host "✅ 后端服务运行正常 (端口8000)" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 后端服务无法连接 (端口8000)" -ForegroundColor Red
    Write-Host "错误信息: $($_.Exception.Message)" -ForegroundColor Red
}

# 检查前端服务状态
Write-Host "🎨 检查前端服务状态..." -ForegroundColor Yellow
try {
    $frontendStatus = Invoke-WebRequest -Uri "http://192.168.1.215:3000" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($frontendStatus.StatusCode -eq 200) {
        Write-Host "✅ 前端服务运行正常 (端口3000)" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 前端服务无法连接 (端口3000)" -ForegroundColor Red
    Write-Host "错误信息: $($_.Exception.Message)" -ForegroundColor Red
}

# 检查数据库连接
Write-Host "🗄️ 检查数据库连接..." -ForegroundColor Yellow
try {
    $dbStatus = Invoke-WebRequest -Uri "http://192.168.1.215:8000/api/v1/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($dbStatus.StatusCode -eq 200) {
        Write-Host "✅ 数据库连接正常" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 数据库连接失败" -ForegroundColor Red
    Write-Host "错误信息: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎯 状态检查完成" -ForegroundColor Green
