#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
hybrid_lab1_checker.py

Гибридная проверка выводов ЛР1:
- regex: числа, плотность, погрешности;
- таблица материалов;
- формула главного вклада погрешности;
- локальная LLM через llama.cpp / llama-cpp-python;
- антиплагиат: локальные эмбеддинги + TF-IDF;
- опциональный эмбеддинг-скрининг.

Пример:
    python hybrid_lab1_checker.py lab_num1.json

Пример с 1.5B моделью:
    python hybrid_lab1_checker.py lab_num1.json \
        --model-repo Qwen/Qwen2.5-1.5B-Instruct-GGUF \
        --model-file qwen2.5-1.5b-instruct-q4_k_m.gguf
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from huggingface_hub import hf_hub_download
except Exception:
    hf_hub_download = None

try:
    from llama_cpp import Llama
except Exception:
    Llama = None


# Константы

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

MATERIAL_STEMS = {
    "алюмин": "Алюминий",
    "бронз": "Бронза",
    "желез": "Железо",
    "золот": "Золото",
    "латун": "Латунь",
    "стал": "Сталь",
    "мед": "Медь",
    "титан": "Титан",
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

REFERENCE_PHRASES_LAB1 = [
    "измерена масса, диаметр и высота образца, по ним рассчитана плотность",
    "определён материал образца по значению плотности",
    "проанализирован вклад погрешностей массы, диаметра и высоты",
]

SYSTEM_PROMPT = """
Ты — система проверки выводов лабораторных работ.
Твоя задача — извлекать только те факты, которые реально есть в тексте.
Не придумывай отсутствующую информацию.
Если чего-то нет, возвращай false или null.
Ответ должен быть строго валидным JSON без пояснений, без комментариев и без лишнего текста.
""".strip()


# Структуры

@dataclass
class RegexLab1Result:
    density: Optional[int] = None
    rel_mass: Optional[float] = None
    rel_diameter: Optional[float] = None
    rel_height: Optional[float] = None
    named_materials: List[str] = field(default_factory=list)
    dominant_calculated: Optional[str] = None
    normalized_text: str = ""


@dataclass
class LLMLab1Result:
    measured_mass: bool = False
    measured_diameter: bool = False
    measured_height: bool = False
    density_calculated: bool = False
    density_value: Optional[float] = None
    material_candidates: List[str] = field(default_factory=list)
    material_is_ambiguous: bool = False
    error_analysis_present: bool = False
    dominant_error_source_named: Optional[str] = None
    valid: bool = False
    raw: Dict[str, Any] = field(default_factory=dict)


# Утилиты

def configure_stdio() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Гибридная проверка выводов ЛР1: regex + таблица + формула + локальная LLM."
    )

    parser.add_argument("json_file", help="Входной JSON-файл вида {ФИО: текст}")

    parser.add_argument(
        "--model-repo",
        default=os.getenv("LLAMA_MODEL_REPO", "Qwen/Qwen2.5-3B-Instruct-GGUF"),
        help="Hugging Face repo id для GGUF-модели",
    )
    parser.add_argument(
        "--model-file",
        default=os.getenv("LLAMA_MODEL_FILENAME", "qwen2.5-3b-instruct-q4_k_m.gguf"),
        help="Имя GGUF-файла в репозитории",
    )
    parser.add_argument(
        "--model-dir",
        default=os.getenv("LLAMA_MODEL_DIR", "models"),
        help="Локальная папка для модели",
    )
    parser.add_argument(
        "--chat-format",
        default=os.getenv("LLAMA_CHAT_FORMAT", ""),
        help="Например: chatml. Обычно не нужно, если модель содержит шаблон.",
    )

    parser.add_argument("--n-gpu-layers", type=int, default=0)
    parser.add_argument("--n-ctx", type=int, default=4096)

    parser.add_argument(
        "--allow-weight-as-mass",
        action="store_true",
        help="Разрешать считать 'вес' признаком массы, если контекст про взвешивание.",
    )

    parser.add_argument(
        "--use-screen",
        action="store_true",
        help="Включить эмбеддинг-скрининг перед LLM.",
    )
    parser.add_argument(
        "--screen-threshold",
        type=float,
        default=0.15,
        help="Порог скрининга. Очень зависит от модели. Для небольших моделей подбирать вручную.",
    )
    parser.add_argument(
        "--embedding-prefix",
        default=os.getenv("EMBED_PREFIX", ""),
        help="Префикс для эмбеддингов, если модель его требует.",
    )

    parser.add_argument("--no-plagiarism", action="store_true", help="Не считать антиплагиат.")
    parser.add_argument("--no-llm", action="store_true", help="Не использовать LLM для смысловых признаков.")
    parser.add_argument("--no-model", action="store_true", help="Не загружать модель вообще.")

    parser.add_argument("--sem-threshold", type=float, default=0.75)
    parser.add_argument("--lex-threshold", type=float, default=0.45)

    parser.add_argument("--llm-retries", type=int, default=2)

    parser.add_argument(
        "--allow-verbal-dominant",
        action="store_true",
        help=(
            "Если числовых погрешностей нет, но студент явно написал главный вклад, "
            "разрешить засчитать К3 с пометкой 'требуется проверка'."
        ),
    )

    parser.add_argument("--output", default="", help="Сохранить итоговую таблицу в CSV.")

    return parser.parse_args()


def normalize_text(text: Any) -> str:
    if text is None:
        return ""
    return str(text).strip()


def normalize_for_regex(text: str) -> str:
    """
    Нормализуем текст для regex:
    - нижний регистр;
    - убираем лишние пробелы;
    - правим типовые разрывы слов.
    """
    t = (text or "").lower()
    t = re.sub(r"\s+", " ", t)

    # Частые дефекты из студенческих текстов
    t = re.sub(r"плотно\s*сть", "плотность", t)
    t = re.sub(r"пр\s*иборов", "приборов", t)
    t = re.sub(r"в\s*ероятности", "вероятности", t)
    t = re.sub(r"довер-ой", "доверительной", t)

    return t


def parse_number(value: str) -> float:
    return float(value.replace(",", "."))


# Regex / детерминированный слой

def extract_density(text_norm: str) -> Optional[int]:
    """
    Ищет плотность:
      - плотность составила 7883
      - (7883,0 +- 30) кг/м^3
      - ρ = 7883
    """
    patterns = [
        r"плотност[а-яё]*[^0-9]{0,40}(\d{3,5}(?:[.,]\d+)?)",
        r"[ρp]\s*[=≈]\s*(\d{3,5}(?:[.,]\d+)?)",
        r"(\d{3,5}(?:[.,]\d+)?)\s*(?:[+\-±]+\s*\d+(?:[.,]\d+)?)?\s*\)?\s*кг\s*/\s*м",
    ]

    for pattern in patterns:
        m = re.search(pattern, text_norm)
        if m:
            try:
                value = parse_number(m.group(1))
                return int(round(value))
            except Exception:
                continue

    return None


def extract_rel_errors(text_norm: str) -> Dict[str, Optional[float]]:
    """
    Ищет относительные погрешности массы, диаметра и высоты.
    """
    result: Dict[str, Optional[float]] = {
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
            pattern = rf"(?<![а-яё0-9]){stem}[а-яё]*"

            for m in re.finditer(pattern, text_norm):
                frag = text_norm[m.start(): m.start() + 200]

                # Вариант 1: проценты
                pm = re.search(r"(\d+(?:[.,]\d+)?)\s*%", frag)
                if pm:
                    try:
                        result[quantity] = parse_number(pm.group(1)) / 100.0
                        break
                    except Exception:
                        pass

                # Вариант 2: число рядом с погрешностью
                if any(marker in frag for marker in ("погреш", "δ", "Δ")):
                    dm = re.search(r"(\d+(?:[.,]\d+)?)", frag)
                    if dm:
                        try:
                            val = parse_number(dm.group(1))

                            if val <= 1.0:
                                result[quantity] = val
                                break
                            elif val <= 100.0:
                                result[quantity] = val / 100.0
                                break
                            else:
                                # слишком похоже на плотность/размер, не погрешность
                                continue
                        except Exception:
                            pass

            if result[quantity] is not None:
                break

    return result


def calculate_dominant_error(
    rel_mass: Optional[float],
    rel_diameter: Optional[float],
    rel_height: Optional[float],
) -> Optional[str]:
    """
    Для плотности цилиндра:
        rho = 4m / (pi d^2 h)

    Вклад:
        масса:      eps_m^2
        диаметр:    (2 * eps_d)^2
        высота:     eps_h^2
    """
    if rel_mass is None or rel_diameter is None or rel_height is None:
        return None

    contributions = {
        "масса": rel_mass ** 2,
        "диаметр": (2.0 * rel_diameter) ** 2,
        "высота": rel_height ** 2,
    }

    return max(contributions, key=contributions.get)


def identify_material(density: Optional[int]) -> Optional[str]:
    if density is None:
        return None

    for material, (low, high) in MATERIALS.items():
        if low <= density <= high:
            return material

    return None


def normalize_material(value: Any) -> Optional[str]:
    if value is None:
        return None

    s = str(value).lower().strip()
    if not s:
        return None

    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s)

    for stem, base in MATERIAL_STEMS.items():
        if stem in s:
            return base

    return None


def materials_equal(a: Any, b: Any) -> bool:
    na = normalize_material(a)
    nb = normalize_material(b)

    if na is None or nb is None:
        return False

    return na == nb


def extract_named_materials(text_norm: str) -> List[str]:
    """
    Фолбэк: ищем названные материалы без LLM.
    """
    found: List[str] = []

    for stem, base in MATERIAL_STEMS.items():
        pattern = rf"(?<![а-яё0-9]){stem}[а-яё]*"
        if re.search(pattern, text_norm):
            if base not in found:
                found.append(base)

    return found


def mentions_without_negation(text_norm: str, keywords: List[str], window: int = 50) -> bool:
    """
    Фолбэк-проверка наличия ключевых слов без отрицания.
    Используется только если LLM недоступна.
    """
    for kw in keywords:
        kw = kw.strip().lower()
        if not kw:
            continue

        pattern = rf"(?<![а-яё0-9]){re.escape(kw)}(?![а-яё0-9])"

        for m in re.finditer(pattern, text_norm):
            start = max(0, m.start() - window)
            end = min(len(text_norm), m.end() + 15)
            frag = text_norm[start:end]

            if not any(neg in frag for neg in NEGATIONS):
                return True

    return False


def verbal_dominant_error(text_norm: str) -> Optional[str]:
    """
    Фолбэк: ищем словесное указание главного вклада.
    """
    mapping = [
        ("масс", "масса"),
        ("диаметр", "диаметр"),
        ("высот", "высота"),
    ]

    for stem, name in mapping:
        pattern_direct = rf"{stem}[а-яё]*.{{0,120}}(вклад|погрешност|основн|главн)"
        pattern_reverse = rf"(вклад|погрешност|основн|главн).{{0,80}}{stem}[а-яё]*"

        if re.search(pattern_direct, text_norm, re.DOTALL):
            return name

        if re.search(pattern_reverse, text_norm, re.DOTALL):
            return name

    return None


def build_regex_result(text: str) -> RegexLab1Result:
    text_norm = normalize_for_regex(text)

    density = extract_density(text_norm)
    rel = extract_rel_errors(text_norm)

    dominant = calculate_dominant_error(
        rel_mass=rel["mass"],
        rel_diameter=rel["diameter"],
        rel_height=rel["height"],
    )

    named_materials = extract_named_materials(text_norm)

    return RegexLab1Result(
        density=density,
        rel_mass=rel["mass"],
        rel_diameter=rel["diameter"],
        rel_height=rel["height"],
        named_materials=named_materials,
        dominant_calculated=dominant,
        normalized_text=text_norm,
    )


# LLM-слой

def build_user_prompt(text: str, allow_weight_as_mass: bool) -> str:
    if allow_weight_as_mass:
        weight_rule = (
            "Если написано 'вес', 'веса', 'весом', это можно считать признаком массы, "
            "только если контекст явно указывает на измерение массы или взвешивание."
        )
    else:
        weight_rule = (
            "Слово 'вес' не считается признаком массы, если явно не сказано, что это масса."
        )

    return f"""
Дан текст вывода студента по лабораторной работе №1.

Текст:
<<<{text}>>>

Извлеки из текста признаки для ЛР 1.

Правила:
1. "measured_mass" = true, если в тексте явно сказано, что масса образца измерена, определена или найдена взвешиванием.
   {weight_rule}
2. "measured_diameter" = true, если явно сказано, что диаметр образца измерен, определён или найден.
3. "measured_height" = true, если явно сказано, что высота образца измерена, определена или найдена.
4. "density_calculated" = true, если сказано, что плотность рассчитана, определена, вычислена, найдена или получена.
5. "density_value" = числовое значение плотности в кг/м^3, если оно есть в тексте.
   Если числа нет, верни null.
   Десятичную запятую считай десятичной точкой.
6. "material_candidates" = список материалов, которые студент явно называет как материал образца.
   Используй только названия из списка:
   "алюминий", "бронза", "железо", "золото", "латунь", "сталь", "медь", "титан".
   Если студент не называет материал, верни пустой список.
7. "material_is_ambiguous" = true, если студент называет несколько возможных материалов или говорит "либо", "или", "возможно".
8. "error_analysis_present" = true, если студент обсуждает вклад погрешностей измерений.
9. "dominant_error_source_named" = "масса", "диаметр", "высота" или null.
   Возвращай значение только если студент явно указывает, какая величина даёт главный/основной/наибольший вклад.

Верни только один объект в таком формате:
{{
  "measured_mass": false,
  "measured_diameter": false,
  "measured_height": false,
  "density_calculated": false,
  "density_value": null,
  "material_candidates": [],
  "material_is_ambiguous": false,
  "error_analysis_present": false,
  "dominant_error_source_named": null
}}
""".strip()


def parse_json_loose(content: str) -> Dict[str, Any]:
    """
    Аккуратно пытаемся достать JSON из ответа модели.
    """
    text = (content or "").strip()

    # убираем markdown-обёртку, если есть
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return json.loads(text)


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "да", "yes", "y"}

    return False


def to_optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        s = value.strip().replace(",", ".")
        if not s:
            return None

        try:
            return float(s)
        except Exception:
            return None

    return None


def to_string_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def normalize_dominant(value: Any) -> Optional[str]:
    if value is None:
        return None

    s = str(value).lower()

    if "масс" in s:
        return "масса"

    if "диаметр" in s or "диам" in s:
        return "диаметр"

    if "высот" in s:
        return "высота"

    return None


def validate_llm_data(data: Dict[str, Any]) -> LLMLab1Result:
    material_candidates_raw = to_string_list(data.get("material_candidates", []))
    material_candidates: List[str] = []

    for item in material_candidates_raw:
        base = normalize_material(item)
        if base and base not in material_candidates:
            material_candidates.append(base)

    return LLMLab1Result(
        measured_mass=to_bool(data.get("measured_mass")),
        measured_diameter=to_bool(data.get("measured_diameter")),
        measured_height=to_bool(data.get("measured_height")),
        density_calculated=to_bool(data.get("density_calculated")),
        density_value=to_optional_float(data.get("density_value")),
        material_candidates=material_candidates,
        material_is_ambiguous=to_bool(data.get("material_is_ambiguous")),
        error_analysis_present=to_bool(data.get("error_analysis_present")),
        dominant_error_source_named=normalize_dominant(data.get("dominant_error_source_named")),
        valid=True,
        raw=data,
    )


def llm_extract_lab1(
    llm: Optional[Llama],
    text: str,
    args: argparse.Namespace,
) -> LLMLab1Result:
    if llm is None or args.no_llm:
        return LLMLab1Result(valid=False)

    user_prompt = build_user_prompt(text, args.allow_weight_as_mass)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    last_error: Optional[Exception] = None
    last_content = ""

    for attempt in range(args.llm_retries + 1):
        try:
            response = llm.create_chat_completion(
                messages=messages,
                temperature=0.0,
                top_p=0.1,
                max_tokens=400,
            )

            last_content = response["choices"][0]["message"]["content"] or ""
            data = parse_json_loose(last_content)
            result = validate_llm_data(data)

            if result.valid:
                return result

            last_error = ValueError("LLM вернула некорректную схему JSON")

        except Exception as exc:
            last_error = exc

        if attempt < args.llm_retries:
            correction = (
                "Твой предыдущий ответ не был валидным JSON или не соответствовал схеме. "
                "Верни только валидный JSON без пояснений."
            )
            messages = messages + [
                {"role": "assistant", "content": last_content},
                {"role": "user", "content": correction},
            ]

    return LLMLab1Result(
        valid=False,
        raw={
            "error": str(last_error),
            "content": last_content,
        },
    )


# Модель / эмбеддинги

def download_model(args: argparse.Namespace) -> str:
    if hf_hub_download is None:
        raise RuntimeError("Не установлен пакет huggingface_hub.")

    local_dir = Path(args.model_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    local_path = local_dir / args.model_file
    if local_path.exists():
        return str(local_path)

    print(
        f"Скачиваю модель:\n"
        f"  repo: {args.model_repo}\n"
        f"  file: {args.model_file}\n"
        f"  dir:  {local_dir.resolve()}",
        file=sys.stderr,
    )

    token = os.getenv("HF_TOKEN")

    path = hf_hub_download(
        repo_id=args.model_repo,
        filename=args.model_file,
        local_dir=str(local_dir),
        token=token if token else None,
    )

    return path


def load_llm(args: argparse.Namespace) -> Optional[Llama]:
    if Llama is None:
        print("Предупреждение: пакет llama_cpp не установлен.", file=sys.stderr)
        return None

    try:
        model_path = download_model(args)
    except Exception as exc:
        print(f"Предупреждение: не удалось скачать модель: {exc}", file=sys.stderr)
        return None

    print("Загружаю локальную модель...", file=sys.stderr)

    kwargs: Dict[str, Any] = dict(
        model_path=model_path,
        embedding=True,
        n_ctx=args.n_ctx,
        n_gpu_layers=args.n_gpu_layers,
        verbose=False,
    )

    if args.chat_format:
        kwargs["chat_format"] = args.chat_format

    try:
        return Llama(**kwargs)
    except Exception as exc:
        print(f"Предупреждение: не удалось загрузить модель: {exc}", file=sys.stderr)
        return None


def truncate_for_embedding(text: str, n_ctx: int) -> str:
    max_chars = max(200, n_ctx * 2)
    return text[:max_chars]


def embed_texts(
    llm: Optional[Llama],
    texts: List[str],
    n_ctx: int,
    prefix: str = "",
) -> np.ndarray:
    """
    Возвращает матрицу эмбеддингов.
    Пустым текстам соответствует нулевой вектор.
    """
    if llm is None:
        return np.zeros((len(texts), 1), dtype=np.float32)

    vectors: List[Optional[np.ndarray]] = []
    dim: Optional[int] = None

    for text in texts:
        t = (text or "").strip()

        if not t:
            vectors.append(None)
            continue

        if prefix:
            t = f"{prefix} {t}".strip()

        t = truncate_for_embedding(t, n_ctx)

        try:
            try:
                response = llm.create_embedding(input=t, truncate=True)
            except TypeError:
                response = llm.create_embedding(input=t)

            arr = np.asarray(response["data"][0]["embedding"], dtype=np.float32)

            if arr.ndim > 1:
                arr = arr.mean(axis=0)

            vectors.append(arr)
            dim = arr.shape[0]

        except Exception as exc:
            print(f"Предупреждение: ошибка эмбеддинга: {exc}", file=sys.stderr)
            vectors.append(None)

    if dim is None:
        dim = 1

    result = []
    for vec in vectors:
        if vec is None:
            result.append(np.zeros(dim, dtype=np.float32))
        else:
            result.append(vec)

    return np.vstack(result)


def normalize_matrix(mat: np.ndarray) -> np.ndarray:
    mat = np.asarray(mat, dtype=np.float32)

    if mat.ndim == 1:
        mat = mat.reshape(1, -1)

    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0

    return mat / norms


def cosine_matrix(a: np.ndarray, b: Optional[np.ndarray] = None) -> np.ndarray:
    a_norm = normalize_matrix(a)

    if b is None:
        return a_norm @ a_norm.T

    b_norm = normalize_matrix(b)
    return a_norm @ b_norm.T


def compute_screen_scores(
    llm: Optional[Llama],
    texts: List[str],
    args: argparse.Namespace,
) -> List[float]:
    if not args.use_screen or llm is None:
        return [1.0 for _ in texts]

    if not any(t.strip() for t in texts):
        return [0.0 for _ in texts]

    text_emb = embed_texts(
        llm,
        texts,
        args.n_ctx,
        prefix=args.embedding_prefix,
    )

    ref_emb = embed_texts(
        llm,
        REFERENCE_PHRASES_LAB1,
        args.n_ctx,
        prefix=args.embedding_prefix,
    )

    sim = cosine_matrix(text_emb, ref_emb)
    return sim.max(axis=1).tolist()


def compute_plagiarism(
    names: List[str],
    texts: List[str],
    llm: Optional[Llama],
    args: argparse.Namespace,
) -> List[Dict[str, Any]]:
    n = len(names)

    semantic_scores = np.zeros((n, n), dtype=np.float32)
    lexical_scores = np.zeros((n, n), dtype=np.float32)

    # 1. Лексический слой
    if any(t.strip() for t in texts):
        tfidf_texts = [t if t.strip() else " " for t in texts]

        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
        )

        tfidf_matrix = vectorizer.fit_transform(tfidf_texts)
        lexical_scores = cosine_similarity(tfidf_matrix)

    # 2. Семантический слой
    if llm is not None and any(t.strip() for t in texts):
        embeddings = embed_texts(
            llm,
            texts,
            args.n_ctx,
            prefix=args.embedding_prefix,
        )
        semantic_scores = cosine_matrix(embeddings)

    cases: List[Dict[str, Any]] = []

    for i in range(n):
        for j in range(i + 1, n):
            if not texts[i].strip() or not texts[j].strip():
                continue

            sem_score = float(semantic_scores[i][j])
            lex_score = float(lexical_scores[i][j])

            is_semantic = sem_score > args.sem_threshold
            is_lexical = lex_score > args.lex_threshold

            if is_semantic or is_lexical:
                reason = []

                if is_semantic:
                    reason.append("семантика")

                if is_lexical:
                    reason.append("лексика")

                cases.append({
                    "Студент 1": names[i],
                    "Студент 2": names[j],
                    "Семантика": f"{sem_score * 100:.1f}%",
                    "Лексика": f"{lex_score * 100:.1f}%",
                    "Причина": " + ".join(reason),
                    "_max": max(sem_score, lex_score),
                })

    cases.sort(key=lambda x: x["_max"], reverse=True)

    for case in cases:
        case.pop("_max", None)

    return cases


# Итоговая логика зачёта

def empty_fail_row(
    name: str,
    screen_score: float,
    reasons: List[str],
) -> Dict[str, Any]:
    return {
        "Студент": name,
        "К1: измерения+плотность": "✘",
        "К2: материал": "✘",
        "К3: главный вклад": "✘",
        "Плотность": "—",
        "Табличный материал": "—",
        "Материал студента": "—",
        "Заявленный вклад": "—",
        "Расчётный вклад": "—",
        "Скрин": f"{screen_score:.3f}",
        "Зачёт": "НЕТ",
        "Причины": "; ".join(reasons),
    }


def merge_student_result(
    name: str,
    text: str,
    screen_score: float,
    regex_result: RegexLab1Result,
    llm_result: LLMLab1Result,
    args: argparse.Namespace,
) -> Dict[str, Any]:
    reasons: List[str] = []

    if not text.strip():
        return empty_fail_row(name, screen_score, ["пустой текст"])

    if len(text.strip()) < 20:
        return empty_fail_row(name, screen_score, ["слишком короткий текст"])

    if args.use_screen and screen_score < args.screen_threshold:
        return empty_fail_row(name, screen_score, ["низкий эмбеддинг-скрининг"])

    # 1. Плотность: сначала доверяем regex, потом LLM
    density: Optional[int] = regex_result.density

    if density is None and llm_result.valid and llm_result.density_value is not None:
        try:
            density = int(round(float(llm_result.density_value)))
        except Exception:
            density = None

    table_material = identify_material(density)

    # 2. Материал, названный студентом
    if llm_result.valid and llm_result.material_candidates:
        student_materials = llm_result.material_candidates
        ambiguous = llm_result.material_is_ambiguous or len(student_materials) != 1
    else:
        student_materials = regex_result.named_materials
        ambiguous = len(student_materials) != 1

    student_material = student_materials[0] if len(student_materials) == 1 and not ambiguous else None

    # 3. Критерий 1: измерения + плотность
    if llm_result.valid:
        measured_mass = llm_result.measured_mass
        measured_diameter = llm_result.measured_diameter
        measured_height = llm_result.measured_height
        density_calculated = llm_result.density_calculated
    else:
        # Фолбэк, если модель недоступна
        text_norm = regex_result.normalized_text

        mass_keywords = ["масса", "массу", "массы", "массой", "массе"]

        if args.allow_weight_as_mass:
            mass_keywords += ["вес", "веса", "весом"]

        measured_mass = mentions_without_negation(text_norm, mass_keywords)
        measured_diameter = mentions_without_negation(
            text_norm,
            ["диаметр", "диаметра", "диаметре", "диаметром"],
        )
        measured_height = mentions_without_negation(
            text_norm,
            ["высота", "высоту", "высоты", "высоте", "высотой"],
        )

        density_calculated = density is not None or bool(
            re.search(
                r"плотност[а-яё]*[^0-9]{0,30}(рассчит|определ|вычисл|найд|получ)",
                text_norm,
            )
        )

    crit1 = (
        measured_mass
        and measured_diameter
        and measured_height
        and density_calculated
        and density is not None
    )

    if not crit1:
        reasons.append("К1: нет явных измерений массы/диаметра/высоты или плотности")

    # 4. Критерий 2: материал
    crit2 = (
        density is not None
        and table_material is not None
        and student_material is not None
        and not ambiguous
        and materials_equal(student_material, table_material)
    )

    if not crit2:
        if density is None:
            reasons.append("К2: нет плотности")
        elif table_material is None:
            reasons.append("К2: плотность не соответствует таблице")
        elif student_material is None or ambiguous:
            reasons.append("К2: студент не назвал материал однозначно")
        else:
            reasons.append("К2: названный материал не совпадает с табличным")

    # 5. Критерий 3: главный вклад
    stated_dominant: Optional[str] = None

    if llm_result.valid:
        stated_dominant = llm_result.dominant_error_source_named
    else:
        stated_dominant = verbal_dominant_error(regex_result.normalized_text)

    calculated_dominant = regex_result.dominant_calculated

    if calculated_dominant is not None:
        crit3 = stated_dominant == calculated_dominant

        if not crit3:
            reasons.append("К3: заявленный главный вклад не совпадает с расчётным")
    else:
        if args.allow_verbal_dominant:
            crit3 = stated_dominant is not None

            if llm_result.valid:
                crit3 = crit3 and llm_result.error_analysis_present

            if crit3:
                reasons.append("К3: только словесный вывод, желательна ручная проверка")
            else:
                reasons.append("К3: нет числовых погрешностей и явного главного вклада")
        else:
            crit3 = False
            reasons.append("К3: нет числовых погрешностей для расчёта главного вклада")

    passed = crit1 and crit2 and crit3

    return {
        "Студент": name,
        "К1: измерения+плотность": "✔" if crit1 else "✘",
        "К2: материал": "✔" if crit2 else "✘",
        "К3: главный вклад": "✔" if crit3 else "✘",
        "Плотность": density if density is not None else "—",
        "Табличный материал": table_material if table_material else "—",
        "Материал студента": student_material if student_material else "—",
        "Заявленный вклад": stated_dominant if stated_dominant else "—",
        "Расчётный вклад": calculated_dominant if calculated_dominant else "—",
        "Скрин": f"{screen_score:.3f}",
        "Зачёт": "ДА" if passed else "НЕТ",
        "Причины": "; ".join(reasons) if reasons else "",
    }


# main

def main() -> None:
    configure_stdio()
    args = parse_args()

    try:
        with open(args.json_file, "r", encoding="utf-8") as f:
            students_data = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: файл '{args.json_file}' не найден.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Ошибка: не удалось разобрать JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(students_data, dict) or not students_data:
        print("Ошибка: JSON должен быть непустым объектом {имя: текст}.", file=sys.stderr)
        sys.exit(1)

    students_data = {
        normalize_text(name): normalize_text(text)
        for name, text in students_data.items()
    }

    names = list(students_data.keys())
    texts = list(students_data.values())

    # Модель нужна, если включены LLM, скрининг или семантический плагиат
    need_model = (
        not args.no_model
        and (
            (not args.no_llm)
            or args.use_screen
            or (not args.no_plagiarism)
        )
    )

    llm: Optional[Llama] = None

    if need_model:
        llm = load_llm(args)
    else:
        print("Модель не загружается: включён детерминированный/лексический режим.", file=sys.stderr)

    # Быстрый скрининг
    screen_scores = compute_screen_scores(llm, texts, args)

    rows: List[Dict[str, Any]] = []

    for name, text, screen_score in zip(names, texts, screen_scores):
        regex_result = build_regex_result(text)

        llm_result = LLMLab1Result(valid=False)

        if llm is not None and not args.no_llm:
            llm_result = llm_extract_lab1(llm, text, args)

        row = merge_student_result(
            name=name,
            text=text,
            screen_score=screen_score,
            regex_result=regex_result,
            llm_result=llm_result,
            args=args,
        )

        rows.append(row)

    # Плагиат
    plagiarism_cases: List[Dict[str, Any]] = []

    if not args.no_plagiarism:
        plagiarism_cases = compute_plagiarism(names, texts, llm, args)

    plagiarism_names = set()

    for case in plagiarism_cases:
        plagiarism_names.add(case["Студент 1"])
        plagiarism_names.add(case["Студент 2"])

    for row in rows:
        row["Плагиат"] = "да" if row["Студент"] in plagiarism_names else "нет"

    # Вывод
    print()
    print("1. Плагиат: локальные эмбеддинги + TF-IDF")

    if args.no_plagiarism:
        print("Плагиат отключён флагом --no-plagiarism.")
    elif plagiarism_cases:
        df_plag = pd.DataFrame(plagiarism_cases)
        print(df_plag.to_string(index=False))
    else:
        print("Подозрительных совпадений не найдено.")

    print()
    print("2. Проверка выводов ЛР1")

    columns = [
        "Студент",
        "К1: измерения+плотность",
        "К2: материал",
        "К3: главный вклад",
        "Плотность",
        "Табличный материал",
        "Материал студента",
        "Заявленный вклад",
        "Расчётный вклад",
        "Скрин",
        "Плагиат",
        "Зачёт",
        "Причины",
    ]

    df = pd.DataFrame(rows, columns=columns)

    print(df.to_string(index=False))

    passed = int((df["Зачёт"] == "ДА").sum())

    print()
    print(f"Зачёт: {passed} из {len(df)}")

    if args.output:
        df.to_csv(args.output, index=False, encoding="utf-8-sig")
        print(f"Результат сохранён: {args.output}")


if __name__ == "__main__":
    main()