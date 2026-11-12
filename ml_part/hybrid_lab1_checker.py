#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
hybrid_lab1_checker.py (v2 - True Hybrid)

Архитектура:
- SentenceTransformer (E5/RuBERT) -> Эмбеддинги, Плагиат, Скрининг.
- llama-cpp-python (Qwen Instruct) -> Извлечение смысловых фактов в JSON.
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

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


#                         Константы

MATERIALS = {
    "Алюминий": (2700, 2700), "Бронза": (8700, 8900), "Железо": (7870, 7870),
    "Золото": (19300, 19300), "Латунь": (8400, 8700), "Сталь": (7500, 7900),
    "Медь": (8930, 8930), "Титан": (4500, 4500),
}

MATERIAL_STEMS = {
    "алюмин": "Алюминий", "бронз": "Бронза", "желез": "Железо", "золот": "Золото",
    "латун": "Латунь", "стал": "Сталь", "мед": "Медь", "титан": "Титан",
}

NEGATIONS = ("не ", "нет ", "отсутств", "не измер", "не определ", "не найд", "не получ")

# По умолчанию используем легкую и быструю русскоязычную модель.
# Если хотите E5, замените на "intfloat/multilingual-e5-base"
DEFAULT_EMBED_MODEL = os.getenv("EMBED_MODEL", "cointegrated/rubert-tiny2")

SYSTEM_PROMPT = """
Ты — строгий, но справедливый эксперт по проверке лабораторных работ.
Извлекай из текста только те факты, которые реально есть. Не выдумывай.
Если студент написал "вес" вместо "масса", но контекст про взвешивание — считай это массой.
Если студент написал "параметры цилиндра" или "размеры" вместо "диаметр и высота" — считай, что они измерены.
Ответ — строго валидный JSON без пояснений и markdown-разметки.
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


# Утилиты и Regex

def configure_stdio() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="Входной JSON-файл")
    
    # LLM args
    parser.add_argument("--model-repo", default="Qwen/Qwen2.5-3B-Instruct-GGUF")
    parser.add_argument("--model-file", default="qwen2.5-3b-instruct-q4_k_m.gguf")
    parser.add_argument("--model-dir", default="models")
    parser.add_argument("--n-gpu-layers", type=int, default=0)
    parser.add_argument("--n-ctx", type=int, default=4096)
    
    # Embedding args
    parser.add_argument("--embed-model", default=DEFAULT_EMBED_MODEL, help="Модель для плагиата (SentenceTransformer)")
    
    # Logic args
    parser.add_argument("--allow-weight-as-mass", action="store_true")
    parser.add_argument("--allow-verbal-dominant", action="store_true")
    parser.add_argument("--use-screen", action="store_true")
    parser.add_argument("--screen-threshold", type=float, default=0.30)
    
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--no-plagiarism", action="store_true")
    parser.add_argument("--debug", action="store_true", help="Печатать сырой ответ LLM")
    
    parser.add_argument("--sem-threshold", type=float, default=0.80)
    parser.add_argument("--lex-threshold", type=float, default=0.45)
    parser.add_argument("--llm-retries", type=int, default=1)
    parser.add_argument("--output", default="")
    
    return parser.parse_args()

def normalize_text(text: Any) -> str:
    return "" if text is None else str(text).strip()

def normalize_for_regex(text: str) -> str:
    t = (text or "").lower()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"плотно\s*сть", "плотность", t)
    t = re.sub(r"пр\s*иборов", "приборов", t)
    return t

def parse_number(value: str) -> float:
    return float(value.replace(",", "."))

def extract_density(text_norm: str) -> Optional[int]:
    patterns = [
        r"плотност[а-яё]*[^0-9]{0,40}(\d{3,5}(?:[.,]\d+)?)",
        r"[ρp]\s*[=≈]\s*(\d{3,5}(?:[.,]\d+)?)",
        r"(\d{3,5}(?:[.,]\d+)?)\s*(?:[+\-±]+\s*\d+(?:[.,]\d+)?)?\s*\)?\s*кг\s*/\s*м",
    ]
    for p in patterns:
        m = re.search(p, text_norm)
        if m:
            try: return int(round(parse_number(m.group(1))))
            except: continue
    return None

def extract_rel_errors(text_norm: str) -> Dict[str, Optional[float]]:
    res = {"mass": None, "diameter": None, "height": None}
    keys = {"mass": ["масс"], "diameter": ["диаметр", "диам"], "height": ["высот"]}
    for q, stems in keys.items():
        for stem in stems:
            for m in re.finditer(rf"(?<![а-яё0-9]){stem}[а-яё]*", text_norm):
                frag = text_norm[m.start(): m.start() + 200]
                pm = re.search(r"(\d+(?:[.,]\d+)?)\s*%", frag)
                if pm:
                    try: res[q] = parse_number(pm.group(1)) / 100.0; break
                    except: pass
                if any(x in frag for x in ("погреш", "δ", "Δ")):
                    dm = re.search(r"(\d+(?:[.,]\d+)?)", frag)
                    if dm:
                        try:
                            val = parse_number(dm.group(1))
                            if val <= 1.0: res[q] = val; break
                            elif val <= 100.0: res[q] = val / 100.0; break
                        except: pass
            if res[q] is not None: break
    return res

def calculate_dominant_error(m, d, h) -> Optional[str]:
    if m is None or d is None or h is None: return None
    c = {"масса": m**2, "диаметр": (2.0*d)**2, "высота": h**2}
    return max(c, key=c.get)

def identify_material(density: Optional[int]) -> Optional[str]:
    if density is None: return None
    for mat, (lo, hi) in MATERIALS.items():
        if lo <= density <= hi: return mat
    return None

def normalize_material(val: Any) -> Optional[str]:
    if val is None: return None
    s = re.sub(r"[^\w\s]", " ", str(val).lower())
    for stem, base in MATERIAL_STEMS.items():
        if stem in s: return base
    return None

def materials_equal(a, b) -> bool:
    na, nb = normalize_material(a), normalize_material(b)
    return na is not None and nb is not None and na == nb

def extract_named_materials(text_norm: str) -> List[str]:
    return [base for stem, base in MATERIAL_STEMS.items() if re.search(rf"(?<![а-яё0-9]){stem}[а-яё]*", text_norm)]

def mentions_without_negation(text_norm: str, kws: List[str], window=50) -> bool:
    for kw in kws:
        kw = kw.strip().lower()
        if not kw: continue
        for m in re.finditer(rf"(?<![а-яё0-9]){re.escape(kw)}(?![а-яё0-9])", text_norm):
            frag = text_norm[max(0, m.start()-window): min(len(text_norm), m.end()+15)]
            if not any(n in frag for n in NEGATIONS): return True
    return False

def verbal_dominant_error(text_norm: str) -> Optional[str]:
    for stem, name in [("масс", "масса"), ("диаметр", "диаметр"), ("высот", "высота")]:
        if re.search(rf"{stem}[а-яё]*.{{0,120}}(вклад|погрешност|основн|главн)", text_norm, re.DOTALL) or \
           re.search(rf"(вклад|погрешност|основн|главн).{{0,80}}{stem}[а-яё]*", text_norm, re.DOTALL):
            return name
    return None

def build_regex_result(text: str) -> RegexLab1Result:
    t = normalize_for_regex(text)
    d = extract_density(t)
    rel = extract_rel_errors(t)
    return RegexLab1Result(
        density=d, rel_mass=rel["mass"], rel_diameter=rel["diameter"], rel_height=rel["height"],
        named_materials=extract_named_materials(t),
        dominant_calculated=calculate_dominant_error(rel["mass"], rel["diameter"], rel["height"]),
        normalized_text=t
    )


# LLM-слой (Qwen)

def build_user_prompt(text: str) -> str:
    return f"""
Дан текст вывода студента по ЛР 1.
Текст:
<<<{text}>>>

Извлеки факты. Правила:
1. "measured_mass": true, если измерена масса (или вес на весах).
2. "measured_diameter": true, если измерен диаметр (или ширина, поперечный размер).
3. "measured_height": true, если измерена высота (или длина, продольный размер).
4. "density_calculated": true, если плотность рассчитана/определена.
5. "density_value": число плотности в кг/м^3 или null.
6. "material_candidates": список названных материалов (алюминий, бронза, железо, золото, латунь, сталь, медь, титан).
7. "material_is_ambiguous": true, если названо несколько вариантов ("либо сталь, либо железо").
8. "error_analysis_present": true, если есть анализ погрешностей.
9. "dominant_error_source_named": "масса", "диаметр", "высота" или null (если явно указан главный вклад).

Верни ТОЛЬКО JSON:
{{
  "measured_mass": false, "measured_diameter": false, "measured_height": false,
  "density_calculated": false, "density_value": null,
  "material_candidates": [], "material_is_ambiguous": false,
  "error_analysis_present": false, "dominant_error_source_named": null
}}
""".strip()

def parse_json_loose(content: str) -> Dict[str, Any]:
    text = re.sub(r"```(?:json)?", "", content or "", flags=re.IGNORECASE).replace("```", "")
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start: text = text[start:end + 1]
    return json.loads(text)

def to_bool(v) -> bool:
    if isinstance(v, bool): return v
    if isinstance(v, str): return v.strip().lower() in {"true", "1", "да", "yes"}
    return False

def to_float(v) -> Optional[float]:
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).replace(",", "."))
    except: return None

def to_str_list(v) -> List[str]:
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str) and v.strip(): return [v.strip()]
    return []

def norm_dom(v) -> Optional[str]:
    if v is None: return None
    s = str(v).lower()
    if "масс" in s: return "масса"
    if "диаметр" in s or "диам" in s: return "диаметр"
    if "высот" in s: return "высота"
    return None

def validate_llm_data(data: Dict[str, Any]) -> LLMLab1Result:
    mats = []
    for item in to_str_list(data.get("material_candidates", [])):
        b = normalize_material(item)
        if b and b not in mats: mats.append(b)
        
    return LLMLab1Result(
        measured_mass=to_bool(data.get("measured_mass")),
        measured_diameter=to_bool(data.get("measured_diameter")),
        measured_height=to_bool(data.get("measured_height")),
        density_calculated=to_bool(data.get("density_calculated")),
        density_value=to_float(data.get("density_value")),
        material_candidates=mats,
        material_is_ambiguous=to_bool(data.get("material_is_ambiguous")),
        error_analysis_present=to_bool(data.get("error_analysis_present")),
        dominant_error_source_named=norm_dom(data.get("dominant_error_source_named")),
        valid=True, raw=data
    )

def download_model(args) -> str:
    local_dir = Path(args.model_dir)
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = local_dir / args.model_file
    if local_path.exists(): return str(local_path)
    print(f"Скачиваю LLM: {args.model_repo}/{args.model_file}", file=sys.stderr)
    return hf_hub_download(repo_id=args.model_repo, filename=args.model_file, local_dir=str(local_dir))

def load_llm(args) -> Optional[Llama]:
    if Llama is None or args.no_llm: return None
    try:
        path = download_model(args)
        print("Загружаю LLM (Qwen)...", file=sys.stderr)
        return Llama(model_path=path, n_ctx=args.n_ctx, n_gpu_layers=args.n_gpu_layers, verbose=False)
    except Exception as e:
        print(f"Ошибка загрузки LLM: {e}", file=sys.stderr)
        return None

def llm_extract(llm: Optional[Llama], text: str, args) -> LLMLab1Result:
    if llm is None: return LLMLab1Result(valid=False)
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": build_user_prompt(text)}]
    last_content = ""
    for attempt in range(args.llm_retries + 1):
        try:
            resp = llm.create_chat_completion(messages=msgs, temperature=0.0, top_p=0.1, max_tokens=300)
            last_content = resp["choices"][0]["message"]["content"] or ""
            if args.debug:
                print(f"\n[DEBUG LLM RAW for {text[:30]}...]:\n{last_content}\n", file=sys.stderr)
            return validate_llm_data(parse_json_loose(last_content))
        except Exception as e:
            if attempt < args.llm_retries:
                msgs += [{"role": "assistant", "content": last_content}, {"role": "user", "content": "Верни строго валидный JSON."}]
            else:
                return LLMLab1Result(valid=False, raw={"error": str(e), "content": last_content})
    return LLMLab1Result(valid=False)


# Эмбеддинги (SentenceTransformer)


def load_embedder(model_name: str):
    if SentenceTransformer is None:
        print("Ошибка: sentence-transformers не установлен!", file=sys.stderr)
        sys.exit(1)
    print(f"Загрузка эмбеддинг-модели ({model_name})...", file=sys.stderr)
    return SentenceTransformer(model_name)

def embed_texts_st(model, texts: List[str], is_query: bool = False) -> np.ndarray:
    # Для E5 нужен префикс, для RuBERT/BGE - нет
    use_prefix = "e5" in model._modules.get('0', model).__class__.__name__.lower() or "e5" in str(model).lower()
    prefix = "query: " if is_query else "passage: " if use_prefix else ""
    
    clean = [t if t.strip() else " " for t in texts]
    prefixed = [f"{prefix}{t}" for t in clean]
    return model.encode(prefixed, convert_to_numpy=True, show_progress_bar=False)

def cosine_matrix(a, b=None):
    a = a / np.linalg.norm(a, axis=1, keepdims=True)
    if b is None: return a @ a.T
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    return a @ b.T


# Плагиат и Скрининг

def compute_plagiarism(names, texts, embedder, args):
    n = len(names)
    sem_scores = np.zeros((n, n))
    lex_scores = np.zeros((n, n))
    
    if any(t.strip() for t in texts):
        # Лексика
        tfidf = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
        lex_scores = cosine_similarity(tfidf.fit_transform([t if t.strip() else " " for t in texts]))
        
        # Семантика
        if embedder is not None:
            embs = embed_texts_st(embedder, texts)
            sem_scores = cosine_matrix(embs)
            
    cases = []
    for i in range(n):
        for j in range(i+1, n):
            if not texts[i].strip() or not texts[j].strip(): continue
            s, l = float(sem_scores[i][j]), float(lex_scores[i][j])
            if s > args.sem_threshold or l > args.lex_threshold:
                reasons = []
                if s > args.sem_threshold: reasons.append("семантика")
                if l > args.lex_threshold: reasons.append("лексика")
                cases.append({
                    "Студент 1": names[i], "Студент 2": names[j],
                    "Семантика": f"{s*100:.1f}%", "Лексика": f"{l*100:.1f}%",
                    "Причина": " + ".join(reasons), "_max": max(s, l)
                })
    cases.sort(key=lambda x: x["_max"], reverse=True)
    for c in cases: c.pop("_max")
    return cases

def compute_screen_scores(embedder, texts, args):
    if not args.use_screen or embedder is None: return [1.0] * len(texts)
    if not any(t.strip() for t in texts): return [0.0] * len(texts)
    
    refs = [
        "измерена масса, диаметр и высота образца, по ним рассчитана плотность",
        "определён материал образца по значению плотности",
        "проанализирован вклад погрешностей массы, диаметра и высоты",
    ]
    t_emb = embed_texts_st(embedder, texts)
    r_emb = embed_texts_st(embedder, refs, is_query=True)
    return cosine_matrix(t_emb, r_emb).max(axis=1).tolist()


# Итоговая логика

def empty_fail_row(name, score, reasons):
    return {
        "Студент": name, "К1": "✘", "К2": "✘", "К3": "✘",
        "Плотность": "—", "Табл.мат": "—", "Студ.мат": "—",
        "Заявл.вклад": "—", "Расч.вклад": "—", "Скрин": f"{score:.3f}",
        "Зачёт": "НЕТ", "Причины": "; ".join(reasons)
    }

def merge_result(name, text, score, reg, llm, args):
    reasons = []
    if not text.strip(): return empty_fail_row(name, score, ["пустой текст"])
    if len(text.strip()) < 20: return empty_fail_row(name, score, ["слишком короткий"])
    if args.use_screen and score < args.screen_threshold: return empty_fail_row(name, score, ["низкий скрининг"])
    
    # 1. Плотность
    density = reg.density
    if density is None and llm.valid and llm.density_value:
        try: density = int(round(llm.density_value))
        except: pass
    table_mat = identify_material(density)
    
    # 2. Материал студента
    if llm.valid and llm.material_candidates:
        stud_mats = llm.material_candidates
        ambig = llm.material_is_ambiguous or len(stud_mats) != 1
    else:
        stud_mats = reg.named_materials
        ambig = len(stud_mats) != 1
    stud_mat = stud_mats[0] if len(stud_mats) == 1 and not ambig else None
    
    # 3. К1 (Измерения)
    if llm.valid:
        m_mass, m_diam, m_hei, d_calc = llm.measured_mass, llm.measured_diameter, llm.measured_height, llm.density_calculated
    else:
        t = reg.normalized_text
        m_kw = ["масса", "массу", "массы", "вес", "веса"] if args.allow_weight_as_mass else ["масса", "массу", "массы"]
        m_mass = mentions_without_negation(t, m_kw + ["параметр", "размер"]) # Смягчение
        m_diam = mentions_without_negation(t, ["диаметр", "диаметра", "поперечн"])
        m_hei = mentions_without_negation(t, ["высота", "высоту", "длин", "продольн"])
        d_calc = density is not None
        
    crit1 = m_mass and m_diam and m_hei and d_calc and density is not None
    if not crit1: reasons.append("К1: нет явных измерений или плотности")
    
    # 4. К2 (Материал)
    crit2 = density is not None and table_mat and stud_mat and not ambig and materials_equal(stud_mat, table_mat)
    if not crit2: reasons.append("К2: материал не совпал или не назван")
    
    # 5. К3 (Вклад)
    stated = llm.dominant_error_source_named if llm.valid else verbal_dominant_error(reg.normalized_text)
    calc = reg.dominant_calculated
    
    if calc is not None:
        crit3 = (stated == calc)
        if not crit3: reasons.append("К3: заявленный вклад != расчётному")
    else:
        if args.allow_verbal_dominant:
            crit3 = stated is not None and (not llm.valid or llm.error_analysis_present)
            if crit3: reasons.append("К3: только словесный (ручная проверка)")
            else: reasons.append("К3: нет чисел и явного вклада")
        else:
            crit3 = False
            reasons.append("К3: нет числовых погрешностей")
            
    passed = crit1 and crit2 and crit3
    
    return {
        "Студент": name,
        "К1": "✔" if crit1 else "✘", "К2": "✔" if crit2 else "✘", "К3": "✔" if crit3 else "✘",
        "Плотность": density or "—", "Табл.мат": table_mat or "—", "Студ.мат": stud_mat or "—",
        "Заявл.вклад": stated or "—", "Расч.вклад": calc or "—",
        "Скрин": f"{score:.3f}", "Зачёт": "ДА" if passed else "НЕТ",
        "Причины": "; ".join(reasons) if reasons else ""
    }

def main():
    configure_stdio()
    args = parse_args()
    
    try:
        with open(args.json_file, "r", encoding="utf-8") as f: data = json.load(f)
    except Exception as e:
        print(f"Ошибка JSON: {e}", file=sys.stderr); sys.exit(1)
        
    data = {normalize_text(k): normalize_text(v) for k, v in data.items()}
    names, texts = list(data.keys()), list(data.values())
    
    # Загрузка моделей
    embedder = load_embedder(args.embed_model) if not args.no_plagiarism or args.use_screen else None
    llm = load_llm(args)
    
    screen_scores = compute_screen_scores(embedder, texts, args)
    rows = []
    
    for name, text, score in zip(names, texts, screen_scores):
        reg = build_regex_result(text)
        llm_res = llm_extract(llm, text, args) if llm else LLMLab1Result(valid=False)
        rows.append(merge_result(name, text, score, reg, llm_res, args))
        
    plag = compute_plagiarism(names, texts, embedder, args) if not args.no_plagiarism else []
    plag_names = {c["Студент 1"] for c in plag} | {c["Студент 2"] for c in plag}
    for r in rows: r["Плагиат"] = "да" if r["Студент"] in plag_names else "нет"
    
    print("\n=== 1. Плагиат ===")
    if plag: print(pd.DataFrame(plag).to_string(index=False))
    else: print("Не найдено.")
    
    print("\n=== 2. Критерии ЛР1 ===")
    cols = ["Студент", "К1", "К2", "К3", "Плотность", "Табл.мат", "Студ.мат", "Заявл.вклад", "Расч.вклад", "Скрин", "Плагиат", "Зачёт", "Причины"]
    df = pd.DataFrame(rows, columns=cols)
    print(df.to_string(index=False))
    print(f"\nЗачёт: {(df['Зачёт']=='ДА').sum()} из {len(df)}")
    
    if args.output: df.to_csv(args.output, index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    main()