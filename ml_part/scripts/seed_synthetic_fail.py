from seed_schema import with_text

SYNTHETIC_FAIL = [
    with_text(
        "Измерены масса 84,1 г, диаметр 20,0 мм и высота 30,0 мм. Плотность образца "
        "8930 кг/м³, что, по нашему мнению, соответствует алюминию. Погрешности: масса 1%, "
        "диаметр 1%, высота 1%. Главный вклад даёт диаметр.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=8930,
        density_calculated=True,
        rel_mass=0.01,
        rel_diameter=0.01,
        rel_height=0.01,
        material_student="Алюминий",
        material_student_raw="алюминий",
        dominant_stated="диаметр",
        error_analysis_present=True,
        flags=["material_mismatch"],
        evidence={
            "k1": [
                "Измерены масса 84,1 г, диаметр 20,0 мм и высота 30,0 мм",
                "Плотность образца 8930 кг/м³",
            ],
            "k2": ["соответствует алюминию"],
            "k3": ["Главный вклад даёт диаметр"],
        },
        review_notes="Плотность 8930 соответствует меди, а не алюминию.",
    ),
    with_text(
        "Измерены масса, диаметр и высота цилиндра. Масса 67,0 г, диаметр 25,0 мм, "
        "высота 50,0 мм. Относительные погрешности: массы 1%, диаметра 1%, высоты 1%. "
        "Главный вклад в погрешность даёт диаметр. Плотность рассчитать не удалось.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=None,
        density_calculated=False,
        rel_mass=0.01,
        rel_diameter=0.01,
        rel_height=0.01,
        dominant_stated="диаметр",
        error_analysis_present=True,
        flags=["missing_density_value"],
        evidence={
            "k1": [
                "Измерены масса, диаметр и высота цилиндра",
                "Плотность рассчитать не удалось",
            ],
            "k3": ["Главный вклад в погрешность даёт диаметр"],
        },
        review_notes="Нет численного значения плотности.",
    ),
    with_text(
        "В работе измерены масса, диаметр и высота цилиндра. Масса 67,2 г, диаметр 25,1 мм, "
        "высота 50,3 мм. Рассчитанная плотность 2700 кг/м³. Погрешности: масса 1%, диаметр 1%, "
        "высота 1%. Главный вклад даёт диаметр.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=2700,
        density_calculated=True,
        rel_mass=0.01,
        rel_diameter=0.01,
        rel_height=0.01,
        dominant_stated="диаметр",
        error_analysis_present=True,
        flags=["material_not_named"],
        evidence={
            "k1": [
                "измерены масса, диаметр и высота цилиндра",
                "Рассчитанная плотность 2700 кг/м³",
            ],
            "k3": ["Главный вклад даёт диаметр"],
        },
        review_notes="Студент не назвал материал.",
    ),
    with_text(
        "Измерены масса, диаметр и высота цилиндра. Масса 193,0 г, диаметр 25,0 мм, "
        "высота 50,0 мм. Плотность 7883 кг/м³. Можно предположить, что образец изготовлен "
        "из стали или железа. Погрешности: масса 1%, диаметр 1%, высота 1%. Главный вклад даёт диаметр.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=7883,
        density_calculated=True,
        rel_mass=0.01,
        rel_diameter=0.01,
        rel_height=0.01,
        material_ambiguous=True,
        material_student_raw="сталь или железо",
        dominant_stated="диаметр",
        error_analysis_present=True,
        flags=["ambiguous_material"],
        evidence={
            "k1": ["Измерены масса, диаметр и высота цилиндра", "Плотность 7883 кг/м³"],
            "k2": ["из стали или железа"],
            "k3": ["Главный вклад даёт диаметр"],
        },
        review_notes="Материал назван неоднозначно.",
    ),
    with_text(
        "Измерены масса 193,0 г, диаметр 25,0 мм и высота 50,0 мм стального цилиндра. "
        "Плотность 7883 кг/м³ соответствует стали. Относительные погрешности: массы 0,1%, "
        "диаметра 1%, высоты 0,1%. Основной вклад в погрешность даёт масса.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=7883,
        density_calculated=True,
        rel_mass=0.001,
        rel_diameter=0.01,
        rel_height=0.001,
        material_student="Сталь",
        material_student_raw="сталь",
        dominant_stated="масса",
        error_analysis_present=True,
        flags=["wrong_dominant"],
        evidence={
            "k1": [
                "Измерены масса 193,0 г, диаметр 25,0 мм и высота 50,0 мм",
                "Плотность 7883 кг/м³",
            ],
            "k2": ["соответствует стали"],
            "k3": ["Основной вклад в погрешность даёт масса"],
        },
        review_notes="По формуле главный вклад даёт диаметр, а не масса.",
    ),
    with_text(
        "Измерены масса 94,2 г, диаметр 20,0 мм и высота 30,0 мм. Плотность образца "
        "10000 кг/м³, что указывает на серебро. Погрешности: масса 1%, диаметр 1%, "
        "высота 1%. Главный вклад даёт диаметр.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=10000,
        density_calculated=True,
        rel_mass=0.01,
        rel_diameter=0.01,
        rel_height=0.01,
        material_student_raw="серебро",
        dominant_stated="диаметр",
        error_analysis_present=True,
        flags=["density_out_of_table", "material_out_of_table"],
        evidence={
            "k1": [
                "Измерены масса 94,2 г, диаметр 20,0 мм и высота 30,0 мм",
                "Плотность образца 10000 кг/м³",
            ],
            "k2": ["указывает на серебро"],
            "k3": ["Главный вклад даёт диаметр"],
        },
        review_notes="Плотность и материал вне таблицы.",
    ),
    with_text(
        "Измерены масса 195,0 г, диаметр 25,0 мм и высота 50,0 мм. Плотность получилась "
        "7950 кг/м³, что соответствует стали. Погрешности: масса 1%, диаметр 1%, высота 1%. "
        "Главный вклад даёт диаметр.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=7950,
        density_calculated=True,
        rel_mass=0.01,
        rel_diameter=0.01,
        rel_height=0.01,
        material_student="Сталь",
        material_student_raw="сталь",
        dominant_stated="диаметр",
        error_analysis_present=True,
        flags=["density_out_of_table", "material_mismatch"],
        evidence={
            "k1": [
                "Измерены масса 195,0 г, диаметр 25,0 мм и высота 50,0 мм",
                "Плотность получилась 7950 кг/м³",
            ],
            "k2": ["соответствует стали"],
            "k3": ["Главный вклад даёт диаметр"],
        },
        review_notes="7950 выше верхней границы стали (7900).",
    ),
    with_text(
        "Измерены масса 67,2 г, диаметр 25,1 мм и высота 50,3 мм алюминиевого цилиндра. "
        "Плотность составила 2700 кг/м³, что соответствует алюминию.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=2700,
        density_calculated=True,
        material_student="Алюминий",
        material_student_raw="алюминий",
        error_analysis_present=False,
        flags=["no_error_analysis"],
        evidence={
            "k1": [
                "Измерены масса 67,2 г, диаметр 25,1 мм и высота 50,3 мм",
                "Плотность составила 2700 кг/м³",
            ],
            "k2": ["соответствует алюминию"],
        },
        review_notes="Нет анализа погрешностей.",
    ),
    with_text(
        "В лабораторной работе изучали закон Ома для участка цепи. Собрали электрическую "
        "цепь, измерили силу тока и напряжение, проверили зависимость I = U/R. Результаты "
        "совпали с теоретическими.",
        off_topic=True,
        flags=["off_topic"],
        review_notes="Не относится к ЛР1.",
    ),
    with_text(
        "",
        empty=True,
        flags=["empty"],
        review_notes="Пустой текст.",
    ),
    with_text(
        "Плотность 2700 кг/м³.",
        density=2700,
        too_short=True,
        flags=["too_short"],
        review_notes="Слишком короткий текст, нет измерений и материала.",
    ),
    with_text(
        "В работе рассматривалась плотность населения в городских районах. Проанализировали "
        "статистические данные за несколько лет и построили график динамики.",
        off_topic=True,
        flags=["off_topic"],
        review_notes="Омонимия: «плотность населения» не относится к ЛР1.",
    ),
]
