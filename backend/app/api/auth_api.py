"""
认证相关API路由
包括登录接口
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# 简单的 HTTP Bearer 认证
security = HTTPBearer(auto_error=False)


# 临时硬编码的用户凭证
HARDCODED_USERS = {
    "admin": {
        "password": "admin",
        "role": "admin"
    }
}


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应模型"""
    success: bool = Field(..., description="是否成功")
    token: Optional[str] = Field(None, description="认证令牌")
    user: Optional[dict] = Field(None, description="用户信息")
    message: Optional[str] = Field(None, description="消息")


class UserInfo(BaseModel):
    """用户信息模型"""
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="角色")


def generate_simple_token(username: str) -> str:
    """
    生成简单的 token（非 JWT，仅用于演示）
    实际生产环境应使用 JWT
    """
    # 简单的 token 格式: username_timestamp
    timestamp = datetime.now().timestamp()
    return f"{username}_{int(timestamp)}"


def verify_token(token: str) -> Optional[str]:
    """
    验证 token 并返回用户名
    """
    if not token:
        return None
    
    try:
        parts = token.split('_')
        if len(parts) >= 2:
            username = parts[0]
            # 检查用户是否存在
            if username in HARDCODED_USERS:
                return username
    except Exception:
        pass
    
    return None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    登录接口
    
    Args:
        request: 登录请求
        
    Returns:
        登录响应
    """
    username = request.username
    password = request.password
    
    # 检查用户是否存在
    if username not in HARDCODED_USERS:
        logger.warning(f"登录失败: 用户不存在 - {username}")
        return LoginResponse(
            success=False,
            message="用户名或密码错误"
        )
    
    # 检查密码
    user_data = HARDCODED_USERS[username]
    if user_data["password"] != password:
        logger.warning(f"登录失败: 密码错误 - {username}")
        return LoginResponse(
            success=False,
            message="用户名或密码错误"
        )
    
    # 生成 token
    token = generate_simple_token(username)
    
    logger.info(f"登录成功: {username}")
    
    return LoginResponse(
        success=True,
        token=token,
        user={
            "username": username,
            "role": user_data["role"]
        },
        message="登录成功"
    )


@router.post("/logout")
async def logout():
    """
    登出接口
    
    Returns:
        登出响应
    """
    return {"success": True, "message": "已登出"}


@router.get("/verify")
async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    验证认证状态
    
    Args:
        credentials: 认证凭证
        
    Returns:
        认证状态
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="未认证")
    
    username = verify_token(credentials.credentials)
    if not username:
        raise HTTPException(status_code=401, detail="认证无效")
    
    return {
        "success": True,
        "username": username,
        "role": HARDCODED_USERS.get(username, {}).get("role", "user")
    }