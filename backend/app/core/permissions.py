"""
系统权限定义
"""

# 用户管理权限
USER_PERMISSIONS = [
    "user_create",      # 创建用户
    "user_read",        # 查看用户
    "user_update",      # 更新用户
    "user_delete",      # 删除用户
    "user_list",        # 查看用户列表
    "user_statistics",  # 查看用户统计
]

# 项目管理权限
PROJECT_PERMISSIONS = [
    "project_create",     # 创建项目
    "project_read",       # 查看项目
    "project_update",     # 更新项目
    "project_delete",     # 删除项目
    "project_list",       # 查看项目列表
    "project_statistics", # 查看项目统计

]

# 财务记录权限
TRANSACTION_PERMISSIONS = [
    "transaction_create",    # 创建交易记录
    "transaction_read",      # 查看交易记录
    "transaction_update",    # 更新交易记录
    "transaction_delete",    # 删除交易记录
    "transaction_approve",   # 审批交易记录
    "transaction_export",    # 导出交易记录
    "transaction_import",    # 导入交易记录
    "transaction_statistics",# 查看交易统计
]

# 分类管理权限
CATEGORY_PERMISSIONS = [
    "category_create",    # 创建分类
    "category_read",      # 查看分类
    "category_update",    # 更新分类
    "category_delete",    # 删除分类
]

# 供应商管理权限
SUPPLIER_PERMISSIONS = [
    "supplier_create",    # 创建供应商
    "supplier_read",      # 查看供应商
    "supplier_update",    # 更新供应商
    "supplier_delete",    # 删除供应商
    "supplier_statistics",# 查看供应商统计
]

# 报表权限
REPORT_PERMISSIONS = [
    "report_financial",   # 查看财务报表
    "report_project",     # 查看项目报表
    "report_export",      # 导出报表
    "report_custom",      # 自定义报表
]

# 系统管理权限
SYSTEM_PERMISSIONS = [
    "system_settings",    # 系统设置
    "tenant_settings",    # 租户设置
    "data_export",        # 数据导出
    "data_import",        # 数据导入
    "audit_log",          # 查看审计日志
]

# 所有权限
ALL_PERMISSIONS = (
    USER_PERMISSIONS +
    PROJECT_PERMISSIONS +
    TRANSACTION_PERMISSIONS +
    CATEGORY_PERMISSIONS +
    SUPPLIER_PERMISSIONS +
    REPORT_PERMISSIONS +
    SYSTEM_PERMISSIONS
)

# 角色权限映射
ROLE_PERMISSIONS = {
    "super_admin": ["*"],  # 超级管理员拥有所有权限
    
    "admin": ALL_PERMISSIONS,  # 管理员拥有所有具体权限
    
    "finance_manager": [
        # 用户相关
        "user_read", "user_list",
        # 项目相关
        "project_read", "project_list", "project_statistics",
        # 财务相关
        *TRANSACTION_PERMISSIONS,
        # 分类和供应商
        *CATEGORY_PERMISSIONS,
        *SUPPLIER_PERMISSIONS,
        # 报表
        *REPORT_PERMISSIONS,
    ],
    
    "project_manager": [
        # 用户相关
        "user_read", "user_list",
        # 项目相关（除删除外的所有权限）
        "project_create", "project_read", "project_update", 
        "project_list", "project_statistics",
    
        # 财务相关（查看和创建）
        "transaction_create", "transaction_read", "transaction_statistics",
        # 分类和供应商（查看）
        "category_read", "supplier_read",
        # 报表（项目相关）
        "report_project", "report_export",
    ],
    
    "finance": [
        # 用户相关
        "user_read", "user_list",
        # 项目相关（查看）
        "project_read", "project_list",
        # 财务相关
        "transaction_create", "transaction_read", "transaction_update",
        "transaction_export", "transaction_import", "transaction_statistics",
        # 分类和供应商
        "category_create", "category_read", "category_update",
        "supplier_create", "supplier_read", "supplier_update",
        # 报表
        "report_financial", "report_export",
    ],
    
    "accountant": [
        # 用户相关
        "user_read",
        # 项目相关（查看）
        "project_read", "project_list",
        # 财务相关（基础操作）
        "transaction_create", "transaction_read", "transaction_update",
        "transaction_statistics",
        # 分类和供应商（查看和创建）
        "category_read", "supplier_read", "supplier_create",
        # 报表（查看）
        "report_financial",
    ],
    
    "viewer": [
        # 查看权限
        "user_read",
        "project_read", "project_list",
        "transaction_read",
        "category_read",
        "supplier_read",
        "report_financial", "report_project",
    ],
    
    "field_worker": [
        # 现场录入员权限
        "project_read",
        "transaction_create", "transaction_read",
        "category_read",
        "supplier_read",
    ]
}

def get_role_permissions(role: str) -> list:
    """获取角色对应的权限列表"""
    return ROLE_PERMISSIONS.get(role, [])

def has_permission(user_permissions: list, required_permission: str) -> bool:
    """检查用户是否拥有指定权限"""
    if "*" in user_permissions:
        return True
    return required_permission in user_permissions

def validate_permissions(permissions: list) -> bool:
    """验证权限列表是否有效"""
    if "*" in permissions:
        return True
    return all(perm in ALL_PERMISSIONS for perm in permissions)
