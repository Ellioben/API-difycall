import requests
import json
from typing import Dict, Any, Optional, List
from config import DIFY_PLATFORMS

class DifyWorkflow:
    def __init__(self, platform: str, user_id: str = "abc-123"):
        if platform not in DIFY_PLATFORMS:
            raise ValueError(f"Unknown platform: {platform}. Available platforms: {list(DIFY_PLATFORMS.keys())}")
            
        self.platform = platform
        platform_config = DIFY_PLATFORMS[platform]
        self.api_key = platform_config["api_key"]
        self.base_url = platform_config["base_url"]
        self.user_id = user_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_completion(
        self,
        inputs: Dict[str, Any] = {},
        query: str = "",
        files: List[Dict] = [],
        response_mode: str = "blocking"
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/completion-messages"
        payload = {
            "inputs": inputs,
            "query": query,
            "response_mode": response_mode,
            "user": self.user_id,
            "files": files
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def create_completion_with_files(
        self,
        query: str,
        file_urls: List[str],
        file_type: str = "image",
        inputs: Dict[str, Any] = {},
        response_mode: str = "blocking"
    ) -> Dict[str, Any]:
        files = [
            {
                "type": file_type,
                "transfer_method": "remote_url",
                "url": url
            } for url in file_urls
        ]
        
        return self.create_completion(
            inputs=inputs,
            query=query,
            files=files,
            response_mode=response_mode
        )

    def create_streaming_completion(
        self,
        query: str,
        inputs: Dict[str, Any] = {},
        files: List[Dict] = []
    ):
        url = f"{self.base_url}/completion-messages"
        payload = {
            "inputs": inputs,
            "query": query,
            "response_mode": "streaming",
            "user": self.user_id,
            "files": files
        }

        response = requests.post(url, headers=self.headers, json=payload, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        json_str = line_str[6:]
                        data = json.loads(json_str)
                        if 'answer' in data:
                            yield data['answer']
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {str(e)}")
                except Exception as e:
                    print(f"处理响应时出错: {str(e)}")

    def get_completion_message(self, message_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/completion-messages/{message_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_completion_messages(
        self,
        last_id: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/completion-messages"
        params = {
            "last_id": last_id,
            "limit": limit,
            "user": self.user_id
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json() 