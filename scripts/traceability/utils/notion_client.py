"""
Notion API Client - Simplified implementation for traceability checking
"""

import os
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import requests


class NotionClient:
    """Notion API 客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('NOTION_API_KEY')
        if not self.api_key:
            raise ValueError("Notion API Key is required. Set NOTION_API_KEY environment variable.")
        
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self._rate_limit_delay = 0.34  # Notion API rate limit: 3 req/sec
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """发送请求并处理响应"""
        url = f"{self.base_url}/{endpoint}"
        
        # Rate limiting
        time.sleep(self._rate_limit_delay)
        
        response = requests.request(method, url, headers=self.headers, **kwargs)
        
        if response.status_code == 429:
            # Rate limited, wait and retry
            time.sleep(1)
            response = requests.request(method, url, headers=self.headers, **kwargs)
        
        response.raise_for_status()
        return response.json()
    
    def query_database(self, database_id: str, filter_obj: Optional[Dict] = None) -> List[Dict]:
        """查询数据库，自动处理分页"""
        results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            payload = {}
            if filter_obj:
                payload["filter"] = filter_obj
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            data = self._request("POST", f"databases/{database_id}/query", json=payload)
            
            results.extend(data.get('results', []))
            has_more = data.get('has_more', False)
            start_cursor = data.get('next_cursor')
        
        return results
    
    def get_page(self, page_id: str) -> Optional[Dict]:
        """获取页面详情"""
        try:
            return self._request("GET", f"pages/{page_id}")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def get_page_property_history(self, page_id: str, property_name: str) -> List[Dict]:
        """获取页面属性变更历史（需要 Notion Enterprise）"""
        # Note: Page history requires Notion Enterprise plan
        # This is a placeholder implementation
        return []
    
    # Helper methods for extracting property values
    
    @staticmethod
    def get_title(properties: Dict, property_name: str = "Name") -> Optional[str]:
        """获取标题属性值"""
        prop = properties.get(property_name, {})
        if prop.get('type') == 'title':
            title_parts = prop.get('title', [])
            return ''.join(t.get('plain_text', '') for t in title_parts)
        return None
    
    @staticmethod
    def get_rich_text(properties: Dict, property_name: str) -> str:
        """获取富文本属性值"""
        prop = properties.get(property_name, {})
        if prop.get('type') == 'rich_text':
            texts = prop.get('rich_text', [])
            return ''.join(t.get('plain_text', '') for t in texts)
        return ""
    
    @staticmethod
    def get_select(properties: Dict, property_name: str) -> Optional[str]:
        """获取单选属性值"""
        prop = properties.get(property_name, {})
        if prop.get('type') == 'select':
            select = prop.get('select')
            return select.get('name') if select else None
        return None
    
    @staticmethod
    def get_status(properties: Dict, property_name: str = "状态") -> Optional[str]:
        """获取状态属性值"""
        prop = properties.get(property_name, {})
        if prop.get('type') == 'status':
            status = prop.get('status')
            return status.get('name') if status else None
        return None
    
    @staticmethod
    def get_date(properties: Dict, property_name: str) -> Optional[date]:
        """获取日期属性值"""
        prop = properties.get(property_name, {})
        if prop.get('type') == 'date':
            date_data = prop.get('date')
            if date_data and date_data.get('start'):
                date_str = date_data['start']
                # Handle both date and datetime formats
                if 'T' in date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                return datetime.strptime(date_str, '%Y-%m-%d').date()
        return None
    
    @staticmethod
    def get_relation(properties: Dict, property_name: str) -> List[str]:
        """获取关联属性值（返回 ID 列表）"""
        prop = properties.get(property_name, {})
        if prop.get('type') == 'relation':
            relations = prop.get('relation', [])
            return [r.get('id') for r in relations]
        return []
    
    @staticmethod
    def get_number(properties: Dict, property_name: str) -> Optional[float]:
        """获取数字属性值"""
        prop = properties.get(property_name, {})
        if prop.get('type') == 'number':
            return prop.get('number')
        return None
    
    @staticmethod
    def get_url(properties: Dict, property_name: str) -> Optional[str]:
        """获取 URL 属性值"""
        prop = properties.get(property_name, {})
        if prop.get('type') == 'url':
            return prop.get('url')
        return None
    
    @staticmethod
    def has_value(properties: Dict, property_name: str) -> bool:
        """检查属性是否有值"""
        prop = properties.get(property_name)
        if not prop:
            return False
        
        prop_type = prop.get('type')
        
        if prop_type == 'title':
            return bool(prop.get('title', []))
        elif prop_type == 'rich_text':
            return bool(prop.get('rich_text', []))
        elif prop_type == 'select':
            return prop.get('select') is not None
        elif prop_type == 'status':
            return prop.get('status', {}).get('name') is not None
        elif prop_type == 'date':
            return prop.get('date') is not None
        elif prop_type == 'relation':
            return bool(prop.get('relation', []))
        elif prop_type == 'number':
            return prop.get('number') is not None
        elif prop_type == 'url':
            return prop.get('url') is not None
        elif prop_type == 'checkbox':
            return prop.get('checkbox') is True
        
        return False


# Database ID helper
class NotionDB:
    """Notion 数据库 ID 管理"""
    
    @staticmethod
    def get_db_id(db_name: str) -> Optional[str]:
        """从环境变量获取数据库 ID"""
        env_map = {
            'external_req': 'NOTION_EXTERNAL_REQ_DB_ID',
            'story': 'NOTION_STORY_DB_ID',
            'task': 'NOTION_TASK_DB_ID',
            'bug': 'NOTION_BUG_DB_ID',
            'iteration': 'NOTION_ITERATION_DB_ID',
            'retro': 'NOTION_RETROSPECTIVE_DB_ID',
        }
        env_var = env_map.get(db_name)
        return os.getenv(env_var) if env_var else None
