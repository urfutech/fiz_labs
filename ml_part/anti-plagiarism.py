import sys
import json
import re
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


if len(sys.argv) < 2 or not sys.argv[1].strip():
    print(
        "Ошибка: не указано имя JSON-файла.\n"
        "Использование: python anti-plagiarism.py <json_name>",
        file=sys.stderr,
    )
    sys.exit(1)

json_name = sys.argv[1]

try:
    with open(json_name, "r", encoding="utf-8") as file:
        students_data = json.load(file)
except FileNotFoundError:
    print(f"Ошибка: файл '{json_name}' не найден.", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Ошибка: не удалось разобрать JSON в '{json_name}': {e}", file=sys.stderr)
    sys.exit(1)

if not isinstance(students_data, dict) or not students_data:
    print("Ошибка: JSON должен быть непустым объектом {имя: текст}.", file=sys.stderr)
    sys.exit(1)


MATERIALS = {
    "Алюминий": (2700, 2700),
    "Бронза":   (8700, 8900),
    "Железо":   (7870, 7870),
    "Золото":   (19300, 19300),
    "Латунь":   (8400, 8700),
    "Сталь":    (7500, 7900),
    "Медь":     (8930, 8930),
    "Титан":    (4500, 4500),
}


NEGATIONS = ("не ", "нет ", "отсутств", "не измер", "не определ")


def mentions_without_negation(text: str, keywords: list[str], window: int = 30) -> bool:
    text_low = text.lower()
    for kw in keywords:
        for m in re.finditer(kw, text_low):
            start = max(0, m.start() - window)
            frag = text_low[start:m.end() + 10]
            if not any(neg in frag for neg in NEGATIONS):
                return True
    return False


def extract_density(text: str):
    patterns = [
        r'плотност\w*[^\d]{0,20}(\d{3,5})',
        r'[ρp]\s*[=≈]\s*(\d{3,5})',
        r'(\d{3,5})\s*кг\s*/\s*м',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def identify_material(density):
    if density is None:
        return None
    for name, (lo, hi) in MATERIALS.items():
        if lo <= density <= hi:
            return name
    return None


def extract_rel_errors(text: str):
    text_low = text.lower()
    result = {"mass": None, "diameter": None, "height": None}
    keys = {"mass": ["масс"], "diameter": ["диаметр"], "height": ["высот"]}
    for q, kws in keys.items():
        for kw in kws:
            for m in re.finditer(kw, text_low):
                frag = text_low[m.start(): m.start() + 120]
                pm = re.search(r'(\d+(?:[.,]\d+)?)\s*%', frag)
                if pm:
                    result[q] = float(pm.group(1).replace(",", ".")) / 100.0
                    break
                dm = re.search(r'(\d+[.,]\d+|\d+)', frag)
                if dm and ('погреш' in frag or 'δ' in frag or 'Δ' in frag):
                    val = float(dm.group(1).replace(",", "."))
                    if val > 1:
                        val /= 100.0
                    result[q] = val
                    break
            if result[q] is not None:
                break
    return result


def dominant_error_source(rel_errors: dict):
    m, d, h = rel_errors["mass"], rel_errors["diameter"], rel_errors["height"]
    if m is None or d is None or h is None:
        return None
    contributions = {"масса": m ** 2, "диаметр": (2 * d) ** 2, "высота": h ** 2}
    return max(contributions, key=contributions.get)


def verbal_error_conclusion(text: str):
    text_low = text.lower()
    for q in ["масса", "диаметр", "высота"]:
        pattern = rf"{q}\w*.{{0,80}}(вклад|погрешност|основн|главн)"
        if re.search(pattern, text_low):
            return q
    return None


print("Загрузка E5 (multilingual-e5-base)...", file=sys.stderr)
model = SentenceTransformer('intfloat/multilingual-e5-base')

names = list(students_data.keys())
clean_texts = list(students_data.values())

# passage: — E5 для документов, контраст выше, чем с query:
e5_texts = [f"passage: {text}" for text in clean_texts]
embeddings = model.encode(e5_texts, convert_to_tensor=True)
semantic_scores = util.cos_sim(embeddings, embeddings).cpu().numpy()


vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
tfidf_matrix = vectorizer.fit_transform(clean_texts)
lexical_scores = cosine_similarity(tfidf_matrix, tfidf_matrix)


SEM_THRESHOLD = 0.88   # E5: «очень похоже по смыслу»
LEX_THRESHOLD = 0.45   # TF-IDF: «много дословных совпадений»

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

REFERENCE_PHRASES = [
    "измерена масса, диаметр и высота образца, по ним рассчитана плотность",
    "определён материал образца по значению плотности",
    "проанализирован вклад погрешностей массы, диаметра и высоты",
]
ref_emb = model.encode(
    [f"passage: {p}" for p in REFERENCE_PHRASES],
    convert_to_tensor=True,
)
screen_scores = util.cos_sim(embeddings, ref_emb).max(dim=1).values.tolist()


def check_work(name: str, text: str, screen_score: float) -> dict:
    has_mass = mentions_without_negation(text, ["масса", "массу", "массы", "m =", "m="])
    has_diam = mentions_without_negation(text, ["диаметр", "диаметра", "d =", "d="])
    has_height = mentions_without_negation(text, ["высота", "высоту", "высоты", "h =", "h="])
    density_val = extract_density(text)
    crit1 = has_mass and has_diam and has_height and (density_val is not None)

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
        "E5-скрин (max sim)": f"{screen_score:.3f}",
        "Зачёт": "ДА" if (crit1 and crit2 and crit3) else "НЕТ",
    }


rows = []
for name, text, score in zip(names, clean_texts, screen_scores):
    if score < 0.55:
        rows.append({
            "Студент": name,
            "К1: измерения+плотность": "✘",
            "Плотность (кг/м³)": "—",
            "К2: материал": "✘",
            "К3: главный вклад": "✘",
            "E5-скрин (max sim)": f"{score:.3f}",
            "Зачёт": "НЕТ",
        })
        continue
    rows.append(check_work(name, text, score))


print("\n=== 1. Плагиат: E5 + TF-IDF "
      f"(sem>{SEM_THRESHOLD:.2f} OR lex>{LEX_THRESHOLD:.2f}) ===")
if plagiarism_cases:
    print("Обнаружены подозрительные совпадения:")
    df_plag = pd.DataFrame(plagiarism_cases).sort_values(by="_max", ascending=False)
    df_plag = df_plag.drop(columns="_max")
    print(df_plag.to_string(index=False))
else:
    print("Подозрительных совпадений не найдено.")

print("\n=== 2. Проверка по критериям ===")
df_crit = pd.DataFrame(rows)
print(df_crit.to_string(index=False))

passed = (df_crit["Зачёт"] == "ДА").sum()
print(f"\nЗачёт: {passed} из {len(df_crit)}")