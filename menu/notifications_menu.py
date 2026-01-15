from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from utils import send_with_keyboard
from keyboards import main_menu
from storage import save_user
from tests import start_test
from texts import TEXTS



async def handle_notifications_menu(update, context):
    user = context.user_data["storage"]
    text = update.message.text

    if text in (TEXTS["setup_fast"], TEXTS["setup_hard"]):
        test_key = "швидкий" if text == TEXTS["setup_fast"] else "важких"

        context.user_data["notification_setup"] = {
            "test_type": test_key,
            "step": "ask_count",
            "times": []
        }

        settings = user.get("notifications")

        msg_lines = [TEXTS["current_notification_settings"].format(name=text)]

        kb_inline = []

        if settings and settings.get("test_type") == test_key and settings.get("times"):
            msg_lines.append(
                TEXTS["times_per_day"].format(count=len(settings["times"]))
            )
            msg_lines.append(
                TEXTS["times_list"].format(times=", ".join(settings["times"]))
            )

            kb_inline.append([
                InlineKeyboardButton(
                    TEXTS["btn_clear_notifications"],
                    callback_data=f"clear_notify:{test_key}"
                )
            ])
        else:
            msg_lines.append(TEXTS["notifications_not_set"])

        back_kb = ReplyKeyboardMarkup(
            [[KeyboardButton(TEXTS["btn_back"])]],
            resize_keyboard=True
        )

        sent = await update.message.reply_text(
            "\n".join(msg_lines),
            reply_markup=InlineKeyboardMarkup(kb_inline) if kb_inline else None
        )

        context.user_data["notification_settings_msg_id"] = sent.message_id
        context.user_data["notification_user_msg_id"] = update.message.message_id



        sent = await update.message.reply_text(
            TEXTS["ask_times_per_day"],
            reply_markup=back_kb
        )

        context.user_data["notification_ask_msg_id"] = sent.message_id

        return



    kb = ReplyKeyboardMarkup(
        [
            [KeyboardButton(TEXTS["setup_fast"]),
            KeyboardButton(TEXTS["setup_hard"])],
            [KeyboardButton(TEXTS["btn_back"])]
        ],
        resize_keyboard=True
    )

    await send_with_keyboard(
        update,
        context,
        TEXTS["notifications_menu"],
        kb
    )



async def handle_notification_input(update, context):
    user = context.user_data["storage"]
    text = update.message.text.strip()

    # 🧹 видаляємо повідомлення "Скільки разів на день..."
    ask_id = context.user_data.pop("notification_ask_msg_id", None)
    if ask_id:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=ask_id
            )
        except:
            pass

    if text == TEXTS["btn_back"]:
    # 🧹 видаляємо повідомлення користувача ("Швидкий раунд")
        user_msg_id = context.user_data.pop("notification_user_msg_id", None)
        if user_msg_id:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=user_msg_id
                )
            except:
                pass

        # 🧹 видаляємо повідомлення з поточними налаштуваннями
        settings_msg_id = context.user_data.pop("notification_settings_msg_id", None)
        if settings_msg_id:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=settings_msg_id
                )
            except:
                pass

        # 🧹 видаляємо питання "Скільки разів на день..."
        ask_id = context.user_data.pop("notification_ask_msg_id", None)
        if ask_id:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=ask_id
                )
            except:
                pass

        context.user_data.pop("notification_setup", None)
        await send_with_keyboard(update, context, TEXTS["main_menu"], main_menu)
        return


    setup = context.user_data.get("notification_setup")
    if not setup:
        return

    back_kb = ReplyKeyboardMarkup(
        [[KeyboardButton(TEXTS["btn_back"])]],
        resize_keyboard=True
    )



    if setup["step"] == "ask_count":
        try:
            count = int(text)
            if count <= 0:
                raise ValueError

            setup["count"] = count
            setup["step"] = "ask_times"
            setup["current_index"] = 1

            await send_with_keyboard(
                update,
                context,
                TEXTS["enter_time"].format(n=1, total=count),
                back_kb
            )

        except:
            await send_with_keyboard(update, context, TEXTS["enter_number_gt_zero"], back_kb)
        return


    if setup["step"] == "ask_times":
        try:
            hh, mm = map(int, text.split(":"))
            if not (0 <= hh < 24 and 0 <= mm < 60):
                raise ValueError

            setup["times"].append(text)

            if len(setup["times"]) < setup["count"]:
                setup["current_index"] += 1
                await send_with_keyboard(
                    update,
                    context,
                    TEXTS["enter_time"].format(
                        n=setup["current_index"],
                        total=setup["count"]
                    ),
                    back_kb
                )

            else:
                user["notifications"] = {
                    "test_type": setup["test_type"],
                    "times": setup["times"]
                }
                save_user(update.effective_chat.id, user)

                msg_id = context.user_data.pop("notification_settings_msg_id", None)
                if msg_id:
                    try:
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=msg_id
                        )
                    except:
                        pass

                # 🧹 видаляємо повідомлення користувача "Швидкий раунд"
                user_msg_id = context.user_data.pop("notification_user_msg_id", None)
                if user_msg_id:
                    try:
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=user_msg_id
                        )
                    except:
                        pass

                # 🧹 видаляємо повідомлення з поточними налаштуваннями
                settings_msg_id = context.user_data.pop("notification_settings_msg_id", None)
                if settings_msg_id:
                    try:
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=settings_msg_id
                        )
                    except:
                        pass

                context.user_data.pop("notification_setup", None)
                await send_with_keyboard(update, context, TEXTS["notifications_saved"], main_menu)


        except:
            await send_with_keyboard(update, context, TEXTS["time_format"], back_kb)


async def handle_clear_notification(update, context):
    query = update.callback_query
    await query.answer()

    _, test_type = query.data.split(":")

    user = context.user_data["storage"]

    if user.get("notifications", {}).get("test_type") == test_type:
        user["notifications"] = {
            "test_type": None,
            "times": []
        }
        save_user(update.effective_chat.id, user)

    await query.edit_message_text(TEXTS["notifications_cleared"])
async def handle_notify_answer(update, context):
    query = update.callback_query
    await query.answer()

    _, test_type, answer = query.data.split(":")

    if answer == "yes":
        await start_test(
            update,
            context,
            scope="звичайний" if test_type == "швидкий" else "важке",
            ttype="обрати",
            test_size=5
        )

    try:
        await query.message.delete()
    except:
        pass
