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
