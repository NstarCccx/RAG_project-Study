"""
FastAPI 应用入口文件

启动命令：
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.exception import global_exception_handler
from app.core.log import logger
from app.db.db_sql import engine, Base
from app.db.chroma import chroma_client
from app.core.exception import ApiResponse
from app.routers.documents import router as documents_router
from app.models.document import Document

# ==================== 创建 FastAPI 应用 ====================
app = FastAPI(
    title="RAG API",
    description="RAG（检索增强生成）后端服务 API",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI 文档地址
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

# ==================== 挂载静态文件目录 ====================
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    logger.info(f"✅ 静态文件目录已挂载：{STATIC_DIR}")

# ==================== 注册路由 ====================
app.include_router(documents_router, prefix="/api/v1")

# ==================== 创建数据库表 ====================
Base.metadata.create_all(bind=engine)
logger.info("✅ 数据库表创建/检查完成")

# ==================== 健康检查接口 ====================
@app.get("/health", tags=["系统"])
async def health_check():
    """
    健康检查接口 - 用于验证服务是否正常运行

    Returns:
        ApiResponse: 包含服务状态信息

    可配合负载均衡器或容器编排工具进行健康探测
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
