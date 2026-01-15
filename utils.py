import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from texts import TEXTS


# ==========================
# Надсилає повідомлення з клавіатурою або тимчасове повідомлення
# ==========================
async def send_with_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, keyboard=None, save_as_menu=True, dont_delete_old=False):
    chat_id = update.effective_chat.id

    # Використовуємо update.message, якщо є, інакше callback_query
    if hasattr(update, "message") and update.message:
        sent = await update.message.reply_text(text, reply_markup=keyboard)
    elif hasattr(update, "callback_query") and update.callback_query:
        sent = await update.effective_chat.send_message(text=text, reply_markup=keyboard)
    else:
        sent = await context.bot.send_message(chat_id, text=text, reply_markup=keyboard)

    if save_as_menu and not dont_delete_old:
        # Видаляємо попереднє меню
        old_menu_id = context.user_data.get("menu_message_id")
        if old_menu_id and old_menu_id != sent.message_id:
            try:
                await context.bot.delete_message(chat_id, old_menu_id)
            except:
                pass
        context.user_data["menu_message_id"] = sent.message_id

        # Видаляємо попередні слова
        old_words_id = context.user_data.get("words_msg_id")
        if old_words_id and old_words_id != sent.message_id:
            try:
                await context.bot.delete_message(chat_id, old_words_id)
            except:
                pass
            context.user_data["words_msg_id"] = None
    elif not save_as_menu:
        old_words_id = context.user_data.get("words_msg_id")
        if old_words_id and old_words_id != sent.message_id:
            try:
                await context.bot.delete_message(chat_id, old_words_id)
            except:
                pass
        context.user_data["words_msg_id"] = sent.message_id

        # 🧹 видаляємо ПОТОЧНЕ повідомлення користувача після відповіді бота
        if hasattr(update, "message") and update.message:
            try:
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=update.message.message_id
                )
            except:
                pass
            
    # 🧹 видаляємо повідомлення користувача З НЕВЕЛИКОЮ ЗАТРИМКОЮ
    if hasattr(update, "message") and update.message:
        msg_id = update.message.message_id
        chat_id = update.effective_chat.id

        async def delayed_delete():
            await asyncio.sleep(0.1)
            try:
                await context.bot.delete_message(chat_id, msg_id)
            except:
                pass

        asyncio.create_task(delayed_delete())
            


    return sent

# ==========================
# Надсилає сповіщення з кнопками Так / Ні
# ==========================
async def send_notification(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, test_type: str):
    keyboard = [
        [InlineKeyboardButton(TEXTS["btn_yes"], callback_data=f"notify:{test_type}:yes")],
        [InlineKeyboardButton(TEXTS["btn_no"], callback_data=f"notify:{test_type}:no")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

def format_word(word: dict) -> str:
    article = word.get("артикль", "").strip()
    base = word.get("німецьке слово", "").strip()
    prep = word.get("präposition", "").strip()

    parts = []

    if article:
        parts.append(article)

    parts.append(base)

    if prep:
        parts.append(prep)

    return " ".join(parts)


def normalize_answer(text: str):
    """
    Розбиває відповідь користувача на (артикль, слово)
    """
    parts = text.strip().lower().split()

    if len(parts) == 1:
        return None, parts[0]

    if len(parts) >= 2 and parts[0] in {"der", "die", "das"}:
        return parts[0], parts[1]

    return None, parts[-1]
