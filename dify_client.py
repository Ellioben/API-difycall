import requests
import json
from config import DIFY_PLATFORMS, DEFAULT_PLATFORM
from typing import Dict, Any, Optional

class DifyClient:
    def __init__(self, platform: str = DEFAULT_PLATFORM, user_id: str = "abc-123"):
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

    @classmethod
    def get_available_platforms(cls) -> Dict[str, str]:
        """获取所有可用的平台及其描述"""
        return {k: v["description"] for k, v in DIFY_PLATFORMS.items()}

    def chat(self, message: str, conversation_id: Optional[str] = None, stream: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}/chat-messages"
        payload = {
            "inputs": {},
            "query": message,
            "response_mode": "streaming" if stream else "blocking",
            "conversation_id": conversation_id if conversation_id else "",
            "user": self.user_id,
            "files": []
        }
        
        response = requests.post(url, headers=self.headers, json=payload, stream=stream)
        response.raise_for_status()
        
        if stream:
            return self._process_sse_response(response)
        return response.json()

    def chat_with_image(self, message: str, image_url: str, conversation_id: Optional[str] = None):
        url = f"{self.base_url}/chat-messages"
        payload = {
            "inputs": {},
            "query": message,
            "response_mode": "streaming",
            "conversation_id": conversation_id if conversation_id else "",
            "user": self.user_id,
            "files": [
                {
                    "type": "image",
                    "transfer_method": "remote_url",
                    "url": image_url
                }
            ]
        }
        
        response = requests.post(url, headers=self.headers, json=payload, stream=True)
        response.raise_for_status()
        return self._process_sse_response(response)

    def _process_sse_response(self, response):
        """
        处理SSE格式的响应
        """
        for line in response.iter_lines():
            if line:
                try:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        # 移除 'data: ' 前缀
                        json_str = line_str[6:]
                        data = json.loads(json_str)
                        if 'answer' in data:
                            yield data['answer']
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {str(e)}")
                    print(f"原始数据: {line_str}")
                except Exception as e:
                    print(f"处理响应时出错: {str(e)}")

    def get_conversation_history(self, conversation_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/messages"
        params = {"conversation_id": conversation_id}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json() 