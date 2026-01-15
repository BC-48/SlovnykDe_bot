from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from utils import send_with_keyboard
from keyboards import custom_words_menu, custom_format_menu
from tests import start_test
from texts import TEXTS



async def handle_trainer_menu(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE):
    user = context.user_data["storage"]
    user_words = user["words"]

    text = update.message.text.strip()

    # =========================
    # ⬅️ Назад
    # =========================
    if text == TEXTS["btn_back"]:
        context.user_data.pop("custom_test", None)
        from keyboards import main_menu
        await send_with_keyboard(update, context, TEXTS["main_menu"], main_menu)
        return

    # 🧠 АРТИКЛІ
    if text == TEXTS["btn_articles"]:
        await start_test(update, context, scope="articles", ttype="article", test_size=10)
        return

    # 🧠 PRÄPOSITIONEN
    if text == TEXTS["btn_prepositions"]:
        await start_test(update, context, scope="prepositions", ttype="preposition", test_size=10)
        return

    # 🧠 ВХІД У ТРЕНАЖЕР (ЗАГАЛЬНИЙ)
    if text == TEXTS["btn_trainer"]:
        kb = ReplyKeyboardMarkup(
            [
                [KeyboardButton(TEXTS["btn_choice"]), KeyboardButton(TEXTS["btn_articles"])],
                [KeyboardButton(TEXTS["btn_write"]), KeyboardButton(TEXTS["btn_prepositions"])],
                [KeyboardButton(TEXTS["btn_custom"])],
                [KeyboardButton(TEXTS["btn_back"])]
            ],
            resize_keyboard=True
        )

        await send_with_keyboard(update, context, TEXTS["choose_test_type"], kb)
        return


    # =========================
    # 🚀 ШВИДКІ РЕЖИМИ
    # =========================
    # швидкі режими працюють ТІЛЬКИ якщо НЕ custom
    if not context.user_data.get("custom_test"):
        if text == TEXTS["btn_choice"]:
            await start_test(update, context, "звичайний", "обрати", 15)
            return


    if not context.user_data.get("custom_test"):
        if text == TEXTS["btn_write"]:
            await start_test(update, context, "звичайний", "написати", 15)
            return
        
    
    #if text == "⚡️ Швидкий раунд":
    #    await start_test(update, context, "звичайний", "обрати", 5)
    #    return

    #if text == "🔥 Вогонь важких":
    #    await start_test(update, context, "важке", "обрати", 5)
    #    return

    # =========================
    # 🛠 Власний режим — старт
    # =========================
    if text == TEXTS["btn_custom"]:
        context.user_data["custom_test"] = {
            "step": "scope"
        }
        await send_with_keyboard(
            update,
            context,
            TEXTS["choose_word_category"],
            custom_words_menu
        )
        return



    custom = context.user_data.get("custom_test")
    if not custom:
        return


    # =========================
    # 🧩 КАТЕГОРІЯ
    # =========================
    if custom["step"] == "scope":
        if text == TEXTS["custom_all"]:
            custom["scope"] = "звичайний"
        elif text == TEXTS["custom_new"]:
            custom["scope"] = "нове"
        elif text == TEXTS["custom_learning"]:
            custom["scope"] = "вивчається"
        elif text == TEXTS["custom_hard"]:
            custom["scope"] = "важке"
        elif text == TEXTS["custom_learned"]:
            custom["scope"] = "вивчене"
        else:
            return

        custom["step"] = "format"
        await send_with_keyboard(
            update,
            context,
            TEXTS["choose_test_format"],
            custom_format_menu
        )
        return



    # =========================
    # ✍️ ФОРМАТ
    # =========================
    if custom["step"] == "format":
        if text == TEXTS["btn_choice"]:
            custom["ttype"] = "обрати"
        elif text == TEXTS["btn_write"]:
            custom["ttype"] = "написати"
        else:
            return

        back_kb = ReplyKeyboardMarkup(
            [[KeyboardButton(TEXTS["btn_back"])]],
            resize_keyboard=True
        )

        custom["step"] = "count"
        await send_with_keyboard(
            update,
            context,
            TEXTS["enter_question_count"],
            back_kb
        )
        return



    # =========================
    # 🔢 КІЛЬКІСТЬ (І ТІЛЬКИ ТУТ СТАРТ)
    # =========================
    if custom["step"] == "count":
        back_kb = ReplyKeyboardMarkup(
            [[KeyboardButton(TEXTS["btn_back"])]],
            resize_keyboard=True
        )

        try:
            count = int(text)
            if count <= 0 or count > 50:
                raise ValueError

            await start_test(
                update,
                context,
                scope=custom["scope"],
                ttype=custom["ttype"],
                test_size=count
            )

            context.user_data.pop("custom_test", None)
            return

        except:
            await send_with_keyboard(
                update,
                context,
                TEXTS["enter_number_1_50"],
                back_kb
            )
            return


