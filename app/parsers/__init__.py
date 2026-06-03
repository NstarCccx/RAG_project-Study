"""
文档解析模块

提供统一的文档解析入口，支持多种文件格式：
- TXT/MD 纯文本文件
- PDF 文件（使用 pdfplumber）
- 图片/OCR 识别（使用 PaddleOCR）
- Word 文档（使用 unstructured）

使用方式：
    from app.parsers import ParserFactory
    
    # 自动识别文件类型并解析
    result = ParserFactory.parse("/path/to/document.pdf")
    
    if result.success:
        print(result.content)
    else:
        print(f"解析失败: {result.error}")
"""

# 导出核心类和函数
from app.parsers.base_parser import BaseParser
from app.parsers.parser_factory import ParserFactory
from app.parsers.txt_parser import TxtParser
from app.parsers.pdf_parser import PdfParser
from app.parsers.ocr_parser import OcrParser
from app.parsers.word_parser import WordParser

# 导出解析结果模型
from app.schemas.document import ParseResult

__all__ = [
    "BaseParser",
    "ParserFactory",
    "TxtParser",
    "PdfParser",
    "OcrParser",
    "WordParser",
    "ParseResult"
]
