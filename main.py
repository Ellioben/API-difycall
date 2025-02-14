from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from dify_client import DifyClient
import uvicorn
from typing import Optional, List, Dict

app = FastAPI()

# 使用默认配置初始化客户端
client = DifyClient()

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

# 简化版的请求模型
class SimpleRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

@app.get("/chat")
@app.post("/chat")
async def chat(request: Optional[SimpleRequest] = None, query: Optional[str] = None):
    try:
        # 处理 GET 请求
        if query is not None:
            message = query
            conversation_id = None
        # 处理 POST 请求
        elif request is not None:
            message = request.query
            conversation_id = request.conversation_id
        else:
            raise HTTPException(status_code=400, detail="Missing query parameter")

        response = client.chat(
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
async def get_history(conversation_id: str):
    try:
        return client.get_conversation_history(conversation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 