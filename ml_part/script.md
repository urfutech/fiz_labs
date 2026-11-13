# Быстрый старт

## 1. Перейти в каталог проекта

```bash
cd fiz_labs/ml_part
```

## 2. Создать виртуальное окружение

```bash
python -m venv venv
```

## 3. Активировать окружение

**Windows PowerShell**

```powershell
.\venv\Scripts\Activate.ps1
```

Если PowerShell запрещает запуск скриптов:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

**Windows CMD**

```cmd
venv\Scripts\activate.bat
```

**Linux / macOS, bash или zsh**

```bash
source venv/bin/activate
```

**Linux / macOS, fish**

```fish
source venv/bin/activate.fish
```

## 4. Установить зависимости

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`llama-cpp-python` может требовать компилятор. Если он не установился, скрипт всё равно запустится без LLM — будет использовать regex и лексический антиплагиат.

## 5. Подготовить входной JSON

Файл должен быть объектом вида `{ "ключ": "текст" }`. В качестве ключа можно использовать ФИО или обезличенный id — он попадёт в колонку «Студент».

```json
{
  "student_1": "В ходе работы была измерена масса...",
  "student_2": "Целью работы было определить..."
}
```

## 6. Запустить проверку

```bash
python hybrid_lab1_checker.py lab_num1.json
```

Первый запуск может скачать GGUF-модель (~2 ГБ) в `models/`.

Быстрый режим без модели и без семантического антиплагиата:

```bash
python hybrid_lab1_checker.py lab_num1.json --no-model --no-plagiarism
```

Сохранить таблицу в CSV:

```bash
python hybrid_lab1_checker.py lab_num1.json --output lab1_report.csv
```

Все параметры:

```bash
python hybrid_lab1_checker.py --help
```

## 7. Выйти из окружения

```bash
deactivate
```

## 8. Создание синтетических тестов

Синтетические тесты — это примеры, которые мы пишем сами и размечаем по `docs/annotation_guideline.md`. Они нужны, чтобы покрыть редкие ошибки, которых мало в реальных студенческих работах.

### 8.1. Быстрый JSON для проверки чекера

Если нужно просто проверить, как `hybrid_lab1_checker.py` реагирует на текст, создай файл `synthetic_tests.json`:

```json
{
  "synthetic_pass": "В ходе работы измерены масса, диаметр и высота цилиндра. Масса 67,2 г, диаметр 25,1 мм, высота 50,3 мм. Плотность 2700 кг/м³, материал — алюминий. Погрешности: массы 0,5%, диаметра 1%, высоты 0,5%. Главный вклад даёт диаметр.",
  "synthetic_fail_material": "Измерены масса 84,1 г, диаметр 20,0 мм и высота 30,0 мм. Плотность 8930 кг/м³, материал — алюминий.",
  "synthetic_review_weight": "Взвесили цилиндр, измерили диаметр и высоту. Вес 67,2 г, диаметр 25,1 мм, высота 50,3 мм. Плотность 2700 кг/м³, алюминий."
}
```

Запуск без модели:

```bash
python hybrid_lab1_checker.py synthetic_tests.json --no-model --no-plagiarism
```

Такой файл не попадает в датасет: это только ручная проверка чекера.

### 8.2. Добавить синтетику в seed-датасет

Синтетические записи лежат в трёх файлах:

- `scripts/seed_synthetic_pass.py` — ожидаемый verdict `pass`;
- `scripts/seed_synthetic_review.py` — ожидаемый `needs_review`;
- `scripts/seed_synthetic_fail.py` — ожидаемый `fail`.

Добавляй новый пример в соответствующий список `SYNTHETIC_*` через `with_text(...)`.

Минимальный пример для `pass`:

```python
with_text(
    "В ходе работы измерены масса, диаметр и высота цилиндра. "
    "Масса 67,2 г, диаметр 25,1 мм, высота 50,3 мм. "
    "Плотность 2700 кг/м³, материал — алюминий. "
    "Погрешности: массы 0,5%, диаметра 1%, высоты 0,5%. "
    "Главный вклад даёт диаметр.",
    measured_mass=True,
    measured_diameter=True,
    measured_height=True,
    density=2700,
    density_calculated=True,
    rel_mass=0.005,
    rel_diameter=0.01,
    rel_height=0.005,
    material_student="Алюминий",
    material_student_raw="алюминий",
    dominant_stated="диаметр",
    error_analysis_present=True,
    evidence={
        "k1": ["измерены масса, диаметр и высота", "Плотность 2700 кг/м³"],
        "k2": ["алюминий"],
        "k3": ["Главный вклад даёт диаметр"],
    },
),
```

Пример для `needs_review` — спорный критерий оставляем `None`, а причину пишем в `flags` и `review_notes`:

```python
with_text(
    "Взвесили цилиндр, измерили диаметр и высоту. Вес 67,2 г, "
    "диаметр 25,1 мм, высота 50,3 мм. Плотность 2700 кг/м³, алюминий. "
    "Погрешности: веса 0,5%, диаметра 1%, высоты 0,5%. "
    "Главный вклад даёт диаметр.",
    measured_mass=None,
    measured_diameter=True,
    measured_height=True,
    density=2700,
    density_calculated=True,
    rel_mass=0.005,
    rel_diameter=0.01,
    rel_height=0.005,
    material_student="Алюминий",
    material_student_raw="алюминий",
    dominant_stated="диаметр",
    error_analysis_present=True,
    flags=["weight_as_mass"],
    review_notes="Вместо массы использован «вес» с массовыми единицами.",
    evidence={
        "k1": ["Взвесили цилиндр", "Вес 67,2 г"],
        "k2": ["алюминий"],
        "k3": ["Главный вклад даёт диаметр"],
    },
),
```

Правила:

- `verdict`, `id`, `student_id`, `source` не указывай — их считает `build_lab1_seed.py`.
- Для каждого критерия `true` или `null` нужна цитата в `evidence`.
- Для `needs_review` добавляй `flags` и `review_notes`, объясняющие сомнение.
- Не добавляй ФИО и другие персональные данные.
- Не редактируй `data/processed/conclusions/lab1_seed.jsonl` вручную: он перезаписывается сборкой.

### 8.3. Пересобрать датасет

```bash
cd fiz_labs/ml_part
python scripts/build_lab1_seed.py
```

Скрипт проверит схему, `evidence`, согласованность критериев и `verdict`, а затем обновит:

- `data/processed/conclusions/lab1_seed.jsonl`;
- `data/processed/conclusions/lab1_seed.manifest.json`.

В манифесте смотри `record_count`, `source_counts.synthetic` и `verdict_counts` — синтетика должна быть помечена `source: "synthetic"`.

### 8.4. Синтетические графики ЛР9

Генератор графиков ещё в плане (задача A5 в `todo.md`). Для них будет отдельный `labels.jsonl` с полями `id`, `lab_id`, `image_path`, `is_correct`, `defects`, `severity`. Пока для графиков используй ручные примеры и не смешивай их с текстовым датасетом ЛР1.
