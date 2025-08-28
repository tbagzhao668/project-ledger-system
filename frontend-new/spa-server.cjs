#!/usr/bin/env node

const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// 静态文件服务
app.use(express.static(path.join(__dirname, 'dist')));

// API代理
app.use('/api', (req, res) => {
  // 代理到后端服务器
  const target = `http://localhost:8000${req.url}`;
  console.log(`Proxying ${req.method} ${req.url} to ${target}`);
  
  // 简单的代理实现
  const http = require('http');
  const options = {
    hostname: 'localhost',
    port: 8000,
    path: req.url,
    method: req.method,
    headers: req.headers
  };
  
  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });
  
  proxyReq.on('error', (err) => {
    console.error('Proxy error:', err);
    res.status(500).send('Proxy error');
  });
  
  req.pipe(proxyReq);
});

// SPA路由支持 - 所有路由都返回index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 SPA服务器启动成功！`);
  console.log(`📍 本地访问: http://localhost:${PORT}`);
  console.log(`🌐 网络访问: http://192.168.4.130:${PORT}`);
  console.log(`📱 健康检查页面: http://192.168.4.130:${PORT}/monitoring/health`);
});
