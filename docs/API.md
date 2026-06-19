# API 文档

## 基础 URL
```
http://localhost:8000/api/v1
```

## 认证 API

### 用户登录
```
POST /auth/login
Content-Type: application/json

Body:
{
  "username": "admin",
  "password": "your_password"
}

Response:
{
  "code": 0,
  "msg": "success",
  "data": {
    "token": "eyJ...",
    "user_id": 1,
    "username": "admin",
    "role": "admin",
    "must_change_password": false
  }
}

# 若 must_change_password=true，前端应强制跳转到 /force-change-password 页面
```

### 获取当前用户
```
GET /auth/me
Authorization: Bearer <token>

Response:
{
  "code": 0,
  "msg": "success",
  "data": {
    "user_id": 1,
    "username": "admin"
  }
}
```

### 修改密码
```
POST /auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "old_password": "old_pw",
  "new_password": "new_pw"
}

Response:
{
  "code": 0,
  "msg": "密码修改成功"
}
```

### 获取月度账单周期设置
```
GET /auth/cycle
Authorization: Bearer <token>

Response:
{
  "code": 0,
  "msg": "success",
  "data": {
    "cycle_start_day": 1
  }
}
```

### 更新月度账单周期设置
```
PUT /auth/cycle
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "cycle_start_day": 15
}

# cycle_start_day: 1-28，代表每月几号开始新的账单周期
# 例如：15 表示每月 15 日到次月 14 日为一个周期

Response:
{
  "code": 0,
  "msg": "success",
  "data": {
    "cycle_start_day": 15
  }
}
```

## 账单 API

### 手动创建账单
```
POST /bills
Content-Type: application/json

Body:
{
  "user_id": 1,
  "value": -50.0,
  "merchant_name": "麦当劳",
  "transaction_date": "2026-06-18T12:00:00",
  "category_id": 1,
  "description": "午饭"
}

# value 约定：负数=支出，正数=收入

Response:
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 10,
    "user_id": 1,
    "value": -50.0,
    "merchant_name": "麦当劳",
    "transaction_date": "2026-06-18T12:00:00",
    "category_id": 1,
    "category": {"id": 1, "name": "餐饮", "icon": "🍽️", "color": "#F97316"},
    "description": "午饭",
    "created_at": "2026-06-18T12:00:00",
    "updated_at": "2026-06-18T12:00:00"
  }
}
```

### 上传并识别账单（并发处理）
```
POST /bills/upload
Content-Type: multipart/form-data

Parameters:
- files: 账单图片文件（JPG/PNG，支持多张并发）
- user_id: 用户 ID（整数）

# 多张图片会并发调用 Qwen API，全部完成后统一返回

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": 10,
      "user_id": 1,
      "value": -50.0,
      "merchant_name": "麦当劳",
      "transaction_date": "2026-06-18 10:00:00",
      "category_id": 1,
      "category": {"id": 1, "name": "餐饮", "icon": "🍽️", "color": "#F97316"},
      "description": null,
      "created_at": "2026-06-18T10:00:00",
      "updated_at": "2026-06-18T10:00:00"
    }
  ]
}
```

### 查询账单列表
```
GET /bills?user_id=1&start_date=2026-06-01&end_date=2026-06-30&category_id=1&merchant_name=麦当劳

Parameters:
- user_id: 用户 ID（必需）
- start_date: 开始日期（可选，YYYY-MM-DD）
- end_date: 结束日期（可选，YYYY-MM-DD）
- category_id: 分类 ID（可选）
- merchant_name: 商户名模糊搜索（可选）

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "value": -50.0,
      "merchant_name": "麦当劳",
      "transaction_date": "2026-06-16 10:00:00",
      "category_id": 1,
      "category": {"id": 1, "name": "餐饮", "icon": "🍽️", "color": "#F97316"},
      "description": "工作午餐",
      "created_at": "2026-06-16T10:00:00",
      "updated_at": "2026-06-16T10:00:00"
    }
  ]
}
```

### 修改账单
```
PUT /bills/{bill_id}
Content-Type: application/json

Body:
{
  "value": -55.0,
  "merchant_name": "麦当劳（修改）",
  "category_id": 1,
  "description": "备注信息"
}

Response:
{
  "code": 0,
  "msg": "success",
  "data": { ... }
}
```

### 删除账单
```
DELETE /bills/{bill_id}

Response:
{
  "code": 0,
  "msg": "success"
}
```

### 批量导入账单
```
POST /bills/batch
Content-Type: application/json

Body:
{
  "user_id": 1,
  "bills": [
    {
      "value": -50.0,
      "merchant_name": "麦当劳",
      "transaction_date": "2026-06-18T12:00:00",
      "category_id": 1,
      "description": "午饭"
    },
    { ... }
  ]
}

# 事务性写入：所有账单成功才提交，任一失败则全部回滚
# category_id 须为已有分类 ID

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    { ...BillRecordInDB },
    ...
  ]
}
```

## 分类 API

### 创建分类
```
POST /categories
Content-Type: application/json

Body:
{
  "name": "午餐",
  "icon": "🍱",
  "color": "#F97316",
  "sort_order": 1,
  "parent_id": 1   # 可选，null 或省略表示创建为根分类
}

Response:
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 9,
    "name": "午餐",
    "icon": "🍱",
    "color": "#F97316",
    "sort_order": 1,
    "parent_id": 1,
    "created_at": "2026-06-19T14:00:00",
    "updated_at": "2026-06-19T14:00:00"
  }
}
```

### 列出所有分类（平铺）
```
GET /categories

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    {"id": 1, "name": "餐饮", "icon": "🍽️", "color": "#F59E0B", "sort_order": 1, "parent_id": null},
    {"id": 2, "name": "交通", "icon": "🚗", "color": "#10B981", "sort_order": 2, "parent_id": null},
    {"id": 9, "name": "午餐", "icon": "🍱", "color": "#F97316", "sort_order": 1, "parent_id": 1}
  ]
}
```

### 查询树形分类列表
```
GET /categories/tree

# 仅返回根分类，子分类递归嵌套在 children 数组中

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "name": "餐饮",
      "icon": "🍽️",
      "color": "#F59E0B",
      "sort_order": 1,
      "parent_id": null,
      "children": [
        {"id": 9, "name": "午餐", "icon": "🍱", "color": "#F97316", "sort_order": 1, "parent_id": 1, "children": []}
      ]
    },
    {
      "id": 2,
      "name": "交通",
      "icon": "🚗",
      "color": "#10B981",
      "sort_order": 2,
      "parent_id": null,
      "children": []
    }
  ]
}
```

### 查询单个分类
```
GET /categories/{category_id}

Response:
{
  "code": 0,
  "msg": "success",
  "data": {"id": 1, "name": "餐饮", ...}
}
```

### 更新分类
```
PUT /categories/{category_id}
Content-Type: application/json

Body:
{
  "name": "美食",
  "color": "#EF4444"
}

Response:
{
  "code": 0,
  "msg": "success",
  "data": { ... }
}
```

### 删除分类
```
DELETE /categories/{category_id}

Response:
{
  "code": 0,
  "msg": "success"
}
```

**删除安全限制**：
- 若分类下还有子分类，返回 400（`ON DELETE RESTRICT` 约束）
- 若分类下还有账单，返回 400："分类「x」下还有账单，请先修改这些账单的分类后再删除"
- 若只剩最后一个分类，返回 400："至少保留一个分类，无法删除"

## 错误处理

所有错误响应格式：
```json
{
  "code": 400,
  "msg": "错误描述",
  "detail": "详细错误信息"
}
```

常见错误码：
- 400: 请求参数错误
- 401: 未授权（token 无效或已过期）
- 403: 权限不足（需要 admin 角色）
- 404: 资源不存在
- 500: 服务器错误

## 用户管理 API（需 admin 角色）

> 以下接口均需携带 admin 用户的 Bearer token，普通用户访问返回 403。

### 获取用户列表
```
GET /users
Authorization: Bearer <admin-token>

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "must_change_password": false,
      "created_at": "2026-06-18T00:00:00"
    }
  ]
}
```

### 创建用户
```
POST /users
Authorization: Bearer <admin-token>
Content-Type: application/json

Body:
{
  "username": "newuser",
  "password": "initial_password",
  "role": "user"
}

# 新用户默认 must_change_password=true，首次登录强制改密

Response:
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 3,
    "username": "newuser",
    "role": "user",
    "must_change_password": true,
    "created_at": "2026-06-19T10:00:00"
  }
}
```

### 修改用户名
```
PUT /users/{user_id}/username
Authorization: Bearer <admin-token>
Content-Type: application/json

Body:
{
  "username": "new_username"
}

# admin 不能修改自己的用户名（返回 403）

Response:
{
  "code": 0,
  "msg": "success",
  "data": { ...AdminUserBrief }
}
```

### 重置用户密码
```
POST /users/{user_id}/reset-password
Authorization: Bearer <admin-token>

# 自动生成临时密码，设置 must_change_password=true

Response:
{
  "code": 0,
  "msg": "success",
  "data": {
    "temp_password": "TempXxxx"
  }
}
```
