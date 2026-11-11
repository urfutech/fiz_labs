from __future__ import annotations

from typing import Any, Dict, Optional

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

MATERIAL_BY_STEM = {
    "алюмин": "Алюминий",
    "бронз": "Бронза",
    "желез": "Железо",
    "золот": "Золото",
    "латун": "Латунь",
    "стал": "Сталь",
    "мед": "Медь",
    "титан": "Титан",
}


def identify_material(density: Optional[float]) -> Optional[str]:
    if density is None:
        return None
    for material, (low, high) in MATERIALS.items():
        if low <= density <= high:
            return material
    return None


def calculate_dominant(
    rel_mass: Optional[float],
    rel_diameter: Optional[float],
    rel_height: Optional[float],
) -> Optional[str]:
    """Главный вклад для rho = 4m / (pi d^2 h)."""
    if rel_mass is None or rel_diameter is None or rel_height is None:
        return None

    contributions = {
        "масса": rel_mass**2,
        "диаметр": (2.0 * rel_diameter) ** 2,
        "высота": rel_height**2,
    }
    best = max(contributions.values())
    winners = [name for name, value in contributions.items() if value == best]
    if len(winners) > 1:
        return None
    return winners[0]


def compute_k1(
    measured_mass: Optional[bool],
    measured_diameter: Optional[bool],
    measured_height: Optional[bool],
    density_calculated: bool,
    density: Optional[float],
) -> Optional[bool]:
    """К1: явно измерены m, d, h; плотность рассчитана и есть её значение."""
    values = (measured_mass, measured_diameter, measured_height)
    if any(value is False for value in values):
        return False
    if any(value is None for value in values):
        return None
    return bool(density_calculated) and density is not None


def compute_k2(
    density: Optional[float],
    material_table: Optional[str],
    material_student: Optional[str],
    material_ambiguous: bool,
) -> bool:
    """К2: плотность попадает в таблицу, материал назван однозначно и совпал."""
    if density is None or material_table is None:
        return False
    if material_student is None or material_ambiguous:
        return False
    return material_student == material_table


def compute_k3(
    dominant_calc: Optional[str],
    dominant_stated: Optional[str],
    error_analysis_present: bool,
) -> Optional[bool]:
    """К3: числовой вклад должен совпасть; словесный — needs_review."""
    if dominant_calc is not None:
        return dominant_stated == dominant_calc
    if dominant_stated is not None and error_analysis_present:
        return None
    return False


def compute_verdict(
    k1: Optional[bool],
    k2: Optional[bool],
    k3: Optional[bool],
    *,
    empty: bool = False,
    off_topic: bool = False,
) -> str:
    if empty or off_topic:
        return "fail"
    if any(value is False for value in (k1, k2, k3)):
        return "fail"
    if any(value is None for value in (k1, k2, k3)):
        return "needs_review"
    return "pass"


def label_defaults(**kwargs: Any) -> Dict[str, Any]:
    """Значения по умолчанию для одной записи разметки."""
    data: Dict[str, Any] = {
        "measured_mass": False,
        "measured_diameter": False,
        "measured_height": False,
        "density": None,
        "density_calculated": False,
        "rel_mass": None,
        "rel_diameter": None,
        "rel_height": None,
        "material_student": None,
        "material_student_raw": None,
        "material_ambiguous": False,
        "dominant_stated": None,
        "error_analysis_present": False,
        "flags": None,
        "evidence": None,
        "review_notes": "",
        "empty": False,
        "off_topic": False,
        "too_short": False,
        "duplicate_group": None,
    }
    data.update(kwargs)
    if data["flags"] is None:
        data["flags"] = []
    if data["evidence"] is None:
        data["evidence"] = {"k1": [], "k2": [], "k3": []}
    return data


def with_text(text: str, **kwargs: Any) -> Dict[str, Any]:
    data = label_defaults(**kwargs)
    data["text"] = text
    return data
