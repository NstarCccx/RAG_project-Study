"""
异常处理模块 - 统一管理 API 异常和返回格式

功能特性：
- 统一 API 响应格式（ApiResponse）
- 全局异常捕获处理器（global_exception_handler）
- 自定义业务异常类（BusinessException）

设计目的：
1. 确保所有 API 响应格式一致，便于前端统一处理
2. 捕获未预期的异常，避免泄露敏感信息
3. 提供业务异常类，便于业务层抛出特定错误
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any
from .log import logger

# ==================== 统一响应模型 ====================
class ApiResponse(BaseModel):
    """
    API 统一响应格式模型
    
    Attributes:
        code: 状态码（200 成功，其他为错误码）
        message: 响应消息（成功时为 "success"，失败时为错误描述）
        data: 响应数据（成功时返回业务数据，失败时为 None）
    """
    code: int = 200
    message: str = "success"
    data: Any = None

# ==================== 全局异常处理器 ====================
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器 - 捕获所有未被处理的异常
    
    Args:
        request: 当前请求对象
        exc: 捕获到的异常对象
    
    Returns:
        JSONResponse: 统一格式的错误响应
    
    说明：
        当代码中抛出未被 try-except 捕获的异常时，
        此处理器会自动捕获并返回统一格式的错误响应，
        同时记录错误日志便于排查问题。
    """
    # 记录错误日志（exc_info=True 会记录完整堆栈信息）
    # 处理可能包含花括号的异常消息，避免 loguru format 错误
    exc_str = str(exc).replace("{", "{{").replace("}", "}}")
    logger.error(f"全局异常：{exc_str}", exc_info=True)
    
    # 返回统一错误格式
    return JSONResponse(
        content={
            "code": 500,
            "message": f"服务器异常：{str(exc)}",
            "data": None
        },
        status_code=500
    )

# ==================== 自定义业务异常 ====================
class BusinessException(HTTPException):
    """
    自定义业务异常类 - 用于业务逻辑中的预期错误
    
    继承自 FastAPI 的 HTTPException，可被 FastAPI 自动捕获处理
    
    Args:
        message: 错误消息（会返回给前端）
        code: HTTP 状态码（默认 400，可根据业务需求调整）
    
    适用场景：
        - 参数校验失败
        - 业务规则不满足（如用户不存在、权限不足等）
        - 资源未找到
    """
    def __init__(self, message: str, code: int = 400):
        super().__init__(status_code=code, detail=message)
