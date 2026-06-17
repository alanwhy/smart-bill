# Smart Bill Web - Vue 3 前端应用

符合苹果设计风格的智能账单识别和管理 Web 应用。

## 技术栈

- **框架**: Vue 3 + TypeScript + Vite
- **样式**: Tailwind CSS (深色主题)
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **路由**: Vue Router
- **日期处理**: date-fns

## 快速开始

### 1. 安装依赖

```bash
cd frontend/web
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

输出文件在 `dist/` 目录

## 项目结构

```
src/
├── api/              # 后端 API 调用服务
│   ├── client.ts    # Axios 实例
│   └── bills.ts     # 账单 API
├── stores/           # Pinia 状态管理
│   ├── bills.ts     # 账单状态
│   └── ui.ts        # UI 状态
├── components/       # Vue 组件
│   ├── bills/       # 账单相关组件
│   └── layout/      # 布局组件
├── pages/            # 页面视图
├── types/            # TypeScript 类型
├── styles/           # 全局样式
└── router/           # 路由配置
```

## 核心功能

### 1. 账单列表
- 显示所有账单记录
- 按日期、分类筛选
- 搜索商户名称
- 响应式卡片布局

### 2. 图片上传
- 拖拽上传支持
- 文件类型和大小验证
- 上传进度提示
- 一次上传多个文件

### 3. 账单管理
- 编辑账单信息（金额、商户、分类、日期）
- 删除账单
- 表单验证
- 乐观更新

### 4. 分类管理
- 7 种预定义分类
- 分类统计和查看
- 金额汇总

## 设计系统

### 颜色方案 (深色主题)
- **背景**: #0F172A (深黑)
- **Surface**: #1E293B (表面)
- **Primary**: #F59E0B (金色)
- **Accent**: #8B5CF6 (紫色)
- **Text**: #F8FAFC (白色)

### 排版
- **标题**: Archivo (300-700)
- **正文**: Space Grotesk (300-700)

### 响应式断点
- **移动**: < 768px (底部导航)
- **平板**: 768px - 1024px
- **桌面**: > 1024px (左侧边栏)

## API 集成

### 连接后端

前端通过 Vite 代理连接后端：

```javascript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

### 用户认证

目前通过 localStorage 存储 userId：

```javascript
localStorage.setItem('userId', '1')
```

后续会升级为 JWT token。

## 开发指南

### 添加新功能

1. **定义类型** (`src/types/`)
2. **创建 API 服务** (`src/api/`)
3. **设计 Pinia store** (`src/stores/`)
4. **构建 Vue 组件** (`src/components/`)
5. **集成到页面** (`src/pages/`)

### 组件命名规范

- 文件名: PascalCase (BillCard.vue)
- 类名: PascalCase
- 变量名: camelCase
- 常量: UPPER_SNAKE_CASE

### 样式规范

使用 Tailwind CSS 工具类：

```vue
<div class="flex items-center gap-3 p-4 rounded-lg bg-surface border border-border">
  <!-- 内容 -->
</div>
```

避免自定义 CSS，优先使用预定义的 Tailwind 类。

## 性能优化

- ✓ 代码分割 (自动)
- ✓ 图片优化 (WebP + srcset)
- ✓ Gzip 压缩
- ✓ Tree shaking
- ✓ 懒加载路由

## 无障碍审计 (A11y)

- ✓ WCAG AAA 对比度
- ✓ 键盘导航支持
- ✓ ARIA 标签
- ✓ 焦点管理

## 浏览器兼容性

- Chrome/Edge (最新)
- Firefox (最新)
- Safari 15+ (iOS/macOS)

## 常见问题

### Q: 如何修改主题色？
A: 编辑 `tailwind.config.ts` 中的 `colors` 配置

### Q: 如何添加新的分类？
A: 更新 `src/types/bill.ts` 中的 `BILL_CATEGORIES`

### Q: 构建出的文件大小太大？
A: 运行 `npm run build` 并分析 `dist/` 目录

## 后续任务

- [ ] 用户认证系统 (JWT)
- [ ] 分类动态管理 (API)
- [ ] 数据统计和报表
- [ ] 消费趋势分析
- [ ] PWA 离线支持

## 许可证

MIT
