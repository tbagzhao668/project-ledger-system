#!/bin/bash

# 🚀 GitHub仓库设置脚本
# 使用方法: 修改下面的变量，然后运行此脚本

echo "🚀 开始设置GitHub远程仓库..."

# ===== 请修改以下变量 =====
GITHUB_USERNAME="tbagzhao668"
REPO_NAME="project-ledger-system"  # 或者您想要的仓库名
# ===============================

# 检查变量是否已设置
if [ "$GITHUB_USERNAME" = "您的GitHub用户名" ]; then
    echo "❌ 请先修改脚本中的 GITHUB_USERNAME 变量"
    echo "   编辑 setup_github_repo.sh 文件，将 '您的GitHub用户名' 替换为实际的GitHub用户名"
    exit 1
fi

echo "📋 配置信息:"
echo "   GitHub用户名: $GITHUB_USERNAME"
echo "   仓库名称: $REPO_NAME"
echo ""

# 选择连接方式
echo "🔗 选择连接方式:"
echo "1) HTTPS (推荐，简单易用)"
echo "2) SSH (需要配置SSH密钥)"
read -p "请选择 (1 或 2): " choice

case $choice in
    1)
        REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        echo "✅ 使用HTTPS连接: $REMOTE_URL"
        ;;
    2)
        REMOTE_URL="git@github.com:$GITHUB_USERNAME/$REPO_NAME.git"
        echo "✅ 使用SSH连接: $REMOTE_URL"
        ;;
    *)
        echo "❌ 无效选择，使用HTTPS"
        REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        ;;
esac

# 添加远程仓库
echo -e "\n🔗 添加远程仓库..."
git remote add origin "$REMOTE_URL"

if [ $? -eq 0 ]; then
    echo "✅ 远程仓库添加成功！"
else
    echo "❌ 远程仓库添加失败！"
    echo "可能的原因:"
    echo "1. 仓库已存在"
    echo "2. 网络连接问题"
    echo "3. 权限问题"
    exit 1
fi

# 验证远程仓库
echo -e "\n🔍 验证远程仓库..."
git remote -v

# 推送代码到GitHub
echo -e "\n📤 推送代码到GitHub..."

# 首先尝试推送主分支
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
else
    echo "❌ 代码推送失败！"
    echo ""
    echo "可能的原因:"
    echo "1. GitHub仓库不存在，需要先在GitHub上创建"
    echo "2. 网络连接问题"
    echo "3. 权限问题"
    echo ""
    echo "💡 解决方案:"
    echo "1. 访问 https://github.com/new 创建新仓库"
    echo "2. 仓库名: $REPO_NAME"
    echo "3. 不要初始化README、.gitignore或license"
    echo "4. 创建后重新运行此脚本"
fi

echo ""
echo "📖 更多帮助:"
echo "   GitHub仓库创建: https://github.com/new"
echo "   Git命令参考: https://git-scm.com/docs"
