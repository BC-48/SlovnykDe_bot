from telegram import ReplyKeyboardMarkup, KeyboardButton
from texts import TEXTS


# ==========================
# Головне меню
# ==========================
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(TEXTS["btn_get_words"])],
        [KeyboardButton(TEXTS["btn_trainer"])],
        [KeyboardButton(TEXTS["btn_my_words"])],
        [KeyboardButton(TEXTS["btn_settings"])]
    ],
    resize_keyboard=True
)

# ==========================
# Меню тесту
# ==========================
test_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(TEXTS["btn_choice"])],
        [KeyboardButton(TEXTS["btn_write"])],
        [KeyboardButton(TEXTS["btn_back"])]
    ],
    resize_keyboard=True
)

# ==========================
# Меню статусів слів
# ==========================
status_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(TEXTS["custom_new"])],
        [KeyboardButton(TEXTS["custom_learning"])],
        [KeyboardButton(TEXTS["custom_hard"])],
        [KeyboardButton(TEXTS["custom_learned"])],
        [KeyboardButton(TEXTS["btn_back"])]
    ],
    resize_keyboard=True
)

# ==========================
# Меню отримання слів
# ==========================
get_words_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(TEXTS["random_words"])],
        [KeyboardButton(TEXTS["by_level"])],
        [KeyboardButton(TEXTS["verbs_with_prep"])],
        [KeyboardButton(TEXTS["btn_back"])]
    ],
    resize_keyboard=True
)

# ==========================
# Меню вибору рівня
# ==========================
level_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(TEXTS["level_a1"]), KeyboardButton(TEXTS["level_a2"])],
        [KeyboardButton("B1"), KeyboardButton("B2")],
        [KeyboardButton(TEXTS["btn_back"])]
    ],
    resize_keyboard=True
)

# ==========================
# Власний режим — вибір типу слів
# ==========================
custom_words_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(TEXTS["custom_all"])],
        [KeyboardButton(TEXTS["custom_new"])],
        [KeyboardButton(TEXTS["custom_learning"])],
        [KeyboardButton(TEXTS["custom_hard"])],
        [KeyboardButton(TEXTS["custom_learned"])],
        [KeyboardButton(TEXTS["btn_back"])]
    ],
    resize_keyboard=True
)

# ==========================
# Власний режим — формат тесту
# ==========================
custom_format_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(TEXTS["btn_choice"])],
        [KeyboardButton(TEXTS["btn_write"])],
        [KeyboardButton(TEXTS["btn_back"])]
    ],
    resize_keyboard=True
)
