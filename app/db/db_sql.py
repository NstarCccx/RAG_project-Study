"""
数据库模块封装 - 基于 SQLAlchemy ORM 实现数据库连接管理

功能特性：
- 统一管理数据库连接配置
- 提供数据库会话（Session）获取方式
- 支持连接池配置
- 声明式模型基类

技术栈：
- SQLAlchemy：Python 最流行的 ORM 框架
- MySQL：数据库后端（通过 pymysql 驱动）
"""
from sqlalchemy.orm.session import Session


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.log import logger

# ==================== 数据库连接配置 ====================
# 数据库连接 URL 格式：dialect+driver://username:password@host:port/database
# - dialect: 数据库类型（mysql）
# - driver: 驱动库（pymysql）
# - username: 用户名（root）
# - password: 密码（CGx2005214.）
# - host: 数据库地址（localhost）
# - port: 端口（3306）
# - database: 数据库名（rag_db）
# - charset: 字符集（utf8mb4 支持完整 Unicode，包括 emoji）
DB_URL = "mysql+pymysql://root:CGx2005214.@localhost:3306/rag_db?charset=utf8mb4"

# ==================== 创建数据库引擎 ====================
# Engine 是 SQLAlchemy 的核心组件，负责管理数据库连接池
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,        # 连接池预检查：获取连接前验证连接是否有效
    pool_recycle=3600,         # 连接回收时间：3600秒（1小时）后自动重新建立连接
    echo=False                 # 是否打印 SQL 语句（调试时设为 True）
)

# ==================== 创建会话工厂与基类 ====================
# SessionLocal：会话工厂，每次调用返回一个新的数据库会话
# - autocommit=False: 关闭自动提交，需要手动 commit
# - autoflush=False: 关闭自动刷新，避免不必要的数据库查询
# - bind=engine: 绑定到上面创建的引擎
SessionLocal = sessionmaker[Session](autocommit=False, autoflush=False, bind=engine)

# Base：所有 ORM 模型类的基类
# 声明模型时继承此类，SQLAlchemy 会自动管理表映射
Base = declarative_base()

# ==================== 依赖函数：获取数据库连接 ====================
def get_db():
    """
    数据库连接依赖函数 - 供 FastAPI 路由使用
    
    使用方式：
        @app.get("/users")
        async def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    
    工作原理：
        1. 调用时创建一个新的数据库会话
        2. 使用 yield 将会话传递给调用方
        3. 路由处理完成后，finally 块确保会话被关闭
        4. 自动管理连接的获取和释放，防止连接泄漏
    """
    db = SessionLocal()  # 创建新会话
    try:
        yield db         # 提供会话给调用方
    finally:
        db.close()       # 确保会话被关闭

# 记录初始化成功日志
logger.info("✅ MySQL 连接成功")
