from .storage import MemoryStorage
from .extractor import extract_entities

class MemoryManager:
    def __init__(self):
        self.storage = MemoryStorage()

    def process_message(self, user_id: int, text: str) -> dict:
        extracted = extract_entities(text)

        for entity in extracted.get("entities", []):
            self.storage.add_fact(
                user_id=user_id,
                entity=entity["entity"],
                attribute=entity["attribute"],
                value=entity["value"],
                confidence=entity["confidence"]
            )

        self.storage.add_message(
            user_id=user_id,
            role="user",
            content=text,
            sentiment=extracted.get("sentiment")
        )

        return extracted

    def get_context(self, user_id: int) -> dict:
        facts = self.storage.get_facts(user_id)
        history = self.storage.get_last_messages(user_id)
        return {
            "facts": facts,
            "history": history
        }

    def close(self):
        self.storage.close()
