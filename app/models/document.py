"""
文档 ORM 模型 - 定义 documents 表结构
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.db.db_sql import Base


class Document(Base):
    """
    文档元数据表模型

    存储上传文件的基本信息，用于文件管理和去重

    表名：documents
    """
    __tablename__ = "documents"

    # 主键自增ID
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # 文件名（最大255字符）
    filename = Column(String(255), nullable=False, comment="文件名")

    # 文件存储路径（相对路径，最大500字符）
    file_path = Column(String(500), nullable=False, comment="文件存储路径")

    # 文件大小（字节）
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")

    # MD5 校验值（32位，唯一索引，用于防重复）
    md5 = Column(String(32), unique=True, nullable=False, index=True, comment="文件MD5")

    # 文件类型（MIME type）
    content_type = Column(String(100), nullable=False, comment="文件类型")

    # 解析后的文本内容
    content = Column(Text, nullable=True, comment="解析后的文本内容")

    # 上传时间
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="上传时间")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', md5='{self.md5}')>"
