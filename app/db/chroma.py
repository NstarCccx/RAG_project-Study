"""
Chroma 向量数据库模块封装 - 基于单例模式实现全局唯一连接

功能特性：
- 单例模式确保整个应用只有一个 Chroma 客户端实例
- 支持数据持久化到本地文件系统
- 全局唯一入口，便于统一管理

技术背景：
- Chroma：轻量级开源向量数据库，专门用于存储和检索向量嵌入
- 常用于 RAG（Retrieval-Augmented Generation）场景
- 支持持久化存储，重启后数据不丢失
"""
import chromadb
from chromadb.config import Settings
from app.core.log import logger
import os

# ==================== 持久化配置 ====================
# Chroma 数据存储目录：当前工作目录下的 chroma_db 文件夹
CHROMA_DB_DIR = os.path.join(os.getcwd(), "chroma_db")
# 确保目录存在，不存在则自动创建
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# ==================== 单例类实现 ====================
class ChromaClientSingleton:
    """
    Chroma 客户端单例类 - 确保全局只有一个客户端实例
    
    单例模式（Singleton Pattern）：
    - 保证一个类只有一个实例
    - 提供全局访问点
    - 避免重复创建连接，节省资源
    
    使用方式：
        client = ChromaClientSingleton().get_client()
    """
    
    # 类级别的实例变量，存储唯一实例
    _instance = None

    def __new__(cls):
        """
        重写 __new__ 方法控制实例创建
        
        Python 创建对象时先调用 __new__ 分配内存，再调用 __init__ 初始化
        通过检查 _instance 是否为 None，决定是否创建新实例
        """
        if cls._instance is None:
            # 如果实例不存在，创建新实例
            cls._instance = super().__new__(cls)
            
            # 初始化 Chroma 持久化客户端
            cls._instance.client = chromadb.PersistentClient(
                path=CHROMA_DB_DIR,          # 数据存储路径
                settings=Settings(allow_reset=True)  # 允许重置数据库（开发环境用）
            )
            
            logger.info("✅ Chroma 持久化客户端初始化完成（单例）")
        
        # 返回已存在的实例（或刚创建的新实例）
        return cls._instance

    def get_client(self):
        """
        获取 Chroma 客户端实例
        
        Returns:
            chromadb.PersistentClient: Chroma 持久化客户端对象
        """
        return self.client

# ==================== 全局单例对象 ====================
# 创建全局唯一的 Chroma 客户端实例
# 其他模块只需导入此对象即可使用，无需重复创建
chroma_client = ChromaClientSingleton().get_client()
