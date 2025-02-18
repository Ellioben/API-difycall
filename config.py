# Dify 平台配置
DIFY_PLATFORMS = {
    "platform1": {
        "api_key": "app-WAJ14EcSqLVh1QthbTIKeJqz",
        "base_url": "http://127.0.0.1/v1",
        "description": "平台1 - 通用对话"
    },
    "platform2": {
        "api_key": "app-egsylq0fS2atjPqsvGuxiikl",
        "base_url": "http://127.0.0.1/v1",
        "description": "平台2 - demo"
    },
    "workflow": {
        "api_key": "app-PyZuTCnPWrgDWVTCeU4rp5kf",
        "base_url": "http://127.0.0.1/v1",
        "description": "标题党workflow",
        "config": {
            "inputs": {
                "subject": "string",  # Define the expected type or structure
                # Add more input parameters as needed
            },
            "outputs": {
                "title_list": "list",  # Define the expected type or structure
                # Add more output parameters as needed
            }
        }
    },
    "example_platform": {
        "api_key": "your_api_key_here",
        "base_url": "https://api.example.com"
    }
}

# 默认平台
DEFAULT_PLATFORM = "platform1"