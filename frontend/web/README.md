# Smart Bill Web - Vue 3 前端应用

符合苹果设计风格的智能账单识别和管理 Web 应用。

## 技术栈

- **框架**: Vue 3 + TypeScript + Vite
- **样式**: Tailwind CSS（深色主题）
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **路由**: Vue Router
- **日期处理**: date-fns
- **图标**: lucide-vue-next

## 快速开始

### 1. 安装依赖

```bash
cd frontend/web
npm install
```

### 2. 启动开发服务器

```bash
# 连接本地后端（http://localhost:8000）
npm run dev

# 连接远程生产后端（读取 .env.remote 中的 VITE_API_TARGET）
npm run dev:remote
```

访问 http://localhost:5173

### 3. 构建生产版本

```bash
# 本地/默认构建
npm run build

# 构建后预览
npm run preview
```

输出文件在 `dist/` 目录

### 4. 环境变量

| 文件 | 用途 |
|---|---|
| `.env.example` | 字段说明模板，可安全提交 |
| `.env.local` | 本地开发环境（`npm run dev`），需自行创建 |
| `.env.remote` | 远程后端地址（`npm run dev:remote`），已配置生产服务器 |

关键变量：
- `VITE_API_BASE_URL`：API 基础路径，默认 `/api/v1`
- `VITE_API_TARGET`：Vite 代理目标，仅 `.env.remote` 中配置

## 项目结构

```
src/
├── api/               # 后端 API 调用服务
│   ├── client.ts      # Axios 实例（含 JWT 拦截器）
│   ├── auth.ts        # 认证 API（登录/获取用户/周期设置）
│   ├── bills.ts       # 账单 API（上传/创建/批量/查询/编辑/删除）
│   ├── categories.ts  # 分类 API（CRUD）
│   └── users.ts       # 用户管理 API（列表/创建/改名/重置密码）
├── stores/            # Pinia 状态管理
│   ├── auth.ts        # 用户认证状态（token/userId/cycleStartDay）
│   ├── bills.ts       # 账单列表状态
│   ├── categories.ts  # 分类状态
│   └── ui.ts          # UI 状态（Toast / Dialog）
├── components/        # Vue 组件
│   ├── bills/         # 账单相关组件
│   │   ├── BillCard.vue         # 账单卡片（支出/收入色差展示）
│   │   ├── BillEditModal.vue    # 编辑弹窗（含动效）
│   │   ├── BillFilters.vue      # 筛选栏（日期/分类/商户搜索）
│   │   └── BillUploadModal.vue  # 图片上传弹窗（并发上传/骨架占位）
│   └── common/        # 通用组件
│       ├── Toast.vue            # 全局通知
│       └── ConfirmDialog.vue    # 确认对话框（含动效）
├── pages/             # 页面视图
│   ├── DashboardPage.vue    # 账单列表（周期切换/收支统计）
│   ├── LoginPage.vue        # 登录页
│   ├── CategoriesPage.vue   # 分类管理
│   ├── SettingsPage.vue     # 设置页（月度周期起始日）
│   ├── UserPage.vue         # 用户信息（修改密码/Excel 导入导出）
│   ├── UsersAdminPage.vue   # 用户管理（仅 admin）
│   └── ForceChangePasswordPage.vue  # 强制改密页（首次登录/重置密码后）
├── router/            # 路由配置（含认证守卫）
├── types/             # TypeScript 类型定义
│   └── bill.ts        # 账单、分类 TS 类型
├── utils/             # 工具函数
│   ├── cycle.ts       # 月度周期日期计算（getCycleDates）
│   ├── excel.ts       # Excel 导入/导出工具（downloadTemplate/exportBills/parseBills）
│   └── useDevice.ts   # 设备检测工具（isMobile/isNarrow）
└── styles/            # 全局样式
    └── main.css       # Tailwind 指令 + 自定义组件类
```

## 核心功能

### 1. 账单列表 & 统计
- 当前周期支出/收入金额汇总（顶部统计栏）
- 按「本期 / 上期」一键切换，支持自定义周期（SettingsPage）
- 按日期区间、分类、商户名称筛选
- 响应式卡片布局，支出/收入颜色区分

### 2. 图片上传识别
- 拖拽或点击上传，支持多张并发识别（调用 Qwen VL）
- 上传过程中显示骨架占位卡（BillUploadModal）
- 文件类型和大小验证

### 3. 手动创建账单
- 无需上传图片，直接填写账单信息创建
- 在 BillUploadModal 内切换「手动录入」模式

### 4. 账单管理
- 编辑账单信息（金额、商户、分类、日期、备注）
- 删除账单（需二次确认）
- 乐观更新（编辑/删除即时反映，失败时回滚）

### 5. 分类管理
- 分类 CRUD（后端 API 驱动，非硬编码）
- 每个分类含名称、图标、颜色

### 6. 用户设置
- 月度账单周期起始日（1–28），保存至后端
- 修改登录密码

### 7. 认证
- JWT token 登录，存储于 `localStorage`
- 路由守卫拦截未登录访问，自动跳转到 `/login`
- 首次登录或被重置密码后，自动强制跳转到 `/force-change-password`

### 8. 用户管理（仅 admin）
- 管理员可新增用户、修改用户名、重置密码
- 新用户默认 `must_change_password=true`，首次登录强制改密
- admin 不能修改自己的用户名

### 9. 批量导入 / 导出
- `UserPage.vue` 提供 Excel 模板下载、模板导入、全量导出
- 导入校验：金额非雰、商户名不空、日期格式 `YYYY-MM-DD`、分类名称匹配已有分类

## 设计系统

### 颜色方案（深色主题）
- **背景**: `#0F172A`（深黑）
- **Surface**: `#1E293B`（表面）
- **Primary**: `#F59E0B`（金色）
- **Success**: 绿色（收入金额）
- **Text**: `#F8FAFC`（白色）

### 自定义 CSS 组件类（`main.css`）
常用组件类：`.card`、`.card-hover`、`.btn`、`.btn-primary`、`.btn-sm`、`.input`、`.modal-overlay`、`.modal-content` 等

### 响应式断点
- **移动端** `< 1024px`：底部导航栏
- **桌面端** `≥ 1024px`：左侧边栏

## API 集成

### 代理配置

`vite.config.ts` 通过 `VITE_API_TARGET` 环境变量动态设置代理目标：

```typescript
const apiTarget = env.VITE_API_TARGET || 'http://localhost:8000'
// proxy: '/api' → apiTarget
```

### 认证机制

登录后将 JWT token 存入 `localStorage`，`client.ts` 的请求拦截器自动注入：

```typescript
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
```

## 开发指南

### 添加新功能

1. **定义类型** (`src/types/`)
2. **创建 API 服务** (`src/api/`)
3. **设计 Pinia store** (`src/stores/`)
4. **构建 Vue 组件** (`src/components/`)
5. **集成到页面** (`src/pages/`)

### 组件命名规范

- 文件名: PascalCase（`BillCard.vue`）
- 变量/方法: camelCase
- 常量: `UPPER_SNAKE_CASE`

### 样式规范

优先使用 `main.css` 中定义的组件类（`.card`、`.btn-primary` 等），其次使用 Tailwind 工具类，避免内联 `style`。

## 性能优化

- ✓ 代码分割（自动）
- ✓ Gzip 压缩（由 Nginx 处理）
- ✓ 静态资源长效缓存（Nginx `Cache-Control: immutable`）
- ✓ Tree shaking
- ✓ TypeScript 类型检查（构建前 `vue-tsc`）

## 浏览器兼容性

- Chrome / Edge（最新）
- Firefox（最新）
- Safari 15+（iOS / macOS）

## 常见问题

### Q: 如何修改主题色？
A: 编辑 `tailwind.config.ts` 中的 `colors` 配置，同步更新 `main.css` 中的 CSS 变量

### Q: 如何连接远程后端调试？
A: 编辑 `frontend/web/.env.remote` 中的 `VITE_API_TARGET`，然后 `npm run dev:remote`

### Q: 构建产物如何部署？
A: 运行根目录的 `./scripts/deploy_frontend.sh`，脚本会自动 `npm run build`、rsync 同步到服务器、重建 Nginx 容器

## 后续计划

- [ ] 账单统计分析与趋势图表
- [ ] 报表导出（PDF/Excel）
- [ ] PWA 离线支持

## 许可证

MIT
