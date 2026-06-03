"""
解析器基类 - 定义所有解析器必须实现的接口
"""
import os
from abc import ABC, abstractmethod
from typing import Optional

from app.schemas.document import ParseResult


class BaseParser(ABC):
    """
    所有文档解析器的抽象基类
    
    子类必须实现 parse 方法，并设置 SUPPORTED_EXTENSIONS 列表
    """
    
    # 子类必须重写此属性，定义支持的文件扩展名
    SUPPORTED_EXTENSIONS: list[str] = []
    
    def can_parse(self, filename: str) -> bool:
        """
        判断是否支持该文件类型
        
        Args:
            filename: 文件名（含扩展名）
        
        Returns:
            bool: 是否支持解析该文件
        """
        # 获取文件扩展名（小写）
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.SUPPORTED_EXTENSIONS
    
    @abstractmethod
    def parse(self, file_path: str) -> ParseResult:
        """
        解析文件，返回解析结果
        
        Args:
            file_path: 文件的完整路径
        
        Returns:
            ParseResult: 解析结果对象
        
        Raises:
            NotImplementedError: 子类未实现此方法时抛出
        """
        raise NotImplementedError("子类必须实现 parse 方法")
