import os
import requests
import jwt
import time
import gradio as gr

# 设置API密钥
os.environ["ZHIPUAI_API_KEY"] = "# 替换为你的API密钥"  # 替换为你的API密钥

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

history = []

def mbti_translate(user_input, input_mbti, output_mbti):
    messages = [
        {"role": "system", "content": f"你是一个MBTI研究专家，请你将{input_mbti}人格的话翻译成{output_mbti}人格能理解的话。"},
        {"role": "user", "content": user_input}
    ]
    
    data = {
        "model": "glm-4",
        "messages": messages,
        "max_tokens": 8192,
        "temperature": 0.8,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    try:
        ans = response.json()
        if "choices" in ans:
            bot_response = ans["choices"][0]["message"]["content"]
            history.append({"input": user_input, "output": bot_response})
            return bot_response
        else:
            return f"API response does not contain 'choices'. Full response: {ans}"
    except Exception as e:
        return f"An error occurred: {str(e)}. Full response: {response.text}"

def get_history():
    return "\n\n".join([f"输入: {entry['input']}\n输出: {entry['output']}" for entry in history])

css = """
body, html { height: 100%; margin: 0; padding: 0; }
.gradio-app { display: flex; flex-direction: column; height: 100%; }
.output-container { flex-grow: 1; overflow-y: auto; padding: 10px; margin-bottom: 60px; }
.input-container { flex-shrink: 0; background: #fff; padding: 10px; width: 100%; position: fixed; bottom: 0; left: 0; z-index: 1000; }
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("# MBTI Translator")
    gr.Markdown("Translate phrases from one MBTI type to another using GLM-4.")

    with gr.Row():
        input_mbti = gr.Dropdown(choices=["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"], label="输入 MBTI 类型")
        output_mbti = gr.Dropdown(choices=["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"], label="输出 MBTI 类型")

    user_input = gr.Textbox(label="输入文本", lines=3)
    output_text = gr.Textbox(label="输出文本", lines=3)
    
    translate_button = gr.Button("翻译")
    translate_button.click(mbti_translate, inputs=[user_input, input_mbti, output_mbti], outputs=output_text)
    
    history_output = gr.Textbox(label="翻译历史", lines=10, interactive=False)
    history_button = gr.Button("查看历史")
    history_button.click(get_history, outputs=history_output)

demo.launch()
