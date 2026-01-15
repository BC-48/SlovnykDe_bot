from telegram.ext import ContextTypes
from utils import send_with_keyboard
from keyboards import main_menu
from .words_menu import handle_words_menu
from .trainer_menu import handle_trainer_menu
from .notifications_menu import handle_notifications_menu
from tests import start_test
from texts import TEXTS




async def start(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE):
    # /start з параметром
    if context.args:
        arg = context.args[0].strip()

        if arg.startswith("ex_"):
            # 🧹 видаляємо повідомлення користувача (/start ex_...)
            try:
                await update.message.delete()
            except:
                pass

            word_id = arg[3:]

            if word_id.startswith("w_"):
                user = context.user_data.get("storage")
                if not user:
                    return

                word = next(
                    (w for w in user.get("words", []) if w.get("id") == word_id),
                    None
                )

                # ❌ слово не знайдено
                if not word:
                    await update.message.reply_text("❌ Слово не знайдено")
                    return

                # 📖 формування відповіді
                lines = [
                    f"📖 <b>{word.get('слово')}</b> — {word.get('український переклад')}"
                ]

                examples = word.get("examples", [])
                if examples:
                    for i, ex in enumerate(examples, 1):
                        lines.append(
                            f"\n{i}️⃣ {ex['de']}\n    {ex['ua']}"
                        )
                else:
                    lines.append("\n⚠️ Приклад ще не додано")

                words_msg_id = context.user_data.get("words_msg_id")
                words_list_text = context.user_data.get("words_list_text")

                if not words_msg_id or not words_list_text:
                    return

                examples_text = "\n".join(lines)

                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=words_msg_id,
                    text=f"{words_list_text}\n\n\n{examples_text}",
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                return


    # звичайний /start
    await send_with_keyboard(
        update,
        context,
        TEXTS["welcome"],
        main_menu
    )

async def handle_menu(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # ==================================================
    # ⬅️ Назад — працює завжди
    # ==================================================
    if text == TEXTS["btn_back"]:
        context.user_data.pop("custom_test", None)
        await send_with_keyboard(update, context, TEXTS["main_menu"], main_menu)
        return

    # ==================================================
    # ❌ Активний тест → меню ігноруємо
    # ==================================================
    if context.user_data.get("test_active"):
        return

    # ==================================================
    # 🛠 ВЛАСНИЙ РЕЖИМ АКТИВНИЙ → ВСЕ в trainer_menu
    # ==================================================
    if context.user_data.get("custom_test"):
        await handle_trainer_menu(update, context)
        return

    # 🧠 АРТИКЛІ — ОКРЕМИЙ ТЕСТ
    if text == TEXTS["btn_articles"]:
        await start_test(update, context, scope="articles", ttype="article", test_size=15)
        return

    # ==================================================
    # 🧠 ВХІД У ТРЕНАЖЕР
    # ==================================================
    if text.startswith(TEXTS["btn_trainer"]):
        await handle_trainer_menu(update, context)
        return

    # ==================================================
    # 🧠 КНОПКИ ТРЕНАЖЕРА (швидкі режими)
    # ==================================================
    if text in (
        TEXTS["btn_choice"],
        TEXTS["btn_write"],
        TEXTS["btn_articles"],
        TEXTS["btn_prepositions"],
        TEXTS["btn_custom"],
    ):
        await handle_trainer_menu(update, context)
        return

    # 🔤 СЛОВА
    if text == TEXTS["btn_get_words"] or text == TEXTS["btn_my_words"]:
        await handle_words_menu(update, context)
        return

    # ВСЕ ІНШЕ, ЩО СТОСУЄТЬСЯ СЛІВ — ТЕЖ ТУДИ
    if context.user_data.get("words_menu_active") and text not in (
        TEXTS["btn_settings"],
    ):
        await handle_words_menu(update, context)
        return



    # ⚙️ СПОВІЩЕННЯ
    if text in (
        TEXTS["btn_settings"],
        TEXTS["setup_fast"],
        TEXTS["setup_hard"],
    ):
        # 🔥 ВАЖЛИВО: прибираємо words_menu_active
        context.user_data.pop("words_menu_active", None)

        await handle_notifications_menu(update, context)
        return



    # ==================================================
    # ❌ FALLBACK
    # ==================================================
    await send_with_keyboard(update, context, TEXTS["unknown_command"], main_menu)

