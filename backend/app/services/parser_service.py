from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import fitz  # PyMuPDF
import docx2txt
import re
import os
import subprocess
from PIL import Image
import pdfplumber
from datetime import datetime

from app import models, schemas
from app.core.config import settings
from .base import BaseService

class ParserService(BaseService[models.Resume, schemas.ResumeCreate, schemas.ResumeUpdate]):
    """简历解析服务"""
    
    def __init__(self):
        super().__init__(models.Resume)

    @staticmethod
    async def _parse_pdf(file_path: str) -> str:
        """使用 PyMuPDF (fitz) 解析 PDF 文件并转换为 Markdown 格式"""
        try:
            print(f"DEBUG - Opening PDF file: {file_path}")
            markdown_parts = []
            
            # 打开PDF文件
            with fitz.open(file_path) as doc:
                print(f"DEBUG - PDF pages: {len(doc)}")
                
                for page_num, page in enumerate(doc):
                    try:
                        print(f"DEBUG - Processing page {page_num + 1}")
                        blocks = page.get_text("dict")["blocks"]
                        
                        for block in blocks:
                            if "lines" in block:
                                for line in block["lines"]:
                                    spans_text = []
                                    
                                    for span in line["spans"]:
                                        if span.get("text"):
                                            spans_text.append(span["text"])
                                            
                                    if spans_text:
                                        line_text = " ".join(spans_text)
                                        # 清理文本
                                        line_text = line_text.replace('\u3000', ' ')  # 替换中文全角空格
                                        line_text = re.sub(r'\s+', ' ', line_text)  # 替换多个空白字符为一个空格
                                        line_text = line_text.strip()  # 去掉前后的空白字符
                                        # 移除重复标点符号
                                        line_text = re.sub(r'([。，、；：？！""''（）【】《》])\1+', r'\1', line_text)
                                        
                                        # 根据字体大小和样式判断标题
                                        font_size = max(span.get("size", 0) for span in line["spans"])
                                        is_bold = any(span.get("flags", 0) & 2 for span in line["spans"])
                                        
                                        if font_size > 14 or is_bold:
                                            line_text = f"## {line_text}"
                                        
                                        markdown_parts.append(line_text)
                                        
                    except Exception as page_error:
                        print(f"DEBUG - Error processing page {page_num + 1}: {str(page_error)}")
                        continue
            
            # 合并处理后的文本
            result = "\n".join(markdown_parts)
            
            # 优化Markdown格式
            # 合并相邻的相同类型的Markdown元素
            result = re.sub(r'- (.*?)\n- ', r'- \1\n- ', result)  # 确保列表项之间只有一个换行
            
            # 移除连续的相同标题
            result = re.sub(r'(## .*?)\n\s*## \1', r'\1', result, flags=re.MULTILINE)
            
            # 优化段落间距
            result = re.sub(r'\n{2,}(## )', r'\n\n\n\1', result)  # 标题前添加额外空行
            
            print(f"DEBUG - Successfully extracted text, length: {len(result)}")
            return result
            
        except Exception as e:
            print(f"DEBUG - PDF parsing failed: {str(e)}")
            raise ValueError(f"PDF解析失败: {str(e)}")

    @staticmethod
    async def _parse_word(file_path: str) -> str:
        """解析 Word 文件，包括正文和表格内容"""
        try:
            print(f"DEBUG - Opening Word file: {file_path}")
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.doc':
                try:
                    print("DEBUG - 使用 antiword 处理 .doc 文件")
                    # 使用 antiword 处理 .doc 文件
                    process = subprocess.run(
                        ['antiword', file_path],
                        capture_output=True,
                        text=True
                    )
                    if process.returncode == 0:
                        return process.stdout
                    else:
                        print(f"DEBUG - antiword failed: {process.stderr}")
                        raise ValueError("DOC文件解析失败")
                except Exception as e:
                    print(f"DEBUG - antiword processing failed: {str(e)}")
                    raise ValueError(f"DOC文件处理失败: {str(e)}")
            
            # 使用 python-docx 处理 .docx 文件
            try:
                from docx import Document
                document = Document(file_path)
                content = []
                
                # 处理正文段落
                for para in document.paragraphs:
                    text = para.text.strip()
                    if text:
                        # 清理文本
                        text = text.replace('\u3000', ' ')
                        text = ' '.join(text.split())
                        content.append(text)
                
                # 处理表格
                for table in document.tables:
                    try:
                        table_content = []
                        for row_idx, row in enumerate(table.rows):
                            cells = []
                            for cell_idx, cell in enumerate(row.cells):
                                try:
                                    text = cell.text.strip()
                                    if text:
                                        # 清理文本
                                        print(f"DEBUG - 单元格 ({row_idx + 1}, {cell_idx + 1}) 原始文本: {text}")
                                        text = text.replace('\u3000', ' ')
                                        text = ' '.join(text.split())
                                        print(f"DEBUG - 单元格 ({row_idx + 1}, {cell_idx + 1}) 清理后文本: {text}")
                                        cells.append(text)
                                except Exception as cell_error:
                                    print(f"DEBUG - Error processing cell ({row_idx + 1}, {cell_idx + 1}): {str(cell_error)}")
                                    continue
                            
                            if cells:  # 其他情况，作为普通行处理
                                # 处理表格行
                                if len(cells) > 1:  # 有多个单元格的情况
                                    # 检查是否存在重复值并清理
                                    cleaned_cells = []
                                    seen = set()
                                    for cell in cells:
                                        cell_text = cell.strip()
                                        if cell_text and cell_text not in seen:
                                            cleaned_cells.append(cell_text)
                                            seen.add(cell_text)
                                    
                                    # 将清理后的单元格文本组合成行
                                    if cleaned_cells:
                                        table_content.append(" | ".join(cleaned_cells))
                                else:  # 单个单元格的情况
                                    table_content.append(cells[0])
                        
                        if table_content:
                            content.extend(table_content)
                            
                    except Exception as table_error:
                        print(f"DEBUG - Error processing table: {str(table_error)}")
                        continue
                
                print(f"DEBUG - 表格处理完成，内容长度: {len(content)}")
                print(f"DEBUG - 表格内容: {content}")
                result = "\n".join(content)
                
                # 验证结果
                if not result.strip():
                    raise ValueError("未能从文档中提取到任何文本内容")
                
                print(f"DEBUG - Successfully extracted text, length: {len(result)}")
                return result
                
            except Exception as e:
                print(f"DEBUG - python-docx parsing failed: {str(e)}")
                print("DEBUG - 尝试使用 docx2txt 提取文本...")
                # 使用 docx2txt 作为备用方案
                try:
                    result = docx2txt.process(file_path)
                    # 清理文本
                    result = result.replace('\u3000', ' ')  # 替换中文全角空格
                    result = '\n'.join(' '.join(line.split()) for line in result.splitlines() if line.strip())
                    
                    if not result.strip():
                        raise ValueError("未能从文档中提取到任何文本内容")
                        
                    print(f"DEBUG - Successfully extracted text, length: {len(result)}")
                    return result
                    
                except Exception as docx2txt_error:
                    print(f"DEBUG - docx2txt parsing failed: {str(docx2txt_error)}")
                    raise ValueError(f"Word文档解析失败: {str(docx2txt_error)}")
                    
        except Exception as e:
            print(f"DEBUG - Document parsing completely failed: {str(e)}")
            raise ValueError(f"文档解析失败: {str(e)}")

    @staticmethod
    async def _parse_image(file_path: str) -> str:
        """解析图片文件"""
        try:
            print(f"DEBUG - Opening image file: {file_path}")
            # 添加图片验证
            with Image.open(file_path) as image:
                # 验证图片完整性
                image.verify()
                # 重新打开图片进行处理
                image = Image.open(file_path)
                # 添加图片预处理
                # TODO: 实现OCR功能
                raise NotImplementedError("图片OCR功能尚未实现")
                
        except Exception as e:
            print(f"DEBUG - Image parsing failed: {str(e)}")
            raise ValueError(f"图片解析失败: {str(e)}")

    @staticmethod
    async def _parse_pdf_with_pdfplumber(file_path: str) -> str:
        """使用 pdfplumber 解析 PDF 文件"""
        import pdfplumber
        
        text = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return "\n".join(text)
        except Exception as e:
            print(f"DEBUG - Error parsing PDF with pdfplumber: {str(e)}")
            return ""

    async def parse_resume(self, file_path: str) -> str:
        """解析简历文件，提取文本内容"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return await self._parse_pdf(file_path)
            elif file_ext in ['.doc', '.docx']:
                return await self._parse_word(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"简历解析失败: {str(e)}"
            )

# 创建服务实例
parser_service = ParserService()

# 只导出实例
__all__ = ["parser_service"] 