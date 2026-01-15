import json
import os
from copy import deepcopy
from texts import TEXTS


DATA_DIR = "data"
WORDS_FILE = "words.json"

os.makedirs(DATA_DIR, exist_ok=True)


# =========================
# 🔹 БАЗОВИЙ ШАБЛОН КОРИСТУВАЧА
# =========================
def _default_user(words_source: list):
    words = []

    for w in deepcopy(words_source):
        word = dict(w)

        # ініціалізація статусу і streak-ів
        word.setdefault("status", "нове")
        word.setdefault("correct_streak", 0)
        word.setdefault("wrong_streak", 0)

        words.append(word)

    return {
        "words": words,              # єдине джерело правди
        "new_words": [],             # ТІЛЬКИ для видачі нових
        "can_get_new_words": True,
        "notifications": {
            "test_type": None,
            "times": []
        }
    }


# =========================
# 🔹 ШЛЯХ ДО ФАЙЛУ КОРИСТУВАЧА
# =========================
def _user_path(chat_id: int) -> str:
    return os.path.join(DATA_DIR, f"user_{chat_id}.json")


# =========================
# 🔹 ЗАВАНТАЖЕННЯ БАЗОВИХ СЛІВ
# =========================
def load_base_words() -> list:
    if not os.path.exists(WORDS_FILE):
        raise FileNotFoundError("words.json not found")

    with open(WORDS_FILE, encoding="utf-8") as f:
        return json.load(f)


# =========================
# 🔹 ЗАВАНТАЖИТИ КОРИСТУВАЧА
# =========================
def load_user(chat_id: int, base_words: list) -> dict:
    path = _user_path(chat_id)

    if not os.path.exists(path):
        user = _default_user(base_words)
        save_user(chat_id, user)
        return user

    with open(path, encoding="utf-8") as f:
        user = json.load(f)

    # 🔧 захист для старих користувачів
    for w in user.get("words", []):
        w.setdefault("status", "нове")
        w.setdefault("correct_streak", 0)
        w.setdefault("wrong_streak", 0)

    user.setdefault("new_words", [])
    user.setdefault("can_get_new_words", True)
    user.setdefault("notifications", {"test_type": None, "times": []})

    return user


# =========================
# 🔹 ЗБЕРЕГТИ КОРИСТУВАЧА
# =========================
def save_user(chat_id: int, user_data: dict):
    path = _user_path(chat_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)
