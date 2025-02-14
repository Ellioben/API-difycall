import requests
import json
from config import DIFY_API_KEY, DIFY_API_BASE_URL
from typing import Dict, Any, Optional

class DifyClient:
    def __init__(self, user_id: str = "abc-123"):
        self.api_key = DIFY_API_KEY
        self.base_url = DIFY_API_BASE_URL
        self.user_id = user_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

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