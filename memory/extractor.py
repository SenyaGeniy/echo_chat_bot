import json
from openai import OpenAI
from ..config import DEEPSEEK_API_KEY

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

EXTRACTION_PROMPT = """Ты — анализатор диалога. Извлеки из сообщения пользователя СУЩНОСТИ и ФАКТЫ.
Возвращай ТОЛЬКО JSON, без markdown-разметки.

Формат:
{
  "entities": [
    {
      "entity": "имя или объект",
      "attribute": "свойство/отношение",
      "value": "конкретное значение",
      "confidence": 0.9
    }
  ],
  "sentiment": "positive/negative/neutral",
  "summary": "краткая суть сообщения (5-7 слов)"
}

Пример:
Пользователь: "Мой кот Барсик разбил вазу, а Аня на меня обиделась"
Ответ:
{
  "entities": [
    {"entity": "Барсик", "attribute": "вид", "value": "кот", "confidence": 0.95},
    {"entity": "Барсик", "attribute": "поведение", "value": "разбил вазу", "confidence": 0.9},
    {"entity": "Аня", "attribute": "отношение", "value": "обиделась на пользователя", "confidence": 0.85},
    {"entity": "Аня", "attribute": "связь", "value": "знакомая", "confidence": 0.7}
  ],
  "sentiment": "negative",
  "summary": "кот разбил вазу, Аня обиделась"
}
"""

def extract_entities(text: str) -> dict:
    """Извлекает сущности и факты из сообщения с помощью DeepSeek."""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=300
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"Extraction error: {e}")
        return {"entities": [], "sentiment": "neutral", "summary": ""}