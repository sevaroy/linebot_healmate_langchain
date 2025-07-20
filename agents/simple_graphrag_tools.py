"""
簡化版 GraphRAG 工具
使用 LangChain 標準 Tool 避免 Pydantic 版本問題
"""

import logging
from langchain.tools import Tool
from services.simple_graphrag import graphrag_service


async def _create_knowledge_base_tool(query: str, user_id: str = "default_user") -> str:
    """建立知識庫工具"""
    try:
        # 從查詢中提取名稱（如果有的話）
        name = None
        if "名為" in query or "叫做" in query or "命名為" in query:
            # 簡單的名稱提取
            parts = query.replace("名為", "|").replace("叫做", "|").replace("命名為", "|")
            if "|" in parts:
                name = parts.split("|")[1].strip()
        
        kb_id = await graphrag_service.create_knowledge_base(
            user_id=user_id,
            name=name
        )
        
        return f"✅ 知識庫已建立！\n知識庫ID: {kb_id}\n現在你可以上傳文件來建立知識圖譜了。"
        
    except Exception as e:
        logging.error(f"Error creating knowledge base: {e}")
        return f"❌ 建立知識庫失敗：{str(e)}"


async def _add_document_tool(query: str, user_id: str = "default_user") -> str:
    """新增文件工具（透過文字輸入）"""
    try:
        # 這個工具主要用於引導用戶如何上傳文件
        return """📄 文件上傳方式：

1. **透過 API 上傳**:
   ```
   POST /graphrag/knowledge-base/{kb_id}/upload
   ```

2. **支援格式**: TXT, PDF, DOC, DOCX, MD, HTML

3. **建議流程**:
   - 先建立知識庫
   - 上傳文件
   - 建立索引
   - 開始查詢

💡 你也可以直接貼上文字內容，我會幫你加入知識庫！"""
        
    except Exception as e:
        logging.error(f"Error in add document tool: {e}")
        return f"❌ 處理失敗：{str(e)}"


async def _list_knowledge_bases_tool(query: str, user_id: str = "default_user") -> str:
    """列出知識庫工具"""
    try:
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
            result += f"   ID: {kb['kb_id'][:8]}...\n"
            result += f"   狀態: {kb['status']}\n"
            result += f"   文件數: {len(kb.get('documents', []))}\n\n"
        
        return result
        
    except Exception as e:
        logging.error(f"Error listing knowledge bases: {e}")
        return f"❌ 無法取得知識庫清單：{str(e)}"


async def _query_graphrag_tool(query: str, user_id: str = "default_user") -> str:
    """查詢 GraphRAG 工具"""
    try:
        knowledge_bases = graphrag_service.get_knowledge_bases(user_id)
        
        if not knowledge_bases:
            return "❌ 你還沒有建立任何知識庫。請先說「建立知識圖譜」來開始。"
        
        # 找到最新的就緒知識庫
        ready_kbs = [kb for kb in knowledge_bases if kb['status'] == 'ready']
        
        if not ready_kbs:
            return "❌ 你的知識庫還沒有建立索引。請先上傳文件並建立索引。"
        
        # 使用最新的知識庫
        kb = ready_kbs[-1]
        kb_id = kb['kb_id']
        
        # 執行查詢
        result = await graphrag_service.query_local(kb_id, query)
        
        if result['success']:
            return f"📚 根據你的知識庫「{kb['name']}」：\n\n{result['answer']}"
        else:
            return f"❌ 查詢失敗：{result['message']}"
            
    except Exception as e:
        logging.error(f"Error querying GraphRAG: {e}")
        return f"❌ 查詢過程中發生錯誤：{str(e)}"


# 建立 LangChain Tool 實例
create_knowledge_base_tool = Tool(
    name="CreateKnowledgeBase",
    description="""當用戶想要建立知識圖譜、上傳文件或建立知識庫時使用。
    適用於包含「建立知識圖譜」、「上傳文件」、「新增文件」、「建立知識庫」等關鍵詞的請求。
    輸入應該是用戶的完整請求。""",
    func=None,
    coroutine=_create_knowledge_base_tool,
)

add_document_tool = Tool(
    name="AddDocument", 
    description="""當用戶詢問如何上傳文件或想要新增文件到知識庫時使用。
    提供文件上傳的指引和說明。
    輸入應該是用戶的完整請求。""",
    func=None,
    coroutine=_add_document_tool,
)

list_knowledge_bases_tool = Tool(
    name="ListKnowledgeBases",
    description="""當用戶想要查看他們的知識庫清單時使用。
    適用於包含「我的知識庫」、「知識庫清單」、「查看知識庫」等關鍵詞的請求。
    輸入應該是用戶的完整請求。""",
    func=None,
    coroutine=_list_knowledge_bases_tool,
)

query_graphrag_tool = Tool(
    name="QueryGraphRAG",
    description="""當用戶詢問知識庫中的內容或想要基於上傳的文件進行問答時使用。
    適用於需要從知識圖譜中查找答案的問題。
    輸入應該是用戶的完整問題。""",
    func=None,
    coroutine=_query_graphrag_tool,
)

# 導出工具清單
SIMPLE_GRAPHRAG_TOOLS = [
    create_knowledge_base_tool,
    add_document_tool, 
    list_knowledge_bases_tool,
    query_graphrag_tool
]