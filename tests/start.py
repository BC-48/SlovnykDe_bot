import random
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from words_service import get_words_by_status
from utils import send_with_keyboard
from keyboards import main_menu
from .choice import send_next_choice
from .write import send_next_write
from .pool_builder import build_test_pool
from texts import TEXTS




async def start_test(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    scope="звичайний",
    ttype="обрати",
    test_size=15
):
    user = context.user_data["storage"]
    user_words = user["words"]

    context.user_data["correct_answers"] = 0

    # =========================
    # 🧠 TEST: VERBEN MIT PRÄPOSITION
    # =========================
    if scope == "prepositions":
        # беремо слова за загальною логікою
        pool = build_test_pool(context, scope, test_size)


        # залишаємо тільки з прийменниками
        pool = [
            w for w in pool
            if w.get("präposition")
        ]

        if not pool:
            await send_with_keyboard(
                update,
                context,
                TEXTS["no_prepositions"],
                main_menu
            )

            return

        context.user_data.update({
            "test_words": pool,
            "current_index": 0,
            "test_type": "preposition",
            "test_active": True,
            "test_message_id": None,
            "answered_words": []
        })

        cancel_kb = ReplyKeyboardMarkup(
            [[KeyboardButton(TEXTS["btn_cancel_test"])]],
            resize_keyboard=True
        )

        await send_with_keyboard(
            update,
            context,
            TEXTS["prepositions_test_started"],
            cancel_kb
        )

        await send_next_choice(update, context)
        return

    # =========================
    # 🧠 ТЕСТ АРТИКЛІВ
    # =========================
    if scope == "articles":
        # беремо слова за загальною логікою
        pool = build_test_pool(context, scope, test_size)


        # залишаємо тільки іменники з артиклем
        pool = [
            w for w in pool
            if w.get("частина_мови") == "іменник" and w.get("артикль")
        ]

        if not pool:
            await send_with_keyboard(
                update,
                context,
                TEXTS["no_articles"],
                main_menu
            )
            return


        context.user_data.update({
            "test_words": pool,
            "current_index": 0,
            "test_type": "article",
            "test_active": True,
            "test_message_id": None,
            "answered_words": []
        })

        cancel_kb = ReplyKeyboardMarkup(
            [[KeyboardButton(TEXTS["btn_cancel_test"])]],
            resize_keyboard=True
        )

        await send_with_keyboard(
            update,
            context,
            TEXTS["articles_test_started"],
            cancel_kb
        )


        await send_next_choice(update, context)
        return

    # =========================
    # 🔴 ВАЖКІ СЛОВА
    # =========================
    if scope == "важке":
        hard_words = get_words_by_status(user_words, "важке")
        pool = random.sample(hard_words, min(len(hard_words), test_size))

    # =========================
    # 🎲 ЗВИЧАЙНИЙ ТЕСТ
    # =========================
    else:
        pool = build_test_pool(context, scope, test_size)


    if not pool:
        await send_with_keyboard(update, context, TEXTS["no_words_for_test"], main_menu)
        return


    random.shuffle(pool)

    context.user_data.update({
        "test_words": pool,
        "current_index": 0,
        "test_type": ttype,
        "test_active": True,
        "test_message_id": None,
        "answered_words": []
    })

    cancel_kb = ReplyKeyboardMarkup(
        [[KeyboardButton(TEXTS["btn_cancel_test"])]],
        resize_keyboard=True
    )

    await send_with_keyboard(
        update,
        context,
        TEXTS["test_started"],
        cancel_kb,
        save_as_menu=False
    )


    if ttype in ("обрати",):
        await send_next_choice(update, context)
    else:
        await send_next_write(update, context)
