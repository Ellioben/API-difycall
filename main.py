from fastapi import FastAPI, HTTPException, Response, Query
from pydantic import BaseModel
from dify_client import DifyClient
import uvicorn
from typing import Optional, List, Dict
from config import DIFY_PLATFORMS
import logging
from datetime import datetime

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()

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
    platform: str  # 平台参数改为必填

# 简化版的请求模型
class SimpleRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    platform: str  # 平台参数改为必填

@app.get("/platforms")
async def get_platforms():
    """获取所有可用的平台及其描述"""
    logger.info("获取平台列表")
    return DifyClient.get_available_platforms()

@app.get("/chat")
@app.post("/chat")
async def chat(
    request: Optional[SimpleRequest] = None,
    query: Optional[str] = None,
    platform: str = Query(None),  # 改为可选参数
    conversation_id: Optional[str] = None  # 添加会话ID参数
):
    try:
        # 处理 GET 请求
        if request and request.query:
            # POST 请求
            message = request.query
            conversation_id = request.conversation_id
            platform = request.platform
            logger.info(f"POST 请求 - 平台: {platform}, 消息: {message}, 对话ID: {conversation_id}")
        elif query:
            # GET 请求
            message = query
            # 使用查询参数中的 conversation_id
            logger.info(f"GET 请求 - 平台: {platform}, 消息: {message}, 对话ID: {conversation_id}")
        else:
            logger.error("缺少查询参数")
            raise HTTPException(status_code=400, detail="Missing query parameter")

        # 验证平台参数
        if not platform:
            logger.error("缺少平台参数")
            raise HTTPException(status_code=400, detail="Platform parameter is required")

        # 验证平台是否有效
        if platform not in DIFY_PLATFORMS:
            logger.error(f"无效的平台: {platform}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(DIFY_PLATFORMS.keys())}"
            )

        # 创建对应平台的客户端
        client = DifyClient(platform=platform)
        logger.info(f"开始调用 Dify API - 平台: {platform}, 对话ID: {conversation_id}")
        
        response = client.chat(
            message=message,
            conversation_id=conversation_id,
            stream=False
        )
        
        # 确保返回的响应中包含 conversation_id
        if isinstance(response, dict):
            # 获取返回的 conversation_id
            current_conversation_id = response.get('conversation_id', '')
            logger.info(f"Dify API 调用成功 - 平台: {platform}, 对话ID: {current_conversation_id}")
            # 确保返回中包含 conversation_id
            return {
                **response,
                'conversation_id': current_conversation_id
            }
            
        return response
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat-messages")
async def dify_chat(request: DifyRequest):
    try:
        logger.info(f"原生 API 请求 - 平台: {request.platform}, 消息: {request.query}")
        
        if request.platform not in DIFY_PLATFORMS:
            logger.error(f"无效的平台: {request.platform}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(DIFY_PLATFORMS.keys())}"
            )

        client = DifyClient(platform=request.platform)
        
        if request.files:
            logger.info(f"带图片的请求 - 平台: {request.platform}")
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
            logger.info(f"流式响应 - 平台: {request.platform}")
            return Response(
                content=response,
                media_type="text/event-stream"
            )
        
        logger.info(f"请求完成 - 平台: {request.platform}")
        return response

    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/messages")
async def get_history(
    conversation_id: str,
    platform: str = Query(..., description="选择平台")  # 平台参数改为必填
):
    try:
        logger.info(f"获取对话历史 - 平台: {platform}, 对话ID: {conversation_id}")
        
        if platform not in DIFY_PLATFORMS:
            logger.error(f"无效的平台: {platform}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(DIFY_PLATFORMS.keys())}"
            )
            
        client = DifyClient(platform=platform)
        response = client.get_conversation_history(conversation_id)
        logger.info(f"获取历史记录成功 - 平台: {platform}")
        return response
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("服务启动")
    uvicorn.run(app, host="0.0.0.0", port=8000) 