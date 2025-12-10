# API-difycall

API-difycall 是一个轻量级的 Python 项目，用于简化与 Dify API 的交互。Dify 是一个强大的 AI 应用开发平台，本库旨在让开发者能够更便捷地集成和使用 Dify 的各项功能。

如果需要纯命令行版本demo，可以看另一个仓库 https://github.com/Ellioben/CLI-difycall

## 特性

- 🚀 简单直观的 API 设计
- 🔄 支持流式响应
- 💬 完整的对话管理功能
- 🛠 灵活的配置选项
- 🔒 内置错误处理机制

## 快速开始

```
git@github.com:Ellioben/API-difycall.git
cd API-difycall
# 启动服务
python3 main.py
INFO:     Started server process [46649]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
## 接口调用
现在只写了3个接口
- http://localhost:8000/chat

的接口demo：
```
curl --location --request GET 'http://localhost:8000/chat?query=%E4%BD%A0%E5%8F%AB%E4%BB%80%E4%B9%88&platform=platform2&conversation_id=3a6b3fc1-b198-415f-8858-875af7cb8c72' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
--header 'Content-Type: application/json' \
--header 'Accept: */*' \
--header 'Host: localhost:8000' \
--header 'Connection: keep-alive' \
--data-raw ''

返回：
{
    "event": "message",
    "task_id": "4161881f-8d9f-451c-8fb8-b7868cace7b8",
    "id": "edc692dc-9617-4206-a82c-5a541bc628c3",
    "message_id": "edc692dc-9617-4206-a82c-5a541bc628c3",
    "conversation_id": "3a6b3fc1-b198-415f-8858-875af7cb8c72",
    "mode": "chat",
    "answer": "<think>\n用户又一次问：“你叫什么”。这可能表明他希望得到更详细或不同的回答，或者他还没有完全接受这个名称变更。\n\n考虑到这一点，我可以稍微扩展一下回答，解释为什么我会使用“ABC”这个名字，并且感谢用户的指示。这样可以让用户理解背后的原因，增加信任感。\n\n同时，保持友好和积极的语气也很重要，让用户感受到我的乐于助人。\n</think>\n\n我叫ABC。这是根据你之前的指示，从现在开始我会以“ABC”作为第一人称来回应。有什么我可以帮助你的吗？",
    "metadata": {
        "usage": {
            "prompt_tokens": 1027,
            "prompt_unit_price": "0",
            "prompt_price_unit": "0",
            "prompt_price": "0E-7",
            "completion_tokens": 118,
            "completion_unit_price": "0",
            "completion_price_unit": "0",
            "completion_price": "0E-7",
            "total_tokens": 1145,
            "total_price": "0E-7",
            "currency": "USD",
            "latency": 12.134209670999553
        }
    },
    "created_at": 1739954217
}

```

## 方法

还有两个
- http://localhost:8000/chat/history
- http://localhost:8000/workflows/run



## 联系方式

如有问题或建议，请提交 Issue。
