"""
文件上传模块 - 提供文件上传接口和 MD5 防重复功能
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import os
import uuid

from app.db.db_sql import get_db
from app.models.document import Document
from app.schemas.document import FileUploadResponse
from app.core.exception import ApiResponse
from app.core.log import logger

# 导入解析器工厂（统一入口）
from app.parsers import ParserFactory

# 创建路由
router = APIRouter(prefix="/documents",tags=["文档管理"])

# 文件存储目录（static/uploads）
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def calculate_md5(file_content: bytes) -> str:
    """
    计算文件内容的 MD5 值

    Args:
        file_content: 文件二进制内容

    Returns:
        str: 32位 MD5 十六进制字符串
    """
    md5_hash = hashlib.md5()
    md5_hash.update(file_content)
    return md5_hash.hexdigest()


@router.post("/upload", response_model=ApiResponse)
async def upload_file(
    file: UploadFile = File(..., description="上传的文件"),
    db: Session = Depends(get_db)
):
    """
    文件上传接口

    功能：
    - 支持任意类型文件上传
    - 计算文件 MD5 实现秒传/防重复
    - 文件落地存储到 static/uploads 目录
    - 写入 MySQL 文档元数据表

    Args:
        file: 上传的文件（FastAPI UploadFile）
        db: 数据库会话（依赖注入）

    Returns:
        ApiResponse: 包含文档元数据的响应

    防重复逻辑：
        1. 计算上传文件的 MD5
        2. 查询数据库是否存在相同 MD5
        3. 若存在 → 返回已有文件信息（秒传）
        4. 若不存在 → 写入文件 + 写入数据库
    """
    # 读取文件内容
    file_content = await file.read()

    # 计算文件 MD5
    file_md5 = calculate_md5(file_content)
    file_size = len(file_content)

    logger.info(f"收到文件上传请求：{file.filename}，大小：{file_size} 字节，MD5：{file_md5}")

    # 检查 MD5 是否已存在（防重复）
    existing_doc = db.query(Document).filter(Document.md5 == file_md5).first()
    if existing_doc:
        logger.info(f"文件已存在（MD5 匹配）：{existing_doc.filename}，ID：{existing_doc.id}")
        return ApiResponse(
            code=200,
            message="文件已存在（秒传成功）",
            data=FileUploadResponse(
                id=existing_doc.id,
                filename=existing_doc.filename,
                file_path=existing_doc.file_path,
                file_size=existing_doc.file_size,
                md5=existing_doc.md5,
                content_type=existing_doc.content_type,
                created_at=existing_doc.created_at
            )
        )

    # 生成唯一文件名（UUID + 原始扩展名）
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"

    # 构建存储路径
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 写入文件到磁盘
    with open(file_path, "wb") as f:
        f.write(file_content)

    # 计算相对路径（用于 API 返回）
    relative_path = f"/static/uploads/{unique_filename}"

    # ========== 自动解析文件 ==========
    logger.info(f"开始解析文件：{file.filename}")
    
    # 调用解析器工厂自动识别并解析
    parse_result = ParserFactory.parse(file_path)
    
    # 获取解析后的文本内容
    extracted_content = parse_result.content if parse_result.success else ""
    
    if parse_result.success:
        logger.info(f"文件解析成功，提取文本长度：{len(extracted_content)} 字符")
    else:
        logger.warning(f"文件解析失败：{parse_result.error}")
    
    # ========== 创建文档记录 ==========
    doc = Document(
        filename=file.filename or unique_filename,
        file_path=relative_path,
        file_size=file_size,
        md5=file_md5,
        content_type=file.content_type or "application/octet-stream",
        content=extracted_content,  # 存入解析后的文本
        created_at=datetime.now()
    )

    # 写入数据库
    db.add(doc)
    db.commit()
    db.refresh(doc)

    logger.info(f"文件上传成功：{file.filename}，存储路径：{relative_path}，ID：{doc.id}")

    return ApiResponse(
        code=200,
        message="上传成功",
        data=FileUploadResponse(
            id=doc.id,
            filename=doc.filename,
            file_path=doc.file_path,
            file_size=doc.file_size,
            md5=doc.md5,
            content_type=doc.content_type,
            created_at=doc.created_at
        )
    )


@router.get("/list", response_model=ApiResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    文档列表接口

    Args:
        skip: 跳过的记录数（分页）
        limit: 返回的记录数（默认100）

    Returns:
        ApiResponse: 包含文档列表的响应
    """
    documents = db.query(Document).offset(skip).limit(limit).all()
    total = db.query(Document).count()

    return ApiResponse(
        code=200,
        message="success",
        data={
            "total": total,
            "documents": [
                FileUploadResponse(
                    id=doc.id,
                    filename=doc.filename,
                    file_path=doc.file_path,
                    file_size=doc.file_size,
                    md5=doc.md5,
                    content_type=doc.content_type,
                    created_at=doc.created_at
                ) for doc in documents
            ]
        }
    )
