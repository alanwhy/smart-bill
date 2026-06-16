# API 文档

## 基础 URL
```
http://localhost:8000/api/v1
```

## 账单 API

### 上传并识别账单
```
POST /bills/upload
Content-Type: multipart/form-data

Parameters:
- files: 账单图片文件（JPG/PNG）
- user_id: 用户 ID（整数）

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "value": 50.0,
      "name": "麦当劳",
      "date": "2026-06-16 10:00:00",
      "category": "餐饮"
    }
  ]
}
```

### 查询账单列表
```
GET /bills?user_id=1&start_date=2026-06-01&end_date=2026-06-30&category=餐饮

Parameters:
- user_id: 用户 ID（必需）
- start_date: 开始日期（可选，YYYY-MM-DD）
- end_date: 结束日期（可选，YYYY-MM-DD）
- category: 分类（可选）

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "value": 50.0,
      "name": "麦当劳",
      "date": "2026-06-16 10:00:00",
      "category": "餐饮",
      "created_at": "2026-06-16T10:00:00"
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
  "value": 55.0,
  "name": "麦当劳（修改）",
  "category": "餐饮"
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

## 分类 API（后续实现）

### 列出分类
```
GET /categories

Response:
{
  "code": 0,
  "msg": "success",
  "data": [
    {"id": 1, "name": "餐饮"},
    {"id": 2, "name": "交通"}
  ]
}
```

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
- 404: 资源不存在
- 500: 服务器错误
