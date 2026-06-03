"""
文档相关 Pydantic 模型 - 用于请求参数校验和响应数据格式化
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    id: int = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件存储路径")
    file_size: int = Field(..., description="文件大小（字节）")
    md5: str = Field(..., description="文件MD5校验值")
    content_type: str = Field(..., description="文件类型")
    created_at: datetime = Field(..., description="上传时间")


class DocumentBase(BaseModel):
    """文档基础模型"""
    filename: str = Field(..., min_length=1, max_length=255, description="文件名")
    content_type: str = Field(..., description="文件类型（MIME type）")


class DocumentCreate(DocumentBase):
    """创建文档时使用的模型"""
    file_size: int = Field(..., gt=0, description="文件大小（字节），必须大于0")
    md5: str = Field(..., min_length=32, max_length=32, description="文件MD5值，固定32位")


class DocumentQuery(BaseModel):
    """文档查询参数模型"""
    md5: Optional[str] = Field(None, min_length=32, max_length=32, description="按MD5查询")
    filename: Optional[str] = Field(None, max_length=255, description="按文件名模糊查询")


class ParseResult(BaseModel):
    """文档解析结果模型"""
    success: bool = Field(..., description="是否解析成功")
    content: str = Field("", description="提取的文本内容")
    file_type: str = Field(..., description="文件类型（txt/md/pdf/ocr/word）")
    page_count: Optional[int] = Field(None, description="PDF页数（可选）")
    error: Optional[str] = Field(None, description="错误信息（可选）")
