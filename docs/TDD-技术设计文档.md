# 工程项目流水账管理系统 - 技术设计文档 (TDD)

**版本**: v1.0  
**创建日期**: 2024年12月  
**技术负责人**: AI开发团队  

## 1. 系统架构设计

### 1.1 总体架构

```
                    Internet
                        |
                   [ Cloudflare CDN ]
                        |
                   [ Nginx (Load Balancer) ]
                        |
            ┌───────────┴───────────┐
            │                       │
      [ Frontend ]           [ Backend API ]
     (Vue.js PWA)           (FastAPI)
            │                       │
            │               ┌───────┴───────┐
            │               │               │
            │        [ PostgreSQL ]   [ Redis Cluster ]
            │               │               │
            │               │        [ Celery Workers ]
            │               │               │
            └───────────────┼───────────────┘
                            │
                    [ File Storage ]
                  (Local/MinIO/Cloud)
```

### 1.2 技术栈选型

#### 1.2.1 后端技术栈
```python
# 核心框架
- Python 3.11+ 
- FastAPI 0.104+ (异步Web框架)
- SQLAlchemy 2.0+ (ORM)
- Alembic (数据库迁移)

# 数据存储
- PostgreSQL 15+ (主数据库)
- Redis 7+ (缓存/会话/任务队列)

# 异步任务
- Celery 5.3+ (任务队列)
- Celery Beat (定时任务)

# 数据处理
- Pandas 2.0+ (数据分析)
- Plotly 5.17+ (图表生成)
- Pillow (图像处理)

# 安全认证
- python-jose[cryptography] (JWT)
- passlib[bcrypt] (密码加密)
- python-multipart (文件上传)

# 集成服务
- httpx (HTTP客户端)
- aiofiles (异步文件操作)
- python-docx (文档生成)
```

#### 1.2.2 前端技术栈
```javascript
// 核心框架
- Vue.js 3.3+ (Composition API)
- Vite 4.5+ (构建工具)
- TypeScript 5.2+ (类型安全)

// UI和样式
- Element Plus 2.4+ (UI组件库)
- Tailwind CSS 3.3+ (原子化CSS)
- Sass (CSS预处理器)

// 状态管理和路由
- Pinia 2.1+ (状态管理)
- Vue Router 4.2+ (路由管理)

// 数据可视化
- ECharts 5.4+ (图表库)
- Vue-ECharts (Vue集成)

// 工具库
- Axios 1.6+ (HTTP客户端)
- Day.js (日期处理)
- VueUse (Vue工具集)

// PWA支持
- Workbox (Service Worker)
- Vue PWA Plugin
```

#### 1.2.3 部署和运维
```yaml
# 容器化
- Docker 24+ 
- Docker Compose 2.21+

# 反向代理
- Nginx 1.24+ (负载均衡/静态文件)
- Certbot (SSL证书)

# 监控和日志
- Prometheus (指标收集)
- Grafana (数据可视化)
- Loki (日志聚合)

# 备份和存储
- pg_dump (数据库备份)
- rsync (文件同步)
- 可选: MinIO (对象存储)
```

## 2. 数据库设计

### 2.1 核心表结构

#### 2.1.1 租户和用户管理
```sql
-- 租户表
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(50) UNIQUE,
    plan_type VARCHAR(20) DEFAULT 'trial', -- trial, basic, professional, enterprise
    settings JSONB DEFAULT '{}',
    subscription_end DATE,
    storage_used BIGINT DEFAULT 0, -- 字节
    storage_limit BIGINT DEFAULT 5368709120, -- 5GB
    api_calls_used INTEGER DEFAULT 0,
    api_calls_limit INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active' -- active, suspended, cancelled
);

-- 用户表  
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- super_admin, admin, finance, project_manager, viewer, field_recorder
    permissions JSONB DEFAULT '[]',
    profile JSONB DEFAULT '{}', -- 头像、电话、部门等
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

-- 用户会话表
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(100) NOT NULL UNIQUE, -- JWT ID
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    last_activity TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2.1.2 项目管理
```sql
-- 项目表
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    project_code VARCHAR(50), -- 项目编号
    description TEXT,
    project_type VARCHAR(50), -- residential, commercial, municipal, etc.
    budget DECIMAL(15,2),
    actual_cost DECIMAL(15,2) DEFAULT 0,
    start_date DATE,
    end_date DATE,
    actual_end_date DATE,
    status VARCHAR(20) DEFAULT 'planning', -- planning, active, paused, completed, cancelled
    progress INTEGER DEFAULT 0, -- 0-100百分比
    location JSONB DEFAULT '{}', -- 地址、GPS坐标等
    client_info JSONB DEFAULT '{}', -- 客户信息
    contract_info JSONB DEFAULT '{}', -- 合同信息
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 项目成员表
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- manager, finance, viewer
    permissions JSONB DEFAULT '[]',
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(project_id, user_id)
);

-- 项目里程碑表
CREATE TABLE project_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    target_date DATE,
    actual_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, delayed
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2.1.3 财务管理
```sql
-- 交易分类表
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) NOT NULL, -- income, expense
    parent_id UUID REFERENCES categories(id),
    icon VARCHAR(50),
    color VARCHAR(7), -- 十六进制颜色
    is_system BOOLEAN DEFAULT false, -- 系统预设分类
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, name, type)
);

-- 交易记录表
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    type VARCHAR(10) NOT NULL, -- income, expense
    category_id UUID REFERENCES categories(id),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    exchange_rate DECIMAL(10,6) DEFAULT 1.0,
    amount_base DECIMAL(15,2) NOT NULL, -- 基准货币金额
    description TEXT,
    tags JSONB DEFAULT '[]', -- 标签数组
    supplier_info JSONB DEFAULT '{}', -- 供应商信息
    payment_method VARCHAR(50), -- cash, bank_transfer, wechat, alipay, etc.
    receipt_urls JSONB DEFAULT '[]', -- 票据图片URLs
    invoice_info JSONB DEFAULT '{}', -- 发票信息
    location JSONB DEFAULT '{}', -- GPS位置信息
    transaction_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed', -- pending, confirmed, cancelled
    approval_status VARCHAR(20) DEFAULT 'approved', -- pending, approved, rejected
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 供应商表
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    tax_number VARCHAR(50),
    bank_info JSONB DEFAULT '{}',
    credit_rating VARCHAR(10), -- A, B, C, D
    payment_terms VARCHAR(100),
    notes TEXT,
    total_amount DECIMAL(15,2) DEFAULT 0, -- 累计交易金额
    transaction_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- 预算表
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id),
    amount DECIMAL(15,2) NOT NULL,
    used_amount DECIMAL(15,2) DEFAULT 0,
    period_type VARCHAR(20) DEFAULT 'project', -- monthly, quarterly, project
    period_start DATE,
    period_end DATE,
    alert_threshold DECIMAL(5,2) DEFAULT 80.0, -- 预警阈值百分比
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2.1.4 文件和附件管理
```sql
-- 文件表
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    file_hash VARCHAR(64), -- SHA256哈希
    thumbnail_path VARCHAR(500), -- 缩略图路径
    metadata JSONB DEFAULT '{}', -- 图片EXIF、文档信息等
    storage_type VARCHAR(20) DEFAULT 'local', -- local, s3, oss
    is_public BOOLEAN DEFAULT false,
    download_count INTEGER DEFAULT 0,
    uploaded_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 文件关联表
CREATE TABLE file_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL, -- transaction, project, user
    entity_id UUID NOT NULL,
    relation_type VARCHAR(50) DEFAULT 'attachment', -- attachment, avatar, thumbnail
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2.1.5 审计和日志
```sql
-- 审计日志表
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL, -- CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    entity_type VARCHAR(50) NOT NULL, -- transaction, project, user, etc.
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 系统日志表
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level VARCHAR(20) NOT NULL, -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    message TEXT NOT NULL,
    module VARCHAR(100), -- 模块名称
    function_name VARCHAR(100), -- 函数名称
    trace_id UUID, -- 请求追踪ID
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- API访问日志表
CREATE TABLE api_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    method VARCHAR(10) NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time INTEGER, -- 毫秒
    request_size INTEGER, -- 字节
    response_size INTEGER, -- 字节
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.2 数据库优化策略

#### 2.2.1 索引设计
```sql
-- 性能关键索引
CREATE INDEX idx_transactions_tenant_project_date ON transactions(tenant_id, project_id, transaction_date DESC);
CREATE INDEX idx_transactions_category_date ON transactions(category_id, transaction_date DESC);
CREATE INDEX idx_transactions_created_date ON transactions(created_at DESC);
CREATE INDEX idx_users_tenant_email ON users(tenant_id, email);
CREATE INDEX idx_projects_tenant_status ON projects(tenant_id, status);
CREATE INDEX idx_audit_logs_tenant_date ON audit_logs(tenant_id, created_at DESC);

-- 全文搜索索引
CREATE INDEX idx_transactions_fts ON transactions USING gin(to_tsvector('chinese', description));
CREATE INDEX idx_projects_fts ON projects USING gin(to_tsvector('chinese', name || ' ' || COALESCE(description, '')));

-- 部分索引
CREATE INDEX idx_active_projects ON projects(tenant_id, created_at) WHERE status IN ('planning', 'active');
CREATE INDEX idx_recent_transactions ON transactions(tenant_id, created_at) WHERE created_at > NOW() - INTERVAL '1 year';
```

#### 2.2.2 分区策略 (大数据量时)
```sql
-- 按时间分区审计日志表
CREATE TABLE audit_logs_2024 PARTITION OF audit_logs
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- 按租户分区API日志表 (如果单租户数据量很大)
CREATE TABLE api_logs_tenant_hash_0 PARTITION OF api_logs
FOR VALUES WITH (modulus 4, remainder 0);
```

#### 2.2.3 多租户数据隔离
```sql
-- Row Level Security (RLS) 策略
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_transactions ON transactions
    FOR ALL TO app_role
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- 应用程序角色
CREATE ROLE app_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_role;
```

## 3. 后端API架构

### 3.1 项目结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py              # 配置管理
│   ├── dependencies.py        # 依赖注入
│   ├── 
│   ├── core/                  # 核心功能
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证相关
│   │   ├── security.py       # 安全工具
│   │   ├── database.py       # 数据库连接
│   │   ├── cache.py          # Redis缓存
│   │   ├── tasks.py          # Celery任务
│   │   └── exceptions.py     # 自定义异常
│   │
│   ├── models/               # SQLAlchemy模型
│   │   ├── __init__.py
│   │   ├── base.py          # 基础模型
│   │   ├── tenant.py        # 租户模型
│   │   ├── user.py          # 用户模型
│   │   ├── project.py       # 项目模型
│   │   ├── transaction.py   # 交易模型
│   │   └── audit.py         # 审计模型
│   │
│   ├── schemas/             # Pydantic模式
│   │   ├── __init__.py
│   │   ├── base.py          # 基础模式
│   │   ├── auth.py          # 认证相关
│   │   ├── tenant.py        # 租户模式
│   │   ├── user.py          # 用户模式
│   │   ├── project.py       # 项目模式
│   │   ├── transaction.py   # 交易模式
│   │   └── report.py        # 报表模式
│   │
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── deps.py          # API依赖
│   │   ├── v1/              # API v1版本
│   │   │   ├── __init__.py
│   │   │   ├── auth.py      # 认证API
│   │   │   ├── tenants.py   # 租户API
│   │   │   ├── users.py     # 用户API
│   │   │   ├── projects.py  # 项目API
│   │   │   ├── transactions.py # 交易API
│   │   │   ├── categories.py   # 分类API
│   │   │   ├── reports.py      # 报表API
│   │   │   ├── files.py        # 文件API
│   │   │   └── integrations.py # 集成API
│   │   └── v2/              # API v2版本 (未来)
│   │
│   ├── services/            # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── auth_service.py  # 认证服务
│   │   ├── tenant_service.py # 租户服务
│   │   ├── project_service.py # 项目服务
│   │   ├── transaction_service.py # 交易服务
│   │   ├── report_service.py    # 报表服务
│   │   ├── file_service.py      # 文件服务
│   │   ├── notification_service.py # 通知服务
│   │   └── integration_service.py  # 集成服务
│   │
│   ├── utils/               # 工具函数
│   │   ├── __init__.py
│   │   ├── email.py         # 邮件工具
│   │   ├── sms.py           # 短信工具
│   │   ├── file_utils.py    # 文件处理
│   │   ├── ocr.py           # OCR识别
│   │   ├── excel.py         # Excel处理
│   │   ├── pdf.py           # PDF生成
│   │   └── validators.py    # 数据验证
│   │
│   ├── workers/             # Celery任务
│   │   ├── __init__.py
│   │   ├── report_tasks.py  # 报表生成任务
│   │   ├── file_tasks.py    # 文件处理任务
│   │   ├── notification_tasks.py # 通知任务
│   │   └── cleanup_tasks.py      # 清理任务
│   │
│   └── middleware/          # 中间件
│       ├── __init__.py
│       ├── tenant.py        # 租户中间件
│       ├── auth.py          # 认证中间件
│       ├── logging.py       # 日志中间件
│       ├── rate_limit.py    # 限流中间件
│       └── cors.py          # CORS中间件
│
├── alembic/                 # 数据库迁移
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/                   # 测试代码
│   ├── __init__.py
│   ├── conftest.py         # 测试配置
│   ├── test_api/           # API测试
│   ├── test_services/      # 服务测试
│   └── test_utils/         # 工具测试
│
├── requirements.txt         # 依赖列表
├── requirements-dev.txt     # 开发依赖
├── Dockerfile              # Docker配置
├── docker-compose.yml      # 开发环境
├── pyproject.toml          # 项目配置
└── README.md               # 项目说明
```

### 3.2 核心组件设计

#### 3.2.1 认证和授权系统
```python
# app/core/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

class AuthManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

# 权限装饰器
def require_permissions(permissions: List[str]):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not has_permissions(current_user, permissions):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

#### 3.2.2 多租户中间件
```python
# app/middleware/tenant.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 从请求中提取租户信息
        tenant_id = self.extract_tenant_id(request)
        
        if tenant_id:
            # 设置数据库连接的租户上下文
            await self.set_tenant_context(tenant_id)
        
        response = await call_next(request)
        return response
    
    def extract_tenant_id(self, request: Request) -> Optional[str]:
        # 方式1: 从子域名提取
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            return self.get_tenant_by_subdomain(subdomain)
        
        # 方式2: 从JWT token提取
        auth_header = request.headers.get("authorization")
        if auth_header:
            return self.get_tenant_from_token(auth_header)
        
        return None
```

#### 3.2.3 数据服务层设计
```python
# app/services/transaction_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

class TransactionService:
    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db
        self.current_user = current_user
        self.tenant_id = current_user.tenant_id

    async def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:
        # 验证项目权限
        await self.verify_project_access(transaction_data.project_id)
        
        # 创建交易记录
        transaction = Transaction(
            **transaction_data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.current_user.id
        )
        
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        
        # 异步更新项目统计
        await self.update_project_stats.delay(transaction_data.project_id)
        
        # 记录审计日志
        await self.log_audit_event("CREATE", "transaction", transaction.id)
        
        return transaction

    async def get_transactions(
        self, 
        project_id: Optional[str] = None,
        category_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        page: int = 1,
        size: int = 20
    ) -> List[Transaction]:
        query = select(Transaction).where(Transaction.tenant_id == self.tenant_id)
        
        if project_id:
            query = query.where(Transaction.project_id == project_id)
        if category_id:
            query = query.where(Transaction.category_id == category_id)
        if date_from:
            query = query.where(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.where(Transaction.transaction_date <= date_to)
        
        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        
        result = await self.db.execute(query)
        return result.scalars().all()
```

#### 3.2.4 报表服务设计
```python
# app/services/report_service.py
import pandas as pd
import plotly.express as px
from app.workers.report_tasks import generate_report_async

class ReportService:
    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db
        self.current_user = current_user
        self.tenant_id = current_user.tenant_id

    async def generate_project_summary(self, project_id: str) -> dict:
        """生成项目汇总报表"""
        # 获取项目基本信息
        project = await self.get_project(project_id)
        
        # 获取收支数据
        transactions = await self.get_project_transactions(project_id)
        
        # 使用Pandas进行数据分析
        df = pd.DataFrame([t.dict() for t in transactions])
        
        if df.empty:
            return {"error": "No transaction data"}
        
        # 计算汇总数据
        summary = {
            "project_info": project.dict(),
            "total_income": df[df['type'] == 'income']['amount'].sum(),
            "total_expense": df[df['type'] == 'expense']['amount'].sum(),
            "net_profit": df[df['type'] == 'income']['amount'].sum() - df[df['type'] == 'expense']['amount'].sum(),
            "transaction_count": len(df),
            "category_breakdown": df.groupby(['type', 'category_name'])['amount'].sum().to_dict()
        }
        
        return summary

    async def generate_cashflow_chart(self, project_id: str) -> dict:
        """生成现金流图表"""
        transactions = await self.get_project_transactions(project_id)
        df = pd.DataFrame([t.dict() for t in transactions])
        
        if df.empty:
            return {"chart": None}
        
        # 按日期汇总现金流
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        daily_flow = df.groupby(['transaction_date', 'type'])['amount'].sum().reset_index()
        
        # 生成图表
        fig = px.bar(
            daily_flow, 
            x='transaction_date', 
            y='amount', 
            color='type',
            title='项目现金流趋势'
        )
        
        return {"chart": fig.to_json()}

    async def generate_large_report_async(self, report_type: str, params: dict) -> str:
        """异步生成大型报表"""
        task = generate_report_async.delay(
            tenant_id=str(self.tenant_id),
            user_id=str(self.current_user.id),
            report_type=report_type,
            params=params
        )
        return task.id
```

### 3.3 集成服务设计（未来规划）

#### 3.3.1 OCR发票识别
```python
# app/utils/ocr.py
import httpx
from typing import Dict, Any

class OCRService:
    def __init__(self):
        self.baidu_api_key = settings.BAIDU_OCR_API_KEY
        self.baidu_secret_key = settings.BAIDU_OCR_SECRET_KEY
        
    async def recognize_invoice(self, image_data: bytes) -> Dict[str, Any]:
        """识别发票信息"""
        # 获取百度OCR访问令牌
        access_token = await self.get_baidu_access_token()
        
        # 调用发票识别API
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/vat_invoice?access_token={access_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                files={"image": image_data},
                timeout=30.0
            )
            
        if response.status_code == 200:
            result = response.json()
            return self.parse_invoice_result(result)
        else:
            raise Exception(f"OCR API error: {response.text}")
    
    def parse_invoice_result(self, result: dict) -> dict:
        """解析发票识别结果"""
        words_result = result.get('words_result', {})
        
        return {
            "invoice_code": words_result.get('InvoiceCode', {}).get('word', ''),
            "invoice_num": words_result.get('InvoiceNum', {}).get('word', ''),
            "amount": self.extract_amount(words_result.get('TotalAmount', {}).get('word', '')),
            "seller_name": words_result.get('SellerName', {}).get('word', ''),
            "invoice_date": words_result.get('InvoiceDate', {}).get('word', ''),
            "confidence": result.get('words_result_num', 0)
        }
```

#### 3.3.2 银行对账单导入
```python
# app/utils/bank_import.py
import pandas as pd
from typing import List, Dict
from app.schemas.transaction import TransactionImport

class BankStatementImporter:
    def __init__(self):
        self.bank_formats = {
            "icbc": self.parse_icbc_format,      # 工商银行
            "ccb": self.parse_ccb_format,        # 建设银行
            "abc": self.parse_abc_format,        # 农业银行
            "boc": self.parse_boc_format,        # 中国银行
        }
    
    async def import_bank_statement(
        self, 
        file_content: bytes, 
        bank_type: str,
        project_id: str
    ) -> List[TransactionImport]:
        """导入银行对账单"""
        
        # 读取Excel/CSV文件
        try:
            if file_content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
                df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8-sig')
            else:
                df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"文件格式错误: {str(e)}")
        
        # 根据银行类型解析数据
        parser = self.bank_formats.get(bank_type)
        if not parser:
            raise ValueError(f"不支持的银行类型: {bank_type}")
        
        transactions = parser(df, project_id)
        return transactions
    
    def parse_icbc_format(self, df: pd.DataFrame, project_id: str) -> List[TransactionImport]:
        """解析工商银行格式"""
        transactions = []
        
        for _, row in df.iterrows():
            transaction = TransactionImport(
                project_id=project_id,
                type="expense" if row['支出金额'] > 0 else "income",
                amount=abs(row['支出金额'] or row['收入金额']),
                description=row['摘要'],
                transaction_date=pd.to_datetime(row['交易日期']).date(),
                payment_method="bank_transfer",
                supplier_info={
                    "name": row.get('对方户名', ''),
                    "account": row.get('对方账号', '')
                }
            )
            transactions.append(transaction)
        
        return transactions
```

#### 3.3.3 移动端支付集成
```python
# app/utils/payment.py
class PaymentService:
    def __init__(self):
        self.wechat_api = WeChatPayAPI()
        self.alipay_api = AlipayAPI()
    
    async def sync_wechat_payments(self, merchant_id: str, start_date: date, end_date: date):
        """同步微信支付记录"""
        payments = await self.wechat_api.get_payment_records(
            merchant_id, start_date, end_date
        )
        
        for payment in payments:
            # 检查是否已存在
            existing = await self.check_payment_exists(payment['transaction_id'])
            if not existing:
                await self.create_payment_transaction(payment)
    
    async def create_payment_transaction(self, payment_data: dict):
        """创建支付交易记录"""
        transaction = TransactionCreate(
            type="expense",  # 通常是支出
            amount=payment_data['amount'],
            description=f"微信支付: {payment_data['description']}",
            payment_method="wechat",
            transaction_date=payment_data['transaction_time'].date(),
            supplier_info={
                "merchant_name": payment_data['merchant_name'],
                "transaction_id": payment_data['transaction_id']
            }
        )
        
        return await self.transaction_service.create_transaction(transaction)
```

## 4. 前端架构设计

### 4.1 组件架构
```
src/
├── components/              # 通用组件
│   ├── layout/             # 布局组件
│   │   ├── AppHeader.vue   # 应用头部
│   │   ├── AppSidebar.vue  # 侧边栏
│   │   ├── AppFooter.vue   # 页脚
│   │   └── AppBreadcrumb.vue # 面包屑
│   │
│   ├── forms/              # 表单组件
│   │   ├── FormField.vue   # 通用表单字段
│   │   ├── DatePicker.vue  # 日期选择器
│   │   ├── CategorySelect.vue # 分类选择器
│   │   └── ProjectSelect.vue  # 项目选择器
│   │
│   ├── charts/             # 图表组件
│   │   ├── LineChart.vue   # 折线图
│   │   ├── BarChart.vue    # 柱状图
│   │   ├── PieChart.vue    # 饼图
│   │   └── Dashboard.vue   # 仪表盘
│   │
│   ├── tables/             # 表格组件
│   │   ├── DataTable.vue   # 通用数据表格
│   │   ├── TransactionTable.vue # 交易记录表格
│   │   └── ProjectTable.vue     # 项目表格
│   │
│   └── common/             # 通用组件
│       ├── FileUpload.vue  # 文件上传
│       ├── ImageViewer.vue # 图片查看器
│       ├── ConfirmDialog.vue # 确认对话框
│       └── LoadingSpinner.vue # 加载动画
│
├── views/                  # 页面组件
│   ├── auth/              # 认证页面
│   │   ├── Login.vue      # 登录页
│   │   ├── Register.vue   # 注册页
│   │   └── ForgotPassword.vue # 忘记密码
│   │
│   ├── dashboard/         # 仪表盘
│   │   ├── Overview.vue   # 总览
│   │   ├── Analytics.vue  # 分析
│   │   └── Notifications.vue # 通知
│   │
│   ├── projects/          # 项目管理
│   │   ├── ProjectList.vue    # 项目列表
│   │   ├── ProjectDetail.vue  # 项目详情
│   │   ├── ProjectCreate.vue  # 创建项目
│   │   └── ProjectSettings.vue # 项目设置
│   │
│   ├── transactions/      # 财务记录
│   │   ├── TransactionList.vue   # 交易列表
│   │   ├── TransactionCreate.vue # 创建交易
│   │   ├── TransactionImport.vue # 批量导入
│   │   └── CategoryManage.vue    # 分类管理
│   │
│   ├── reports/           # 报表分析
│   │   ├── ProjectReport.vue     # 项目报表
│   │   ├── FinancialReport.vue   # 财务报表
│   │   ├── ComparisonReport.vue  # 对比分析
│   │   └── CustomReport.vue     # 自定义报表
│   │
│   ├── settings/          # 系统设置
│   │   ├── Profile.vue        # 个人资料
│   │   ├── TeamManage.vue     # 团队管理
│   │   ├── Billing.vue        # 计费设置
│   │   └── Integrations.vue   # 集成设置
│   │
│   └── mobile/            # 移动端专用页面
│       ├── MobileLogin.vue    # 移动端登录
│       ├── QuickEntry.vue     # 快速录入
│       ├── CameraCapture.vue  # 拍照录入
│       └── OfflineSync.vue    # 离线同步
```

### 4.2 状态管理设计
```javascript
// stores/auth.js - 认证状态
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    refreshToken: null,
    tenant: null,
    permissions: []
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    hasPermission: (state) => (permission) => state.permissions.includes(permission),
    userRole: (state) => state.user?.role
  },
  
  actions: {
    async login(credentials) {
      const response = await authAPI.login(credentials)
      this.setAuth(response.data)
      router.push('/dashboard')
    },
    
    async refreshAuth() {
      if (!this.refreshToken) return false
      try {
        const response = await authAPI.refresh(this.refreshToken)
        this.setAuth(response.data)
        return true
      } catch (error) {
        this.logout()
        return false
      }
    },
    
    setAuth(authData) {
      this.user = authData.user
      this.token = authData.access_token
      this.refreshToken = authData.refresh_token
      this.tenant = authData.tenant
      this.permissions = authData.permissions
      
      // 保存到localStorage
      localStorage.setItem('auth', JSON.stringify(authData))
    },
    
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      this.tenant = null
      this.permissions = []
      localStorage.removeItem('auth')
      router.push('/login')
    }
  }
})

// stores/projects.js - 项目状态
export const useProjectStore = defineStore('projects', {
  state: () => ({
    projects: [],
    currentProject: null,
    loading: false,
    pagination: {
      page: 1,
      size: 20,
      total: 0
    }
  }),
  
  actions: {
    async fetchProjects(params = {}) {
      this.loading = true
      try {
        const response = await projectAPI.getProjects({
          ...params,
          page: this.pagination.page,
          size: this.pagination.size
        })
        
        this.projects = response.data.items
        this.pagination.total = response.data.total
      } finally {
        this.loading = false
      }
    },
    
    async createProject(projectData) {
      const response = await projectAPI.createProject(projectData)
      this.projects.unshift(response.data)
      return response.data
    },
    
    async updateProject(id, updateData) {
      const response = await projectAPI.updateProject(id, updateData)
      const index = this.projects.findIndex(p => p.id === id)
      if (index !== -1) {
        this.projects[index] = response.data
      }
      return response.data
    }
  }
})
```

### 4.3 PWA配置
```javascript
// vite.config.js
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.project-ledger\.com\/.*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 3,
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      },
      manifest: {
        name: '工程项目流水账',
        short_name: '项目账本',
        description: '专业的工程项目财务管理系统',
        theme_color: '#409EFF',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-72x72.png',
            sizes: '72x72',
            type: 'image/png'
          },
          {
            src: '/icons/icon-96x96.png',
            sizes: '96x96',
            type: 'image/png'
          },
          {
            src: '/icons/icon-128x128.png',
            sizes: '128x128',
            type: 'image/png'
          },
          {
            src: '/icons/icon-144x144.png',
            sizes: '144x144',
            type: 'image/png'
          },
          {
            src: '/icons/icon-152x152.png',
            sizes: '152x152',
            type: 'image/png'
          },
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icons/icon-384x384.png',
            sizes: '384x384',
            type: 'image/png'
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ]
})

// src/utils/offline.js - 离线支持
class OfflineManager {
  constructor() {
    this.db = null
    this.initIndexedDB()
  }
  
  async initIndexedDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ProjectLedgerDB', 1)
      
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        this.db = request.result
        resolve(this.db)
      }
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result
        
        // 离线交易记录
        if (!db.objectStoreNames.contains('offline_transactions')) {
          const store = db.createObjectStore('offline_transactions', {
            keyPath: 'id',
            autoIncrement: true
          })
          store.createIndex('project_id', 'project_id', { unique: false })
          store.createIndex('created_at', 'created_at', { unique: false })
        }
      }
    })
  }
  
  async saveOfflineTransaction(transaction) {
    const tx = this.db.transaction(['offline_transactions'], 'readwrite')
    const store = tx.objectStore('offline_transactions')
    
    await store.add({
      ...transaction,
      created_at: new Date(),
      synced: false
    })
  }
  
  async syncOfflineData() {
    if (!navigator.onLine) return
    
    const tx = this.db.transaction(['offline_transactions'], 'readonly')
    const store = tx.objectStore('offline_transactions')
    const unsyncedData = await store.getAll()
    
    for (const transaction of unsyncedData.filter(t => !t.synced)) {
      try {
        await transactionAPI.createTransaction(transaction)
        await this.markAsSynced(transaction.id)
      } catch (error) {
        console.error('同步失败:', error)
      }
    }
  }
}
```

## 5. 部署架构

### 5.1 Docker容器化部署
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # 数据库服务
  postgres:
    image: postgres:15-alpine
    container_name: ledger_postgres
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=zh_CN.UTF-8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: ledger_redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 后端API服务
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: ledger_backend
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery工作进程
  celery_worker:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: ledger_celery_worker
    command: celery -A app.worker worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Celery定时任务
  celery_beat:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: ledger_celery_beat
    command: celery -A app.worker beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # 前端服务
  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: ledger_frontend
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped

  # 监控服务
  prometheus:
    image: prom/prometheus:latest
    container_name: ledger_prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: ledger_grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    ports:
      - "3001:3000"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    name: ledger_network
```

### 5.2 Nginx配置
```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # 基础配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 上游服务器
    upstream backend {
        server backend:8000;
        keepalive 32;
    }
    
    # HTTP重定向到HTTPS
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }
    
    # HTTPS主服务器
    server {
        listen 443 ssl http2;
        server_name projectledger.com www.projectledger.com;
        
        # SSL配置
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
        add_header Referrer-Policy "strict-origin-when-cross-origin";
        
        # 静态文件
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            
            # 缓存静态资源
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }
        
        # API代理
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }
        
        # WebSocket支持
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # 文件上传
        location /uploads/ {
            alias /app/uploads/;
            expires 1y;
            add_header Cache-Control "public";
        }
        
        # 健康检查
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
    }
    
    # 子域名支持 (多租户)
    server {
        listen 443 ssl http2;
        server_name *.projectledger.com;
        
        ssl_certificate /etc/nginx/ssl/wildcard.pem;
        ssl_certificate_key /etc/nginx/ssl/wildcard.key;
        
        # 其他配置同上...
        
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }
        
        location /api/ {
            proxy_pass http://backend;
            # 传递子域名信息
            proxy_set_header X-Tenant-Domain $host;
            # 其他代理配置同上...
        }
    }
}
```

### 5.3 监控和日志配置
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'nginx'
    static_configs:
      - targets: ['frontend:80']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

```yaml
# monitoring/alert_rules.yml
groups:
  - name: database
    rules:
      - alert: PostgreSQLDown
        expr: up{job="postgres"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
          
      - alert: HighDatabaseConnections
        expr: pg_stat_database_numbackends > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High number of database connections"

  - name: application
    rules:
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API response time"
          
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

## 6. 安全设计

### 6.1 认证和授权安全
```python
# app/core/security.py
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

class SecurityManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        
    def create_secure_token(self, data: dict, expires_delta: timedelta) -> str:
        """创建安全JWT令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        
        # 添加安全字段
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_hex(16),  # JWT ID
            "iss": "project-ledger",       # 发行者
            "aud": "project-ledger-users"  # 受众
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience="project-ledger-users",
                issuer="project-ledger"
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
    
    def hash_password(self, password: str) -> str:
        """安全密码哈希"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_csrf_token(self, session_id: str) -> str:
        """生成CSRF令牌"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        token_data = f"{session_id}:{timestamp}:{settings.SECRET_KEY}"
        return hashlib.sha256(token_data.encode()).hexdigest()
    
    def verify_csrf_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """验证CSRF令牌"""
        try:
            # 重新生成并比较
            timestamp = str(int(datetime.utcnow().timestamp()))
            for i in range(max_age):  # 允许时间窗口
                test_timestamp = str(int(datetime.utcnow().timestamp()) - i)
                test_data = f"{session_id}:{test_timestamp}:{settings.SECRET_KEY}"
                test_token = hashlib.sha256(test_data.encode()).hexdigest()
                if secrets.compare_digest(token, test_token):
                    return True
            return False
        except Exception:
            return False

# 限流装饰器
from functools import wraps
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.failed_attempts = defaultdict(list)
    
    def limit(self, max_requests: int = 100, window: int = 3600, max_failures: int = 5):
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                client_ip = request.client.host
                now = time.time()
                
                # 清理过期记录
                self.requests[client_ip] = [
                    req_time for req_time in self.requests[client_ip] 
                    if now - req_time < window
                ]
                
                # 检查请求限制
                if len(self.requests[client_ip]) >= max_requests:
                    raise HTTPException(
                        status_code=429, 
                        detail="Too many requests"
                    )
                
                # 检查失败次数限制
                recent_failures = [
                    fail_time for fail_time in self.failed_attempts[client_ip]
                    if now - fail_time < 900  # 15分钟窗口
                ]
                
                if len(recent_failures) >= max_failures:
                    raise HTTPException(
                        status_code=429,
                        detail="Too many failed attempts. Try again later."
                    )
                
                # 记录请求
                self.requests[client_ip].append(now)
                
                try:
                    result = await func(request, *args, **kwargs)
                    return result
                except HTTPException as e:
                    if e.status_code in [401, 403]:
                        self.failed_attempts[client_ip].append(now)
                    raise
                    
            return wrapper
        return decorator

rate_limiter = RateLimiter()
```

### 6.2 数据安全
```python
# app/utils/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataEncryption:
    def __init__(self, password: str = None):
        if password:
            self.key = self._derive_key(password)
        else:
            self.key = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        """从密码派生加密密钥"""
        password_bytes = password.encode()
        salt = settings.ENCRYPTION_SALT.encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password_bytes))
    
    def encrypt(self, data: str) -> str:
        """加密数据"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        if not encrypted_data:
            return encrypted_data
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# SQLAlchemy加密字段类型
from sqlalchemy.types import TypeDecorator, String

class EncryptedType(TypeDecorator):
    """加密字段类型"""
    impl = String
    
    def __init__(self, *args, **kwargs):
        self.encryption = DataEncryption()
        super().__init__(*args, **kwargs)
    
    def process_bind_param(self, value, dialect):
        """保存时加密"""
        if value is not None:
            return self.encryption.encrypt(value)
        return value
    
    def process_result_value(self, value, dialect):
        """读取时解密"""
        if value is not None:
            return self.encryption.decrypt(value)
        return value

# 使用示例
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True)
    email = Column(String(100), nullable=False)
    phone = Column(EncryptedType(20))  # 加密存储手机号
    id_number = Column(EncryptedType(50))  # 加密存储身份证号
```

### 6.3 文件安全
```python
# app/utils/file_security.py
import magic
import hashlib
from pathlib import Path
from typing import List, Optional
from PIL import Image
import av  # video processing

class FileSecurityManager:
    ALLOWED_EXTENSIONS = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv'],
        'videos': ['.mp4', '.avi', '.mov', '.wmv'],
        'audio': ['.mp3', '.wav', '.ogg']
    }
    
    MAX_FILE_SIZE = {
        'images': 10 * 1024 * 1024,      # 10MB
        'documents': 50 * 1024 * 1024,   # 50MB
        'videos': 100 * 1024 * 1024,     # 100MB
        'audio': 20 * 1024 * 1024        # 20MB
    }
    
    def validate_file(self, file_content: bytes, filename: str) -> dict:
        """验证文件安全性"""
        result = {
            'valid': False,
            'file_type': None,
            'mime_type': None,
            'size': len(file_content),
            'errors': []
        }
        
        # 检查文件大小
        if len(file_content) == 0:
            result['errors'].append('文件为空')
            return result
        
        # 检测真实MIME类型
        mime_type = magic.from_buffer(file_content, mime=True)
        result['mime_type'] = mime_type
        
        # 确定文件类型
        file_type = self._determine_file_type(mime_type, filename)
        if not file_type:
            result['errors'].append('不支持的文件类型')
            return result
        
        result['file_type'] = file_type
        
        # 检查文件大小限制
        if len(file_content) > self.MAX_FILE_SIZE.get(file_type, 0):
            result['errors'].append(f'文件大小超过限制')
            return result
        
        # 文件内容安全检查
        if file_type == 'images':
            if not self._validate_image(file_content):
                result['errors'].append('图片文件可能损坏或包含恶意内容')
                return result
        
        elif file_type == 'documents':
            if not self._validate_document(file_content):
                result['errors'].append('文档文件可能包含恶意内容')
                return result
        
        if not result['errors']:
            result['valid'] = True
        
        return result
    
    def _determine_file_type(self, mime_type: str, filename: str) -> Optional[str]:
        """确定文件类型"""
        suffix = Path(filename).suffix.lower()
        
        if mime_type.startswith('image/') and suffix in self.ALLOWED_EXTENSIONS['images']:
            return 'images'
        elif mime_type in ['application/pdf', 'application/msword', 'application/vnd.ms-excel'] \
             and suffix in self.ALLOWED_EXTENSIONS['documents']:
            return 'documents'
        elif mime_type.startswith('video/') and suffix in self.ALLOWED_EXTENSIONS['videos']:
            return 'videos'
        elif mime_type.startswith('audio/') and suffix in self.ALLOWED_EXTENSIONS['audio']:
            return 'audio'
        
        return None
    
    def _validate_image(self, file_content: bytes) -> bool:
        """验证图片文件"""
        try:
            # 使用PIL验证图片
            img = Image.open(io.BytesIO(file_content))
            img.verify()  # 验证图片完整性
            
            # 检查图片尺寸限制
            if img.size[0] > 10000 or img.size[1] > 10000:
                return False
            
            return True
        except Exception:
            return False
    
    def _validate_document(self, file_content: bytes) -> bool:
        """验证文档文件"""
        # 基础文件头检查
        pdf_headers = [b'%PDF-1.', b'%PDF-2.']
        office_headers = [b'PK\x03\x04', b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1']
        
        for header in pdf_headers + office_headers:
            if file_content.startswith(header):
                return True
        
        return False
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """计算文件哈希值"""
        return hashlib.sha256(file_content).hexdigest()
    
    def scan_for_malware(self, file_path: str) -> bool:
        """恶意软件扫描（集成第三方服务）"""
        # 这里可以集成ClamAV或其他反病毒引擎
        # 或调用云端安全扫描API
        return True  # 简化实现
```

## 7. 性能优化策略

### 7.1 数据库性能优化
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

class DatabaseManager:
    def __init__(self):
        # 数据库连接池配置
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=20,              # 连接池大小
            max_overflow=30,           # 最大溢出连接
            pool_pre_ping=True,        # 连接前检查
            pool_recycle=3600,         # 连接回收时间（1小时）
            echo=settings.DEBUG        # 是否打印SQL
        )
        
        self.async_session_maker = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

# 查询优化示例
class OptimizedTransactionService:
    async def get_project_summary(self, project_id: str) -> dict:
        """优化的项目汇总查询"""
        # 使用聚合查询减少数据传输
        query = select(
            Transaction.type,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('count'),
            Category.name.label('category_name')
        ).select_from(
            Transaction.join(Category, Transaction.category_id == Category.id)
        ).where(
            Transaction.tenant_id == self.tenant_id,
            Transaction.project_id == project_id
        ).group_by(
            Transaction.type, 
            Category.name
        )
        
        result = await self.db.execute(query)
        return result.fetchall()
    
    async def get_transactions_with_pagination(
        self, 
        filters: dict,
        page: int = 1,
        size: int = 20
    ) -> dict:
        """分页查询优化"""
        # 基础查询
        base_query = select(Transaction).where(
            Transaction.tenant_id == self.tenant_id
        )
        
        # 动态添加过滤条件
        if filters.get('project_id'):
            base_query = base_query.where(
                Transaction.project_id == filters['project_id']
            )
        
        if filters.get('date_from'):
            base_query = base_query.where(
                Transaction.transaction_date >= filters['date_from']
            )
        
        if filters.get('search'):
            base_query = base_query.where(
                Transaction.description.ilike(f"%{filters['search']}%")
            )
        
        # 总数查询（使用COUNT优化）
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.db.scalar(count_query)
        
        # 分页数据查询
        data_query = base_query.order_by(
            Transaction.transaction_date.desc()
        ).offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(data_query)
        items = result.scalars().all()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'size': size,
            'pages': math.ceil(total / size)
        }
```

### 7.2 缓存策略
```python
# app/core/cache.py
import json
import pickle
from typing import Any, Optional, Union
from redis.asyncio import Redis
from functools import wraps

class CacheManager:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=False)
        self.default_expire = 3600  # 1小时
    
    async def get(self, key: str, default: Any = None) -> Any:
        """获取缓存"""
        try:
            value = await self.redis.get(key)
            if value is None:
                return default
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return default
    
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """设置缓存"""
        try:
            expire = expire or self.default_expire
            serialized = pickle.dumps(value)
            return await self.redis.setex(key, expire, serialized)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0

cache = CacheManager()

def cached(expire: int = 3600, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试获取缓存
            result = await cache.get(cache_key)
            if result is not None:
                return result
            
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 设置缓存
            await cache.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator

# 使用示例
class ReportService:
    @cached(expire=1800, key_prefix="report")  # 缓存30分钟
    async def get_project_report(self, project_id: str) -> dict:
        """获取项目报表（缓存版）"""
        # 复杂的报表计算逻辑
        return await self._generate_project_report(project_id)
    
    async def invalidate_project_cache(self, project_id: str):
        """清除项目相关缓存"""
        pattern = f"report:*{project_id}*"
        await cache.delete_pattern(pattern)
```

### 7.3 异步任务优化
```python
# app/workers/report_tasks.py
from celery import Celery
from celery.result import AsyncResult
import pandas as pd

celery_app = Celery('project_ledger')

@celery_app.task(bind=True, max_retries=3)
def generate_large_report(self, tenant_id: str, report_type: str, params: dict):
    """生成大型报表的异步任务"""
    try:
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': '开始生成报表...'}
        )
        
        # 获取数据
        transactions = get_transaction_data(tenant_id, params)
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': '数据获取完成...'}
        )
        
        # 数据处理
        df = pd.DataFrame(transactions)
        processed_data = process_report_data(df, report_type)
        self.update_state(
            state='PROGRESS',
            meta={'current': 70, 'total': 100, 'status': '数据处理完成...'}
        )
        
        # 生成图表
        charts = generate_charts(processed_data)
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': '图表生成完成...'}
        )
        
        # 保存结果
        report_id = save_report_result(tenant_id, processed_data, charts)
        
        return {
            'status': 'SUCCESS',
            'report_id': report_id,
            'download_url': f'/api/v1/reports/download/{report_id}'
        }
        
    except Exception as exc:
        # 重试机制
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        # 失败处理
        return {
            'status': 'FAILURE',
            'error': str(exc)
        }

@celery_app.task
def cleanup_old_files():
    """清理旧文件的定时任务"""
    # 清理30天前的临时文件
    cutoff_date = datetime.now() - timedelta(days=30)
    # 清理逻辑...

@celery_app.task
def send_monthly_reports():
    """发送月度报表的定时任务"""
    # 获取所有需要发送报表的租户
    # 生成并发送报表
    pass

# Celery Beat 定时任务配置
celery_app.conf.beat_schedule = {
    'cleanup-old-files': {
        'task': 'app.workers.report_tasks.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点
    },
    'send-monthly-reports': {
        'task': 'app.workers.report_tasks.send_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 每月1号上午9点
    },
}
```

---

**文档状态**: 技术设计完成  
**下一步**: 开发计划文档编写  
**技术栈确认**: Python FastAPI + PostgreSQL + Vue.js + Redis + Celery  
**特色功能**: OCR识别、银行对账单导入、PWA移动支持、多租户架构
