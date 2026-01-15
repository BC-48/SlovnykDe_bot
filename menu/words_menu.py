import random
from collections import defaultdict
from telegram.ext import ContextTypes
from utils import send_with_keyboard
from keyboards import main_menu
from telegram.ext import ContextTypes
from utils import send_with_keyboard
from keyboards import main_menu, status_menu
from words_service import get_words_by_status
from telegram import ReplyKeyboardMarkup, KeyboardButton
from keyboards import get_words_menu, level_menu
from storage import save_user
from texts import TEXTS





MAX_NEW_WORDS = 15


async def get_new_words(update, context, level=None, only_verben=False):
    user = context.user_data["storage"]
    user_words = user["words"]

    # ❌ не дозволяємо брати нові слова, поки не пройдено тест
    if not user.get("can_get_new_words", True):
        await send_with_keyboard(update, context, TEXTS["need_finish_test"], main_menu)
        return

    user.setdefault("new_words", [])

    # 🆕 беремо тільки нові слова з ОСНОВНОГО словника
    unknown_words = [
        w for w in user_words
        if w.get("status") == "нове"
        and w not in user["new_words"]
        and (level is None or w.get("рівень") == level)
        and (
            not only_verben
            or w.get("частина_мови") == "verb_mit_praeposition"
        )
    ]

    if not unknown_words:
        await send_with_keyboard(update, context, TEXTS["no_new_words"], main_menu)
        return

    # групування по темах
    theme_dict = defaultdict(list)
    for w in unknown_words:
        theme_dict[w.get("тема", "Без теми")].append(w)

    main_theme = random.choice(list(theme_dict.keys()))
    main_theme_words = theme_dict[main_theme]

    count_main = min(int(MAX_NEW_WORDS * 0.7), len(main_theme_words))
    selected_words = random.sample(main_theme_words, count_main)

    # добір з інших тем
    other_words = [
        w for theme, lst in theme_dict.items()
        if theme != main_theme
        for w in lst
    ]

    remaining = MAX_NEW_WORDS - len(selected_words)
    if remaining > 0 and other_words:
        selected_words += random.sample(other_words, min(remaining, len(other_words)))

    # добір, якщо все ще не вистачає
    rest = [w for w in unknown_words if w not in selected_words]
    while len(selected_words) < MAX_NEW_WORDS and rest:
        selected_words.append(rest.pop())

    # 🧠 ФІКС: статус + додавання
    for w in selected_words:
        w["status"] = "нове"
        if w not in user["new_words"]:
            user["new_words"].append(w)

    user["can_get_new_words"] = False

    from utils import format_word

    msg = "\n".join(
        TEXTS["new_word_line"].format(
            word=(
                f'<a href="https://t.me/SlovnykDe_bot?start=ex_{w["id"]}">'
                f'{format_word(w)}'
                f'</a>'
                f'{", " + w["множина"] if w.get("множина") else ""}'
                f' — {w["український переклад"]}'
            )
        )
        for w in selected_words
    )

    save_user(update.effective_chat.id, user)
    sent = await update.message.reply_text(
        msg,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

    import asyncio

    async def delayed_delete():
        await asyncio.sleep(0.1)
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except:
            pass

    asyncio.create_task(delayed_delete())

    context.user_data["words_msg_id"] = sent.message_id
    context.user_data["words_list_text"] = msg



async def handle_words_menu(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE):
    user = context.user_data["storage"]
    user_words = user["words"]
    text = update.message.text
    from keyboards import get_words_menu
    if text == TEXTS["btn_back"]:
        context.user_data.pop("words_menu_active", None)
        await send_with_keyboard(update, context, TEXTS["main_menu"], main_menu)
        return

    if text == TEXTS["btn_get_words"]:
        context.user_data["words_menu_active"] = True

        await send_with_keyboard(
            update,
            context,
            TEXTS["how_get_words"],
            get_words_menu
        )
        return



    if text == TEXTS["random_words"]:
        await get_new_words(update, context)
        return

    if text == TEXTS["by_level"]:
        await send_with_keyboard(
            update,
            context,
            TEXTS["choose_level"],
            level_menu
        )
        return


    if text in (
        TEXTS["level_a1"],
        TEXTS["level_a2"],
        TEXTS["level_b1"],
        TEXTS["level_b2"],
    ):
        await get_new_words(update, context, level=text)
        return

    if text == TEXTS["verbs_with_prep"]:
        await get_new_words(update, context, only_verben=True)
        return



    if text == TEXTS["btn_my_words"]:
        context.user_data["words_menu_active"] = True

        counts = {
            TEXTS["custom_new"]: len(user.get("new_words", [])),
            TEXTS["custom_learning"]: len(get_words_by_status(user_words, "вивчається")),
            TEXTS["custom_hard"]: len(get_words_by_status(user_words, "важке")),
            TEXTS["custom_learned"]: len(get_words_by_status(user_words, "вивчене")),
        }




        keyboard = [
            [KeyboardButton(f"{TEXTS['custom_new']} ({counts[TEXTS['custom_new']]})")],
            [KeyboardButton(f"{TEXTS['custom_learning']} ({counts[TEXTS['custom_learning']]})")],
            [KeyboardButton(f"{TEXTS['custom_hard']} ({counts[TEXTS['custom_hard']]})")],
            [KeyboardButton(f"{TEXTS['custom_learned']} ({counts[TEXTS['custom_learned']]})")],
            [KeyboardButton(TEXTS["btn_back"])],
        ]


        kb = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await send_with_keyboard(update, context, TEXTS["choose_category"], kb)
        return


    if text.startswith(TEXTS["custom_new"]):
        words = user.get("new_words", [])

    elif text.startswith(TEXTS["custom_learning"]):
        words = get_words_by_status(user_words, "вивчається")

    elif text.startswith(TEXTS["custom_hard"]):
        words = get_words_by_status(user_words, "важке")

    elif text.startswith(TEXTS["custom_learned"]):
        words = get_words_by_status(user_words, "вивчене")

    else:
        return



    from utils import format_word

    msg = "\n".join(
        f'• <a href="https://t.me/SlovnykDe_bot?start=ex_{w["id"]}">'
        f'<b>{format_word(w)}</b></a>'
        f'{", " + w["множина"] if w.get("множина") else ""}'
        f' — {w["український переклад"]}'
        for w in words
    ) or TEXTS["no_words"]

    sent = await send_with_keyboard(
        update,
        context,
        msg,
        keyboard=None,
        save_as_menu=False
    )

    # 🔧 примусовий перерендер (але без падіння)
    try:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=sent.message_id,
            text=msg,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except:
        pass



    context.user_data["words_msg_id"] = sent.message_id
    context.user_data["words_list_text"] = msg


