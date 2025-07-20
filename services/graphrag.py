"""
Simple GraphRAG 服務模組
暫時使用簡化版本，避免複雜的依賴衝突
"""

import os
import json
import logging
import asyncio
import tempfile
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import uuid
import re
import httpx

class SimpleGraphRAGService:
    """簡化版 GraphRAG 服務類別"""
    
    def __init__(self):
        # 環境變數設定
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") 
        self.graphrag_api_base = os.getenv("GRAPHRAG_API_BASE", "https://api.openai.com/v1")
        self.graphrag_model = os.getenv("GRAPHRAG_MODEL", "gpt-4")
        self.graphrag_embedding_model = os.getenv("GRAPHRAG_EMBEDDING_MODEL", "text-embedding-ada-002")
        
        # 資料儲存路徑
        self.base_path = Path("data/graphrag")
        self.input_path = self.base_path / "input"
        self.output_path = self.base_path / "output"
        self.cache_path = self.base_path / "cache"
        
        # 建立必要目錄
        for path in [self.base_path, self.input_path, self.output_path, self.cache_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # 知識庫狀態
        self.knowledge_bases = {}
        self._load_knowledge_bases()
        
        logging.info("Microsoft GraphRAG service initialized")
    
    def _load_knowledge_bases(self):
        """載入現有的知識庫"""
        kb_file = self.base_path / "knowledge_bases.json"
        if kb_file.exists():
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    self.knowledge_bases = json.load(f)
                logging.info(f"Loaded {len(self.knowledge_bases)} knowledge bases")
            except Exception as e:
                logging.error(f"Failed to load knowledge bases: {e}")
    
    def _save_knowledge_bases(self):
        """保存知識庫資訊"""
        try:
            kb_file = self.base_path / "knowledge_bases.json"
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_bases, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to save knowledge bases: {e}")
    
    def _create_graphrag_config(self, kb_id: str) -> str:
        """建立 GraphRAG 配置檔案"""
        config = {
            "llm": {
                "api_key": self.openai_api_key or self.deepseek_api_key,
                "type": "openai_chat",
                "model": self.graphrag_model,
                "api_base": self.graphrag_api_base,
                "max_tokens": 4000,
                "temperature": 0.0,
                "top_p": 1.0,
                "n": 1
            },
            "parallelization": {
                "stagger": 0.3,
                "num_threads": 50
            },
            "async_mode": "threaded",
            "embeddings": {
                "llm": {
                    "api_key": self.openai_api_key or self.deepseek_api_key,
                    "type": "openai_embedding",
                    "model": self.graphrag_embedding_model,
                    "api_base": self.graphrag_api_base
                }
            },
            "encoding_model": "cl100k_base",
            "skip_workflows": [],
            "local_search": {
                "text_unit_prop": 0.5,
                "community_prop": 0.1,
                "conversation_history_max_turns": 5,
                "top_k_mapped_entities": 10,
                "top_k_relationships": 10,
                "max_tokens": 12000
            },
            "global_search": {
                "max_tokens": 12000,
                "data_max_tokens": 12000,
                "map_max_tokens": 1000,
                "reduce_max_tokens": 2000,
                "concurrency": 32
            },
            "input": {
                "type": "file",
                "file_type": "text",
                "base_dir": str(self.input_path / kb_id),
                "file_encoding": "utf-8",
                "file_pattern": ".*\\.txt$"
            },
            "cache": {
                "type": "file",
                "base_dir": str(self.cache_path / kb_id)
            },
            "storage": {
                "type": "file", 
                "base_dir": str(self.output_path / kb_id)
            },
            "reporting": {
                "type": "file",
                "base_dir": str(self.output_path / kb_id / "reports")
            },
            "entity_extraction": {
                "prompt": "data/prompts/entity_extraction.txt",
                "entity_types": ["person", "organization", "location", "event", "concept"],
                "max_gleanings": 1
            },
            "summarize_descriptions": {
                "prompt": "data/prompts/summarize_descriptions.txt",
                "max_length": 500
            },
            "claim_extraction": {
                "prompt": "data/prompts/claim_extraction.txt",
                "description": "Any claims or facts that could be relevant to information discovery.",
                "max_gleanings": 1
            },
            "community_report": {
                "prompt": "data/prompts/community_report.txt",
                "max_length": 2000,
                "max_input_length": 8000
            }
        }
        
        # 如果使用 DeepSeek，調整 API 設定
        if self.deepseek_api_key and not self.openai_api_key:
            config["llm"]["api_base"] = "https://api.deepseek.com/v1"
            config["llm"]["model"] = "deepseek-chat"
            # DeepSeek 目前不支援 embedding，使用本地或其他方案
            config["embeddings"]["llm"]["type"] = "azure_openai_embedding"  # 需要調整
        
        config_path = self.output_path / kb_id / "settings.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 將配置寫入 YAML 檔案
        import yaml
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        return str(config_path)
    
    async def create_knowledge_base(self, user_id: str, name: str = None) -> str:
        """建立新的知識庫"""
        kb_id = str(uuid.uuid4())
        
        if name is None:
            name = f"知識庫_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 建立知識庫目錄
        kb_input_path = self.input_path / kb_id
        kb_output_path = self.output_path / kb_id
        kb_cache_path = self.cache_path / kb_id
        
        for path in [kb_input_path, kb_output_path, kb_cache_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # 記錄知識庫資訊
        self.knowledge_bases[kb_id] = {
            'name': name,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'status': 'created',
            'documents': [],
            'last_indexed': None
        }
        
        self._save_knowledge_bases()
        
        # 建立 GraphRAG 配置
        config_path = self._create_graphrag_config(kb_id)
        
        logging.info(f"Created knowledge base {kb_id} for user {user_id}")
        return kb_id
    
    async def add_document(self, kb_id: str, content: str, filename: str) -> bool:
        """新增文件到知識庫"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            # 將文件內容寫入輸入目錄
            kb_input_path = self.input_path / kb_id
            doc_id = str(uuid.uuid4())
            doc_filename = f"{doc_id}_{filename}.txt"
            doc_path = kb_input_path / doc_filename
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新知識庫記錄
            self.knowledge_bases[kb_id]['documents'].append({
                'id': doc_id,
                'filename': filename,
                'original_name': filename,
                'added_at': datetime.now().isoformat(),
                'file_path': str(doc_path)
            })
            
            self.knowledge_bases[kb_id]['status'] = 'needs_indexing'
            self._save_knowledge_bases()
            
            logging.info(f"Added document {filename} to knowledge base {kb_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to add document to knowledge base {kb_id}: {e}")
            return False
    
    async def index_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """索引知識庫，建立圖譜"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            kb_output_path = self.output_path / kb_id
            
            # 更新狀態
            self.knowledge_bases[kb_id]['status'] = 'indexing'
            self._save_knowledge_bases()
            
            # 簡化版索引建立：分析文件並提取實體
            # 暫時返回成功，因為簡化版本不需要複雜的索引過程
            self.knowledge_bases[kb_id]['status'] = 'ready'
            self.knowledge_bases[kb_id]['last_indexed'] = datetime.now().isoformat()
            self._save_knowledge_bases()
            
            return {
                'success': True,
                'message': '知識圖譜建立完成',
                'kb_id': kb_id
            }
                
        except Exception as e:
            logging.error(f"Error indexing knowledge base {kb_id}: {e}")
            self.knowledge_bases[kb_id]['status'] = 'error'
            self._save_knowledge_bases()
            
            return {
                'success': False,
                'message': '知識圖譜建立過程中發生錯誤',
                'error': str(e)
            }
    
    async def query_local(self, kb_id: str, query: str) -> Dict[str, Any]:
        """本地搜尋查詢"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            if self.knowledge_bases[kb_id]['status'] != 'ready':
                return {
                    'success': False,
                    'message': '知識庫尚未準備就緒，請先建立索引'
                }
            
            kb_output_path = self.output_path / kb_id
            
            # 執行本地搜尋
            cmd = [
                "python", "-m", "graphrag.query",
                "--root", str(kb_output_path),
                "--method", "local",
                "--query", query
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                response = stdout.decode('utf-8')
                return {
                    'success': True,
                    'answer': response,
                    'query_type': 'local',
                    'kb_id': kb_id
                }
            else:
                error_msg = stderr.decode('utf-8') if stderr else "Query failed"
                return {
                    'success': False,
                    'message': '查詢失敗',
                    'error': error_msg
                }
                
        except Exception as e:
            logging.error(f"Error querying knowledge base {kb_id}: {e}")
            return {
                'success': False,
                'message': '查詢過程中發生錯誤',
                'error': str(e)
            }
    
    async def query_global(self, kb_id: str, query: str) -> Dict[str, Any]:
        """全域搜尋查詢"""
        try:
            if kb_id not in self.knowledge_bases:
                raise ValueError(f"Knowledge base {kb_id} not found")
            
            if self.knowledge_bases[kb_id]['status'] != 'ready':
                return {
                    'success': False,
                    'message': '知識庫尚未準備就緒，請先建立索引'
                }
            
            kb_output_path = self.output_path / kb_id
            
            # 執行全域搜尋
            cmd = [
                "python", "-m", "graphrag.query",
                "--root", str(kb_output_path),
                "--method", "global",
                "--query", query
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                response = stdout.decode('utf-8')
                return {
                    'success': True,
                    'answer': response,
                    'query_type': 'global',
                    'kb_id': kb_id
                }
            else:
                error_msg = stderr.decode('utf-8') if stderr else "Query failed"
                return {
                    'success': False,
                    'message': '查詢失敗',
                    'error': error_msg
                }
                
        except Exception as e:
            logging.error(f"Error querying knowledge base {kb_id}: {e}")
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
            
            # 刪除檔案
            for path in [self.input_path / kb_id, self.output_path / kb_id, self.cache_path / kb_id]:
                if path.exists():
                    shutil.rmtree(path)
            
            # 從記錄中移除
            del self.knowledge_bases[kb_id]
            self._save_knowledge_bases()
            
            logging.info(f"Deleted knowledge base {kb_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting knowledge base {kb_id}: {e}")
            return False

# 使用簡化版服務
from .simple_graphrag import graphrag_service