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

    def execute_workflow(
        self,
        inputs: Dict[str, Any] = {},
        files: List[Dict] = []
    ):
        url = f"{self.base_url}/workflows/run"
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": self.user_id,
            "files": files
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        # Assuming the response is a JSON object
        data = response.json()
        if 'data' in data:
            # Check if 'data' is a dictionary
            if isinstance(data['data'], dict):
                outputs = data['data'].get('outputs')
                print(f"Outputs: {outputs}")  # Debug log
                if outputs and 'title_list' in outputs:
                    for title in outputs['title_list']:
                        yield title + "\n"
                else:
                    raise ValueError("Unexpected response format: missing 'outputs' or 'title_list'")
            else:
                raise ValueError("Unexpected response format: 'data' is not a dictionary")
        else:
            raise ValueError("Unexpected response format: missing 'data'")

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