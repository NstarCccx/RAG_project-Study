"""
日志模块封装 - 基于 loguru 库实现统一日志管理

功能特性：
- 支持控制台输出（带颜色）
- 支持文件持久化（自动滚动、自动清理）
- 统一日志级别控制
- 全局单例 logger 对象

使用方式：
    from app.core.log import logger
    
    logger.debug("调试信息")      # 仅开发调试用
    logger.info("一般信息")       # 常规运行日志
    logger.warning("警告信息")    # 需要关注的异常情况
    logger.error("错误信息")      # 可恢复的错误
    logger.critical("严重错误")   # 不可恢复的致命错误
"""
from loguru import logger
import sys
import os

# ==================== 日志目录配置 ====================
# 日志文件保存路径：当前工作目录下的 logs 文件夹
log_path = os.path.join(os.getcwd(), "logs")
# 确保日志目录存在，不存在则自动创建（exist_ok=True 避免重复创建报错）
os.makedirs(log_path, exist_ok=True)

# ==================== 控制台输出配置 ====================
# 移除 loguru 默认的 stderr 输出处理器，避免重复输出
logger.remove()

# 添加控制台输出处理器
logger.add(
    sink=sys.stdout,                      # 输出目标：标准输出（控制台）
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
    # 日志格式说明：
    #   {time:YYYY-MM-DD HH:mm:ss} - 时间戳（绿色）
    #   {level}                   - 日志级别（自动着色）
    #   {message}                 - 日志消息（青色）
    level="INFO"                         # 日志级别：仅输出 INFO 及以上级别
)

# ==================== 文件输出配置 ====================
logger.add(
    sink=os.path.join(log_path, "rag_{time}.log"),
    # 输出目标：logs/rag_<时间戳>.log 文件
    # {time} 会被替换为实际时间，如 rag_2024-01-01_12-00-00.log
    
    rotation="50MB",                     # 滚动策略：单个文件最大 50MB
    # 可选值："50MB", "1 week", "00:00" 等
    
    encoding="utf-8",                    # 文件编码：UTF-8（支持中文）
    
    retention="7 days",                  # 保留策略：日志文件最多保留 7 天
    # 可选值："7 days", "1 month", 3 等（数字表示文件数量）
    
    level="INFO"                         # 日志级别：仅记录 INFO 及以上级别
)

# ==================== 模块导出 ====================
# 声明对外暴露的接口，其他模块只需导入 logger 即可使用
__all__ = ["logger"]