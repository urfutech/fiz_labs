import sys
import json
import pandas as pd
from sentence_transformers import SentenceTransformer, util

if len(sys.argv) < 2 or not sys.argv[1].strip():
    print(
        "Ошибка: не указано имя JSON-файла.\n"
        "Использование: python anti-plagiarism.py <json_name>",
        file=sys.stderr
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

model = SentenceTransformer('intfloat/multilingual-e5-base')

names = list(students_data.keys())
texts = list(students_data.values())

embeddings = model.encode(texts, convert_to_tensor=True)
cosine_scores = util.cos_sim(embeddings, embeddings)

THRESHOLD = 0.82
plagiarism_cases = []

for i in range(len(names)):
    for j in range(i + 1, len(names)):
        score = cosine_scores[i][j].item()
        if score > THRESHOLD:
            plagiarism_cases.append({
                "Студент 1": names[i],
                "Студент 2": names[j],
                "Схожесть": f"{score * 100:.1f}%"
            })

if plagiarism_cases:
    print("Обнаружены подозрительные совпадения:")
    df = pd.DataFrame(plagiarism_cases)
    print(df.to_string(index=False))
else:
    print("Все работы уникальны (в пределах семантического порога).")