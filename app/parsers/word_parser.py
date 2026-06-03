"""
Word 文档解析器
使用 unstructured 库解析 Word 文档
支持 .docx 和 .doc 格式
"""
import os

from app.parsers.base_parser import BaseParser
from app.schemas.document import ParseResult
from app.core.log import logger


class WordParser(BaseParser):
    """
    Word 文档解析器
    
    支持的文件类型：
    - .docx: Office Open XML 格式（新版 Word）
    - .doc: 旧版 Word 格式（需要 antiword 或 libreoffice）
    
    依赖：unstructured[docx]
    安装命令：pip install "unstructured[docx]"
    
    对于 .doc 格式，需要额外安装：
    - macOS: brew install antiword
    - Ubuntu: sudo apt-get install antiword
    - 或使用 libreoffice
    """
    
    SUPPORTED_EXTENSIONS = [".docx", ".doc"]
    
    def __init__(self):
        """初始化解析器"""
        # 延迟导入，避免启动时加载
        self.partition_docx = None
        self.partition_doc = None
    
    def _ensure_dependencies(self):
        """确保依赖已安装"""
        if self.partition_docx is None:
            try:
                from unstructured.partition.docx import partition_docx
                self.partition_docx = partition_docx
            except ImportError:
                raise ImportError(
                    "未安装 unstructured，请运行: pip install 'unstructured[docx]'"
                )
        
        if self.partition_doc is None:
            try:
                from unstructured.partition.doc import partition_doc
                self.partition_doc = partition_doc
            except ImportError:
                # .doc 支持是可选的
                self.partition_doc = None
    
    def parse(self, file_path: str) -> ParseResult:
        """
        解析 Word 文档
        
        Args:
            file_path: 文件的完整路径
        
        Returns:
            ParseResult: 解析结果
        """
        logger.info(f"开始解析 Word 文件: {file_path}")
        
        try:
            self._ensure_dependencies()
            
            # 获取文件扩展名
            ext = os.path.splitext(file_path)[1].lower()
            
            # 根据扩展名选择解析方法
            if ext == ".docx":
                elements = self.partition_docx(file_path)
            elif ext == ".doc":
                if self.partition_doc is None:
                    raise NotImplementedError(
                        ".doc 格式需要安装 unstructured[doc] 依赖"
                    )
                elements = self.partition_doc(file_path)
            else:
                raise ValueError(f"不支持的文件类型: {ext}")
            
            # 提取文本内容
            content_lines = []
            for element in elements:
                text = str(element).strip()
                if text:
                    content_lines.append(text)
            
            content = "\n\n".join(content_lines)
            
            logger.info(f"Word 文件解析成功，内容长度: {len(content)} 字符")
            return ParseResult(
                success=True,
                content=content,
                file_type="word",
                page_count=None,
                error=None
            )
        
        except ImportError as e:
            error_msg = str(e)
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="word",
                page_count=None,
                error=error_msg
            )
        except NotImplementedError as e:
            error_msg = str(e)
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="word",
                page_count=None,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Word 文件解析失败: {str(e)}"
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="word",
                page_count=None,
                error=error_msg
            )
