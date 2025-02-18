from fastapi import APIRouter, HTTPException, Response, Query
from pydantic import BaseModel
from typing import Optional, List, Dict
from config import DIFY_PLATFORMS
from chat_logic import DifyClient
from workflow_logic import DifyWorkflow
import logging

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

router = APIRouter()

# 请求模型
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
    platform: str

class SimpleRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    platform: str

class WorkflowRequest(BaseModel):
    inputs: Dict = {}
    query: str
    file_urls: Optional[List[str]] = None
    file_type: str = "image"
    response_mode: str = "blocking"
    platform: str

class WorkflowRunRequest(BaseModel):
    inputs: Dict
    response_mode: str = "streaming"
    user: str
    platform: str

@router.get("/platforms")
async def get_platforms():
    logger.info("获取平台列表")
    return DifyClient.get_available_platforms()

@router.get("/chat")
@router.post("/chat")
async def chat(
    request: Optional[SimpleRequest] = None,
    query: Optional[str] = None,
    platform: str = Query(None),
    conversation_id: Optional[str] = None
):
    try:
        if request and request.query:
            message = request.query
            conversation_id = request.conversation_id
            platform = request.platform
            logger.info(f"POST 请求 - 平台: {platform}, 消息: {message}, 对话ID: {conversation_id}")
        elif query:
            message = query
            logger.info(f"GET 请求 - 平台: {platform}, 消息: {message}, 对话ID: {conversation_id}")
        else:
            logger.error("缺少查询参数")
            raise HTTPException(status_code=400, detail="Missing query parameter")

        if not platform:
            logger.error("缺少平台参数")
            raise HTTPException(status_code=400, detail="Platform parameter is required")

        if platform not in DIFY_PLATFORMS:
            logger.error(f"无效的平台: {platform}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(DIFY_PLATFORMS.keys())}"
            )

        client = DifyClient(platform=platform)
        logger.info(f"开始调用 Dify API - 平台: {platform}, 对话ID: {conversation_id}")
        
        response = client.chat(
            message=message,
            conversation_id=conversation_id,
            stream=False
        )
        
        if isinstance(response, dict):
            current_conversation_id = response.get('conversation_id', '')
            logger.info(f"Dify API 调用成功 - 平台: {platform}, 对话ID: {current_conversation_id}")
            return {
                **response,
                'conversation_id': current_conversation_id
            }
            
        return response
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history")
async def get_chat_history(
    conversation_id: str = Query(..., description="对话ID"),
    platform: str = Query(..., description="选择平台")
):
    """
    获取聊天历史记录

    :param conversation_id: 对话ID
    :param platform: 平台名称
    :return: 聊天历史记录
    """
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
        
        if isinstance(response, dict):
            logger.info(f"获取历史记录成功 - 平台: {platform}")
            return {
                'data': [
                    {
                        'id': msg.get('id'),
                        'conversation_id': msg.get('conversation_id'),
                        'inputs': msg.get('inputs', {}),
                        'query': msg.get('query'),
                        'message_files': [
                            {
                                'id': file.get('id'),
                                'type': file.get('type'),
                                'url': file.get('url'),
                                'belongs_to': file.get('belongs_to')
                            } for file in msg.get('message_files', [])
                        ],
                        'agent_thoughts': [
                            {
                                'id': thought.get('id'),
                                'message_id': thought.get('message_id'),
                                'position': thought.get('position'),
                                'thought': thought.get('thought'),
                                'observation': thought.get('observation'),
                                'tool': thought.get('tool'),
                                'tool_input': thought.get('tool_input'),
                                'created_at': thought.get('created_at'),
                                'message_files': thought.get('message_files', [])
                            } for thought in msg.get('agent_thoughts', [])
                        ],
                        'answer': msg.get('answer'),
                        'created_at': msg.get('created_at'),
                        'feedback': msg.get('feedback', {}),
                        'retriever_resources': msg.get('retriever_resources', [])
                    } for msg in response.get('data', [])
                ],
                'has_more': response.get('has_more', False),
                'limit': response.get('limit')
            }
        return response
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/completion")
async def create_workflow_completion(request: WorkflowRequest):
    try:
        logger.info(f"创建工作流任务 - 平台: {request.platform}, 查询: {request.query}")
        
        if request.platform not in DIFY_PLATFORMS:
            logger.error(f"无效的平台: {request.platform}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(DIFY_PLATFORMS.keys())}"
            )

        workflow_client = DifyWorkflow(platform=request.platform)
        
        if request.file_urls:
            response = workflow_client.create_completion_with_files(
                query=request.query,
                file_urls=request.file_urls,
                file_type=request.file_type,
                inputs=request.inputs,
                response_mode=request.response_mode
            )
        else:
            response = workflow_client.create_completion(
                inputs=request.inputs,
                query=request.query,
                response_mode=request.response_mode
            )
        
        logger.info(f"工作流任务创建成功 - 平台: {request.platform}")
        return response

    except Exception as e:
        logger.error(f"创建工作流任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/streaming-completion")
async def create_streaming_workflow_completion(request: WorkflowRequest):
    try:
        logger.info(f"创建流式工作流任务 - 平台: {request.platform}, 查询: {request.query}")
        
        if request.platform not in DIFY_PLATFORMS:
            logger.error(f"无效的平台: {request.platform}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(DIFY_PLATFORMS.keys())}"
            )

        workflow_client = DifyWorkflow(platform=request.platform)
        
        response = workflow_client.create_streaming_completion(
            query=request.query,
            inputs=request.inputs,
            files=[{"type": request.file_type, "url": url} for url in request.file_urls or []]
        )
        
        logger.info(f"流式工作流任务创建成功 - 平台: {request.platform}")
        return Response(content=response, media_type="text/event-stream")

    except Exception as e:
        logger.error(f"创建流式工作流任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/run")
async def run_workflow(request: WorkflowRunRequest):
    """
    运行工作流任务

    :param request: 请求体
    :return: 工作流响应
    """
    try:
        logger.info(f"运行工作流任务 - 平台：{request.platform}, 用户: {request.user}, 输入: {request.inputs}")
        
        if request.platform not in DIFY_PLATFORMS:
            logger.error(f"无效的平台: {request.platform}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Available platforms: {list(DIFY_PLATFORMS.keys())}"
            )

        workflow_client = DifyWorkflow(platform=request.platform, user_id=request.user)
        
        response = workflow_client.create_streaming_completion(
            query="",
            inputs=request.inputs
        )
        
        logger.info(f"工作流任务运行成功 - 用户: {request.user}")
        return Response(content=response, media_type="text/event-stream")

    except Exception as e:
        logger.error(f"运行工作流任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 