import os
os.environ["ZHIPUAI_API_KEY"] = "6ed79daefe0c3719ff4ef145d404ef68.YB22hpkc0QGmrYfv"
import requests
import jwt
import time

def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )

api_key = os.environ["ZHIPUAI_API_KEY"]
token = generate_token(api_key, 60)
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# 初始化对话历史，去掉笑话请求
messages = [
    {
        "role": "system",
        "content": "你是一个乐于助人的助手"
    }
]

while True:
    # 获取用户输入
    user_input = input("用户: ")
    if user_input.lower() == '退出':
        break

    # 将用户输入添加到对话历史中
    messages.append({
        "role": "user",
        "content": user_input
    })

    data = {
        "model": "glm-4",
        "messages": messages,
        "max_tokens": 8192,
        "temperature": 0.8,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    ans = response.json()

    # 打印GLM-4模型的回复
    print("GLM-4:", ans["choices"][0]["message"]["content"])

    # 将GLM-4模型的回复添加到对话历史中
    messages.append({
        "role": "assistant",
        "content": ans["choices"][0]["message"]["content"]
    })
