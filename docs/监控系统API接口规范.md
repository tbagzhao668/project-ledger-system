# 监控系统API接口规范

## 📋 文档信息
- **文档版本**: v1.0
- **创建日期**: 2025-08-27
- **文档状态**: 草稿
- **负责人**: 后端开发工程师
- **审核人**: 技术负责人

## 🎯 接口概述

### 接口基础信息
- **基础URL**: `/api/v1/admin`
- **认证方式**: JWT Token (Bearer)
- **权限要求**: 仅限 `super_admin` 角色
- **数据格式**: JSON
- **字符编码**: UTF-8

### 通用响应格式
```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "timestamp": "2025-08-27T10:00:00Z"
}
```

### 错误响应格式
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {},
  "timestamp": "2025-08-27T10:00:00Z"
}
```

### HTTP状态码
- `200`: 请求成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 🔍 监控相关接口

### 1. 系统健康检查

#### GET /admin/health
**描述**: 检查系统各服务的健康状态

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "message": "系统健康检查完成",
  "data": {
    "overall_status": "healthy",
    "services": [
      {
        "name": "database",
        "status": "healthy",
        "response_time": 15,
        "last_check": "2025-08-27T10:00:00Z",
        "details": {
          "connection_pool": "active",
          "active_connections": 5
        }
      },
      {
        "name": "api_service",
        "status": "healthy",
        "response_time": 5,
        "last_check": "2025-08-27T10:00:00Z",
        "details": {
          "uptime": "24h 30m",
          "memory_usage": "45%"
        }
      }
    ],
    "timestamp": "2025-08-27T10:00:00Z"
  }
}
```

**状态码说明**:
- `healthy`: 服务正常
- `warning`: 服务警告
- `error`: 服务异常
- `unknown`: 状态未知

### 2. 获取监控数据

#### GET /admin/monitoring
**描述**: 获取指定时间范围内的监控数据

**查询参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| service_name | string | 否 | - | 服务名称筛选 |
| hours | integer | 否 | 24 | 查询时间范围(小时) |
| status | string | 否 | - | 状态筛选 |

**响应示例**:
```json
{
  "success": true,
  "message": "获取监控数据成功",
  "data": {
    "monitoring_data": [
      {
        "id": "uuid",
        "service_name": "database",
        "status": "healthy",
        "response_time": 15,
        "error_message": null,
        "metadata": {
          "connection_count": 5,
          "query_count": 120
        },
        "created_at": "2025-08-27T10:00:00Z"
      }
    ],
    "summary": {
      "total_records": 100,
      "healthy_count": 95,
      "warning_count": 3,
      "error_count": 2,
      "avg_response_time": 18.5
    }
  }
}
```

### 3. 系统统计概览

#### GET /admin/statistics/overview
**描述**: 获取系统整体统计信息

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "message": "获取系统统计成功",
  "data": {
    "tenant_statistics": {
      "total_tenants": 15,
      "active_tenants": 12,
      "disabled_tenants": 3,
      "new_tenants_today": 2,
      "new_tenants_this_week": 5
    },
    "system_statistics": {
      "total_projects": 45,
      "total_transactions": 1234,
      "total_suppliers": 67,
      "system_uptime": "168h 30m"
    },
    "performance_statistics": {
      "avg_api_response_time": 120,
      "database_connection_usage": "65%",
      "memory_usage": "45%",
      "cpu_usage": "30%"
    },
    "last_updated": "2025-08-27T10:00:00Z"
  }
}
```

## 👥 租户管理接口

### 1. 获取租户列表

#### GET /admin/tenants
**描述**: 获取系统中所有租户的列表信息

**查询参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| size | integer | 否 | 20 | 每页数量 |
| status | string | 否 | - | 状态筛选(active/disabled) |
| search | string | 否 | - | 搜索关键词(名称/邮箱) |
| sort_by | string | 否 | created_at | 排序字段 |
| sort_order | string | 否 | desc | 排序方向(asc/desc) |

**响应示例**:
```json
{
  "success": true,
  "message": "获取租户列表成功",
  "data": {
    "tenants": [
      {
        "id": "uuid",
        "name": "测试租户",
        "email": "test@example.com",
        "status": "active",
        "created_at": "2025-08-19T10:00:00Z",
        "last_login_at": "2025-08-27T09:30:00Z",
        "statistics": {
          "project_count": 5,
          "transaction_count": 45,
          "supplier_count": 8
        }
      }
    ],
    "pagination": {
      "current_page": 1,
      "page_size": 20,
      "total_pages": 1,
      "total_records": 15
    }
  }
}
```

### 2. 重置租户密码

#### PUT /admin/tenants/{tenant_id}/reset-password
**描述**: 管理员重置指定租户的密码

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| tenant_id | string | 是 | 租户ID |

**请求体**: 无

**响应示例**:
```json
{
  "success": true,
  "message": "密码重置成功",
  "data": {
    "tenant_id": "uuid",
    "new_password": "TmpP@ss123",
    "password_expires_at": "2025-08-28T10:00:00Z",
    "reset_at": "2025-08-27T10:00:00Z",
    "reset_by": "admin_user_id"
  }
}
```

**注意事项**:
- 新密码为随机生成，符合安全要求
- 密码有效期24小时
- 重置后需要租户立即修改密码

### 3. 更新租户状态

#### PUT /admin/tenants/{tenant_id}/status
**描述**: 启用或禁用租户账户

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| tenant_id | string | 是 | 租户ID |

**请求体**:
```json
{
  "status": "disabled",
  "reason": "账户违规操作",
  "notes": "临时禁用，等待处理"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "租户状态更新成功",
  "data": {
    "tenant_id": "uuid",
    "old_status": "active",
    "new_status": "disabled",
    "status_changed_at": "2025-08-27T10:00:00Z",
    "changed_by": "admin_user_id",
    "reason": "账户违规操作"
  }
}
```

### 4. 获取租户详情

#### GET /admin/tenants/{tenant_id}
**描述**: 获取指定租户的详细信息

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| tenant_id | string | 是 | 租户ID |

**响应示例**:
```json
{
  "success": true,
  "message": "获取租户详情成功",
  "data": {
    "id": "uuid",
    "name": "测试租户",
    "email": "test@example.com",
    "status": "active",
    "created_at": "2025-08-19T10:00:00Z",
    "last_login_at": "2025-08-27T09:30:00Z",
    "profile": {
      "company_name": "测试公司",
      "industry": "制造业",
      "company_size": "100-500人"
    },
    "statistics": {
      "project_count": 5,
      "transaction_count": 45,
      "supplier_count": 8,
      "total_amount": 1500000.00
    },
    "activity": {
      "login_frequency": "daily",
      "last_activity": "2025-08-27T09:30:00Z",
      "activity_score": 85
    }
  }
}
```

## 📊 统计信息接口

### 1. 租户活跃度统计

#### GET /admin/statistics/tenant-activity
**描述**: 获取租户活跃度统计数据

**查询参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| days | integer | 否 | 30 | 统计天数 |
| group_by | string | 否 | day | 分组方式(day/week/month) |

**响应示例**:
```json
{
  "success": true,
  "message": "获取活跃度统计成功",
  "data": {
    "activity_summary": {
      "total_tenants": 15,
      "active_tenants": 12,
      "inactive_tenants": 3,
      "avg_activity_score": 78.5
    },
    "daily_activity": [
      {
        "date": "2025-08-27",
        "active_tenants": 12,
        "login_count": 45,
        "operation_count": 156,
        "avg_activity_score": 82.3
      }
    ],
    "tenant_ranking": [
      {
        "tenant_id": "uuid",
        "tenant_name": "活跃租户",
        "activity_score": 95,
        "login_count": 8,
        "operation_count": 25
      }
    ]
  }
}
```

### 2. 系统性能统计

#### GET /admin/statistics/performance
**描述**: 获取系统性能统计数据

**查询参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| hours | integer | 否 | 24 | 统计时间范围(小时) |

**响应示例**:
```json
{
  "success": true,
  "message": "获取性能统计成功",
  "data": {
    "api_performance": {
      "avg_response_time": 120,
      "max_response_time": 500,
      "min_response_time": 15,
      "total_requests": 1500,
      "success_rate": 99.8
    },
    "database_performance": {
      "avg_query_time": 25,
      "slow_queries": 3,
      "connection_usage": "65%",
      "active_connections": 8
    },
    "system_resources": {
      "cpu_usage": "30%",
      "memory_usage": "45%",
      "disk_usage": "60%",
      "network_io": "2.5 MB/s"
    }
  }
}
```

## 📝 操作日志接口

### 1. 获取操作日志

#### GET /admin/logs
**描述**: 获取管理员操作日志

**查询参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| size | integer | 否 | 50 | 每页数量 |
| operation_type | string | 否 | - | 操作类型筛选 |
| target_type | string | 否 | - | 目标类型筛选 |
| admin_user_id | string | 否 | - | 管理员ID筛选 |
| start_date | string | 否 | - | 开始日期 |
| end_date | string | 否 | - | 结束日期 |

**响应示例**:
```json
{
  "success": true,
  "message": "获取操作日志成功",
  "data": {
    "logs": [
      {
        "id": "uuid",
        "admin_user_id": "admin_uuid",
        "admin_name": "管理员",
        "operation_type": "password_reset",
        "target_type": "tenant",
        "target_id": "tenant_uuid",
        "target_name": "测试租户",
        "operation_details": {
          "old_status": "active",
          "new_status": "disabled",
          "reason": "账户违规"
        },
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "created_at": "2025-08-27T10:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "page_size": 50,
      "total_pages": 1,
      "total_records": 25
    }
  }
}
```

### 2. 导出操作日志

#### GET /admin/logs/export
**描述**: 导出操作日志为Excel文件

**查询参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| format | string | 否 | excel | 导出格式(excel/csv) |
| start_date | string | 否 | - | 开始日期 |
| end_date | string | 否 | - | 结束日期 |
| operation_type | string | 否 | - | 操作类型筛选 |

**响应**: Excel文件下载

## 🔒 安全规范

### 认证要求
- 所有接口都需要JWT Token认证
- Token通过Authorization头传递: `Bearer <token>`
- Token过期时间: 1小时

### 权限控制
- 仅限 `super_admin` 角色访问
- 操作日志记录所有操作
- 敏感操作需要二次确认

### 数据验证
- 所有输入参数进行类型和格式验证
- 防止SQL注入和XSS攻击
- 敏感数据加密存储

### 限流控制
- API调用频率限制: 100次/分钟
- 健康检查频率限制: 10次/分钟
- 密码重置频率限制: 5次/小时

## 📋 错误码定义

### 通用错误码
| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| VALIDATION_ERROR | 400 | 参数验证失败 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 业务错误码
| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| TENANT_NOT_FOUND | 404 | 租户不存在 |
| TENANT_DISABLED | 400 | 租户已被禁用 |
| PASSWORD_RESET_LIMIT | 429 | 密码重置次数超限 |
| INVALID_STATUS | 400 | 无效的状态值 |
| OPERATION_FAILED | 500 | 操作执行失败 |

## 🧪 接口测试

### 测试环境
- **测试URL**: `http://localhost:8000/api/v1/admin`
- **测试数据库**: 独立的测试数据库
- **测试用户**: 专门的测试管理员账户

### 测试工具
- **API测试**: Postman / Insomnia
- **自动化测试**: pytest + httpx
- **性能测试**: Apache Bench / wrk

### 测试用例
- 正常流程测试
- 异常情况测试
- 权限验证测试
- 性能压力测试
- 安全漏洞测试

## 📚 接口文档

### 自动生成文档
- 使用FastAPI的自动文档生成
- 访问地址: `/docs` (Swagger UI)
- 访问地址: `/redoc` (ReDoc)

### 文档维护
- 接口变更时及时更新文档
- 添加详细的参数说明和示例
- 保持文档与代码同步

---

**文档版本历史**
| 版本 | 日期 | 修改内容 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2025-08-27 | 初始版本 | 后端开发工程师 |
