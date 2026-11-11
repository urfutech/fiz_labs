from seed_schema import label_defaults

SOURCE_LABELS = {
    "Моткина": label_defaults(
        density=7883,
        density_calculated=True,
        material_student="Сталь",
        material_student_raw="сталь",
        error_analysis_present=True,
        flags=["missing_measurement_details", "total_error_only"],
        evidence={
            "k1": ["На основе измерений и вычислений"],
            "k2": ["совпадает с табличными значениями стали"],
            "k3": [],
        },
        review_notes=(
            "Плотность и материал указаны, но масса/диаметр/высота явно не названы; "
            "погрешность только суммарная."
        ),
    ),
    "Романескул": label_defaults(
        measured_diameter=True,
        measured_height=True,
        density_calculated=True,
        material_ambiguous=True,
        material_student_raw="железо либо сталь",
        error_analysis_present=True,
        flags=["weight_as_mass", "missing_density_value", "ambiguous_material"],
        evidence={
            "k1": [
                "измерены диаметр, высота и вес цилиндра",
                "рассчитаны плотность образца",
            ],
            "k2": ["либо из железа, либо из стали"],
            "k3": [],
        },
        review_notes=(
            "Вес не равен массе; численного значения плотности нет; "
            "материал назван неоднозначно."
        ),
    ),
    "Кузнецов": label_defaults(
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=2700,
        density_calculated=True,
        material_student="Алюминий",
        material_student_raw="алюминий",
        dominant_stated="высота",
        error_analysis_present=True,
        flags=["verbal_dominant_only", "total_error_only"],
        evidence={
            "k1": [
                "Масса 0,067 кг, диаметр 25,10 мм, высота 50,20 мм",
                "Плотность получилась 2700 кг/м^3",
            ],
            "k2": ["точно как в табличке для алюминия"],
            "k3": ["Основной вклад даёт погрешность измерения высоты"],
        },
        review_notes=(
            "Есть только суммарная погрешность; главный вклад заявлен словесно, "
            "без разбивки по величинам."
        ),
    ),
    "Сидоров": label_defaults(
        off_topic=True,
        duplicate_group="kirchhoff_duplicate_1",
        flags=["off_topic"],
        review_notes="Текст про законы Кирхгофа, не относится к ЛР1.",
    ),
    "Балбесов": label_defaults(
        off_topic=True,
        duplicate_group="kirchhoff_duplicate_1",
        flags=["off_topic"],
        review_notes="Точный дубль текста Сидорова; оставлен для проверки антиплагиата.",
    ),
    "Иванов": label_defaults(
        off_topic=True,
        flags=["off_topic"],
        review_notes="Текст про измерение g математическим маятником, не ЛР1.",
    ),
    "Петров": label_defaults(
        off_topic=True,
        flags=["off_topic"],
        review_notes="Текст про измерение g математическим маятником, не ЛР1.",
    ),
    "Карасова": label_defaults(
        empty=True,
        flags=["empty"],
        review_notes="Пустой текст.",
    ),
    "Волков": label_defaults(
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=5200,
        density_calculated=True,
        material_student="Титан",
        material_student_raw="титан",
        flags=["density_out_of_table", "material_mismatch"],
        evidence={
            "k1": [
                "Измеренные массу, диаметр и высоту подставляли в формулу",
                "плотность вышла 5200 кг/м^3",
            ],
            "k2": ["образец изготовлен из титана"],
            "k3": [],
        },
        review_notes="Плотность 5200 не попадает в табличные диапазоны; титан 4500.",
    ),
    "Лебедев": label_defaults(
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=2700,
        density_calculated=True,
        rel_mass=0.0005,
        rel_diameter=0.002,
        rel_height=0.0003,
        material_student="Алюминий",
        material_student_raw="алюминий",
        dominant_stated="масса",
        error_analysis_present=True,
        flags=["wrong_dominant"],
        evidence={
            "k1": [
                "измерены масса, диаметр и высота цилиндра",
                "Плотность образца 2700 кг/м^3",
            ],
            "k2": ["материал - алюминий"],
            "k3": [
                "Главным источником погрешности является погрешность измерения массы"
            ],
        },
        review_notes="По формуле главный вклад даёт диаметр, а не масса.",
    ),
    "Новикова": label_defaults(
        density=2700,
        material_student="Алюминий",
        material_student_raw="алюминий",
        flags=["missing_measurement_details"],
        evidence={
            "k2": ["что соответствует алюминию"],
        },
        review_notes="Есть только плотность и материал; измерения не описаны.",
    ),
    "Громов": label_defaults(
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=3000,
        density_calculated=True,
        material_student="Алюминий",
        material_student_raw="алюминий",
        flags=["density_out_of_table", "material_mismatch"],
        evidence={
            "k1": [
                "Штангенциркулем измерили диаметр и высоту цилиндра, весами - его массу",
                "Вычисленная плотность равна 3000 кг/м^3",
            ],
            "k2": ["что указывает на алюминий"],
            "k3": [],
        },
        review_notes="Плотность 3000 не попадает в таблицу, хотя студент называет алюминий.",
    ),
    "Смирнова": label_defaults(
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=8930,
        density_calculated=True,
        material_student="Медь",
        material_student_raw="медь",
        dominant_stated="масса",
        error_analysis_present=True,
        flags=["verbal_dominant_only"],
        evidence={
            "k1": [
                "измерены диаметр и высота медного цилиндра, а также его масса",
                "Плотность образца составила 8930 кг/м^3",
            ],
            "k2": ["точно соответствует табличной плотности меди"],
            "k3": ["Основную погрешность результата вносит измерение массы"],
        },
        review_notes="Главный вклад заявлен словесно; числовых погрешностей по величинам нет.",
    ),
    "Белова": label_defaults(
        density=788,
        density_calculated=True,
        material_student="Сталь",
        material_student_raw="сталь",
        error_analysis_present=True,
        flags=[
            "density_out_of_table",
            "material_mismatch",
            "missing_measurement_details",
            "possible_typo",
        ],
        evidence={
            "k2": ["подтверждает наличие стали в образце"],
        },
        review_notes="Плотность 788, вероятно опечатка (7880?); в диапазон стали не попадает.",
    ),
    "Ефимов": label_defaults(
        density=8000,
        density_calculated=True,
        material_ambiguous=True,
        material_student_raw="сталь или чугун",
        error_analysis_present=True,
        flags=[
            "weight_as_mass",
            "vague_measurements",
            "density_out_of_table",
            "ambiguous_material",
        ],
        evidence={
            "k1": ["Взвесили цилиндр, обмерили его линейкой"],
            "k2": ["материал - сталь или чугун"],
        },
        review_notes="Измерения описаны нечётко, плотность вне таблицы, материал неоднозначен.",
    ),
    "Эталонов": label_defaults(
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=7883,
        density_calculated=True,
        rel_mass=0.01,
        rel_diameter=0.01,
        rel_height=0.01,
        material_student="Сталь",
        material_student_raw="сталь",
        dominant_stated="диаметр",
        error_analysis_present=True,
        evidence={
            "k1": [
                "С помощью весов измерена масса образца m, микрометром измерен диаметр d, "
                "штангенциркулем измерена высота h",
                "рассчитана плотность образца",
            ],
            "k2": ["материал образца — сталь"],
            "k3": ["главный вклад в общую погрешность результата даёт диаметр"],
        },
        review_notes="Эталонный текст, все три критерия выполнены численно.",
    ),
    "Эталонный": label_defaults(
        measured_mass=True,
        measured_diameter=True,
        measured_height=True,
        density=7883,
        density_calculated=True,
        rel_mass=0.01,
        rel_diameter=0.01,
        rel_height=0.01,
        material_student="Сталь",
        material_student_raw="сталь",
        dominant_stated="диаметр",
        error_analysis_present=True,
        evidence={
            "k1": [
                "Измерены масса m, диаметр d и высота h образца",
                "рассчитана плотность",
            ],
            "k2": ["материал образца сталь"],
            "k3": ["Главный вклад в общую погрешность даёт диаметр"],
        },
        review_notes="Эталонный текст, все три критерия выполнены численно.",
    ),
}
