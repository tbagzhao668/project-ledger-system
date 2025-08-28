# 工程项目流水账管理系统 - 前端

## 项目概述

这是一个基于 Vue 3 + Element Plus 的工程项目流水账管理系统前端，采用响应式设计，支持所有设备（桌面、平板、手机）。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - Vue 3 的组件库
- **Vue Router 4** - 官方路由管理器
- **Pinia** - Vue 的状态管理库
- **Vite** - 下一代前端构建工具

## 功能特性

### 🎯 响应式侧边导航

- **多级菜单支持**：支持主菜单和子菜单的层级结构
- **自适应布局**：根据屏幕尺寸自动调整导航显示方式
- **移动端优化**：在小屏幕设备上提供汉堡菜单和遮罩层
- **触摸友好**：针对触摸设备优化的交互体验

### 📱 设备适配

- **桌面端**：完整侧边栏，支持折叠/展开
- **平板端**：适中宽度的侧边栏，优化触摸操作
- **手机端**：全屏遮罩式侧边栏，手势友好

### 🎨 界面设计

- **深色主题**：专业的深色侧边栏设计
- **图标系统**：使用 Element Plus 图标库
- **状态管理**：活跃菜单项高亮显示
- **动画效果**：平滑的过渡动画

## 菜单结构

```
📊 仪表盘
📁 项目管理
  ├── 项目列表
  └── 新建项目
💰 财务管理
  ├── 财务记录
  ├── 分类管理
  └── 财务统计
📋 供应商管理
👥 用户管理
⚙️ 系统设置
```

## 响应式断点

| 设备类型 | 屏幕宽度 | 侧边栏行为 |
|---------|----------|-----------|
| 大屏幕 | ≥1440px | 260px 宽度，完整功能 |
| 桌面端 | 1024px-1439px | 240px 宽度，标准功能 |
| 平板端 | 769px-1023px | 200px 宽度，触摸优化 |
| 手机端 | ≤768px | 全屏遮罩，手势操作 |

## 使用方法

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产版本

```bash
npm run preview
```

## 项目结构

```
src/
├── components/          # 公共组件
├── layouts/            # 布局组件
│   └── MainLayout.vue  # 主布局（包含侧边导航）
├── views/              # 页面组件
│   ├── Dashboard.vue   # 仪表盘
│   ├── Projects.vue    # 项目管理
│   ├── Transactions.vue # 财务记录
│   ├── Categories.vue  # 分类管理
│   ├── Reports.vue     # 财务统计
│   ├── Suppliers.vue   # 供应商管理
│   ├── Users.vue       # 用户管理
│   └── Settings.vue    # 系统设置
├── router/             # 路由配置
├── stores/             # 状态管理
└── utils/              # 工具函数
```

## 侧边导航组件

### MainLayout.vue

主要的布局组件，包含：

- **响应式侧边栏**：根据设备类型自动调整
- **顶部导航栏**：面包屑、通知、用户菜单
- **移动端适配**：汉堡菜单、遮罩层
- **路由集成**：自动高亮当前页面

### 关键特性

1. **设备检测**：自动检测屏幕尺寸并调整布局
2. **触摸优化**：移动端友好的交互设计
3. **性能优化**：使用 CSS 变换而非改变布局属性
4. **无障碍支持**：支持键盘导航和屏幕阅读器

## 自定义配置

### 修改菜单项

在 `MainLayout.vue` 中修改 `el-menu` 部分：

```vue
<el-menu-item index="/your-route">
  <el-icon><YourIcon /></el-icon>
  <template #title>菜单名称</template>
</el-menu-item>
```

### 调整响应式断点

在 CSS 中修改媒体查询断点：

```css
@media (max-width: 768px) {
  /* 手机端样式 */
}

@media (min-width: 769px) and (max-width: 1024px) {
  /* 平板端样式 */
}
```

### 修改主题颜色

在 CSS 变量中调整颜色：

```css
:root {
  --sidebar-bg: #304156;
  --sidebar-active: #409eff;
  --sidebar-text: #bfcbd9;
}
```

## 浏览器支持

- Chrome ≥ 88
- Firefox ≥ 85
- Safari ≥ 14
- Edge ≥ 88

## 开发指南

### 添加新页面

1. 在 `src/views/` 创建新的 Vue 组件
2. 在 `src/router/index.js` 添加路由配置
3. 在 `MainLayout.vue` 中添加对应的菜单项

### 样式规范

- 使用 CSS 变量管理主题色彩
- 采用 BEM 命名规范
- 优先使用 Flexbox 和 Grid 布局
- 确保所有交互元素有足够大的触摸目标

### 性能优化

- 使用 Vue 3 的 Composition API
- 合理使用 `v-show` 和 `v-if`
- 避免在模板中使用复杂计算
- 使用 `v-memo` 优化列表渲染

## 部署说明

### 构建

```bash
npm run build
```

### 部署到服务器

将 `dist` 目录的内容上传到 Web 服务器，确保配置了正确的路由重写规则。

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 常见问题

### Q: 侧边栏在移动端不显示？
A: 检查是否正确设置了 `isMobile` 状态和相关的 CSS 类。

### Q: 菜单项点击后没有高亮？
A: 确保路由配置正确，并且 `activeMenu` 计算属性返回正确的路径。

### Q: 在平板设备上显示异常？
A: 检查媒体查询断点设置，确保覆盖了所有设备尺寸。

## 更新日志

### v1.0.0 (2024-01-01)
- ✨ 实现响应式侧边导航
- ✨ 支持多级菜单结构
- ✨ 完整的移动端适配
- ✨ 深色主题设计
- ✨ 触摸友好的交互体验

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。
