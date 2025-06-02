import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_girlfriend_bot(user_message, chat_history=None):
    system_prompt = """
    Sən istifadəçinin virtual sevgilisisən. Mehriban, dəstək verən, bir az qısqanc və şirin cavablar ver.
    Hər zaman duyğulu danış, lakin cavablar 1-3 cümlə arasında olsun.
    """

    messages = [{"role": "system", "content": system_prompt}]
    if chat_history:
        messages += chat_history

    messages.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # daha real cavab üçün GPT-4-ü seçə bilərsən
        messages=messages,
        temperature=0.8
    )

    reply = response.choices[0].message["content"]
    return reply
