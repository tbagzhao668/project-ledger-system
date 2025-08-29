#!/bin/bash

# SSL证书生成脚本
# 用于生成自签名SSL证书

echo "=== SSL证书生成脚本 ==="

# 检查是否以root权限运行
if [[ $EUID -ne 0 ]]; then
   echo "❌ 此脚本需要root权限运行，请使用 sudo"
   exit 1
fi

# 创建SSL目录
SSL_DIR="/etc/nginx/ssl"
mkdir -p "$SSL_DIR"

# 设置证书信息
COUNTRY="CN"
STATE="Beijing"
CITY="Beijing"
ORGANIZATION="FinceProject"
ORGANIZATIONAL_UNIT="IT"
COMMON_NAME="localhost"

# 生成私钥和证书
echo "🔐 正在生成SSL证书..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/fince-project.key" \
    -out "$SSL_DIR/fince-project.crt" \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=$COMMON_NAME"

# 设置权限
chmod 600 "$SSL_DIR/fince-project.key"
chmod 644 "$SSL_DIR/fince-project.crt"

# 验证证书
echo "✅ SSL证书生成完成！"
echo "📁 证书位置: $SSL_DIR/fince-project.crt"
echo "🔑 私钥位置: $SSL_DIR/fince-project.key"
echo "📅 有效期: 365天"

# 显示证书信息
echo ""
echo "📋 证书信息:"
openssl x509 -in "$SSL_DIR/fince-project.crt" -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:)"

echo ""
echo "⚠️  注意：这是自签名证书，浏览器会显示安全警告"
echo "   在生产环境中，请使用受信任的CA机构颁发的证书"
