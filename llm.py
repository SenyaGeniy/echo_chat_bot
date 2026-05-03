from openai import OpenAI
from config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


def generate_response(system_prompt: str, messages_history: list, user_message: str, user_facts: str = "") -> str:
    full_messages = [{"role": "system", "content": system_prompt}]

    if user_facts:
        full_messages.append({
            "role": "system",
            "content": f"Информация о пользователе, которую ты знаешь (используй естественно, не перечисляй списком):\n{user_facts}"
        })

    for msg in messages_history:
        full_messages.append(msg)

    full_messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=full_messages,
            temperature=0.8,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM error: {e}")
        return "Прости, я немного завис. Можешь повторить?"