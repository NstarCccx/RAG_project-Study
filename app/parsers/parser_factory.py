"""
解析器工厂 - 统一文档解析入口

根据文件扩展名自动选择合适的解析器，实现解析器的注册和调度
"""
import os
from typing import Type, Optional

from app.parsers.base_parser import BaseParser
from app.schemas.document import ParseResult
from app.core.log import logger


class ParserFactory:
    """
    解析器工厂类
    
    提供统一的文档解析入口，支持自动识别文件类型并选择合适的解析器
    
    使用方式：
        # 注册解析器
        ParserFactory.register_parser(TxtParser)
        ParserFactory.register_parser(PdfParser)
        
        # 自动识别并解析
        result = ParserFactory.parse("/path/to/file.pdf")
    """
    
    # 存储已注册的解析器类
    _parsers: list[Type[BaseParser]] = []
    
    @classmethod
    def register_parser(cls, parser_class: Type[BaseParser]) -> None:
        """
        注册解析器
        
        Args:
            parser_class: 解析器类（必须继承自 BaseParser）
        
        Raises:
            TypeError: 如果 parser_class 不是 BaseParser 的子类
        """
        if not issubclass(parser_class, BaseParser):
            raise TypeError(f"解析器类必须继承自 BaseParser，当前类型: {type(parser_class)}")
        
        if parser_class not in cls._parsers:
            cls._parsers.append(parser_class)
            logger.info(f"已注册解析器: {parser_class.__name__}")
    
    @classmethod
    def get_parser(cls, filename: str) -> Optional[BaseParser]:
        """
        根据文件名获取合适的解析器
        
        Args:
            filename: 文件名（含扩展名）
        
        Returns:
            Optional[BaseParser]: 解析器实例，如果没有找到则返回 None
        """
        for parser_class in cls._parsers:
            parser = parser_class()
            if parser.can_parse(filename):
                logger.debug(f"为文件 {filename} 选择解析器: {parser_class.__name__}")
                return parser
        
        logger.warning(f"未找到支持 {filename} 的解析器")
        return None
    
    @classmethod
    def parse(cls, file_path: str) -> ParseResult:
        """
        统一解析入口 - 自动识别文件类型并解析
        
        Args:
            file_path: 文件的完整路径
        
        Returns:
            ParseResult: 解析结果
        """
        # 获取文件名
        filename = os.path.basename(file_path)
        logger.info(f"开始解析文件: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            error_msg = f"文件不存在: {file_path}"
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="unknown",
                page_count=None,
                error=error_msg
            )
        
        # 获取解析器
        parser = cls.get_parser(filename)
        if parser is None:
            error_msg = f"不支持的文件类型: {filename}"
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="unknown",
                page_count=None,
                error=error_msg
            )
        
        # 执行解析
        return parser.parse(file_path)
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """
        获取所有支持的文件扩展名
        
        Returns:
            list[str]: 支持的扩展名列表
        """
        extensions = []
        for parser_class in cls._parsers:
            extensions.extend(parser_class.SUPPORTED_EXTENSIONS)
        return list(set(extensions))
    
    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """
        判断文件是否支持解析
        
        Args:
            filename: 文件名（含扩展名）
        
        Returns:
            bool: 是否支持
        """
        return cls.get_parser(filename) is not None


# 自动注册所有解析器
# 这样在导入 parser_factory 时就自动注册好了
try:
    from app.parsers.txt_parser import TxtParser
    ParserFactory.register_parser(TxtParser)
except ImportError as e:
    logger.warning(f"无法注册 TxtParser: {e}")

try:
    from app.parsers.pdf_parser import PdfParser
    ParserFactory.register_parser(PdfParser)
except ImportError as e:
    logger.warning(f"无法注册 PdfParser: {e}")

try:
    from app.parsers.ocr_parser import OcrParser
    ParserFactory.register_parser(OcrParser)
except ImportError as e:
    logger.warning(f"无法注册 OcrParser: {e}")

try:
    from app.parsers.word_parser import WordParser
    ParserFactory.register_parser(WordParser)
except ImportError as e:
    logger.warning(f"无法注册 WordParser: {e}")
