#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Антиплагиат + проверка выводов ЛР1 через локальную модель в формате GGUF.

Работает через:
- llama-cpp-python
- huggingface_hub

По умолчанию используется:
- Qwen/Qwen2.5-3B-Instruct-GGUF
- qwen2.5-3b-instruct-q4_k_m.gguf

Запуск:
    python anti_plagiarism_llama.py lab_num1.json

Модель можно поменять переменными окружения:
    LLAMA_MODEL_REPO
    LLAMA_MODEL_FILENAME
"""

import sys
import os
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from huggingface_hub import hf_hub_download
from llama_cpp import Llama


# Чтобы русский текст нормально выводился в консоль
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


# Настройки модели

# Модель по умолчанию: Qwen2.5-3B-Instruct GGUF
MODEL_REPO_ID = os.getenv(
    "LLAMA_MODEL_REPO",
    "Qwen/Qwen2.5-3B-Instruct-GGUF"
)

MODEL_FILENAME = os.getenv(
    "LLAMA_MODEL_FILENAME",
    "qwen2.5-3b-instruct-q4_k_m.gguf"
)

MODEL_LOCAL_DIR = os.getenv("LLAMA_MODEL_DIR", "models")

# 0 = CPU
# 99 или -1 = по максимуму на GPU, если llama-cpp-python собран с GPU
N_GPU_LAYERS = int(os.getenv("LLAMA_N_GPU_LAYERS", "-1"))

# Контекст модели
N_CTX = int(os.getenv("LLAMA_N_CTX", "2048"))

# Пороги для плагиата.
# Для небольших/генеративных моделей пороги часто нужно подбирать ниже,
# чем для E5. Начните с 0.70-0.80 для семантики.
SEM_THRESHOLD = float(os.getenv("SEM_THRESHOLD", "0.75"))
LEX_THRESHOLD = float(os.getenv("LEX_THRESHOLD", "0.45"))

# Если SCREEN_THRESHOLD = 0.0, то проверка критериев выполняется для всех
# непустых текстов. Для небольших моделей скрининг может быть не очень
# показательным, поэтому по умолчанию лучше держать 0.0.
SCREEN_THRESHOLD = float(os.getenv("SCREEN_THRESHOLD", "0.0"))

# Префикс для эмбеддингов.
# Для генеративных моделей можно оставить пустым.
# Для специализированных эмбеддинг-моделей может быть нужен префикс,
# например "passage:" или "search_document:".
EMBED_PREFIX = os.getenv("EMBED_PREFIX", "")

# Если хотите считать слово "вес" признаком массы, запустите с:
# ALLOW_WEIGHT_AS_MASS=1
ALLOW_WEIGHT_AS_MASS = os.getenv("ALLOW_WEIGHT_AS_MASS", "0") == "1"


# Чтение входного JSON

def die(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


if len(sys.argv) < 2 or not sys.argv[1].strip():
    die(
        "Ошибка: не указано имя JSON-файла.\n"
        "Использование: python anti_plagiarism_llama.py <json_name>"
    )

json_name = sys.argv[1]

try:
    with open(json_name, "r", encoding="utf-8") as file:
        students_data = json.load(file)
except FileNotFoundError:
    die(f"Ошибка: файл '{json_name}' не найден.")
except json.JSONDecodeError as e:
    die(f"Ошибка: не удалось разобрать JSON в '{json_name}': {e}")

if not isinstance(students_data, dict) or not students_data:
    die("Ошибка: JSON должен быть непустым объектом {имя: текст}.")

# Убираем лишние пробелы в именах и текстах
students_data = {
    str(name).strip(): ("" if text is None else str(text).strip())
    for name, text in students_data.items()
}

names = list(students_data.keys())
clean_texts = list(students_data.values())


#  Таблица материалов

MATERIALS = {
    "Алюминий": (2700, 2700),
    "Бронза": (8700, 8900),
    "Железо": (7870, 7870),
    "Золото": (19300, 19300),
    "Латунь": (8400, 8700),
    "Сталь": (7500, 7900),
    "Медь": (8930, 8930),
    "Титан": (4500, 4500),
}

NEGATIONS = (
    "не ",
    "нет ",
    "отсутств",
    "не измер",
    "не определ",
    "не найд",
    "не получ",
)


# Вспомогательные функции

def mentions_without_negation(
    text: str,
    keywords: list[str],
    window: int = 40
) -> bool:
    """
    Проверяет, встречаются ли ключевые слова без отрицания рядом.
    """
    text_low = text.lower()

    for kw in keywords:
        kw = kw.strip().lower()
        if not kw:
            continue

        # Границы слова для кириллицы/латиницы/цифр.
        # Для ключей вида "m=" граница справа не обязательна.
        pattern = rf"(?<![а-яё0-9]){re.escape(kw)}"
        if kw[-1].isalnum():
            pattern += r"(?![а-яё0-9])"

        for m in re.finditer(pattern, text_low):
            start = max(0, m.start() - window)
            end = min(len(text_low), m.end() + 15)
            frag = text_low[start:end]

            if not any(neg in frag for neg in NEGATIONS):
                return True

    return False


def extract_density(text: str):
    """
    Ищет значение плотности вида:
        7883 кг/м^3
        (7883,0 +- 30) кг/м^3
        плотность составила 7883
        ρ = 7883
    """
    patterns = [
        r"плотност[а-яё]*[^0-9]{0,35}(\d{3,5}(?:[.,]\d+)?)",
        r"[ρp]\s*[=≈]\s*(\d{3,5}(?:[.,]\d+)?)",
        r"(\d{3,5}(?:[.,]\d+)?)\s*(?:[+\-±]+\s*\d+(?:[.,]\d+)?)?\s*\)?\s*кг\s*/\s*м",
    ]

    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                value = float(m.group(1).replace(",", "."))
                return int(round(value))
            except Exception:
                continue

    return None


def identify_material(density):
    if density is None:
        return None

    for material, (low, high) in MATERIALS.items():
        if low <= density <= high:
            return material

    return None


def extract_rel_errors(text: str) -> dict:
    """
    Пытается найти относительные погрешности массы, диаметра и высоты.
    Ищет проценты рядом со словами: масса, диаметр, высота.
    """
    text_low = text.lower()

    result = {
        "mass": None,
        "diameter": None,
        "height": None,
    }

    keys = {
        "mass": ["масс"],
        "diameter": ["диаметр", "диам"],
        "height": ["высот"],
    }

    for quantity, stems in keys.items():
        for stem in stems:
            pattern = rf"(?<![а-яё0-9]){re.escape(stem)}[а-яё]*"

            for m in re.finditer(pattern, text_low):
                frag = text_low[m.start(): m.start() + 180]

                # Вариант 1: рядом есть проценты
                pm = re.search(r"(\d+(?:[.,]\d+)?)\s*%", frag)
                if pm:
                    try:
                        result[quantity] = float(pm.group(1).replace(",", ".")) / 100.0
                        break
                    except Exception:
                        pass

                # Вариант 2: рядом есть число и слово "погрешность"
                dm = re.search(r"(\d+(?:[.,]\d+)?)", frag)
                if dm and any(marker in frag for marker in ("погреш", "δ", "Δ")):
                    try:
                        val = float(dm.group(1).replace(",", "."))
                        if val > 1:
                            val /= 100.0
                        result[quantity] = val
                        break
                    except Exception:
                        pass

            if result[quantity] is not None:
                break

    return result


def dominant_error_source(rel_errors: dict):
    """
    Оценивает главный вклад по формуле косвенных погрешностей.
    Для плотности цилиндра:
        ρ = 4m / (π d^2 h)

    Поэтому вклад диаметра считается как (2 * ε_d)^2.
    """
    m = rel_errors.get("mass")
    d = rel_errors.get("diameter")
    h = rel_errors.get("height")

    if m is None or d is None or h is None:
        return None

    contributions = {
        "масса": m ** 2,
        "диаметр": (2 * d) ** 2,
        "высота": h ** 2,
    }

    return max(contributions, key=contributions.get)


def verbal_error_conclusion(text: str):
    """
    Ищет словесное указание главного вклада:
    "главный вклад даёт погрешность диаметра" и т.п.
    """
    text_low = text.lower()

    mapping = [
        ("масс", "масса"),
        ("диаметр", "диаметр"),
        ("высот", "высота"),
    ]

    for stem, full_name in mapping:
        pattern_direct = rf"{stem}[а-яё]*.{{0,120}}(вклад|погрешност|основн|главн)"
        pattern_reverse = rf"(вклад|погрешност|основн|главн).{{0,80}}{stem}[а-яё]*"

        if re.search(pattern_direct, text_low, re.DOTALL):
            return full_name

        if re.search(pattern_reverse, text_low, re.DOTALL):
            return full_name

    return None


def check_work(name: str, text: str, screen_score: float) -> dict:
    """
    Проверка критериев ЛР1.
    """
    mass_words = [
        "масса",
        "массу",
        "массы",
        "массой",
        "m=",
        "m =",
    ]

    if ALLOW_WEIGHT_AS_MASS:
        mass_words += [
            "вес",
            "веса",
            "весом",
        ]

    has_mass = mentions_without_negation(text, mass_words)

    has_diam = mentions_without_negation(
        text,
        [
            "диаметр",
            "диаметра",
            "диаметре",
            "диаметром",
            "d=",
            "d =",
        ],
    )

    has_height = mentions_without_negation(
        text,
        [
            "высота",
            "высоту",
            "высоты",
            "высоте",
            "высотой",
            "h=",
            "h =",
        ],
    )

    density_val = extract_density(text)

    crit1 = (
        has_mass
        and has_diam
        and has_height
        and density_val is not None
    )

    material = identify_material(density_val)
    crit2 = material is not None

    rel = extract_rel_errors(text)
    dominant = dominant_error_source(rel) or verbal_error_conclusion(text)
    crit3 = dominant is not None

    return {
        "Студент": name,
        "К1: измерения+плотность": "✔" if crit1 else "✘",
        "Плотность (кг/м³)": density_val if density_val is not None else "—",
        "К2: материал": material if material else "✘",
        "К3: главный вклад": dominant if dominant else "✘",
        "Llama-скрин (max sim)": f"{screen_score:.3f}",
        "Зачёт": "ДА" if (crit1 and crit2 and crit3) else "НЕТ",
    }


def empty_row(name: str, score: float) -> dict:
    return {
        "Студент": name,
        "К1: измерения+плотность": "✘",
        "Плотность (кг/м³)": "—",
        "К2: материал": "✘",
        "К3: главный вклад": "✘",
        "Llama-скрин (max sim)": f"{score:.3f}",
        "Зачёт": "НЕТ",
    }


# Загрузка модели через Hugging Face

def get_model_path() -> str:
    local_dir = Path(MODEL_LOCAL_DIR)
    local_dir.mkdir(parents=True, exist_ok=True)

    local_path = local_dir / MODEL_FILENAME
    if local_path.exists():
        return str(local_path)

    print(
        f"Скачиваю модель: {MODEL_REPO_ID}\n"
        f"Файл: {MODEL_FILENAME}\n"
        f"Каталог: {local_dir.resolve()}",
        file=sys.stderr,
    )

    token = os.getenv("HF_TOKEN")

    path = hf_hub_download(
        repo_id=MODEL_REPO_ID,
        filename=MODEL_FILENAME,
        local_dir=str(local_dir),
        token=token if token else None,
    )

    return path


def load_llm() -> Llama:
    model_path = get_model_path()

    print("Загружаю модель через llama.cpp...", file=sys.stderr)

    llm = Llama(
        model_path=model_path,
        embedding=True,
        n_ctx=N_CTX,
        n_gpu_layers=N_GPU_LAYERS,
        verbose=False,
    )

    return llm


llm = load_llm()


# Эмбеддинги через llama.cpp

def truncate_text(text: str) -> str:
    """
    Грубое ограничение по длине, чтобы не выйти за контекст.
    Для лабораторных выводов обычно хватает с запасом.
    """
    max_chars = max(200, N_CTX * 2)
    return text[:max_chars]


def embed_text(text: str) -> np.ndarray:
    """
    Получаем один эмбеддинг через llama-cpp-python.
    """
    text = text.strip()

    if EMBED_PREFIX:
        text = f"{EMBED_PREFIX} {text}".strip()

    text = truncate_text(text)

    try:
        response = llm.create_embedding(
            input=text,
            truncate=True,
        )
    except TypeError:
        # Если версия llama-cpp-python не знает аргумент truncate
        response = llm.create_embedding(input=text)

    embedding = response["data"][0]["embedding"]
    arr = np.asarray(embedding, dtype=np.float32)

    # Некоторые модели/режимы могут вернуть список списков.
    # Тогда усредняем по токенам.
    if arr.ndim > 1:
        arr = arr.mean(axis=0)

    return arr


def build_embeddings(texts: list[str]) -> np.ndarray:
    """
    Строит матрицу эмбеддингов для списка текстов.
    Для пустых текстов возвращает нулевой вектор.
    """
    vectors = []
    dim = None

    for text in texts:
        if not text.strip():
            vectors.append(None)
            continue

        vec = embed_text(text)
        vectors.append(vec)

        if dim is None:
            dim = vec.shape[0]

    if dim is None:
        # Все тексты пустые
        dim = 1

    for i, vec in enumerate(vectors):
        if vec is None:
            vectors[i] = np.zeros(dim, dtype=np.float32)

    return np.vstack(vectors)


def normalize_matrix(mat: np.ndarray) -> np.ndarray:
    mat = np.asarray(mat, dtype=np.float32)

    if mat.ndim == 1:
        mat = mat.reshape(1, -1)

    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0

    return mat / norms


def cosine_matrix(a: np.ndarray, b: np.ndarray = None) -> np.ndarray:
    a_norm = normalize_matrix(a)

    if b is None:
        return a_norm @ a_norm.T

    b_norm = normalize_matrix(b)
    return a_norm @ b_norm.T


# Плагиат: семантика

print("Строю эмбеддинги текстов студентов...", file=sys.stderr)

if any(text.strip() for text in clean_texts):
    embeddings = build_embeddings(clean_texts)
    semantic_scores = cosine_matrix(embeddings)
else:
    embeddings = np.zeros((len(clean_texts), 1), dtype=np.float32)
    semantic_scores = np.zeros((len(clean_texts), len(clean_texts)), dtype=np.float32)

# Плагиат: TF-IDF

if any(text.strip() for text in clean_texts):
    tfidf_texts = [text if text.strip() else " " for text in clean_texts]

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
    )

    tfidf_matrix = vectorizer.fit_transform(tfidf_texts)
    lexical_scores = cosine_similarity(tfidf_matrix)
else:
    lexical_scores = np.zeros((len(names), len(names)), dtype=np.float32)


plagiarism_cases = []

for i in range(len(names)):
    for j in range(i + 1, len(names)):
        sem_score = float(semantic_scores[i][j])
        lex_score = float(lexical_scores[i][j])

        is_semantic = sem_score > SEM_THRESHOLD
        is_lexical = lex_score > LEX_THRESHOLD

        if is_semantic or is_lexical:
            reason = []

            if is_semantic:
                reason.append("семантика")

            if is_lexical:
                reason.append("лексика")

            plagiarism_cases.append({
                "Студент 1": names[i],
                "Студент 2": names[j],
                "Семантика": f"{sem_score * 100:.1f}%",
                "Лексика": f"{lex_score * 100:.1f}%",
                "Причина": " + ".join(reason),
                "_max": max(sem_score, lex_score),
            })


# ============================================================
#               Скрининг по опорным фразам
# ============================================================

REFERENCE_PHRASES = [
    "измерена масса, диаметр и высота образца, по ним рассчитана плотность",
    "определён материал образца по значению плотности",
    "проанализирован вклад погрешностей массы, диаметра и высоты",
]

if any(text.strip() for text in clean_texts):
    print("Строю эмбеддинги опорных фраз...", file=sys.stderr)
    ref_emb = build_embeddings(REFERENCE_PHRASES)
    screen_sim = cosine_matrix(embeddings, ref_emb)
    screen_scores = screen_sim.max(axis=1).tolist()
else:
    screen_scores = [0.0 for _ in names]


# ============================================================
#                    Проверка критериев
# ============================================================

rows = []

for name, text, score in zip(names, clean_texts, screen_scores):
    if not text.strip() or score < SCREEN_THRESHOLD:
        rows.append(empty_row(name, score))
        continue

    rows.append(check_work(name, text, score))


# ============================================================
#                         Вывод
# ============================================================

print()
print(
    "=== 1. Плагиат: llama.cpp + TF-IDF "
    f"(sem>{SEM_THRESHOLD:.2f} OR lex>{LEX_THRESHOLD:.2f}) ==="
)

if plagiarism_cases:
    print("Обнаружены подозрительные совпадения:")

    df_plag = pd.DataFrame(plagiarism_cases).sort_values(
        by="_max",
        ascending=False,
    )

    df_plag = df_plag.drop(columns="_max")

    print(df_plag.to_string(index=False))
else:
    print("Подозрительных совпадений не найдено.")

print()
print("=== 2. Проверка по критериям ===")

df_crit = pd.DataFrame(rows)

print(df_crit.to_string(index=False))

passed = int((df_crit["Зачёт"] == "ДА").sum())

print()
print(f"Зачёт: {passed} из {len(df_crit)}")