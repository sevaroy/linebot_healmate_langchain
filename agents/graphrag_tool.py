"""
GraphRAG 工具模組
為 LangChain agent 提供 GraphRAG 相關工具
"""

from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import logging
import asyncio

from services.graphrag import graphrag_service


class CreateKnowledgeBaseInput(BaseModel):
    """建立知識庫的輸入參數"""
    name: Optional[str] = Field(None, description="知識庫名稱")


class AddDocumentInput(BaseModel):
    """新增文件的輸入參數"""
    kb_id: str = Field(..., description="知識庫ID")
    content: str = Field(..., description="文件內容")
    filename: str = Field(..., description="文件名稱")


class IndexKnowledgeBaseInput(BaseModel):
    """索引知識庫的輸入參數"""
    kb_id: str = Field(..., description="知識庫ID")


class QueryGraphRAGInput(BaseModel):
    """查詢 GraphRAG 的輸入參數"""
    kb_id: str = Field(..., description="知識庫ID")
    query: str = Field(..., description="查詢問題")
    method: str = Field("local", description="查詢方法：local 或 global")


class CreateKnowledgeBaseTool(BaseTool):
    """建立知識庫工具"""
    name: str = "create_knowledge_base"
    description: str = """建立新的 GraphRAG 知識庫。當用戶說要建立知識圖譜或想要上傳文件時使用此工具。"""
    args_schema = CreateKnowledgeBaseInput

    def _run(self, name: Optional[str] = None, **kwargs) -> str:
        """同步執行（不推薦）"""
        return "請使用異步版本"

    async def _arun(self, name: Optional[str] = None, **kwargs) -> str:
        """異步執行"""
        try:
            # 從 kwargs 獲取 user_id（應該由 agent 傳入）
            user_id = kwargs.get('user_id', 'default_user')
            
            kb_id = await graphrag_service.create_knowledge_base(
                user_id=user_id,
                name=name
            )
            
            return f"✅ 知識庫已建立！\n知識庫ID: {kb_id}\n你現在可以上傳文件來建立知識圖譜了。"
            
        except Exception as e:
            logging.error(f"Error creating knowledge base: {e}")
            return f"❌ 建立知識庫失敗：{str(e)}"


class AddDocumentTool(BaseTool):
    """新增文件到知識庫工具"""
    name: str = "add_document"
    description: str = """將文件內容新增到指定的知識庫中。文件內容應該是純文字格式。"""
    args_schema = AddDocumentInput

    def _run(self, kb_id: str, content: str, filename: str, **kwargs) -> str:
        """同步執行（不推薦）"""
        return "請使用異步版本"

    async def _arun(self, kb_id: str, content: str, filename: str, **kwargs) -> str:
        """異步執行"""
        try:
            success = await graphrag_service.add_document(
                kb_id=kb_id,
                content=content,
                filename=filename
            )
            
            if success:
                return f"✅ 文件 '{filename}' 已成功新增到知識庫！\n現在需要重新索引知識庫來更新圖譜。"
            else:
                return f"❌ 新增文件失敗"
                
        except Exception as e:
            logging.error(f"Error adding document: {e}")
            return f"❌ 新增文件失敗：{str(e)}"


class IndexKnowledgeBaseTool(BaseTool):
    """索引知識庫工具"""
    name: str = "index_knowledge_base"
    description: str = """對知識庫進行索引，建立 GraphRAG 知識圖譜。在新增文件後必須執行此操作。"""
    args_schema = IndexKnowledgeBaseInput

    def _run(self, kb_id: str, **kwargs) -> str:
        """同步執行（不推薦）"""
        return "請使用異步版本"

    async def _arun(self, kb_id: str, **kwargs) -> str:
        """異步執行"""
        try:
            result = await graphrag_service.index_knowledge_base(kb_id)
            
            if result['success']:
                return f"✅ 知識圖譜建立完成！\n{result['message']}\n現在可以開始詢問相關問題了。"
            else:
                return f"❌ 知識圖譜建立失敗：{result['message']}"
                
        except Exception as e:
            logging.error(f"Error indexing knowledge base: {e}")
            return f"❌ 索引失敗：{str(e)}"


class QueryGraphRAGTool(BaseTool):
    """查詢 GraphRAG 工具"""
    name: str = "query_graphrag"
    description: str = """使用 GraphRAG 查詢知識庫。支援本地搜尋(local)和全域搜尋(global)兩種方法。"""
    args_schema = QueryGraphRAGInput

    def _run(self, kb_id: str, query: str, method: str = "local", **kwargs) -> str:
        """同步執行（不推薦）"""
        return "請使用異步版本"

    async def _arun(self, kb_id: str, query: str, method: str = "local", **kwargs) -> str:
        """異步執行"""
        try:
            if method == "global":
                result = await graphrag_service.query_global(kb_id, query)
            else:
                result = await graphrag_service.query_local(kb_id, query)
            
            if result['success']:
                return f"📚 GraphRAG 查詢結果：\n\n{result['answer']}"
            else:
                return f"❌ 查詢失敗：{result['message']}"
                
        except Exception as e:
            logging.error(f"Error querying GraphRAG: {e}")
            return f"❌ 查詢過程中發生錯誤：{str(e)}"


class ListKnowledgeBasesTool(BaseTool):
    """列出知識庫工具"""
    name: str = "list_knowledge_bases"
    description: str = """列出用戶的所有知識庫"""

    def _run(self, **kwargs) -> str:
        """同步執行"""
        try:
            user_id = kwargs.get('user_id', 'default_user')
            knowledge_bases = graphrag_service.get_knowledge_bases(user_id)
            
            if not knowledge_bases:
                return "📝 你目前沒有任何知識庫。\n可以說「建立知識圖譜」來開始！"
            
            result = "📚 你的知識庫列表：\n\n"
            for kb in knowledge_bases:
                status_emoji = {
                    'created': '🆕',
                    'needs_indexing': '⏳', 
                    'indexing': '🔄',
                    'ready': '✅',
                    'error': '❌'
                }.get(kb['status'], '❓')
                
                result += f"{status_emoji} {kb['name']}\n"
                result += f"   ID: {kb['kb_id']}\n"
                result += f"   狀態: {kb['status']}\n"
                result += f"   文件數: {len(kb.get('documents', []))}\n\n"
            
            return result
            
        except Exception as e:
            logging.error(f"Error listing knowledge bases: {e}")
            return f"❌ 無法取得知識庫清單：{str(e)}"

    async def _arun(self, **kwargs) -> str:
        """異步執行"""
        return self._run(**kwargs)


# 導出所有工具
GRAPHRAG_TOOLS = [
    CreateKnowledgeBaseTool(),
    AddDocumentTool(),
    IndexKnowledgeBaseTool(),
    QueryGraphRAGTool(),
    ListKnowledgeBasesTool()
]