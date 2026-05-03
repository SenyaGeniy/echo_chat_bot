from memory import MemoryManager
from persona.persona_manager import PersonaManager
from bot import EchoBot


def main():
    print("📦 Инициализация памяти...")
    memory = MemoryManager()

    print("🎭 Загрузка архетипов...")
    persona = PersonaManager()

    print("🚀 Запуск бота...")
    bot = EchoBot(memory, persona)
    bot.run()


if __name__ == "__main__":
    main()