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
    "username": "admin"
  }
}
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

## 分类 API

### 创建分类
```
POST /categories
Content-Type: application/json

Body:
{
  "name": "旅行",
  "icon": "✈️",
  "color": "#3B82F6",
  "sort_order": 10
}

Response:
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 8,
    "name": "旅行",
    "icon": "✈️",
    "color": "#3B82F6",
    "sort_order": 10,
    "created_at": "2026-06-17T14:00:00"
  }
}
```

### 列出所有分类
```
GET /categories

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    {"id": 1, "name": "餐饮", "icon": "🍽️", "color": "#F59E0B", "sort_order": 1},
    {"id": 2, "name": "交通", "icon": "🚗", "color": "#10B981", "sort_order": 2}
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
- 404: 资源不存在
- 500: 服务器错误
