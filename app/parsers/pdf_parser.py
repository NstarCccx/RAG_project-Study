"""
PDF 文件解析器
使用 pdfplumber 库提取 PDF 文本内容
支持普通可复制的 PDF 文件
"""
import os

from app.parsers.base_parser import BaseParser
from app.schemas.document import ParseResult
from app.core.log import logger


class PdfParser(BaseParser):
    """
    PDF 文件解析器
    
    支持的文件类型：
    - .pdf: PDF 文件（仅支持可复制文本的 PDF）
    
    依赖：pdfplumber
    安装命令：pip install pdfplumber
    """
    
    SUPPORTED_EXTENSIONS = [".pdf"]
    
    def __init__(self):
        """初始化解析器"""
        # 延迟导入，避免启动时加载
        self.pdfplumber = None
    
    def _ensure_dependencies(self):
        """确保依赖已安装"""
        if self.pdfplumber is None:
            try:
                import pdfplumber
                self.pdfplumber = pdfplumber
            except ImportError:
                raise ImportError(
                    "未安装 pdfplumber，请运行: pip install pdfplumber"
                )
    
    def parse(self, file_path: str) -> ParseResult:
        """
        解析 PDF 文件
        
        Args:
            file_path: 文件的完整路径
        
        Returns:
            ParseResult: 解析结果
        """
        logger.info(f"开始解析 PDF 文件: {file_path}")
        
        try:
            self._ensure_dependencies()
            
            content = ""
            page_count = 0
            
            with self.pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.debug(f"解析第 {page_num}/{page_count} 页")
                    
                    # 提取文本
                    text = page.extract_text()
                    if text:
                        content += text + "\n\n"
                
                # 清理多余空行
                content = "\n".join([line.strip() for line in content.splitlines() if line.strip()])
            
            logger.info(f"PDF 文件解析成功，页数: {page_count}，内容长度: {len(content)} 字符")
            return ParseResult(
                success=True,
                content=content,
                file_type="pdf",
                page_count=page_count,
                error=None
            )
        
        except ImportError as e:
            error_msg = str(e)
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="pdf",
                page_count=None,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"PDF 文件解析失败: {str(e)}"
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="pdf",
                page_count=None,
                error=error_msg
            )
