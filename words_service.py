# words_service.py

MAX_WORDS = 15


# =========================
# 🔹 ОНОВЛЕННЯ СТАТУСУ СЛОВА
# =========================
def update_status(word: dict):
    c = word.get("correct_streak", 0)
    w = word.get("wrong_streak", 0)

    if c == 0 and w == 0:
        word["status"] = "нове"
    elif w >= 3:
        word["status"] = "важке"
    elif c >= 3:
        word["status"] = "вивчене"
    else:
        word["status"] = "вивчається"


# =========================
# 🔹 СЛОВА ЗА СТАТУСОМ (USER-SCOPE)
# =========================
def get_words_by_status(user_words: list, status: str) -> list:
    return [w for w in user_words if w.get("status") == status]


# =========================
# 🔹 ФОРМУВАННЯ ПУЛУ ДЛЯ ТЕСТУ
# =========================
def get_test_words(user_words: list, test_type="звичайний") -> list:
    if test_type == "важкі":
        return [w for w in user_words if w["status"] == "важке"][:MAX_WORDS]

    if test_type == "вивчені":
        return [w for w in user_words if w["status"] == "вивчене"][:MAX_WORDS]

    # звичайний тест — пріоритети
    hard = [w for w in user_words if w["status"] == "важке"]
    learn = [w for w in user_words if w["status"] == "вивчається"]
    new = [w for w in user_words if w["status"] == "нове"]

    result = []
    result += hard
    result += learn
    result += new

    return result[:MAX_WORDS]
