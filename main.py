from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from dify_client import DifyClient
import uvicorn
from typing import Optional, List, Dict
from config import DEFAULT_PLATFORM

app = FastAPI()

# 创建平台客户端字典
clients = {platform: DifyClient(platform=platform) for platform in DifyClient.get_available_platforms()}

# Dify 原生 API 的请求模型
class FileInfo(BaseModel):
    type: str
    transfer_method: str
    url: str

class DifyRequest(BaseModel):
    inputs: Dict = {}
    query: str
    response_mode: str = "streaming"
    conversation_id: str = ""
    user: str = "abc-123"
    files: List[FileInfo] = []
    platform: Optional[str] = None  # 新增平台选择字段

# 简化版的请求模型
class SimpleRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    platform: Optional[str] = None  # 新增平台选择字段

@app.get("/platforms")
async def get_platforms():
    """获取所有可用的平台及其描述"""
    return DifyClient.get_available_platforms()

@app.get("/chat")
@app.post("/chat")
async def chat(
    request: Optional[SimpleRequest] = None,
    query: Optional[str] = None,
    platform: Optional[str] = None
):
    try:
        # 处理 GET 请求
        if query is not None:
            message = query
            conversation_id = None
            selected_platform = platform
        # 处理 POST 请求
        elif request is not None:
            message = request.query
            conversation_id = request.conversation_id
            selected_platform = request.platform
        else:
            raise HTTPException(status_code=400, detail="Missing query parameter")

        # 使用指定的平台或默认平台
        selected_platform = selected_platform or DEFAULT_PLATFORM
        if selected_platform not in clients:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(clients.keys())}"
            )

        response = clients[selected_platform].chat(
            message=message,
            conversation_id=conversation_id,
            stream=False
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat-messages")
async def dify_chat(request: DifyRequest):
    try:
        selected_platform = request.platform or DEFAULT_PLATFORM
        if selected_platform not in clients:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(clients.keys())}"
            )

        client = clients[selected_platform]
        
        if request.files:
            response = client.chat_with_image(
                message=request.query,
                image_url=request.files[0].url,
                conversation_id=request.conversation_id
            )
        else:
            response = client.chat(
                message=request.query,
                conversation_id=request.conversation_id,
                stream=request.response_mode == "streaming"
            )

        if request.response_mode == "streaming":
            return Response(
                content=response,
                media_type="text/event-stream"
            )
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/messages")
async def get_history(conversation_id: str, platform: Optional[str] = None):
    try:
        selected_platform = platform or DEFAULT_PLATFORM
        if selected_platform not in clients:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(clients.keys())}"
            )
            
        return clients[selected_platform].get_conversation_history(conversation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 