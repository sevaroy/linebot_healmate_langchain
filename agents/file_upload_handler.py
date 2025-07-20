"""
文件上傳處理器
處理用戶上傳的文件並整合到 GraphRAG 系統中
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import aiofiles
from fastapi import UploadFile
import mimetypes

from services.simple_graphrag import graphrag_service


class FileUploadHandler:
    """文件上傳處理器"""
    
    SUPPORTED_TEXT_FORMATS = {
        'text/plain': '.txt',
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'text/markdown': '.md',
        'text/html': '.html'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "healmate_uploads"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def handle_file_upload(self, file: UploadFile, user_id: str, kb_id: str = None) -> Dict[str, Any]:
        """
        處理文件上傳
        
        Args:
            file: 上傳的文件
            user_id: 用戶ID
            kb_id: 知識庫ID，如果為 None 會自動建立新的知識庫
        
        Returns:
            處理結果字典
        """
        try:
            # 檢查文件大小
            if file.size and file.size > self.MAX_FILE_SIZE:
                return {
                    'success': False,
                    'message': f'文件大小超過限制 ({self.MAX_FILE_SIZE // 1024 // 1024}MB)'
                }
            
            # 檢查文件類型
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
            if content_type not in self.SUPPORTED_TEXT_FORMATS:
                return {
                    'success': False,
                    'message': f'不支援的文件格式。支援格式：{", ".join(self.SUPPORTED_TEXT_FORMATS.values())}'
                }
            
            # 讀取文件內容
            content = await self._extract_text_content(file, content_type)
            if not content.strip():
                return {
                    'success': False,
                    'message': '文件內容為空或無法讀取'
                }
            
            # 如果沒有指定知識庫，建立新的
            if not kb_id:
                kb_id = await graphrag_service.create_knowledge_base(
                    user_id=user_id,
                    name=f"來自文件 {file.filename} 的知識庫"
                )
                logging.info(f"Created new knowledge base {kb_id} for file upload")
            
            # 新增文件到知識庫
            success = await graphrag_service.add_document(
                kb_id=kb_id,
                content=content,
                filename=file.filename
            )
            
            if not success:
                return {
                    'success': False,
                    'message': '文件新增到知識庫失敗'
                }
            
            return {
                'success': True,
                'message': f'文件 "{file.filename}" 已成功上傳！',
                'kb_id': kb_id,
                'filename': file.filename,
                'content_length': len(content),
                'next_step': '需要建立索引才能開始查詢'
            }
            
        except Exception as e:
            logging.error(f"Error handling file upload: {e}")
            return {
                'success': False,
                'message': f'文件處理失敗：{str(e)}'
            }
    
    async def _extract_text_content(self, file: UploadFile, content_type: str) -> str:
        """提取文件的文字內容"""
        try:
            if content_type == 'text/plain':
                content = await file.read()
                return content.decode('utf-8', errors='ignore')
            
            elif content_type == 'text/markdown':
                content = await file.read()
                return content.decode('utf-8', errors='ignore')
            
            elif content_type == 'text/html':
                content = await file.read()
                # 簡單的 HTML 文字提取，移除標籤
                import re
                text = content.decode('utf-8', errors='ignore')
                text = re.sub(r'<[^>]+>', '', text)
                return text.strip()
            
            elif content_type == 'application/pdf':
                return await self._extract_pdf_text(file)
            
            elif content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                return await self._extract_word_text(file)
            
            else:
                # 嘗試作為純文字讀取
                content = await file.read()
                return content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            logging.error(f"Error extracting text from file: {e}")
            raise
    
    async def _extract_pdf_text(self, file: UploadFile) -> str:
        """提取 PDF 文字內容"""
        try:
            import PyPDF2
            from io import BytesIO
            
            content = await file.read()
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            return text.strip()
            
        except ImportError:
            logging.warning("PyPDF2 not installed, cannot extract PDF text")
            raise Exception("系統不支援 PDF 文件處理，請安裝相關套件")
        except Exception as e:
            logging.error(f"Error extracting PDF text: {e}")
            raise Exception(f"PDF 文件處理失敗：{str(e)}")
    
    async def _extract_word_text(self, file: UploadFile) -> str:
        """提取 Word 文件文字內容"""
        try:
            import python_docx
            from io import BytesIO
            
            content = await file.read()
            doc_file = BytesIO(content)
            doc = python_docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except ImportError:
            logging.warning("python-docx not installed, cannot extract Word text")
            raise Exception("系統不支援 Word 文件處理，請安裝相關套件")
        except Exception as e:
            logging.error(f"Error extracting Word text: {e}")
            raise Exception(f"Word 文件處理失敗：{str(e)}")
    
    def get_supported_formats_info(self) -> str:
        """取得支援格式的說明"""
        formats = list(self.SUPPORTED_TEXT_FORMATS.values())
        return f"支援的文件格式：{', '.join(formats)}\n最大文件大小：{self.MAX_FILE_SIZE // 1024 // 1024}MB"


# 全域實例
file_upload_handler = FileUploadHandler()