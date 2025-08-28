# 工程项目流水账管理系统 - API接口规范文档

**版本**: v1.0  
**Base URL**: `https://api.project-ledger.com/api/v1`  
**认证方式**: JWT Bearer Token  
**内容格式**: JSON  

---

## 📋 API概览

### 认证机制
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Tenant-ID: <tenant_uuid>  (可选，从token中提取)
```

### 响应格式
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "code": 200,
  "timestamp": "2024-12-01T10:00:00Z"
}
```

### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": {
      "field": "email",
      "issue": "邮箱格式不正确"
    }
  },
  "timestamp": "2024-12-01T10:00:00Z"
}
```

### 分页响应格式
```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

---

## 🔐 认证API

### 1. 租户注册
```http
POST /auth/register
```

**请求体:**
```json
{
  "company_name": "示例工程公司",
  "admin_name": "张三",
  "admin_email": "admin@example.com",
  "admin_phone": "13800138000",
  "password": "SecurePass123!",
  "industry_type": "construction",
  "company_size": "small"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "tenant_id": "uuid",
    "verification_sent": true,
    "trial_expires": "2024-12-31T23:59:59Z"
  }
}
```

### 2. 用户登录
```http
POST /auth/login
```

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": true
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "张三",
      "role": "admin",
      "permissions": ["project:read", "transaction:write"],
      "tenant": {
        "id": "uuid",
        "name": "示例公司",
        "plan": "professional"
      }
    }
  }
}
```

### 3. 刷新令牌
```http
POST /auth/refresh
```

**请求体:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

### 4. 登出
```http
POST /auth/logout
```

**请求头:**
```
Authorization: Bearer <token>
```

### 5. 忘记密码
```http
POST /auth/forgot-password
```

**请求体:**
```json
{
  "email": "user@example.com"
}
```

### 6. 重置密码
```http
POST /auth/reset-password
```

**请求体:**
```json
{
  "token": "reset_token",
  "new_password": "NewPassword123!"
}
```

---

## 🏢 租户管理API

### 1. 获取租户信息
```http
GET /tenants/current
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "示例工程公司",
    "domain": "example",
    "plan_type": "professional",
    "subscription_end": "2024-12-31T23:59:59Z",
    "storage_used": 1073741824,
    "storage_limit": 21474836480,
    "api_calls_used": 1500,
    "api_calls_limit": 10000,
    "status": "active",
    "settings": {
      "currency": "CNY",
      "timezone": "Asia/Shanghai",
      "language": "zh-CN"
    },
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2. 更新租户信息
```http
PUT /tenants/current
```

**请求体:**
```json
{
  "name": "新公司名称",
  "settings": {
    "currency": "USD",
    "timezone": "UTC"
  }
}
```

### 3. 获取使用统计
```http
GET /tenants/usage-stats
```

**查询参数:**
- `period`: `daily|weekly|monthly` (默认: monthly)
- `start_date`: 开始日期 (ISO格式)
- `end_date`: 结束日期 (ISO格式)

**响应:**
```json
{
  "success": true,
  "data": {
    "storage": {
      "used": 1073741824,
      "limit": 21474836480,
      "percentage": 5.0
    },
    "api_calls": {
      "used": 1500,
      "limit": 10000,
      "percentage": 15.0
    },
    "projects": {
      "active": 25,
      "total": 50,
      "limit": 100
    },
    "users": {
      "active": 8,
      "total": 12,
      "limit": 50
    }
  }
}
```

---

## 👥 用户管理API

### 1. 获取用户列表
```http
GET /users
```

**查询参数:**
- `page`: 页码 (默认: 1)
- `size`: 每页数量 (默认: 20)
- `role`: 角色筛选
- `status`: 状态筛选 (`active|inactive`)
- `search`: 搜索关键词

**响应:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "role": "admin",
        "status": "active",
        "last_login": "2024-12-01T09:00:00Z",
        "created_at": "2024-01-01T00:00:00Z",
        "profile": {
          "name": "张三",
          "phone": "13800138000",
          "department": "财务部",
          "avatar_url": "/uploads/avatars/uuid.jpg"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 50,
      "pages": 3
    }
  }
}
```

### 2. 创建用户
```http
POST /users
```

**请求体:**
```json
{
  "username": "lisi",
  "email": "lisi@example.com",
  "password": "TempPass123!",
  "role": "finance",
  "profile": {
    "name": "李四",
    "phone": "13900139000",
    "department": "工程部"
  },
  "permissions": ["project:read", "transaction:write"],
  "send_invitation": true
}
```

### 3. 获取用户详情
```http
GET /users/{user_id}
```

### 4. 更新用户信息
```http
PUT /users/{user_id}
```

**请求体:**
```json
{
  "role": "project_manager",
  "status": "active",
  "profile": {
    "name": "李四",
    "department": "项目部"
  },
  "permissions": ["project:read", "project:write", "transaction:read"]
}
```

### 5. 删除用户
```http
DELETE /users/{user_id}
```

### 6. 邀请用户
```http
POST /users/invite
```

**请求体:**
```json
{
  "email": "newuser@example.com",
  "role": "viewer",
  "message": "欢迎加入我们的团队"
}
```

---

## 📁 项目管理API

### 1. 获取项目列表
```http
GET /projects
```

**查询参数:**
- `page`: 页码
- `size`: 每页数量
- `status`: 状态筛选 (`planning|active|paused|completed|cancelled`)
- `search`: 搜索关键词
- `sort`: 排序字段 (`created_at|name|budget|status`)
- `order`: 排序方向 (`asc|desc`)

**响应:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "万达广场装修项目",
        "project_code": "WD2024001",
        "description": "商业综合体装修改造",
        "project_type": "commercial",
        "budget": 5000000.00,
        "actual_cost": 2500000.00,
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "status": "active",
        "progress": 65,
        "client_info": {
          "name": "万达集团",
          "contact": "王经理",
          "phone": "13700137000"
        },
        "created_by": {
          "id": "uuid",
          "name": "张三"
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-12-01T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 25,
      "pages": 2
    }
  }
}
```

### 2. 创建项目
```http
POST /projects
```

**请求体:**
```json
{
  "name": "新项目名称",
  "project_code": "NP2024001",
  "description": "项目描述",
  "project_type": "residential",
  "budget": 3000000.00,
  "start_date": "2024-02-01",
  "end_date": "2024-08-31",
  "location": {
    "address": "北京市朝阳区xxx",
    "latitude": 39.9042,
    "longitude": 116.4074
  },
  "client_info": {
    "name": "客户名称",
    "contact": "联系人",
    "phone": "联系电话",
    "email": "client@example.com"
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "新项目名称",
    "project_code": "NP2024001",
    "status": "planning",
    "created_at": "2024-12-01T10:00:00Z"
  }
}
```

### 3. 获取项目详情
```http
GET /projects/{project_id}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "万达广场装修项目",
    "project_code": "WD2024001",
    "description": "商业综合体装修改造",
    "project_type": "commercial",
    "budget": 5000000.00,
    "actual_cost": 2500000.00,
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "actual_end_date": null,
    "status": "active",
    "progress": 65,
    "location": {
      "address": "北京市朝阳区万达广场",
      "latitude": 39.9042,
      "longitude": 116.4074
    },
    "client_info": {
      "name": "万达集团",
      "contact": "王经理",
      "phone": "13700137000",
      "email": "wang@wanda.com"
    },
    "contract_info": {
      "number": "HT2024001",
      "amount": 5000000.00,
      "signed_date": "2023-12-15"
    },
    "members": [
      {
        "user_id": "uuid",
        "name": "张三",
        "role": "manager",
        "joined_at": "2024-01-01T00:00:00Z"
      }
    ],
    "milestones": [
      {
        "id": "uuid",
        "name": "基础施工完成",
        "target_date": "2024-03-31",
        "status": "completed",
        "actual_date": "2024-03-28"
      }
    ],
    "financial_summary": {
      "total_income": 3000000.00,
      "total_expense": 2500000.00,
      "net_profit": 500000.00,
      "profit_margin": 16.67
    },
    "created_by": {
      "id": "uuid",
      "name": "张三"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-12-01T10:00:00Z"
  }
}
```

### 4. 更新项目
```http
PUT /projects/{project_id}
```

### 5. 删除项目
```http
DELETE /projects/{project_id}
```

### 6. 项目成员管理
```http
POST /projects/{project_id}/members
```

**请求体:**
```json
{
  "user_id": "uuid",
  "role": "finance",
  "permissions": ["transaction:read", "transaction:write"]
}
```

```http
DELETE /projects/{project_id}/members/{user_id}
```

### 7. 项目里程碑管理
```http
GET /projects/{project_id}/milestones
POST /projects/{project_id}/milestones
PUT /projects/{project_id}/milestones/{milestone_id}
DELETE /projects/{project_id}/milestones/{milestone_id}
```

---

## 💰 交易记录API

### 1. 获取交易记录
```http
GET /transactions
```

**查询参数:**
- `project_id`: 项目ID筛选
- `type`: 交易类型 (`income|expense`)
- `category_id`: 分类ID筛选
- `date_from`: 开始日期 (YYYY-MM-DD)
- `date_to`: 结束日期 (YYYY-MM-DD)
- `amount_min`: 最小金额
- `amount_max`: 最大金额
- `search`: 搜索关键词 (描述、供应商)
- `page`: 页码
- `size`: 每页数量
- `sort`: 排序字段 (`transaction_date|amount|created_at`)
- `order`: 排序方向 (`asc|desc`)

**响应:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "project": {
          "id": "uuid",
          "name": "万达广场装修项目",
          "project_code": "WD2024001"
        },
        "type": "expense",
        "category": {
          "id": "uuid",
          "name": "材料费",
          "icon": "material-icon",
          "color": "#409EFF"
        },
        "amount": 50000.00,
        "currency": "CNY",
        "description": "购买装修材料 - 地砖、油漆等",
        "tags": ["urgent", "material"],
        "supplier_info": {
          "name": "建材供应商",
          "contact": "李经理",
          "phone": "13600136000"
        },
        "payment_method": "bank_transfer",
        "receipts": [
          {
            "id": "uuid",
            "filename": "receipt_001.jpg",
            "url": "/uploads/receipts/uuid.jpg",
            "thumbnail_url": "/uploads/thumbnails/uuid.jpg"
          }
        ],
        "invoice_info": {
          "number": "12345678",
          "amount": 50000.00,
          "tax_amount": 6500.00,
          "verified": true
        },
        "location": {
          "latitude": 39.9042,
          "longitude": 116.4074,
          "address": "项目现场"
        },
        "transaction_date": "2024-12-01",
        "status": "confirmed",
        "approval_status": "approved",
        "approved_by": {
          "id": "uuid",
          "name": "张主管"
        },
        "approved_at": "2024-12-01T14:00:00Z",
        "created_by": {
          "id": "uuid",
          "name": "王财务"
        },
        "created_at": "2024-12-01T13:00:00Z",
        "updated_at": "2024-12-01T14:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 500,
      "pages": 25
    },
    "summary": {
      "total_income": 3000000.00,
      "total_expense": 2500000.00,
      "net_amount": 500000.00,
      "count": 500
    }
  }
}
```

### 2. 创建交易记录
```http
POST /transactions
```

**请求体:**
```json
{
  "project_id": "uuid",
  "type": "expense",
  "category_id": "uuid",
  "amount": 50000.00,
  "currency": "CNY",
  "description": "购买装修材料",
  "tags": ["material", "urgent"],
  "supplier_info": {
    "name": "建材供应商",
    "contact": "李经理",
    "phone": "13600136000",
    "tax_number": "91110000000000000X"
  },
  "payment_method": "bank_transfer",
  "transaction_date": "2024-12-01",
  "receipt_files": ["file_id_1", "file_id_2"],
  "invoice_info": {
    "number": "12345678",
    "amount": 50000.00,
    "tax_amount": 6500.00
  },
  "location": {
    "latitude": 39.9042,
    "longitude": 116.4074,
    "address": "项目现场"
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type": "expense",
    "amount": 50000.00,
    "status": "confirmed",
    "approval_status": "pending",
    "created_at": "2024-12-01T13:00:00Z"
  }
}
```

### 3. 获取交易详情
```http
GET /transactions/{transaction_id}
```

### 4. 更新交易记录
```http
PUT /transactions/{transaction_id}
```

### 5. 删除交易记录
```http
DELETE /transactions/{transaction_id}
```

### 6. 批量操作
```http
POST /transactions/batch
```

**请求体:**
```json
{
  "action": "approve",  // approve, reject, delete
  "transaction_ids": ["uuid1", "uuid2", "uuid3"],
  "note": "批量审批通过"
}
```

### 7. 批量导入
```http
POST /transactions/import
```

**请求体 (multipart/form-data):**
- `file`: Excel/CSV文件
- `project_id`: 项目ID
- `import_type`: 导入类型 (`excel|csv|bank_statement`)
- `bank_type`: 银行类型 (如果是银行对账单)

**响应:**
```json
{
  "success": true,
  "data": {
    "import_id": "uuid",
    "total_rows": 100,
    "valid_rows": 95,
    "invalid_rows": 5,
    "preview": [
      {
        "row": 1,
        "data": {
          "type": "expense",
          "amount": 1000.00,
          "description": "材料费"
        },
        "status": "valid"
      }
    ],
    "errors": [
      {
        "row": 2,
        "field": "amount",
        "message": "金额格式不正确"
      }
    ]
  }
}
```

### 8. 确认导入
```http
POST /transactions/import/{import_id}/confirm
```

---

## 📊 分类管理API

### 1. 获取分类列表
```http
GET /categories
```

**查询参数:**
- `type`: 分类类型 (`income|expense`)
- `parent_id`: 父分类ID (获取子分类)
- `include_stats`: 是否包含使用统计 (`true|false`)

**响应:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "材料费",
      "type": "expense",
      "parent_id": null,
      "icon": "material-icon",
      "color": "#409EFF",
      "is_system": false,
      "is_active": true,
      "sort_order": 1,
      "children": [
        {
          "id": "uuid",
          "name": "建筑材料",
          "parent_id": "parent_uuid",
          "usage_count": 45,
          "total_amount": 500000.00
        }
      ],
      "usage_stats": {
        "transaction_count": 120,
        "total_amount": 1500000.00,
        "last_used": "2024-12-01T10:00:00Z"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 2. 创建分类
```http
POST /categories
```

**请求体:**
```json
{
  "name": "设备费",
  "type": "expense",
  "parent_id": null,
  "icon": "equipment-icon",
  "color": "#67C23A",
  "sort_order": 5
}
```

### 3. 更新分类
```http
PUT /categories/{category_id}
```

### 4. 删除分类
```http
DELETE /categories/{category_id}
```

**注意**: 如果分类下有交易记录，需要先处理关联数据。

### 5. 批量排序
```http
POST /categories/reorder
```

**请求体:**
```json
{
  "categories": [
    {"id": "uuid1", "sort_order": 1},
    {"id": "uuid2", "sort_order": 2},
    {"id": "uuid3", "sort_order": 3}
  ]
}
```

---

## 📈 报表API

### 1. 项目汇总报表
```http
GET /reports/projects/{project_id}/summary
```

**查询参数:**
- `date_from`: 开始日期
- `date_to`: 结束日期
- `include_forecast`: 是否包含预测数据

**响应:**
```json
{
  "success": true,
  "data": {
    "project_info": {
      "id": "uuid",
      "name": "万达广场装修项目",
      "budget": 5000000.00,
      "progress": 65
    },
    "financial_summary": {
      "total_income": 3000000.00,
      "total_expense": 2500000.00,
      "net_profit": 500000.00,
      "profit_margin": 16.67,
      "budget_used": 50.00
    },
    "category_breakdown": {
      "income": [
        {
          "category": "工程款",
          "amount": 2500000.00,
          "percentage": 83.33,
          "count": 5
        }
      ],
      "expense": [
        {
          "category": "材料费",
          "amount": 1500000.00,
          "percentage": 60.00,
          "count": 45
        }
      ]
    },
    "monthly_trend": [
      {
        "month": "2024-01",
        "income": 500000.00,
        "expense": 300000.00,
        "net": 200000.00
      }
    ],
    "recent_transactions": [
      {
        "id": "uuid",
        "type": "expense",
        "amount": 50000.00,
        "description": "购买材料",
        "date": "2024-12-01"
      }
    ],
    "alerts": [
      {
        "type": "budget_warning",
        "message": "材料费预算即将超支",
        "severity": "warning"
      }
    ]
  }
}
```

### 2. 现金流报表
```http
GET /reports/projects/{project_id}/cashflow
```

**查询参数:**
- `period`: 周期 (`daily|weekly|monthly`)
- `date_from`: 开始日期
- `date_to`: 结束日期

**响应:**
```json
{
  "success": true,
  "data": {
    "cashflow_data": [
      {
        "period": "2024-01",
        "cash_in": 500000.00,
        "cash_out": 300000.00,
        "net_cashflow": 200000.00,
        "cumulative": 200000.00
      }
    ],
    "forecast": [
      {
        "period": "2024-02",
        "projected_in": 600000.00,
        "projected_out": 400000.00,
        "projected_net": 200000.00
      }
    ],
    "chart_data": {
      "type": "line",
      "categories": ["2024-01", "2024-02", "2024-03"],
      "series": [
        {
          "name": "现金流入",
          "data": [500000, 600000, 700000]
        },
        {
          "name": "现金流出",
          "data": [300000, 400000, 500000]
        }
      ]
    }
  }
}
```

### 3. 项目对比分析
```http
GET /reports/projects/comparison
```

**查询参数:**
- `project_ids`: 项目ID列表 (逗号分隔)
- `metrics`: 对比指标 (`profit|cost|efficiency`)
- `date_from`: 开始日期
- `date_to`: 结束日期

**响应:**
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "id": "uuid",
        "name": "项目A",
        "metrics": {
          "total_revenue": 5000000.00,
          "total_cost": 4000000.00,
          "profit_margin": 20.00,
          "roi": 25.00,
          "duration_days": 180,
          "cost_per_day": 22222.22
        }
      }
    ],
    "comparison_matrix": {
      "most_profitable": "项目A",
      "most_efficient": "项目B",
      "average_profit_margin": 18.5
    },
    "chart_data": {
      "type": "bar",
      "categories": ["项目A", "项目B", "项目C"],
      "series": [
        {
          "name": "利润率",
          "data": [20.0, 15.0, 22.0]
        }
      ]
    }
  }
}
```

### 4. 供应商分析报表
```http
GET /reports/suppliers
```

**查询参数:**
- `project_id`: 项目ID (可选)
- `date_from`: 开始日期
- `date_to`: 结束日期
- `top_n`: 返回Top N供应商 (默认: 10)

**响应:**
```json
{
  "success": true,
  "data": {
    "suppliers": [
      {
        "name": "建材供应商A",
        "total_amount": 500000.00,
        "transaction_count": 25,
        "average_amount": 20000.00,
        "payment_terms": "月结30天",
        "credit_rating": "A",
        "projects": ["项目A", "项目B"]
      }
    ],
    "summary": {
      "total_suppliers": 15,
      "total_amount": 2000000.00,
      "average_per_supplier": 133333.33
    },
    "recommendations": [
      {
        "type": "cost_optimization",
        "message": "建议与供应商A谈判更好的价格",
        "potential_savings": 50000.00
      }
    ]
  }
}
```

### 5. 自定义报表
```http
POST /reports/custom
```

**请求体:**
```json
{
  "name": "月度成本分析",
  "filters": {
    "project_ids": ["uuid1", "uuid2"],
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "categories": ["材料费", "人工费"]
  },
  "groupby": ["category", "month"],
  "metrics": ["sum", "count", "avg"],
  "chart_type": "bar"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "report_id": "uuid",
    "results": {
      "data": [
        {
          "category": "材料费",
          "month": "2024-01",
          "sum": 500000.00,
          "count": 25,
          "avg": 20000.00
        }
      ],
      "chart_data": {
        "type": "bar",
        "categories": ["2024-01", "2024-02"],
        "series": [
          {
            "name": "材料费",
            "data": [500000, 600000]
          }
        ]
      }
    },
    "created_at": "2024-12-01T10:00:00Z"
  }
}
```

### 6. 异步生成大型报表
```http
POST /reports/generate-async
```

**请求体:**
```json
{
  "report_type": "annual_summary",
  "project_ids": ["uuid1", "uuid2"],
  "year": 2024,
  "format": "pdf",
  "include_charts": true,
  "email_when_ready": true
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "estimated_time": 300,
    "status_url": "/reports/tasks/uuid/status"
  }
}
```

### 7. 查询异步任务状态
```http
GET /reports/tasks/{task_id}/status
```

**响应:**
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "status": "processing",
    "progress": 65,
    "message": "正在生成图表...",
    "estimated_remaining": 120,
    "result": null
  }
}
```

### 8. 下载报表
```http
GET /reports/download/{report_id}
```

**查询参数:**
- `format`: 格式 (`pdf|excel|csv`)

---

## 📁 文件管理API

### 1. 上传文件
```http
POST /files/upload
```

**请求体 (multipart/form-data):**
- `file`: 文件数据
- `category`: 文件分类 (`receipt|invoice|contract|avatar`)
- `entity_type`: 关联实体类型 (`transaction|project|user`)
- `entity_id`: 关联实体ID

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "filename": "receipt_001.jpg",
    "original_filename": "发票001.jpg",
    "file_size": 1048576,
    "mime_type": "image/jpeg",
    "url": "/uploads/receipts/uuid.jpg",
    "thumbnail_url": "/uploads/thumbnails/uuid.jpg",
    "file_hash": "sha256_hash",
    "created_at": "2024-12-01T10:00:00Z"
  }
}
```

### 2. 批量上传
```http
POST /files/upload-batch
```

### 3. 获取文件列表
```http
GET /files
```

**查询参数:**
- `entity_type`: 实体类型
- `entity_id`: 实体ID
- `category`: 文件分类
- `page`: 页码
- `size`: 每页数量

### 4. 获取文件详情
```http
GET /files/{file_id}
```

### 5. 删除文件
```http
DELETE /files/{file_id}
```

### 6. OCR识别
```http
POST /files/{file_id}/ocr
```

**请求体:**
```json
{
  "ocr_type": "invoice",  // invoice, receipt, id_card
  "auto_extract": true
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "file_id": "uuid",
    "ocr_result": {
      "invoice_code": "12345678",
      "invoice_number": "00000001",
      "amount": 50000.00,
      "tax_amount": 6500.00,
      "seller_name": "供应商名称",
      "invoice_date": "2024-12-01",
      "confidence": 0.95
    },
    "suggested_transaction": {
      "type": "expense",
      "amount": 50000.00,
      "description": "根据发票信息生成",
      "supplier_name": "供应商名称"
    }
  }
}
```

---

## 🔗 集成API

### 1. 支付集成

#### 微信支付流水同步
```http
POST /integrations/wechat/sync-payments
```

**请求体:**
```json
{
  "merchant_id": "1234567890",
  "start_date": "2024-12-01",
  "end_date": "2024-12-01",
  "auto_create_transactions": true,
  "default_project_id": "uuid"
}
```

#### 支付宝流水同步
```http
POST /integrations/alipay/sync-payments
```

### 2. 银行对账单集成

#### 导入银行对账单
```http
POST /integrations/bank/import-statement
```

**请求体 (multipart/form-data):**
- `file`: 对账单文件
- `bank_type`: 银行类型 (`icbc|ccb|abc|boc`)
- `account_number`: 银行账号
- `statement_period`: 对账单期间

**响应:**
```json
{
  "success": true,
  "data": {
    "import_id": "uuid",
    "total_records": 150,
    "matched_records": 120,
    "new_records": 25,
    "unmatched_records": 5,
    "preview": [
      {
        "date": "2024-12-01",
        "amount": 50000.00,
        "description": "工程款收入",
        "counterpart": "万达集团",
        "status": "matched",
        "matched_transaction_id": "uuid"
      }
    ]
  }
}
```

#### 确认银行对账
```http
POST /integrations/bank/confirm-import/{import_id}
```

### 3. 税务集成

#### 发票验真
```http
POST /integrations/tax/verify-invoice
```

**请求体:**
```json
{
  "invoice_code": "12345678",
  "invoice_number": "00000001",
  "invoice_date": "2024-12-01",
  "amount": 50000.00,
  "tax_number": "91110000000000000X"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "invoice_info": {
      "status": "正常",
      "seller_name": "供应商名称",
      "buyer_name": "购买方名称",
      "amount": 50000.00,
      "tax_amount": 6500.00
    },
    "verification_time": "2024-12-01T10:00:00Z"
  }
}
```

### 4. 通知服务

#### 发送邮件通知
```http
POST /integrations/notifications/email
```

**请求体:**
```json
{
  "to": ["user@example.com"],
  "cc": ["manager@example.com"],
  "subject": "月度财务报表",
  "template": "monthly_report",
  "variables": {
    "project_name": "万达广场项目",
    "month": "2024年11月"
  },
  "attachments": ["report_file_id"]
}
```

#### 发送短信通知
```http
POST /integrations/notifications/sms
```

**请求体:**
```json
{
  "phone": "13800138000",
  "template": "budget_alert",
  "variables": {
    "project_name": "万达广场项目",
    "budget_usage": "85%"
  }
}
```

---

## 🔧 系统管理API

### 1. 系统设置

#### 获取系统设置
```http
GET /system/settings
```

#### 更新系统设置
```http
PUT /system/settings
```

**请求体:**
```json
{
  "currency": "CNY",
  "timezone": "Asia/Shanghai",
  "language": "zh-CN",
  "date_format": "YYYY-MM-DD",
  "decimal_places": 2,
  "email_notifications": true,
  "sms_notifications": false
}
```

### 2. 审计日志

#### 获取审计日志
```http
GET /system/audit-logs
```

**查询参数:**
- `user_id`: 用户ID筛选
- `action`: 操作类型筛选
- `entity_type`: 实体类型筛选
- `date_from`: 开始日期
- `date_to`: 结束日期
- `page`: 页码
- `size`: 每页数量

**响应:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "user": {
          "id": "uuid",
          "name": "张三",
          "email": "zhangsan@example.com"
        },
        "action": "UPDATE",
        "entity_type": "transaction",
        "entity_id": "uuid",
        "old_values": {
          "amount": 40000.00
        },
        "new_values": {
          "amount": 50000.00
        },
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "created_at": "2024-12-01T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 1000,
      "pages": 50
    }
  }
}
```

### 3. 系统健康检查

#### 健康检查
```http
GET /health
```

**响应:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-12-01T10:00:00Z",
    "version": "1.0.0",
    "services": {
      "database": {
        "status": "healthy",
        "response_time": 5
      },
      "redis": {
        "status": "healthy",
        "response_time": 2
      },
      "storage": {
        "status": "healthy",
        "available_space": "85%"
      }
    },
    "metrics": {
      "active_users": 125,
      "total_tenants": 50,
      "api_calls_today": 15000
    }
  }
}
```

#### 系统指标
```http
GET /system/metrics
```

**响应:**
```json
{
  "success": true,
  "data": {
    "performance": {
      "avg_response_time": 245,
      "requests_per_second": 50,
      "error_rate": 0.02
    },
    "usage": {
      "active_tenants": 45,
      "active_users": 125,
      "storage_used": "15.5GB",
      "api_calls_today": 15000
    },
    "resources": {
      "cpu_usage": 35.5,
      "memory_usage": 68.2,
      "disk_usage": 42.8
    }
  }
}
```

---

## 📱 移动端API扩展

### 1. 快速录入
```http
POST /mobile/quick-entry
```

**请求体:**
```json
{
  "project_id": "uuid",
  "type": "expense",
  "amount": 500.00,
  "description": "午餐费",
  "category_name": "餐饮费",
  "location": {
    "latitude": 39.9042,
    "longitude": 116.4074
  },
  "photo_ids": ["uuid1"]
}
```

### 2. 语音转文字
```http
POST /mobile/speech-to-text
```

**请求体 (multipart/form-data):**
- `audio`: 音频文件
- `language`: 语言 (`zh-CN|en-US`)

### 3. 离线同步
```http
POST /mobile/sync
```

**请求体:**
```json
{
  "offline_data": [
    {
      "local_id": "local_001",
      "type": "transaction",
      "data": {
        "project_id": "uuid",
        "type": "expense",
        "amount": 100.00,
        "description": "出租车费"
      },
      "created_at": "2024-12-01T10:00:00Z"
    }
  ]
}
```

---

## 🚫 错误代码参考

### HTTP状态码
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `409`: 资源冲突
- `422`: 参数验证失败
- `429`: 请求频率限制
- `500`: 服务器内部错误

### 业务错误代码
```json
{
  "VALIDATION_ERROR": "参数验证失败",
  "UNAUTHORIZED": "认证失败",
  "FORBIDDEN": "权限不足",
  "RESOURCE_NOT_FOUND": "资源不存在",
  "DUPLICATE_RESOURCE": "资源已存在",
  "INSUFFICIENT_QUOTA": "配额不足",
  "PAYMENT_REQUIRED": "需要付费",
  "RATE_LIMIT_EXCEEDED": "请求频率超限",
  "FILE_TOO_LARGE": "文件过大",
  "INVALID_FILE_FORMAT": "文件格式不支持",
  "OCR_SERVICE_UNAVAILABLE": "OCR服务不可用",
  "BANK_API_ERROR": "银行接口错误",
  "TAX_API_ERROR": "税务接口错误"
}
```

---

## 📚 SDK和集成示例

### JavaScript SDK示例
```javascript
// 安装: npm install @project-ledger/js-sdk

import ProjectLedgerSDK from '@project-ledger/js-sdk';

const client = new ProjectLedgerSDK({
  baseURL: 'https://api.project-ledger.com/api/v1',
  apiKey: 'your-api-key'
});

// 创建交易记录
const transaction = await client.transactions.create({
  project_id: 'uuid',
  type: 'expense',
  amount: 1000.00,
  description: '购买材料'
});

// 获取项目报表
const report = await client.reports.getProjectSummary('project_id', {
  date_from: '2024-01-01',
  date_to: '2024-12-31'
});
```

### Python SDK示例
```python
# 安装: pip install project-ledger-sdk

from project_ledger import ProjectLedgerClient

client = ProjectLedgerClient(
    base_url='https://api.project-ledger.com/api/v1',
    api_key='your-api-key'
)

# 创建项目
project = client.projects.create(
    name='新项目',
    budget=5000000.00,
    start_date='2024-01-01'
)

# 批量导入交易
result = client.transactions.import_from_file(
    file_path='transactions.xlsx',
    project_id=project['id']
)
```

---

**文档版本**: v1.0  
**最后更新**: 2024年12月  
**API版本**: v1  
**支持**: api-support@project-ledger.com

**下一步**: 根据此接口规范开始后端API开发
