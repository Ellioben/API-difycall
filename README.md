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
直接启动就行
curl --location --request GET 'http://localhost:8000/chat?query=%E5%8F%AF%E4%BB%A5%E7%BB%99%E6%88%91%E4%BB%8B%E7%BB%8D%E4%B8%80%E4%B8%8B%E9%A1%B9%E7%9B%AE%E5%90%97&platform=platform1' \
--header 'Content-Type: application/json' \
--header 'Accept: */*' \
--header 'Host: localhost:8000' \
--header 'Connection: keep-alive' \

```
上面的接口：
```
你: 介绍一下你自己

AI: <think>
好，我现在要处理用户的请求：“介绍一下你自己”。这是一个比较通用的自我介绍问题。用户可能想了解我的功能、用途或者能力。

首先，我需要回忆一下自己的设定。

接下来，我应该组织一下自我介绍的内容。包括我的定位、主要功能以及一些优势，比如多领域知识和学习能力。这样用户能有一个全面的了解。

然后，考虑用中文表达，确保口语化自然流畅。不需要太正式，但要清晰明了。

最后，整合这些信息，生成一个合适的回答，让用户明白我是如何帮助他们的。
</think>

您好！我是由中国的深度求索（DeepSeek）公司开发的智能助手DeepSeek-R1。如您有任何任何问题，我会尽我所能为您提供帮助。

你: 
```

## 方法

- `chat(options)`: 发送对话消息
- `completion(options)`: 获取文本补全
- `messages(conversationId)`: 获取对话历史记录



## 联系方式

如有问题或建议，请提交 Issue。