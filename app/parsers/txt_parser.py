"""
TXT/MD 纯文本解析器
支持 .txt、.md、.markdown 等纯文本格式
"""
import os
from typing import Optional

from app.parsers.base_parser import BaseParser
from app.schemas.document import ParseResult
from app.core.log import logger


class TxtParser(BaseParser):
    """
    纯文本文件解析器
    
    支持的文件类型：
    - .txt: 普通文本文件
    - .md: Markdown 文件
    - .markdown: Markdown 文件（完整扩展名）
    """
    
    SUPPORTED_EXTENSIONS = [".txt", ".md", ".markdown"]
    
    def __init__(self):
        """初始化解析器"""
        self.encodings = ["utf-8", "gbk", "gb2312", "gb18030", "big5"]
    
    def parse(self, file_path: str) -> ParseResult:
        """
        解析纯文本文件
        
        Args:
            file_path: 文件的完整路径
        
        Returns:
            ParseResult: 解析结果
        """
        logger.info(f"开始解析纯文本文件: {file_path}")
        
        try:
            content = self._read_file_with_fallback(file_path)
            
            logger.info(f"纯文本文件解析成功，内容长度: {len(content)} 字符")
            return ParseResult(
                success=True,
                content=content,
                file_type="txt",
                page_count=None,
                error=None
            )
        
        except Exception as e:
            error_msg = f"纯文本文件解析失败: {str(e)}"
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="txt",
                page_count=None,
                error=error_msg
            )
    
    def _read_file_with_fallback(self, file_path: str) -> str:
        """
        尝试多种编码读取文件，处理编码问题
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: 文件内容
        
        Raises:
            Exception: 所有编码都失败时抛出
        """
        last_exception = None
        
        for encoding in self.encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError as e:
                last_exception = e
                continue
            except Exception as e:
                last_exception = e
                continue
        
        # 所有编码都失败，使用 errors="replace" 模式
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            raise last_exception or Exception("无法读取文件")
