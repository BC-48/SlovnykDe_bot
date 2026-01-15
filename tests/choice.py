import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from words_service import update_status
from .finish import finish_test
from utils import format_word
from texts import TEXTS




async def send_next_choice(update, context):
    user = context.user_data["storage"]
    user_words = user["words"]

    chat = update.effective_chat
    idx = context.user_data["current_index"]
    words = context.user_data["test_words"]

    total = len(words)
    current = idx + 1

    if idx >= len(words):
        await finish_test(update, context)
        return

    word = words[idx]
    test_type = context.user_data.get("test_type")
    msg_id = context.user_data.get("test_message_id")

    # =========================
    # 🧠 PRÄPOSITIONEN
    # =========================
    if test_type == "preposition":
        correct_prep = word.get("präposition")

        preps = list({
            w.get("präposition")
            for w in user_words
            if w.get("präposition")
        })

        options = [correct_prep]
        others = [p for p in preps if p != correct_prep]
        options += random.sample(others, min(3, len(others)))
        random.shuffle(options)

        keyboard = [
            [InlineKeyboardButton(p, callback_data=f"ans:{p}")]
            for p in options
        ]
        markup = InlineKeyboardMarkup(keyboard)

        text = (
            TEXTS["question_counter"].format(current=current, total=total)
            + f"{TEXTS['choose_preposition']}\n"
            + f"<b>{word['німецьке слово']}</b> __"
        )




        if msg_id:
            await context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=msg_id,
                text=text,
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            msg = await chat.send_message(
                text=text,
                reply_markup=markup,
                parse_mode="HTML"
            )
            context.user_data["test_message_id"] = msg.message_id
        return

    # =========================
    # 🧠 АРТИКЛІ
    # =========================
    if test_type == "article":
        keyboard = [
            [InlineKeyboardButton("der", callback_data="ans:der")],
            [InlineKeyboardButton("die", callback_data="ans:die")],
            [InlineKeyboardButton("das", callback_data="ans:das")],
        ]
        markup = InlineKeyboardMarkup(keyboard)

        text = (
            TEXTS["question_counter"].format(current=current, total=total)
            + f"{TEXTS['choose_article']}\n"
            + f"__ {word['німецьке слово']}"
        )




        if msg_id:
            await context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=msg_id,
                text=text,
                reply_markup=markup
            )
        else:
            msg = await chat.send_message(
                text=text,
                reply_markup=markup
            )
            context.user_data["test_message_id"] = msg.message_id
        return

    # =========================
    # 🟦 ЗВИЧАЙНИЙ CHOICE
    # =========================
    pos = word.get("частина_мови")

    options = [format_word(word)]

    others = [
        format_word(w)
        for w in user_words
        if w != word and w.get("частина_мови") == pos
    ]

    # fallback, якщо мало слів тієї ж частини мови
    if len(others) < 3:
        others = [
            format_word(w)
            for w in user_words
            if w != word
        ]

    options += random.sample(others, min(3, len(others)))
    random.shuffle(options)


    keyboard = [
        [InlineKeyboardButton(o, callback_data=f"ans:{o}")]
        for o in options
    ]
    markup = InlineKeyboardMarkup(keyboard)

    text = TEXTS["question_choice"].format(
        current=current,
        total=total,
        ua=word["український переклад"]
    )



    if msg_id:
        await context.bot.edit_message_text(
            chat_id=chat.id,
            message_id=msg_id,
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    else:
        msg = await chat.send_message(
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        context.user_data["test_message_id"] = msg.message_id

async def handle_inline_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context.user_data["storage"]
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("test_active"):
        return

    choice = query.data.replace("ans:", "").strip().lower()

    idx = context.user_data["current_index"]
    word = context.user_data["test_words"][idx]

    # 🧹 прибираємо слово з "нових" ПІСЛЯ відповіді
    new_words = user.get("new_words", [])
    new_words[:] = [
        w for w in new_words
        if not (
            w.get("німецьке слово") == word.get("німецьке слово")
            and w.get("артикль", "") == word.get("артикль", "")
            and w.get("präposition", "") == word.get("präposition", "")
        )
    ]

    test_type = context.user_data.get("test_type")

    # =========================
    # 🧠 АРТИКЛІ
    # =========================
    if test_type == "article":
        correct = choice == word.get("артикль", "").strip().lower()

        if correct:
            word["correct_streak"] += 1
            word["wrong_streak"] = 0
            context.user_data["correct_answers"] += 1
        else:
            word["wrong_streak"] += 1
            word["correct_streak"] = 0

        update_status(word)

        context.user_data.setdefault("answered_words", []).append(word)
        context.user_data["current_index"] += 1

        await query.edit_message_reply_markup(reply_markup=None)
        await query.edit_message_text(
            TEXTS["answer_correct"]
            if correct
            else f"{TEXTS['answer_wrong']}\n{TEXTS['answer_right_is']} {word.get('артикль')} {word['німецьке слово']}"
        )


        await asyncio.sleep(1 if correct else 2)
        await send_next_choice(update, context)
        return

    # =========================
    # 🧠 PRÄPOSITIONEN
    # =========================
    if test_type == "preposition":
        correct = choice == word.get("präposition", "").strip().lower()

        if correct:
            word["correct_streak"] += 1
            word["wrong_streak"] = 0
            context.user_data["correct_answers"] += 1
        else:
            word["wrong_streak"] += 1
            word["correct_streak"] = 0

        update_status(word)

        context.user_data.setdefault("answered_words", []).append(word)
        context.user_data["current_index"] += 1

        await query.edit_message_reply_markup(reply_markup=None)
        await query.edit_message_text(
            TEXTS["answer_correct"]
            if correct
            else f"{TEXTS['answer_wrong']}\n{TEXTS['answer_right_is']} {word['німецьке слово']} {word.get('präposition')}"
        )


        await asyncio.sleep(1 if correct else 2)
        await send_next_choice(update, context)
        return

    # =========================
    # 🟦 ЗВИЧАЙНИЙ CHOICE
    # =========================
    correct = choice == format_word(word).lower()

    if correct:
        word["correct_streak"] += 1
        word["wrong_streak"] = 0
        context.user_data["correct_answers"] += 1
    else:
        word["wrong_streak"] += 1
        word["correct_streak"] = 0

    update_status(word)

    context.user_data.setdefault("answered_words", []).append(word)
    context.user_data["current_index"] += 1

    await query.edit_message_reply_markup(reply_markup=None)
    await query.edit_message_text(
        TEXTS["answer_correct"]
        if correct
        else f"{TEXTS['answer_wrong']}\n{TEXTS['answer_right_is']} {format_word(word)}"
    )


    await asyncio.sleep(1 if correct else 2)
    await send_next_choice(update, context)


