"""
簡化版 GraphRAG 服務
使用基本的文字分析和檢索功能，避免複雜依賴
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import uuid
import re
import httpx
from collections import defaultdict


class SimpleGraphRAGService:
    """簡化版 GraphRAG 服務類別"""
    
    def __init__(self):
        # API 設定
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # 資料儲存路徑
        self.base_path = Path("data/simple_graphrag")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 知識庫
        self.knowledge_bases = {}
        self.documents = {}
        self.entities = defaultdict(list)  # 實體到文檔的映射
        self.relationships = defaultdict(list)  # 關係列表
        
        self._load_data()
        
        logging.info("Simple GraphRAG service initialized")
    
    def _load_data(self):
        """載入已存在的資料"""
        data_file = self.base_path / "data.json"
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge_bases = data.get('knowledge_bases', {})
                    self.documents = data.get('documents', {})
                    self.entities = defaultdict(list, data.get('entities', {}))
                    self.relationships = defaultdict(list, data.get('relationships', {}))
                logging.info(f"Loaded {len(self.knowledge_bases)} knowledge bases")
            except Exception as e:
                logging.error(f"Failed to load data: {e}")
    
    def _save_data(self):
        """保存資料"""
        try:
            data = {
                'knowledge_bases': self.knowledge_bases,
                'documents': self.documents,
                'entities': dict(self.entities),
                'relationships': dict(self.relationships),
                'updated_at': datetime.now().isoformat()
            }
            
            data_file = self.base_path / "data.json"
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to save data: {e}")
    
    async def create_knowledge_base(self, user_id: str, name: str = None) -> str:
        """建立新的知識庫"""
        kb_id = str(uuid.uuid4())
        
        if name is None:
            name = f"知識庫_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.knowledge_bases[kb_id] = {
            'name': name,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'status': 'created',
            'documents': [],
            'last_indexed': None
        }
        
        self._save_data()
        
        logging.info(f"Created knowledge base {kb_id} for user {user_id}")
        return kb_id
    
    async def add_document(self, kb_id: str, content: str, filename: str) -> bool:
        """新增文件到知識庫"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            doc_id = str(uuid.uuid4())
            
            # 儲存文檔
            self.documents[doc_id] = {
                'kb_id': kb_id,
                'content': content,
                'filename': filename,
                'added_at': datetime.now().isoformat(),
                'processed': False
            }
            
            # 更新知識庫記錄
            self.knowledge_bases[kb_id]['documents'].append(doc_id)
            self.knowledge_bases[kb_id]['status'] = 'needs_indexing'
            
            self._save_data()
            
            logging.info(f"Added document {filename} to knowledge base {kb_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to add document to knowledge base {kb_id}: {e}")
            return False
    
    async def index_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """建立知識庫索引"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            self.knowledge_bases[kb_id]['status'] = 'indexing'
            self._save_data()
            
            # 處理所有文檔
            doc_ids = self.knowledge_bases[kb_id]['documents']
            for doc_id in doc_ids:
                if doc_id in self.documents:
                    await self._process_document(doc_id)
            
            # 更新狀態
            self.knowledge_bases[kb_id]['status'] = 'ready'
            self.knowledge_bases[kb_id]['last_indexed'] = datetime.now().isoformat()
            self._save_data()
            
            return {
                'success': True,
                'message': '知識圖譜建立完成',
                'kb_id': kb_id
            }
            
        except Exception as e:
            logging.error(f"Error indexing knowledge base {kb_id}: {e}")
            self.knowledge_bases[kb_id]['status'] = 'error'
            self._save_data()
            
            return {
                'success': False,
                'message': '知識圖譜建立失敗',
                'error': str(e)
            }
    
    async def _process_document(self, doc_id: str):
        """處理單個文檔，提取實體和關係"""
        try:
            doc = self.documents[doc_id]
            content = doc['content']
            
            # 簡單的實體提取（基於規則）
            entities = self._extract_simple_entities(content)
            
            # 儲存實體
            for entity in entities:
                self.entities[entity].append({
                    'doc_id': doc_id,
                    'context': self._get_entity_context(entity, content)
                })
            
            # 簡單的關係提取
            relationships = self._extract_simple_relationships(content, entities)
            
            # 儲存關係
            for rel in relationships:
                self.relationships[f"{rel['source']}-{rel['target']}"].append({
                    'doc_id': doc_id,
                    'relation': rel['relation'],
                    'context': rel['context']
                })
            
            # 標記為已處理
            self.documents[doc_id]['processed'] = True
            
        except Exception as e:
            logging.error(f"Error processing document {doc_id}: {e}")
    
    def _extract_simple_entities(self, content: str) -> List[str]:
        """簡單的實體提取（基於規則）"""
        entities = set()
        
        # 尋找可能的實體（大寫開頭的詞組）
        # 這是一個很基本的方法，可以根據需要改進
        patterns = [
            r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',  # 標題格式的詞組
            r'[一-龥]{2,}',  # 中文詞組
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 1 and not match.isdigit():
                    entities.add(match.strip())
        
        # 過濾常見停用詞
        stop_words = {'是', '的', '了', '在', '和', '與', '或', '但', '然而', '因為', '所以'}
        entities = [e for e in entities if e not in stop_words]
        
        return list(entities)[:50]  # 限制數量
    
    def _get_entity_context(self, entity: str, content: str) -> str:
        """獲取實體的上下文"""
        # 找到實體在文本中的位置並提取周圍文字
        index = content.find(entity)
        if index == -1:
            return ""
        
        start = max(0, index - 50)
        end = min(len(content), index + len(entity) + 50)
        
        return content[start:end].strip()
    
    def _extract_simple_relationships(self, content: str, entities: List[str]) -> List[Dict[str, str]]:
        """簡單的關係提取"""
        relationships = []
        
        # 簡單的關係模式
        relation_patterns = [
            r'(\w+)\s*是\s*(\w+)',
            r'(\w+)\s*屬於\s*(\w+)',
            r'(\w+)\s*包含\s*(\w+)',
            r'(\w+)\s*使用\s*(\w+)',
            r'(\w+)\s*導致\s*(\w+)',
        ]
        
        for pattern in relation_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    source, target = match
                    if source in entities and target in entities:
                        relationships.append({
                            'source': source,
                            'target': target,
                            'relation': '相關',
                            'context': self._get_entity_context(f"{source} {target}", content)
                        })
        
        return relationships[:20]  # 限制數量
    
    async def query_local(self, kb_id: str, query: str) -> Dict[str, Any]:
        """本地搜尋查詢"""
        return await self._query(kb_id, query, "local")
    
    async def query_global(self, kb_id: str, query: str) -> Dict[str, Any]:
        """全域搜尋查詢"""
        return await self._query(kb_id, query, "global")
    
    async def _query(self, kb_id: str, query: str, method: str) -> Dict[str, Any]:
        """查詢實作"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            if self.knowledge_bases[kb_id]['status'] != 'ready':
                return {
                    'success': False,
                    'message': '知識庫尚未準備就緒，請先建立索引'
                }
            
            # 尋找相關實體和文檔
            relevant_docs = self._find_relevant_documents(kb_id, query)
            
            if not relevant_docs:
                return {
                    'success': True,
                    'answer': '抱歉，我在知識庫中找不到相關資訊。',
                    'query_type': method,
                    'kb_id': kb_id
                }
            
            # 構建上下文
            context = self._build_context(relevant_docs, query)
            
            # 使用 LLM 生成回答
            answer = await self._generate_answer(query, context)
            
            return {
                'success': True,
                'answer': answer,
                'query_type': method,
                'kb_id': kb_id,
                'sources': len(relevant_docs)
            }
            
        except Exception as e:
            logging.error(f"Error querying knowledge base {kb_id}: {e}")
            return {
                'success': False,
                'message': '查詢過程中發生錯誤',
                'error': str(e)
            }
    
    def _find_relevant_documents(self, kb_id: str, query: str) -> List[Dict[str, Any]]:
        """尋找相關文檔"""
        relevant_docs = []
        
        # 獲取知識庫的所有文檔
        doc_ids = self.knowledge_bases[kb_id]['documents']
        
        for doc_id in doc_ids:
            if doc_id in self.documents:
                doc = self.documents[doc_id]
                content = doc['content']
                
                # 計算相關性分數（簡單的關鍵字匹配）
                score = self._calculate_relevance_score(query, content)
                
                if score > 0:
                    relevant_docs.append({
                        'doc_id': doc_id,
                        'content': content,
                        'filename': doc['filename'],
                        'score': score
                    })
        
        # 按分數排序
        relevant_docs.sort(key=lambda x: x['score'], reverse=True)
        
        return relevant_docs[:3]  # 返回最相關的3個文檔
    
    def _calculate_relevance_score(self, query: str, content: str) -> float:
        """計算相關性分數"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        # 計算交集
        intersection = query_words & content_words
        
        # 簡單的 TF-IDF 風格評分
        score = len(intersection) / len(query_words) if query_words else 0
        
        return score
    
    def _build_context(self, relevant_docs: List[Dict[str, Any]], query: str) -> str:
        """構建上下文"""
        context_parts = []
        
        for doc in relevant_docs:
            # 提取相關段落
            content = doc['content']
            relevant_part = self._extract_relevant_part(content, query)
            
            context_parts.append(f"文檔：{doc['filename']}\n內容：{relevant_part}")
        
        return "\n\n".join(context_parts)
    
    def _extract_relevant_part(self, content: str, query: str) -> str:
        """提取文檔中與查詢相關的部分"""
        # 簡單方法：找到包含查詢詞的段落
        paragraphs = content.split('\n')
        relevant_paragraphs = []
        
        query_words = query.lower().split()
        
        for para in paragraphs:
            if any(word in para.lower() for word in query_words):
                relevant_paragraphs.append(para.strip())
        
        # 如果沒有找到相關段落，返回開頭部分
        if not relevant_paragraphs:
            return content[:500] + "..." if len(content) > 500 else content
        
        result = "\n".join(relevant_paragraphs)
        return result[:1000] + "..." if len(result) > 1000 else result
    
    async def _generate_answer(self, query: str, context: str) -> str:
        """使用 LLM 生成回答"""
        try:
            prompt = f"""基於以下知識庫內容回答問題：

知識庫內容：
{context}

問題：{query}

請根據知識庫中的資訊提供準確且有用的回答。如果資訊不足，請明確說明。
"""
            
            if self.deepseek_api_key:
                return await self._call_deepseek_api(prompt)
            elif self.openai_api_key:
                return await self._call_openai_api(prompt)
            else:
                return "無法生成回答：缺少 API 金鑰配置"
                
        except Exception as e:
            logging.error(f"Error generating answer: {e}")
            return "抱歉，生成回答時發生錯誤。"
    
    async def _call_deepseek_api(self, prompt: str) -> str:
        """調用 DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logging.error(f"DeepSeek API call failed: {e}")
            return f"API 調用失敗：{str(e)}"
    
    async def _call_openai_api(self, prompt: str) -> str:
        """調用 OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logging.error(f"OpenAI API call failed: {e}")
            return f"API 調用失敗：{str(e)}"
    
    def get_knowledge_bases(self, user_id: str = None) -> List[Dict[str, Any]]:
        """取得知識庫清單"""
        if user_id:
            return [
                {**kb_info, 'kb_id': kb_id} 
                for kb_id, kb_info in self.knowledge_bases.items() 
                if kb_info.get('user_id') == user_id
            ]
        else:
            return [
                {**kb_info, 'kb_id': kb_id} 
                for kb_id, kb_info in self.knowledge_bases.items()
            ]
    
    def get_knowledge_base_info(self, kb_id: str) -> Optional[Dict[str, Any]]:
        """取得特定知識庫資訊"""
        if kb_id in self.knowledge_bases:
            return {**self.knowledge_bases[kb_id], 'kb_id': kb_id}
        return None
    
    def delete_knowledge_base(self, kb_id: str, user_id: str) -> bool:
        """刪除知識庫"""
        try:
            if kb_id not in self.knowledge_bases:
                return False
            
            kb_info = self.knowledge_bases[kb_id]
            if kb_info.get('user_id') != user_id:
                logging.warning(f"User {user_id} attempted to delete KB {kb_id} owned by {kb_info.get('user_id')}")
                return False
            
            # 刪除相關文檔
            doc_ids = kb_info.get('documents', [])
            for doc_id in doc_ids:
                if doc_id in self.documents:
                    del self.documents[doc_id]
            
            # 從記錄中移除
            del self.knowledge_bases[kb_id]
            self._save_data()
            
            logging.info(f"Deleted knowledge base {kb_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting knowledge base {kb_id}: {e}")
            return False


# 全域實例
graphrag_service = SimpleGraphRAGService()