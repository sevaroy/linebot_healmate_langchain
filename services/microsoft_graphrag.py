"""
Microsoft GraphRAG 服務
使用正式的 Microsoft GraphRAG 套件
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
import uuid
import tempfile
import shutil

# Microsoft GraphRAG imports
import subprocess
import yaml


class MicrosoftGraphRAGService:
    """Microsoft GraphRAG 服務類別"""
    
    def __init__(self):
        # API 設定
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        # GraphRAG 設定
        self.graphrag_api_base = os.getenv("GRAPHRAG_API_BASE", "https://api.openai.com/v1")
        self.graphrag_model = os.getenv("GRAPHRAG_MODEL", "gpt-4")
        self.graphrag_embedding_model = os.getenv("GRAPHRAG_EMBEDDING_MODEL", "text-embedding-ada-002")
        
        # 資料儲存路徑
        self.base_path = Path("/app/data/microsoft_graphrag")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 知識庫管理
        self.knowledge_bases = {}
        self._load_knowledge_bases()
        
        logging.info("Microsoft GraphRAG service initialized")
    
    def _load_knowledge_bases(self):
        """載入知識庫清單"""
        kb_file = self.base_path / "knowledge_bases.json"
        if kb_file.exists():
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    self.knowledge_bases = json.load(f)
                logging.info(f"Loaded {len(self.knowledge_bases)} knowledge bases")
            except Exception as e:
                logging.error(f"Failed to load knowledge bases: {e}")
    
    def _save_knowledge_bases(self):
        """保存知識庫清單"""
        try:
            kb_file = self.base_path / "knowledge_bases.json"
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_bases, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to save knowledge bases: {e}")
    
    def _create_graphrag_config(self, kb_path: Path) -> Dict[str, Any]:
        """建立 GraphRAG 配置"""
        config = {
            "llm": {
                "api_key": self.openai_api_key or self.deepseek_api_key,
                "type": "openai_chat",
                "model": self.graphrag_model,
                "api_base": self.graphrag_api_base,
                "max_tokens": int(os.getenv("GRAPHRAG_LLM_MAX_TOKENS", "4000")),
                "temperature": float(os.getenv("GRAPHRAG_LLM_TEMPERATURE", "0.7")),
                "top_p": float(os.getenv("GRAPHRAG_LLM_TOP_P", "1.0")),
                "request_timeout": int(os.getenv("GRAPHRAG_LLM_TIMEOUT", "180")),
                "max_retries": int(os.getenv("GRAPHRAG_LLM_MAX_RETRIES", "3")),
            },
            "embeddings": {
                "api_key": self.openai_api_key or self.deepseek_api_key,
                "type": "openai_embedding",
                "model": self.graphrag_embedding_model,
                "api_base": self.graphrag_api_base,
                "batch_size": int(os.getenv("GRAPHRAG_EMBEDDING_BATCH_SIZE", "16")),
                "max_tokens": int(os.getenv("GRAPHRAG_EMBEDDING_MAX_TOKENS", "8191")),
                "request_timeout": int(os.getenv("GRAPHRAG_EMBEDDING_TIMEOUT", "180")),
                "max_retries": int(os.getenv("GRAPHRAG_EMBEDDING_MAX_RETRIES", "3")),
                "concurrent_requests": int(os.getenv("GRAPHRAG_EMBEDDING_CONCURRENT", "25")),
            },
            "input": {
                "type": "file",
                "file_type": "text",
                "base_dir": str(kb_path / "input"),
                "file_encoding": "utf-8",
            },
            "cache": {
                "type": "file",
                "base_dir": str(kb_path / "cache"),
            },
            "storage": {
                "type": "file",
                "base_dir": str(kb_path / "output"),
            },
            "reporting": {
                "type": "file",
                "base_dir": str(kb_path / "reporting"),
            },
            "chunks": {
                "size": int(os.getenv("GRAPHRAG_CHUNK_SIZE", "300")),
                "overlap": int(os.getenv("GRAPHRAG_CHUNK_OVERLAP", "100")),
                "group_by_columns": ["id"],
            },
            "text_embedding": {
                "batch_size": int(os.getenv("GRAPHRAG_TEXT_EMBEDDING_BATCH_SIZE", "16")),
                "batch_max_tokens": int(os.getenv("GRAPHRAG_TEXT_EMBEDDING_MAX_TOKENS", "8191")),
            },
            "entity_extraction": {
                "entity_types": ["person", "organization", "location", "event", "concept"],
                "max_gleanings": int(os.getenv("GRAPHRAG_ENTITY_MAX_GLEANINGS", "1")),
            },
            "relationship_extraction": {
                "max_gleanings": int(os.getenv("GRAPHRAG_RELATIONSHIP_MAX_GLEANINGS", "1")),
            },
            "community_detection": {
                "max_cluster_size": int(os.getenv("GRAPHRAG_COMMUNITY_MAX_CLUSTER_SIZE", "10")),
            },
            "global_search": {
                "temperature": float(os.getenv("GRAPHRAG_GLOBAL_TEMPERATURE", "0.0")),
                "top_p": float(os.getenv("GRAPHRAG_GLOBAL_TOP_P", "1.0")),
                "max_tokens": int(os.getenv("GRAPHRAG_GLOBAL_MAX_TOKENS", "12000")),
                "concurrency": int(os.getenv("GRAPHRAG_GLOBAL_CONCURRENCY", "32")),
            },
            "local_search": {
                "temperature": float(os.getenv("GRAPHRAG_LOCAL_TEMPERATURE", "0.0")),
                "top_p": float(os.getenv("GRAPHRAG_LOCAL_TOP_P", "1.0")),
                "max_tokens": int(os.getenv("GRAPHRAG_LOCAL_MAX_TOKENS", "12000")),
                "text_unit_prop": float(os.getenv("GRAPHRAG_LOCAL_TEXT_UNIT_PROP", "0.5")),
                "community_prop": float(os.getenv("GRAPHRAG_LOCAL_COMMUNITY_PROP", "0.1")),
                "top_k_mapped_entities": int(os.getenv("GRAPHRAG_LOCAL_TOP_K_ENTITIES", "10")),
                "top_k_relationships": int(os.getenv("GRAPHRAG_LOCAL_TOP_K_RELATIONSHIPS", "10")),
            },
        }
        
        # 如果使用 DeepSeek，調整設定
        if self.deepseek_api_key and not self.openai_api_key:
            config["llm"]["api_base"] = "https://api.deepseek.com/v1"
            config["embeddings"]["api_base"] = "https://api.deepseek.com/v1"
        
        return config
    
    async def create_knowledge_base(self, user_id: str, name: str = None) -> str:
        """建立新的知識庫"""
        kb_id = str(uuid.uuid4())
        
        if name is None:
            name = f"知識庫_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 建立知識庫目錄結構
        kb_path = self.base_path / kb_id
        kb_path.mkdir(parents=True, exist_ok=True)
        
        # 建立必要的子目錄
        (kb_path / "input").mkdir(exist_ok=True)
        (kb_path / "cache").mkdir(exist_ok=True)
        (kb_path / "output").mkdir(exist_ok=True)
        (kb_path / "reporting").mkdir(exist_ok=True)
        
        # 建立配置檔案
        config = self._create_graphrag_config(kb_path)
        config_file = kb_path / "settings.yaml"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        # 記錄知識庫資訊
        self.knowledge_bases[kb_id] = {
            'name': name,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'status': 'created',
            'path': str(kb_path),
            'documents': [],
            'last_indexed': None
        }
        
        self._save_knowledge_bases()
        
        logging.info(f"Created Microsoft GraphRAG knowledge base {kb_id} for user {user_id}")
        return kb_id
    
    async def add_document(self, kb_id: str, content: str, filename: str) -> bool:
        """新增文件到知識庫"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            kb_info = self.knowledge_bases[kb_id]
            kb_path = Path(kb_info['path'])
            input_dir = kb_path / "input"
            
            # 生成文件 ID 和檔案名
            doc_id = str(uuid.uuid4())
            safe_filename = f"{doc_id}_{filename}"
            file_path = input_dir / safe_filename
            
            # 儲存文件內容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新知識庫記錄
            self.knowledge_bases[kb_id]['documents'].append({
                'doc_id': doc_id,
                'filename': filename,
                'file_path': str(file_path),
                'added_at': datetime.now().isoformat()
            })
            self.knowledge_bases[kb_id]['status'] = 'needs_indexing'
            
            self._save_knowledge_bases()
            
            logging.info(f"Added document {filename} to GraphRAG knowledge base {kb_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to add document to GraphRAG knowledge base {kb_id}: {e}")
            return False
    
    async def index_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """建立知識庫索引"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            kb_info = self.knowledge_bases[kb_id]
            kb_path = Path(kb_info['path'])
            
            # 檢查是否有文件
            input_dir = kb_path / "input"
            if not any(input_dir.iterdir()):
                return {
                    'success': False,
                    'message': '知識庫中沒有文件，請先新增文件'
                }
            
            # 更新狀態
            self.knowledge_bases[kb_id]['status'] = 'indexing'
            self._save_knowledge_bases()
            
            # 執行 GraphRAG 索引建立
            logging.info(f"Starting GraphRAG indexing for knowledge base {kb_id}")
            
            # 使用 GraphRAG CLI 命令執行索引
            result = subprocess.run([
                "python", "-m", "graphrag", "index",
                "--root", str(kb_path),
                "--verbose"
            ], capture_output=True, text=True, cwd=str(kb_path))
            
            if result.returncode == 0:
                # 索引建立成功
                self.knowledge_bases[kb_id]['status'] = 'ready'
                self.knowledge_bases[kb_id]['last_indexed'] = datetime.now().isoformat()
                self._save_knowledge_bases()
                
                logging.info(f"GraphRAG indexing completed for knowledge base {kb_id}")
                
                return {
                    'success': True,
                    'message': 'GraphRAG 知識圖譜建立完成',
                    'kb_id': kb_id
                }
            else:
                # 索引建立失敗
                self.knowledge_bases[kb_id]['status'] = 'error'
                self._save_knowledge_bases()
                
                logging.error(f"GraphRAG indexing failed for knowledge base {kb_id}: {result.stderr}")
                
                return {
                    'success': False,
                    'message': f'GraphRAG 索引建立失敗: {result.stderr}',
                    'error': result.stderr
                }
                
        except Exception as e:
            logging.error(f"Error indexing GraphRAG knowledge base {kb_id}: {e}")
            self.knowledge_bases[kb_id]['status'] = 'error'
            self._save_knowledge_bases()
            
            return {
                'success': False,
                'message': 'GraphRAG 索引建立失敗',
                'error': str(e)
            }
    
    async def query_local(self, kb_id: str, query: str) -> Dict[str, Any]:
        """本地搜尋查詢"""
        return await self._query(kb_id, query, "local")
    
    async def query_global(self, kb_id: str, query: str) -> Dict[str, Any]:
        """全域搜尋查詢"""
        return await self._query(kb_id, query, "global")
    
    async def _query(self, kb_id: str, query: str, method: str) -> Dict[str, Any]:
        """執行 GraphRAG 查詢"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            kb_info = self.knowledge_bases[kb_id]
            
            if kb_info['status'] != 'ready':
                return {
                    'success': False,
                    'message': 'GraphRAG 知識庫尚未準備就緒，請先建立索引'
                }
            
            kb_path = Path(kb_info['path'])
            
            # 使用 GraphRAG CLI 執行查詢
            query_type = "local" if method == "local" else "global"
            
            result = subprocess.run([
                "python", "-m", "graphrag", "query",
                "--root", str(kb_path),
                "--method", query_type,
                "-q", query
            ], capture_output=True, text=True, cwd=str(kb_path))
            
            if result.returncode == 0:
                answer = result.stdout.strip()
                
                return {
                    'success': True,
                    'answer': answer,
                    'query_type': method,
                    'kb_id': kb_id
                }
            else:
                logging.error(f"GraphRAG query failed: {result.stderr}")
                return {
                    'success': False,
                    'message': f'查詢失敗: {result.stderr}',
                    'error': result.stderr
                }
                
        except Exception as e:
            logging.error(f"Error querying GraphRAG knowledge base {kb_id}: {e}")
            return {
                'success': False,
                'message': '查詢過程中發生錯誤',
                'error': str(e)
            }
    
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
            
            # 刪除知識庫目錄
            kb_path = Path(kb_info['path'])
            if kb_path.exists():
                shutil.rmtree(kb_path)
            
            # 從記錄中移除
            del self.knowledge_bases[kb_id]
            self._save_knowledge_bases()
            
            logging.info(f"Deleted GraphRAG knowledge base {kb_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting GraphRAG knowledge base {kb_id}: {e}")
            return False


# 全域實例
microsoft_graphrag_service = MicrosoftGraphRAGService()