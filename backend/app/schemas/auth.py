"""
认证相关数据模式
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    """用户响应信息"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
    role: str = Field(..., description="用户角色")
    is_active: bool = Field(..., description="是否激活")
    profile: Optional[dict] = Field(None, description="用户资料")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    remember_me: bool = Field(False, description="记住我")

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    confirm_password: str = Field(..., min_length=6, max_length=50, description="确认密码")
    
    def validate_passwords_match(self):
        """验证密码匹配"""
        if self.password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return self

class TenantRegister(BaseModel):
    """租户注册请求"""
    # 企业信息
    company_name: str = Field(..., min_length=2, max_length=100, description="企业名称")
    industry_type: str = Field("construction", description="行业类型")
    company_size: str = Field("small", description="企业规模")
    
    # 管理员信息  
    admin_name: str = Field(..., min_length=2, max_length=50, description="管理员姓名")
    admin_email: EmailStr = Field(..., description="管理员邮箱")
    admin_phone: Optional[str] = Field(None, description="管理员电话")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    confirm_password: str = Field(..., min_length=6, max_length=50, description="确认密码")
    
    def validate_passwords_match(self):
        """验证密码匹配"""
        if self.password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return True

class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌") 
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user: Optional[dict] = Field(None, description="用户信息")

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")

class PasswordReset(BaseModel):
    """密码重置请求"""
    email: EmailStr = Field(..., description="邮箱地址")

class PasswordResetConfirm(BaseModel):
    """密码重置确认"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=50, description="确认新密码")
    
    def validate_passwords_match(self):
        """验证密码匹配"""
        if self.new_password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return self

class TenantResponse(BaseModel):
    """租户响应信息"""
    id: str = Field(..., description="租户ID")
    name: str = Field(..., description="租户名称") 
    domain: Optional[str] = Field(None, description="租户域名")
    plan_type: str = Field(..., description="订阅计划")
    status: str = Field(..., description="租户状态")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True

# 前向引用问题已通过使用dict类型解决
