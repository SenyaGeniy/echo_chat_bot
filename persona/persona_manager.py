from persona.archetypes import ARCHETYPES

class PersonaManager:
    def __init__(self):
        self.user_archetypes = {}
        self.archetypes = ARCHETYPES

    def set_archetype(self, user_id: int, archetype_key: str):
        if archetype_key in self.archetypes:
            self.user_archetypes[user_id] = archetype_key
            print(f"[Persona] User {user_id} switched to {archetype_key}")

    def get_archetype(self, user_id: int) -> str:
        return self.user_archetypes.get(user_id, "mentor")

    def get_system_prompt(self, user_id: int) -> str:
        key = self.get_archetype(user_id)
        return self.archetypes[key]["system_prompt"]

    def get_greeting(self, user_id: int) -> str:
        key = self.get_archetype(user_id)
        return self.archetypes[key]["greeting"]

    def get_current_archetype_name(self, user_id: int) -> str:
        key = self.get_archetype(user_id)
        return self.archetypes[key]["name"]