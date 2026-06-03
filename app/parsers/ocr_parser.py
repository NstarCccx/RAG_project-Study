"""
OCR 图片解析器
使用 PaddleOCR 识别图片中的文字
支持扫描件、图片格式的文档
"""
import os

from app.parsers.base_parser import BaseParser
from app.schemas.document import ParseResult
from app.core.log import logger


class OcrParser(BaseParser):
    """
    OCR 图片解析器
    
    支持的文件类型：
    - .jpg: JPEG 图片
    - .jpeg: JPEG 图片（完整扩展名）
    - .png: PNG 图片
    - .bmp: BMP 图片
    - .tiff: TIFF 图片
    - .tif: TIFF 图片（简写扩展名）
    
    依赖：paddlepaddle、paddleocr
    安装命令：
        pip install paddlepaddle
        pip install paddleocr
    """
    
    SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"]
    
    def __init__(self):
        """初始化解析器"""
        # 延迟初始化 OCR 模型
        self.ocr = None
    
    def _ensure_dependencies(self):
        """确保依赖已安装并初始化 OCR"""
        if self.ocr is None:
            try:
                from paddleocr import PaddleOCR
                
                # 初始化 PaddleOCR
                # use_angle_cls=True: 启用角度检测
                # lang="ch": 中英文识别
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang="ch",
                    show_log=False
                )
            except ImportError:
                raise ImportError(
                    "未安装 paddleocr，请运行:\n"
                    "pip install paddlepaddle\n"
                    "pip install paddleocr"
                )
    
    def parse(self, file_path: str) -> ParseResult:
        """
        使用 OCR 解析图片中的文字
        
        Args:
            file_path: 文件的完整路径
        
        Returns:
            ParseResult: 解析结果
        """
        logger.info(f"开始 OCR 识别图片: {file_path}")
        
        try:
            self._ensure_dependencies()
            
            # 执行 OCR 识别
            result = self.ocr.ocr(file_path, cls=True)
            
            # 提取识别结果
            content_lines = []
            for page in result:
                for line in page:
                    # line[1][0] 是识别出的文本内容
                    text = line[1][0]
                    if text.strip():
                        content_lines.append(text.strip())
            
            content = "\n".join(content_lines)
            
            logger.info(f"OCR 识别成功，内容长度: {len(content)} 字符")
            return ParseResult(
                success=True,
                content=content,
                file_type="ocr",
                page_count=len(result) if result else 0,
                error=None
            )
        
        except ImportError as e:
            error_msg = str(e)
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="ocr",
                page_count=None,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"OCR 识别失败: {str(e)}"
            logger.error(error_msg)
            return ParseResult(
                success=False,
                content="",
                file_type="ocr",
                page_count=None,
                error=error_msg
            )
