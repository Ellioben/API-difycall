from dify_client import DifyClient

def main():
    client = DifyClient(user_id="abc-123")  # 使用与curl相同的用户ID
    conversation_id = ""
    
    print("欢迎使用Dify聊天! (输入 'quit' 退出, 输入 'image' 发送图片消息)")
    
    while True:
        user_input = input("\n你: ")
        
        if user_input.lower() == 'quit':
            break
        
        if user_input.lower() == 'image':
            image_url = input("请输入图片URL: ")
            message = input("请输入消息: ")
            print("\nAI: ", end='')
            for chunk in client.chat_with_image(message, image_url, conversation_id):
                print(chunk, end='', flush=True)
        else:
            print("\nAI: ", end='')
            for chunk in client.chat(user_input, conversation_id):
                print(chunk, end='', flush=True)
        print()

if __name__ == "__main__":
    main() 