from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN


class EchoBot:
    def __init__(self, memory_manager, persona_manager):
        self.memory = memory_manager
        self.persona = persona_manager
        self.app = Application.builder().token(BOT_TOKEN).build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("profile", self.cmd_profile))
        self.app.add_handler(CommandHandler("whoami", self.cmd_whoami))
        self.app.add_handler(CommandHandler("reset", self.cmd_reset))

        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        self.app.add_error_handler(self.error_handler)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name

        keyboard = [
            [KeyboardButton("🧘 Ментор-стоик")],
            [KeyboardButton("😎 Лучший друг")],
            [KeyboardButton("✨ Творческая муза")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            f"Привет, {user_name}! 👋\n\n"
            f"Я — Эхо, нейросеть с памятью. Выбери, каким собеседником мне быть сегодня:\n\n"
            f"🧘 Ментор-стоик — мудрый, спокойный\n"
            f"😎 Лучший друг — дерзкий, с юмором\n"
            f"✨ Творческая муза — вдохновляющая, хаотичная\n\n"
            f"Потом можно сменить архетип командой /profile",
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        text = update.message.text.strip()

        archetype_map = {
            "🧘 Ментор-стоик": "mentor",
            "😎 Лучший друг": "best_friend",
            "✨ Творческая муза": "muse"
        }

        if text in archetype_map:
            self.persona.set_archetype(user_id, archetype_map[text])
            greeting = self.persona.get_greeting(user_id)
            await update.message.reply_text(
                f"✅ Архетип «{text[2:]}» активирован!\n\n{greeting}"
            )
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        extracted = self.memory.process_message(user_id, text)
        print(f"[DEBUG] Extracted from '{text}': {extracted}")

        context_data = self.memory.get_context(user_id)

        facts_str = self._format_facts(context_data["facts"])

        history_for_llm = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in context_data["history"][-20:]
        ]

        system_prompt = self.persona.get_system_prompt(user_id)

        from llm import generate_response
        response = generate_response(system_prompt, history_for_llm, text, facts_str)

        self.memory.storage.add_message(user_id, "bot", response)

        await update.message.reply_text(response)

    async def cmd_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [KeyboardButton("🧘 Ментор-стоик")],
            [KeyboardButton("😎 Лучший друг")],
            [KeyboardButton("✨ Творческая муза")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        current = self.persona.get_current_archetype_name(update.effective_user.id)
        await update.message.reply_text(
            f"Сейчас активен: {current}\n\nВыбери новый архетип:",
            reply_markup=reply_markup
        )

    async def cmd_whoami(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        facts = self.memory.storage.get_facts(user_id)

        if not facts:
            await update.message.reply_text(
                "🤷 Я пока ничего о тебе не знаю. Расскажи что-нибудь!"
            )
            return

        grouped = {}
        for fact in facts:
            entity = fact["entity"]
            if entity not in grouped:
                grouped[entity] = []
            grouped[entity].append(f"{fact['attribute']} = {fact['value']}")

        dossier = "📋 Твоё досье:\n\n"
        for entity, attrs in grouped.items():
            dossier += f"🔹 {entity}:\n"
            for attr in attrs:
                dossier += f"   • {attr}\n"

        dossier += f"\nВсего фактов: {len(facts)}"
        await update.message.reply_text(dossier)

    async def cmd_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.memory.storage.cursor.execute("DELETE FROM facts WHERE user_id = ?", (user_id,))
        self.memory.storage.cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        self.memory.storage.conn.commit()

        await update.message.reply_text(
            "🧹 Память очищена. Начинаем с чистого листа.\n"
            "Выбери архетип: /start"
        )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"Error: {context.error}")
        if update and update.message:
            await update.message.reply_text("Что-то пошло не так. Попробуй ещё раз.")

    def _format_facts(self, facts: list) -> str:
        if not facts:
            return ""
        lines = []
        for f in facts:
            lines.append(f"- {f['entity']}: {f['attribute']} = {f['value']}")
        return "\n".join(lines)

    def run(self):
        print("🤖 Echo Bot запущен...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)