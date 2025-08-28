#!/bin/bash

# 🚀 自动创建GitHub仓库脚本
# 使用方法: 设置GitHub令牌，然后运行此脚本

echo "🚀 开始自动创建GitHub仓库..."

# ===== 请修改以下变量 =====
GITHUB_USERNAME="tbagzhao668"
REPO_NAME="project-ledger-system"
REPO_DESCRIPTION="工程项目流水账管理系统 - 专业的多租户工程项目财务管理SaaS系统"
# ===============================

# 检查GitHub令牌
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 请先设置GitHub令牌环境变量"
    echo ""
    echo "💡 设置方法:"
    echo "1. 创建GitHub个人访问令牌: https://github.com/settings/tokens"
    echo "2. 设置环境变量:"
    echo "   export GITHUB_TOKEN='your_token_here'"
    echo "3. 或者直接运行: GITHUB_TOKEN='your_token_here' ./create_github_repo.sh"
    echo ""
    echo "🔑 令牌权限要求:"
    echo "   - repo (完整的仓库访问权限)"
    echo "   - workflow (GitHub Actions工作流)"
    exit 1
fi

echo "📋 配置信息:"
echo "   GitHub用户名: $GITHUB_USERNAME"
echo "   仓库名称: $REPO_NAME"
echo "   仓库描述: $REPO_DESCRIPTION"
echo ""

# 创建仓库
echo "🔗 创建GitHub仓库..."
CREATE_RESPONSE=$(curl -s -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{
        \"name\": \"$REPO_NAME\",
        \"description\": \"$REPO_DESCRIPTION\",
        \"private\": false,
        \"has_issues\": true,
        \"has_wiki\": true,
        \"has_downloads\": true,
        \"auto_init\": false
    }")

# 检查响应
if echo "$CREATE_RESPONSE" | grep -q "already exists"; then
    echo "⚠️ 仓库已存在，继续设置..."
elif echo "$CREATE_RESPONSE" | grep -q "created_at"; then
    echo "✅ GitHub仓库创建成功！"
else
    echo "❌ 仓库创建失败！"
    echo "响应: $CREATE_RESPONSE"
    echo ""
    echo "可能的原因:"
    echo "1. 令牌权限不足"
    echo "2. 令牌已过期"
    echo "3. 网络连接问题"
    exit 1
fi

# 设置远程仓库
echo -e "\n🔗 设置Git远程仓库..."
if git remote get-url origin > /dev/null 2>&1; then
    echo "远程仓库已存在，更新URL..."
    git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
else
    echo "添加远程仓库..."
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
fi

# 验证远程仓库
echo -e "\n🔍 验证远程仓库..."
git remote -v

# 推送代码
echo -e "\n📤 推送代码到GitHub..."

# 使用令牌进行认证
git remote set-url origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# 推送主分支
echo "推送主分支..."
git push -u origin master

if [ $? -eq 0 ]; then
    echo "✅ 代码推送成功！"
    echo ""
    echo "🎉 GitHub仓库设置完成！"
    echo "🔗 仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "📋 后续操作:"
    echo "1. 查看仓库: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo "2. 推送更新: git push origin master"
    echo "3. 拉取更新: git pull origin master"
    echo "4. 创建分支: git checkout -b feature-name"
    echo "5. 推送分支: git push origin feature-name"
    
    # 恢复原始远程URL（不包含令牌）
    git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo ""
    echo "🔒 安全提醒: 令牌已从远程URL中移除"
    
else
    echo "❌ 代码推送失败！"
    echo ""
    echo "可能的原因:"
    echo "1. 令牌权限不足"
    echo "2. 网络连接问题"
    echo "3. 仓库访问权限问题"
    
    # 恢复原始远程URL
    git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    exit 1
fi

echo ""
echo "📖 更多帮助:"
echo "   GitHub仓库: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "   GitHub令牌设置: https://github.com/settings/tokens"
echo "   Git命令参考: https://git-scm.com/docs"
