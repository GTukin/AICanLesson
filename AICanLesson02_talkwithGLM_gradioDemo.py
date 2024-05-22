import os
import requests
import jwt
import time
import numpy as np
import gradio as gr

# 设置API密钥
os.environ["ZHIPUAI_API_KEY"] = "替换为你的API密钥"  # 

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
token = generate_token(api_key, 200)
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

messages = [{"role": "system", "content": "你是一个乐于助人的助手"}]
all_messages_html = ""

def chat_with_glm4(user_input):
    global messages, all_messages_html

    if user_input.lower() == '退出':
        messages = [{"role": "system", "content": "你是一个乐于助人的助手"}]
        all_messages_html = ""
        return all_messages_html, "对话已结束，欢迎再次使用。"

    messages.append({"role": "user", "content": user_input})

    data = {
        "model": "glm-4",
        "messages": messages,
        "max_tokens": 8192,
        "temperature": 0.8,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    ans = response.json()

    bot_response = ans["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": bot_response})

    user_bubble = f'<div class="bubble user-bubble">{user_input}</div>'
    copy_button = f'<button onclick="navigator.clipboard.writeText(\'{bot_response}\')" class="copy-button">&#x1f4cb;</button>'

    bot_bubble = f'<div class="bubble bot-bubble">{bot_response}{copy_button}</div>'
    all_messages_html += user_bubble + bot_bubble

    return all_messages_html

css="""
body, html { height: 100%; margin: 0; padding: 0; }
.gradio-app { display: flex; flex-direction: column; height: 100%; }
.output-container { flex-grow: 1; overflow-y: auto; padding: 10px; margin-bottom: 60px; }
.input-container { flex-shrink: 0; background: #fff; padding: 10px; width: 100%; position: fixed; bottom: 0; left: 0; z-index: 1000; }
.bubble { padding: 10px; margin: 10px; border-radius: 20px; max-width: 70%; clear: both; display: flex; align-items: center; }
.user-bubble { background-color: #f1f0f0; float: right; }
.bot-bubble { background-color: #007bff; color: #ffffff; float: left; }
.copy-button {margin-left: 8px;background-color: #ffffff;color: #007bff;border: none;cursor: pointer;padding: 2px 6px;font-size: 14px;border-radius: 6px;}
.send-button { padding: 4px 6px; font-size: 18px; height: 80px; width: auto; border-radius: 4px;}  /* 显式设置按钮的宽度、高度、填充、字体和圆角 */
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("# Design with AI")  # 使用 Markdown 添加标题
    gr.Markdown("Explore the possibilities of designing with artificial intelligence.")
    
    with gr.Tab("Chat with GLM-4"):
        with gr.Column():
            text_output_html = gr.HTML()
        with gr.Row(variant="panel"):
            with gr.Column(variant="panel",scale=8):
                text_input = gr.Textbox(label="输入您的问题：", lines=1)
            with gr.Column(variant="panel",scale=2):
                text_button = gr.Button("发送", variant="primary")
                text_button.click(chat_with_glm4, inputs=text_input, outputs=[text_output_html])
                text_button.elem_classes = ["send-button"]  # 为 Send 按钮应用自定义类
    
    with gr.Tab("Hello World"):
        gr.Markdown("### This is a simple Hello World module")
        gr.Textbox(value="Hello, World!", label="Sample Output")

demo.launch()
