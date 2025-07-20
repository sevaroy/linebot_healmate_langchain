"""
GraphRAG API 端點
提供 GraphRAG 相關的 HTTP API 端點
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
import logging

from services.simple_graphrag import graphrag_service
from services.microsoft_graphrag import microsoft_graphrag_service
from agents.file_upload_handler import file_upload_handler

# 建立路由器
router = APIRouter(prefix="/graphrag", tags=["GraphRAG"])

# --- 請求模型 ---

class CreateKnowledgeBaseRequest(BaseModel):
    user_id: str
    name: Optional[str] = None

class AddDocumentRequest(BaseModel):
    kb_id: str
    content: str
    filename: str

class IndexKnowledgeBaseRequest(BaseModel):
    kb_id: str

class QueryRequest(BaseModel):
    kb_id: str
    query: str
    method: str = "local"  # local 或 global

# --- API 端點 ---

@router.post("/knowledge-base")
async def create_knowledge_base(request: CreateKnowledgeBaseRequest) -> Dict[str, Any]:
    """建立新的知識庫"""
    try:
        kb_id = await graphrag_service.create_knowledge_base(
            user_id=request.user_id,
            name=request.name
        )
        
        return {
            "success": True,
            "kb_id": kb_id,
            "message": "知識庫建立成功"
        }
        
    except Exception as e:
        logging.error(f"Error creating knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-base/{kb_id}/document")
async def add_document(kb_id: str, request: AddDocumentRequest) -> Dict[str, Any]:
    """新增文件到知識庫"""
    try:
        success = await graphrag_service.add_document(
            kb_id=kb_id,
            content=request.content,
            filename=request.filename
        )
        
        if success:
            return {
                "success": True,
                "message": f"文件 '{request.filename}' 新增成功"
            }
        else:
            raise HTTPException(status_code=400, detail="文件新增失敗")
            
    except Exception as e:
        logging.error(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-base/{kb_id}/upload")
async def upload_file(
    kb_id: str,
    user_id: str = Form(...),
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """上傳文件到知識庫"""
    try:
        result = await file_upload_handler.handle_file_upload(
            file=file,
            user_id=user_id,
            kb_id=kb_id
        )
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-base/{kb_id}/index")
async def index_knowledge_base(kb_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """建立知識庫索引"""
    try:
        # 在背景執行索引建立，因為這可能需要較長時間
        background_tasks.add_task(graphrag_service.index_knowledge_base, kb_id)
        
        return {
            "success": True,
            "message": "索引建立已開始，請稍後查詢狀態"
        }
        
    except Exception as e:
        logging.error(f"Error starting indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-base/{kb_id}/index/sync")
async def index_knowledge_base_sync(kb_id: str) -> Dict[str, Any]:
    """同步建立知識庫索引"""
    try:
        result = await graphrag_service.index_knowledge_base(kb_id)
        return result
        
    except Exception as e:
        logging.error(f"Error indexing knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-base/{kb_id}/query")
async def query_knowledge_base(kb_id: str, request: QueryRequest) -> Dict[str, Any]:
    """查詢知識庫"""
    try:
        if request.method == "global":
            result = await graphrag_service.query_global(kb_id, request.query)
        else:
            result = await graphrag_service.query_local(kb_id, request.query)
        
        return result
        
    except Exception as e:
        logging.error(f"Error querying knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base")
async def list_knowledge_bases(user_id: Optional[str] = None) -> Dict[str, Any]:
    """列出知識庫"""
    try:
        knowledge_bases = graphrag_service.get_knowledge_bases(user_id)
        
        return {
            "success": True,
            "knowledge_bases": knowledge_bases,
            "count": len(knowledge_bases)
        }
        
    except Exception as e:
        logging.error(f"Error listing knowledge bases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base/{kb_id}")
async def get_knowledge_base(kb_id: str) -> Dict[str, Any]:
    """取得特定知識庫資訊"""
    try:
        kb_info = graphrag_service.get_knowledge_base_info(kb_id)
        
        if kb_info:
            return {
                "success": True,
                "knowledge_base": kb_info
            }
        else:
            raise HTTPException(status_code=404, detail="知識庫不存在")
            
    except Exception as e:
        logging.error(f"Error getting knowledge base info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/knowledge-base/{kb_id}")
async def delete_knowledge_base(kb_id: str, user_id: str) -> Dict[str, Any]:
    """刪除知識庫"""
    try:
        success = graphrag_service.delete_knowledge_base(kb_id, user_id)
        
        if success:
            return {
                "success": True,
                "message": "知識庫刪除成功"
            }
        else:
            raise HTTPException(status_code=400, detail="刪除失敗或權限不足")
            
    except Exception as e:
        logging.error(f"Error deleting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-formats")
async def get_supported_formats() -> Dict[str, Any]:
    """取得支援的文件格式"""
    return {
        "success": True,
        "info": file_upload_handler.get_supported_formats_info(),
        "formats": list(file_upload_handler.SUPPORTED_TEXT_FORMATS.values()),
        "max_size_mb": file_upload_handler.MAX_FILE_SIZE // 1024 // 1024
    }

# --- Microsoft GraphRAG 專用端點 ---

@router.post("/microsoft/knowledge-base")
async def create_microsoft_knowledge_base(request: CreateKnowledgeBaseRequest) -> Dict[str, Any]:
    """建立新的 Microsoft GraphRAG 知識庫"""
    try:
        kb_id = await microsoft_graphrag_service.create_knowledge_base(
            user_id=request.user_id,
            name=request.name
        )
        
        return {
            "success": True,
            "kb_id": kb_id,
            "message": "Microsoft GraphRAG 知識庫建立成功",
            "type": "microsoft_graphrag"
        }
        
    except Exception as e:
        logging.error(f"Error creating Microsoft GraphRAG knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/microsoft/knowledge-base/{kb_id}/document")
async def add_microsoft_document(kb_id: str, request: AddDocumentRequest) -> Dict[str, Any]:
    """新增文件到 Microsoft GraphRAG 知識庫"""
    try:
        success = await microsoft_graphrag_service.add_document(
            kb_id=kb_id,
            content=request.content,
            filename=request.filename
        )
        
        if success:
            return {
                "success": True,
                "message": f"文件 '{request.filename}' 已新增到 Microsoft GraphRAG 知識庫",
                "type": "microsoft_graphrag"
            }
        else:
            raise HTTPException(status_code=400, detail="文件新增失敗")
            
    except Exception as e:
        logging.error(f"Error adding document to Microsoft GraphRAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/microsoft/knowledge-base/{kb_id}/upload")
async def upload_microsoft_file(
    kb_id: str,
    user_id: str = Form(...),
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """上傳文件到 Microsoft GraphRAG 知識庫"""
    try:
        # 讀取文件內容
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')
        
        success = await microsoft_graphrag_service.add_document(
            kb_id=kb_id,
            content=text_content,
            filename=file.filename or "uploaded_file.txt"
        )
        
        if success:
            return {
                "success": True,
                "message": f"文件 '{file.filename}' 已上傳到 Microsoft GraphRAG 知識庫",
                "type": "microsoft_graphrag",
                "next_step": "請執行索引建立以啟用 GraphRAG 功能"
            }
        else:
            raise HTTPException(status_code=400, detail="文件上傳失敗")
            
    except Exception as e:
        logging.error(f"Error uploading file to Microsoft GraphRAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/microsoft/knowledge-base/{kb_id}/index")
async def index_microsoft_knowledge_base(kb_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """建立 Microsoft GraphRAG 知識庫索引"""
    try:
        # 在背景執行索引建立
        background_tasks.add_task(microsoft_graphrag_service.index_knowledge_base, kb_id)
        
        return {
            "success": True,
            "message": "Microsoft GraphRAG 索引建立已開始，這可能需要幾分鐘時間",
            "type": "microsoft_graphrag"
        }
        
    except Exception as e:
        logging.error(f"Error starting Microsoft GraphRAG indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/microsoft/knowledge-base/{kb_id}/index/sync")
async def index_microsoft_knowledge_base_sync(kb_id: str) -> Dict[str, Any]:
    """同步建立 Microsoft GraphRAG 知識庫索引"""
    try:
        result = await microsoft_graphrag_service.index_knowledge_base(kb_id)
        result["type"] = "microsoft_graphrag"
        return result
        
    except Exception as e:
        logging.error(f"Error indexing Microsoft GraphRAG knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/microsoft/knowledge-base/{kb_id}/query")
async def query_microsoft_knowledge_base(kb_id: str, request: QueryRequest) -> Dict[str, Any]:
    """查詢 Microsoft GraphRAG 知識庫"""
    try:
        if request.method == "global":
            result = await microsoft_graphrag_service.query_global(kb_id, request.query)
        else:
            result = await microsoft_graphrag_service.query_local(kb_id, request.query)
        
        result["type"] = "microsoft_graphrag"
        return result
        
    except Exception as e:
        logging.error(f"Error querying Microsoft GraphRAG knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/microsoft/knowledge-base")
async def list_microsoft_knowledge_bases(user_id: Optional[str] = None) -> Dict[str, Any]:
    """列出 Microsoft GraphRAG 知識庫"""
    try:
        knowledge_bases = microsoft_graphrag_service.get_knowledge_bases(user_id)
        
        return {
            "success": True,
            "knowledge_bases": knowledge_bases,
            "count": len(knowledge_bases),
            "type": "microsoft_graphrag"
        }
        
    except Exception as e:
        logging.error(f"Error listing Microsoft GraphRAG knowledge bases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/microsoft/knowledge-base/{kb_id}")
async def get_microsoft_knowledge_base(kb_id: str) -> Dict[str, Any]:
    """取得特定 Microsoft GraphRAG 知識庫資訊"""
    try:
        kb_info = microsoft_graphrag_service.get_knowledge_base_info(kb_id)
        
        if kb_info:
            return {
                "success": True,
                "knowledge_base": kb_info,
                "type": "microsoft_graphrag"
            }
        else:
            raise HTTPException(status_code=404, detail="Microsoft GraphRAG 知識庫不存在")
            
    except Exception as e:
        logging.error(f"Error getting Microsoft GraphRAG knowledge base info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/microsoft/knowledge-base/{kb_id}")
async def delete_microsoft_knowledge_base(kb_id: str, user_id: str) -> Dict[str, Any]:
    """刪除 Microsoft GraphRAG 知識庫"""
    try:
        success = microsoft_graphrag_service.delete_knowledge_base(kb_id, user_id)
        
        if success:
            return {
                "success": True,
                "message": "Microsoft GraphRAG 知識庫刪除成功",
                "type": "microsoft_graphrag"
            }
        else:
            raise HTTPException(status_code=400, detail="刪除失敗或權限不足")
            
    except Exception as e:
        logging.error(f"Error deleting Microsoft GraphRAG knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))