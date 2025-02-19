# API-difycall

API-difycall 是一个轻量级的 Python 项目，用于简化与 Dify API 的交互。Dify 是一个强大的 AI 应用开发平台，本库旨在让开发者能够更便捷地集成和使用 Dify 的各项功能。

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
- http://localhost:8000/chat/history
- http://localhost:8000/workflows/run


上面的接口：
```

```

## 方法

- `chat(options)`: 发送对话消息
- `completion(options)`: 获取文本补全
- `messages(conversationId)`: 获取对话历史记录



## 联系方式

如有问题或建议，请提交 Issue。