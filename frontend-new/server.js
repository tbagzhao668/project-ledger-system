const express = require('express')
const { createServer: createViteServer } = require('vite')
const path = require('path')

async function createServer() {
  const app = express()

  // 创建Vite服务器
  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa'
  })

  // 使用Vite中间件
  app.use(vite.middlewares)

  // SPA路由支持 - 所有路由都返回index.html
  app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname, 'index.html'))
  })

  app.listen(3000, () => {
    console.log('🚀 开发服务器运行在 http://localhost:3000')
    console.log('📱 支持SPA路由，所有路径都会正确加载')
  })
}

createServer()
