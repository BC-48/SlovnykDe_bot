import asyncio
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from words_service import update_status
from utils import send_with_keyboard
from .finish import finish_test
from utils import format_word, normalize_answer
from telegram.error import BadRequest
from texts import TEXTS


async def send_next_write(update, context):
    user = context.user_data["storage"]
    chat = update.effective_chat
    idx = context.user_data["current_index"]
    words = context.user_data["test_words"]

    # кінець тесту
    if idx >= len(words):
        await finish_test(update, context)
        return

    word = words[idx]
    msg_id = context.user_data.get("test_message_id")

    total = len(words)
    current = idx + 1

    text = TEXTS["question_write"].format(
        current=current,
        total=total,
        ua=word["український переклад"]
    )


    if msg_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=msg_id,
                text=text,
                parse_mode="HTML"
            )
        except BadRequest:
            # повідомлення вже має такий самий текст — нічого не робимо
            pass
    else:
        msg = await chat.send_message(
            text=text,
            parse_mode="HTML"
        )
        context.user_data["test_message_id"] = msg.message_id


async def handle_write(update, context):
    user = context.user_data["storage"]
    text = update.message.text.strip().lower()

    # ❌ скасування тесту
    if text.lower() == TEXTS["btn_cancel_test"].lower():
        await finish_test(update, context, stopped=True)
        return
    
    # 🧹 видаляємо повідомлення користувача
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except:
        pass


    if not context.user_data.get("test_active"):
        return

    idx = context.user_data["current_index"]
    word = context.user_data["test_words"][idx]

    correct_word = word["німецьке слово"].lower()
    correct_article = word.get("артикль", "").lower()

    parts = text.split()

    # ⬇️ розбір відповіді
    if len(parts) == 1:
        user_article = None
        user_word = parts[0]
    elif parts[0] in ("der", "die", "das"):
        user_article = parts[0]
        user_word = parts[1]
    else:
        user_article = None
        user_word = parts[-1]

    # ✅ перевірка
    word_ok = user_word == correct_word
    article_ok = (
        not correct_article
        or user_article is None
        or user_article == correct_article
    )

    correct = word_ok and article_ok

    # 📊 streaks
    if correct:
        word["correct_streak"] += 1
        word["wrong_streak"] = 0
        context.user_data["correct_answers"] += 1

    else:
        word["wrong_streak"] += 1
        word["correct_streak"] = 0

    update_status(word)

    # прибираємо зі "нових"
    new_words = user.get("new_words", [])
    if word in new_words:
        new_words.remove(word)

    context.user_data.setdefault("answered_words", []).append(word)
    context.user_data["current_index"] += 1

    msg_id = context.user_data.get("test_message_id")
    chat = update.effective_chat

    result_text = (
        TEXTS["answer_correct"]
        if correct
        else f"{TEXTS['answer_wrong']}\n{TEXTS['answer_right_is']} <b>{format_word(word)}</b>"
    )


    if msg_id:
        await context.bot.edit_message_text(
            chat_id=chat.id,
            message_id=msg_id,
            text=result_text,
            parse_mode="HTML"
        )

    await asyncio.sleep(1 if correct else 2)
    await send_next_write(update, context)

    await asyncio.sleep(1 if correct else 2)
    await send_next_write(update, context)
