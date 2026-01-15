import random
from words_service import get_words_by_status
from texts import TEXTS


# порядок важливості для звичайного тесту
PRIORITY = ["важке", "вивчається", "вивчене"]


def _filter_by_scope(scope, pool):
    if scope == "articles":
        return [w for w in pool if w.get("артикль")]

    if scope == "prepositions":
        return [w for w in pool if w.get("präposition")]

    # для статусів фільтрація вже зроблена ДО виклику
    if scope in ("важке", "вивчається", "вивчене"):
        return pool

    if scope == "нове":
        return pool

    return pool



def build_test_pool(context, scope, test_size):
    user = context.user_data["storage"]
    user_words = user["words"]

    result = []
    used = set()

    # =========================
    # 🎲 ЗВИЧАЙНИЙ ТЕСТ (усі слова)
    # =========================
    if scope == "звичайний":
        new_words = user.get("new_words", [])

        # 1️⃣ статусні слова за пріоритетом
        for status in PRIORITY:
            candidates = get_words_by_status(user_words, status)
            for w in candidates:
                if id(w) in used:
                    continue
                result.append(w)
                used.add(id(w))
                if len(result) >= test_size:
                    return result

        # 2️⃣ добір нових, якщо не вистачає
        for w in new_words:
            if id(w) in used:
                continue
            result.append(w)
            used.add(id(w))
            if len(result) >= test_size:
                return result

        return result

    # =========================
    # 🧠 ARTICLES / PRÄPOSITIONEN
    # =========================
    if scope in ("articles", "prepositions"):
        new_words = user.get("new_words", [])
        new_words = _filter_by_scope(scope, new_words)

        for w in new_words:
            result.append(w)
            if len(result) >= test_size:
                return result

        for status in PRIORITY:
            candidates = get_words_by_status(user_words, status)
            candidates = _filter_by_scope(scope, candidates)

            for w in candidates:
                if id(w) in used:
                    continue
                result.append(w)
                used.add(id(w))
                if len(result) >= test_size:
                    return result

        return result

    # =========================
    # 🛠 CUSTOM-КАТЕГОРІЇ
    # =========================
    if scope == "нове":
        pool = user.get("new_words", [])
    else:
        pool = get_words_by_status(user_words, scope)

    pool = _filter_by_scope(scope, pool)
    random.shuffle(pool)

    return pool[:test_size]
