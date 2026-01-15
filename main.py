import asyncio
from datetime import datetime
from storage import load_user, save_user, load_base_words
import os
from menu.notifications_menu import handle_clear_notification
from texts import TEXTS




from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from utils import send_notification

# меню
from menu import (
    start,
    handle_menu,
    handle_notification_input,
    handle_notify_answer,
)



# тести
from tests import (
    handle_inline_answer,
    handle_write,
    finish_test,
)
BASE_WORDS = load_base_words()

# ==========================
# ТЕКСТОВИЙ РОУТЕР
# ==========================
async def text_router(update, context):
    text = update.message.text.strip()
    chat_id = update.effective_chat.id

    if "storage" not in context.user_data:
        context.user_data["storage"] = load_user(chat_id, BASE_WORDS)

    # 🔔 Налаштування сповіщень (активний сценарій)
    if context.user_data.get("notification_setup"):
        await handle_notification_input(update, context)
        return

    # ❌ Скасування тесту
    if text == TEXTS["btn_cancel_test"] and context.user_data.get("test_active"):
        await finish_test(update, context, stopped=True)
        return

    # ✍️ Написання слова (під час тесту)
    if context.user_data.get("test_active") and context.user_data.get("test_type") == "написати":
        await handle_write(update, context)
        return

    save_user(chat_id, context.user_data["storage"])

    # 📋 Звичайне меню
    await handle_menu(update, context)


# ==========================
# ФОНОВА ЗАДАЧА СПОВІЩЕНЬ
# ==========================
async def notification_task(app):
    sent_flags = {}  # chat_id -> set(HH:MM)

    while True:
        now = datetime.now()
        for filename in os.listdir("data"):
            if not filename.startswith("user_"):
                continue

            chat_id = int(filename.replace("user_", "").replace(".json", ""))
            user = load_user(chat_id, BASE_WORDS)

            settings = user.get("notifications")
            if not settings or not settings.get("times"):
                continue


            test_type = settings.get("test_type")
            times = settings.get("times", [])
            sent_today = sent_flags.setdefault(chat_id, set())

            for t in times:
                if t in sent_today:
                    continue

                try:
                    hh, mm = map(int, t.split(":"))
                except:
                    continue

                if now.hour == hh and now.minute == mm:
                    await send_notification(
                        app,
                        chat_id,
                        TEXTS["notify_question"],
                        test_type
                    )
                    sent_today.add(t)
                    save_user(chat_id, user)


        # очищення опівночі
        if now.hour == 0 and now.minute == 0:
            for k in sent_flags:
                sent_flags[k].clear()

        await asyncio.sleep(20)


# ==========================
# POST INIT
# ==========================
async def post_init(app):
    app.bot_data["notification_task"] = asyncio.create_task(
        notification_task(app)
    )

async def post_shutdown(app):
    task = app.bot_data.get("notification_task")
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


# ==========================
# ЗАПУСК БОТА
# ==========================
if __name__ == "__main__":
    TOKEN = "8018987749:AAE_MlaizCQl2HOGFE_VDXydZ0Z7fGoCsBo"

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_inline_answer, pattern="^ans:"))
    app.add_handler(CallbackQueryHandler(handle_notify_answer, pattern="^notify:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.add_handler(
        CallbackQueryHandler(handle_clear_notification, pattern="^clear_notify:")
    )


    print("Бот запущений...")
    app.run_polling()
