from seed_schema import with_text

SYNTHETIC_REVIEW = [
    with_text(
        "В работе измерены масса, диаметр и высота алюминиевого цилиндра. Масса 67,2 г, "
        "диаметр 25,1 мм, высота 50,3 мм. Плотность составила 2700 кг/м³, материал — алюминий. "
        "Погрешности отдельных величин не рассчитывали, но основной вклад в общую погрешность "
        "даёт высота.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=2700,
        density_calculated=True,
        material_student="Алюминий",
        material_student_raw="алюминий",
        dominant_stated="высота",
        error_analysis_present=True,
        flags=["verbal_dominant_only"],
        evidence={
            "k1": [
                "измерены масса, диаметр и высота алюминиевого цилиндра",
                "Плотность составила 2700 кг/м³",
            ],
            "k2": ["материал — алюминий"],
            "k3": ["основной вклад в общую погрешность даёт высота"],
        },
        review_notes="Главный вклад только словесный, без числовых погрешностей по величинам.",
    ),
    with_text(
        "Взвесили цилиндр, измерили диаметр и высоту. Вес цилиндра 67,2 г, диаметр 25,1 мм, "
        "высота 50,3 мм. Плотность 2700 кг/м³, алюминий. Погрешности: веса 0,5%, диаметра 1%, "
        "высоты 0,5%. Главный вклад даёт диаметр.",
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
        evidence={
            "k1": [
                "Взвесили цилиндр, измерили диаметр и высоту",
                "Вес цилиндра 67,2 г",
            ],
            "k2": ["алюминий"],
            "k3": ["Главный вклад даёт диаметр"],
        },
        review_notes="Вместо массы использован «вес» с массовыми единицами; нужна ручная проверка.",
    ),
    with_text(
        "Измерены масса, диаметр и высота стального цилиндра. Масса 193,0 г, диаметр 25,0 мм, "
        "высота 50,0 мм. Плотность 7883 кг/м³ соответствует стали. Численные погрешности не "
        "рассчитывали, но главный вклад в погрешность, по нашему мнению, даёт масса.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=7883,
        density_calculated=True,
        material_student="Сталь",
        material_student_raw="сталь",
        dominant_stated="масса",
        error_analysis_present=True,
        flags=["verbal_dominant_only"],
        evidence={
            "k1": [
                "Измерены масса, диаметр и высота стального цилиндра",
                "Плотность 7883 кг/м³",
            ],
            "k2": ["соответствует стали"],
            "k3": ["главный вклад в погрешность ... даёт масса"],
        },
        review_notes="Главный вклад только словесный; числовой расчёт отсутствует.",
    ),
    with_text(
        "В работе измерены масса, диаметр и высота алюминиевого цилиндра. Масса 67,0 г, "
        "диаметр 25,0 мм, высота 50,0 мм. Плотность равна 2700 кг/м³, материал — алюминий. "
        "Относительная погрешность массы 0,5%, диаметра 1%; погрешность высоты не оценивали. "
        "Главный вклад вносит диаметр.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=2700,
        density_calculated=True,
        rel_mass=0.005,
        rel_diameter=0.01,
        material_student="Алюминий",
        material_student_raw="алюминий",
        dominant_stated="диаметр",
        error_analysis_present=True,
        flags=["incomplete_error_data"],
        evidence={
            "k1": [
                "измерены масса, диаметр и высота алюминиевого цилиндра",
                "Плотность равна 2700 кг/м³",
            ],
            "k2": ["материал — алюминий"],
            "k3": ["Главный вклад вносит диаметр"],
        },
        review_notes="Не хватает погрешности высоты, поэтому числовой вклад не вычисляется.",
    ),
    with_text(
        "Для стального образца измерены масса 193,6 г, диаметр 25,0 мм и высота 50,0 мм. "
        "Плотность составила 7900 кг/м³, что соответствует стали. Погрешности по величинам "
        "не рассчитывали, но основной вклад даёт диаметр.",
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=7900,
        density_calculated=True,
        material_student="Сталь",
        material_student_raw="сталь",
        dominant_stated="диаметр",
        error_analysis_present=True,
        flags=["verbal_dominant_only", "boundary_density"],
        evidence={
            "k1": [
                "измерены масса 193,6 г, диаметр 25,0 мм и высота 50,0 мм",
                "Плотность составила 7900 кг/м³",
            ],
            "k2": ["соответствует стали"],
            "k3": ["основной вклад даёт диаметр"],
        },
        review_notes="Плотность на верхней границе стали; главный вклад только словесный.",
    ),
]
