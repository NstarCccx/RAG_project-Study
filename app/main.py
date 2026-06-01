"""
FastAPI 应用入口文件

启动命令：
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exception import global_exception_handler
from app.core.log import logger
from app.db.db_sql import engine
from app.db.chroma import chroma_client
from app.core.exception import ApiResponse

# ==================== 创建 FastAPI 应用 ====================
app = FastAPI(
    title="RAG API",
    description="RAG（检索增强生成）后端服务 API",
    version="1.0.0",
    docs_url="/swagger",      # Swagger UI 文档地址
    redoc_url="/redoc"     # ReDoc 文档地址（备选）
)

# ==================== 配置 CORS（跨域资源共享） ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允许所有来源（生产环境应限制具体域名）
    allow_credentials=True,   # 允许携带凭证
    allow_methods=["*"],      # 允许所有 HTTP 方法
    allow_headers=["*"],      # 允许所有请求头
)

# ==================== 注册全局异常处理器 ====================
app.add_exception_handler(Exception, global_exception_handler)

# ==================== 健康检查接口 ====================
@app.get("/health", tags=["系统"])
async def health_check():
    """
    健康检查接口 - 用于验证服务是否正常运行

    Returns:
        ApiResponse: 包含服务状态信息

    """
    return ApiResponse(
        code=200,
        message="success",
        data={
            "status": "healthy",
            "service": "RAG API",
            "version": "1.0.0"
        }
    )
# ==================== 初始化日志 ====================
logger.info("🚀 FastAPI 应用启动完成")
logger.info("📚 API 文档地址：http://127.0.0.1:8000/docs")

