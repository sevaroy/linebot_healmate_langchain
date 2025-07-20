"""
Microsoft GraphRAG 工具
使用正式的 Microsoft GraphRAG 套件
"""

import logging
from langchain.tools import Tool
from services.microsoft_graphrag import microsoft_graphrag_service


async def _create_knowledge_base_tool(query: str, user_id: str = "default_user") -> str:
    """建立 Microsoft GraphRAG 知識庫工具"""
    try:
        # 從查詢中提取名稱（如果有的話）
        name = None
        if "名為" in query or "叫做" in query or "命名為" in query:
            # 簡單的名稱提取
            parts = query.replace("名為", "|").replace("叫做", "|").replace("命名為", "|")
            if "|" in parts:
                name = parts.split("|")[1].strip()
        
        kb_id = await microsoft_graphrag_service.create_knowledge_base(
            user_id=user_id,
            name=name
        )
        
        return f"""✅ Microsoft GraphRAG 知識庫已建立！

🆔 知識庫ID: {kb_id}
📚 使用技術: Microsoft GraphRAG
🔧 功能特色:
   • 先進的實體關係提取
   • 智能社群偵測
   • 多層級知識圖譜分析
   • 本地和全域搜尋

📁 現在你可以上傳文件來建立專業的知識圖譜了！"""
        
    except Exception as e:
        logging.error(f"Error creating Microsoft GraphRAG knowledge base: {e}")
        return f"❌ 建立 GraphRAG 知識庫失敗：{str(e)}"


async def _add_document_tool(query: str, user_id: str = "default_user") -> str:
    """新增文件到 GraphRAG 知識庫工具"""
    try:
        return """📄 Microsoft GraphRAG 文件上傳方式：

🔗 **API 上傳**:
   ```
   POST /graphrag/knowledge-base/{kb_id}/upload
   ```

📋 **支援格式**: 
   • TXT - 純文字文件
   • PDF - PDF 文件  
   • DOC/DOCX - Word 文件
   • MD - Markdown 文件
   • HTML - 網頁文件

⚡ **GraphRAG 建議流程**:
   1️⃣ 建立知識庫
   2️⃣ 上傳多個相關文件
   3️⃣ 執行 GraphRAG 索引建立
   4️⃣ 使用本地/全域搜尋查詢

💡 **GraphRAG 特色**:
   • 自動提取實體和關係
   • 建立階層式知識圖譜
   • 支援複雜推理查詢
   • 社群偵測分析

你也可以直接貼上文字內容，我會幫你加入 GraphRAG 知識庫！"""
        
    except Exception as e:
        logging.error(f"Error in GraphRAG add document tool: {e}")
        return f"❌ 處理失敗：{str(e)}"


async def _list_knowledge_bases_tool(query: str, user_id: str = "default_user") -> str:
    """列出 GraphRAG 知識庫工具"""
    try:
        knowledge_bases = microsoft_graphrag_service.get_knowledge_bases(user_id)
        
        if not knowledge_bases:
            return """📝 你目前沒有任何 Microsoft GraphRAG 知識庫。

🚀 可以說「建立知識圖譜」來開始使用專業的 GraphRAG 技術！

✨ GraphRAG 優勢：
   • 微軟研發的先進技術
   • 自動實體關係提取
   • 智能社群分析
   • 支援複雜推理查詢"""
        
        result = "📚 你的 Microsoft GraphRAG 知識庫列表：\n\n"
        for kb in knowledge_bases:
            status_emoji = {
                'created': '🆕',
                'needs_indexing': '⏳', 
                'indexing': '🔄',
                'ready': '✅',
                'error': '❌'
            }.get(kb['status'], '❓')
            
            result += f"{status_emoji} **{kb['name']}**\n"
            result += f"   🆔 ID: {kb['kb_id'][:8]}...\n"
            result += f"   📊 狀態: {kb['status']}\n"
            result += f"   📄 文件數: {len(kb.get('documents', []))}\n"
            result += f"   🕒 建立時間: {kb['created_at'][:19]}\n\n"
        
        return result
        
    except Exception as e:
        logging.error(f"Error listing GraphRAG knowledge bases: {e}")
        return f"❌ 無法取得 GraphRAG 知識庫清單：{str(e)}"


async def _query_graphrag_tool(query: str, user_id: str = "default_user") -> str:
    """查詢 Microsoft GraphRAG 工具"""
    try:
        knowledge_bases = microsoft_graphrag_service.get_knowledge_bases(user_id)
        
        if not knowledge_bases:
            return """❌ 你還沒有建立任何 Microsoft GraphRAG 知識庫。

🚀 請先說「建立知識圖譜」來開始使用專業的 GraphRAG 技術！"""
        
        # 找到最新的就緒知識庫
        ready_kbs = [kb for kb in knowledge_bases if kb['status'] == 'ready']
        
        if not ready_kbs:
            return """❌ 你的 GraphRAG 知識庫還沒有建立索引。

📋 請依照以下步驟：
   1️⃣ 上傳文件到知識庫
   2️⃣ 執行 GraphRAG 索引建立
   3️⃣ 等待索引完成後開始查詢

💡 GraphRAG 索引建立需要一些時間，但能提供更精確的查詢結果！"""
        
        # 使用最新的知識庫進行全域搜尋（GraphRAG 的特色功能）
        kb = ready_kbs[-1]
        kb_id = kb['kb_id']
        
        # 執行 GraphRAG 全域搜尋
        result = await microsoft_graphrag_service.query_global(kb_id, query)
        
        if result['success']:
            return f"""🔍 **Microsoft GraphRAG 全域搜尋結果**

📚 知識庫：「{kb['name']}」
🧠 查詢方式：GraphRAG 全域分析

**回答：**
{result['answer']}

💡 這個回答基於 GraphRAG 的社群偵測和知識圖譜分析技術生成。"""
        else:
            return f"❌ GraphRAG 查詢失敗：{result['message']}"
            
    except Exception as e:
        logging.error(f"Error querying Microsoft GraphRAG: {e}")
        return f"❌ GraphRAG 查詢過程中發生錯誤：{str(e)}"


async def _index_knowledge_base_tool(query: str, user_id: str = "default_user") -> str:
    """建立 GraphRAG 索引工具"""
    try:
        knowledge_bases = microsoft_graphrag_service.get_knowledge_bases(user_id)
        
        if not knowledge_bases:
            return "❌ 你還沒有建立任何知識庫。請先說「建立知識圖譜」。"
        
        # 找到需要索引的知識庫
        needs_indexing = [kb for kb in knowledge_bases if kb['status'] in ['created', 'needs_indexing']]
        
        if not needs_indexing:
            return "✅ 你的所有知識庫都已建立索引或正在處理中！"
        
        # 對最新的知識庫建立索引
        kb = needs_indexing[-1]
        kb_id = kb['kb_id']
        
        result = await microsoft_graphrag_service.index_knowledge_base(kb_id)
        
        if result['success']:
            return f"""✅ Microsoft GraphRAG 索引建立成功！

📚 知識庫：「{kb['name']}」
🔧 已完成：
   • 實體提取和關係分析
   • 社群偵測和層級建構  
   • 知識圖譜優化
   • 搜尋索引建立

🎉 現在可以開始進行 GraphRAG 查詢了！"""
        else:
            return f"❌ GraphRAG 索引建立失敗：{result['message']}"
            
    except Exception as e:
        logging.error(f"Error indexing GraphRAG knowledge base: {e}")
        return f"❌ 索引建立過程中發生錯誤：{str(e)}"


# 建立 LangChain Tool 實例
create_ms_graphrag_kb_tool = Tool(
    name="CreateMicrosoftGraphRAGKnowledgeBase",
    description="""當用戶想要建立專業的知識圖譜、使用 Microsoft GraphRAG 或建立高級知識庫時使用。
    適用於包含「建立知識圖譜」、「GraphRAG」、「專業知識庫」、「智能分析」等關鍵詞的請求。
    輸入應該是用戶的完整請求。""",
    func=None,
    coroutine=_create_knowledge_base_tool,
)

add_ms_graphrag_document_tool = Tool(
    name="AddMicrosoftGraphRAGDocument", 
    description="""當用戶詢問如何上傳文件到 GraphRAG 知識庫或想要新增文件進行圖譜分析時使用。
    提供 Microsoft GraphRAG 文件上傳的專業指引和說明。
    輸入應該是用戶的完整請求。""",
    func=None,
    coroutine=_add_document_tool,
)

list_ms_graphrag_kb_tool = Tool(
    name="ListMicrosoftGraphRAGKnowledgeBases",
    description="""當用戶想要查看他們的 Microsoft GraphRAG 知識庫清單時使用。
    適用於包含「我的知識庫」、「GraphRAG 清單」、「查看知識庫」等關鍵詞的請求。
    輸入應該是用戶的完整請求。""",
    func=None,
    coroutine=_list_knowledge_bases_tool,
)

query_ms_graphrag_tool = Tool(
    name="QueryMicrosoftGraphRAG",
    description="""當用戶想要基於 Microsoft GraphRAG 知識庫進行深度查詢或複雜推理時使用。
    適用於需要從專業知識圖譜中查找答案、進行社群分析或複雜推理的問題。
    輸入應該是用戶的完整問題。""",
    func=None,
    coroutine=_query_graphrag_tool,
)

index_ms_graphrag_tool = Tool(
    name="IndexMicrosoftGraphRAGKnowledgeBase",
    description="""當用戶想要對 GraphRAG 知識庫建立索引或準備開始查詢時使用。
    適用於包含「建立索引」、「準備查詢」、「開始分析」等關鍵詞的請求。
    輸入應該是用戶的完整請求。""",
    func=None,
    coroutine=_index_knowledge_base_tool,
)

# 導出工具清單
MICROSOFT_GRAPHRAG_TOOLS = [
    create_ms_graphrag_kb_tool,
    add_ms_graphrag_document_tool, 
    list_ms_graphrag_kb_tool,
    query_ms_graphrag_tool,
    index_ms_graphrag_tool
]