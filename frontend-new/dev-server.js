import express from 'express'
import { createServer as createViteServer } from 'vite'
import path from 'path'
import { fileURLToPath } from 'url'

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
    const __filename = fileURLToPath(import.meta.url)
    const __dirname = path.dirname(__filename)
    res.sendFile(path.resolve(__dirname, 'index.html'))
  })

  app.listen(3000, () => {
    console.log('🚀 自定义开发服务器运行在 http://localhost:3000')
    console.log('📱 支持SPA路由，所有路径都会正确加载')
    console.log('🔐 根路径 / 将根据认证状态重定向')
  })
}

createServer().catch(console.error)
