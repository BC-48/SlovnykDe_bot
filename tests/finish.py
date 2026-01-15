from utils import send_with_keyboard
from keyboards import main_menu
from texts import TEXTS



async def finish_test(update, context, stopped=False):
    user = context.user_data["storage"]
    chat_id = update.effective_chat.id

    # 🧹 видаляємо повідомлення з питанням
    msg_id = context.user_data.get("test_message_id")
    if msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except:
            pass

    # якщо тест вже не активний — нічого не робимо
    if not context.user_data.get("test_active"):
        return

    # дозволяємо знову брати нові слова
    user["can_get_new_words"] = True
    context.user_data.pop("custom_test", None)

    test_words = context.user_data.get("test_words", [])
    total = len(test_words)

    # ✅ ПРАВИЛЬНИЙ підрахунок
    correct = context.user_data.get("correct_answers", 0)

    # 🧹 чистимо стан тесту
    for key in [
        "test_words",
        "current_index",
        "test_type",
        "test_active",
        "test_message_id",
        "answered_words",
        "correct_answers",
    ]:
        context.user_data.pop(key, None)

   # 📝 формуємо фінальне повідомлення
    if stopped:
        msg = TEXTS["test_stopped"]
    else:
        percent = (correct / total * 100) if total else 0

        if percent < 30:
            comment = TEXTS["result_bad"]
        elif percent < 50:
            comment = TEXTS["result_ok"]
        elif percent < 80:
            comment = TEXTS["result_good"]
        else:
            comment = TEXTS["result_top"]

        msg = f"{comment}\n\n{TEXTS['test_finished']}\n{correct}/{total}"


    await send_with_keyboard(update, context, msg, main_menu)
