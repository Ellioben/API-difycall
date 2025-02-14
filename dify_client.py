import requests
import json
from config import DIFY_API_KEY, DIFY_API_BASE_URL

class DifyClient:
    def __init__(self, user_id="default_user"):
        self.api_key = DIFY_API_KEY
        self.base_url = DIFY_API_BASE_URL
        self.user_id = user_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
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

    def chat(self, message, conversation_id=None):
        """
        """
        endpoint = f"{self.base_url}/chat-messages"
        
        payload = {
            "inputs": {},
            "query": message,
            "user": self.user_id,
            "response_mode": "streaming",
            "conversation_id": conversation_id if conversation_id else "",
            "files": []
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                yield from self._process_sse_response(response)
            else:
                error_message = f"API错误: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_message += f" - {error_detail}"
                except:
                    error_message += f" - {response.text}"
                yield error_message
                
        except Exception as e:
            yield f"连接错误: {str(e)}"

    def chat_with_image(self, message, image_url, conversation_id=None):
        """
        发送带图片的消息到Dify API并获取响应
        """
        endpoint = f"{self.base_url}/chat-messages"
        
        payload = {
            "inputs": {},
            "query": message,
            "user": self.user_id,
            "response_mode": "streaming",
            "conversation_id": conversation_id if conversation_id else "",
            "files": [
                {
                    "type": "image",
                    "transfer_method": "remote_url",
                    "url": image_url
                }
            ]
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                yield from self._process_sse_response(response)
            else:
                error_message = f"API错误: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_message += f" - {error_detail}"
                except:
                    error_message += f" - {response.text}"
                yield error_message
                
        except Exception as e:
            yield f"连接错误: {str(e)}" 