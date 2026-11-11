from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from seed_schema import (
    calculate_dominant,
    compute_k1,
    compute_k2,
    compute_k3,
    compute_verdict,
    identify_material,
)
from seed_source import SOURCE_LABELS
from seed_synthetic_fail import SYNTHETIC_FAIL
from seed_synthetic_pass import SYNTHETIC_PASS
from seed_synthetic_review import SYNTHETIC_REVIEW

ROOT = Path(__file__).resolve().parents[1]
TEST_JSON = ROOT / "test.json"
LAB1_JSON = ROOT / "lab_num1.json"
OUT_DIR = ROOT / "data" / "processed" / "conclusions"
OUT_JSONL = OUT_DIR / "lab1_seed.jsonl"
OUT_MANIFEST = OUT_DIR / "lab1_seed.manifest.json"
DATASET_VERSION = "0.1.0"
DATASET_DATE = "2026-11-10"

REQUIRED_KEYS = {
    "id",
    "lab_id",
    "student_id",
    "text",
    "verdict",
    "criteria",
    "extraction",
    "evidence",
    "quality",
    "flags",
    "source",
    "annotator",
    "reviewed",
    "dataset_version",
}


def load_source_pairs() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for path in (TEST_JSON, LAB1_JSON):
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        for name, text in data.items():
            key = (name, text)
            if key in seen:
                continue
            seen.add(key)
            pairs.append((name, text))
    return pairs


def source_student_id(name: str) -> str:
    digest = hashlib.sha256(("fiz_labs:" + name).encode("utf-8")).hexdigest()
    return "src_" + digest[:12]


def build_record(
    record_id: str,
    student_id: str,
    text: str,
    label: dict[str, Any],
    source: str,
) -> dict[str, Any]:
    density = label["density"]
    material_table = identify_material(density)
    dominant_calc = calculate_dominant(
        label["rel_mass"],
        label["rel_diameter"],
        label["rel_height"],
    )

    k1 = compute_k1(
        label["measured_mass"],
        label["measured_diameter"],
        label["measured_height"],
        label["density_calculated"],
        density,
    )
    k2 = compute_k2(
        density,
        material_table,
        label["material_student"],
        label["material_ambiguous"],
    )
    k3 = compute_k3(
        dominant_calc,
        label["dominant_stated"],
        label["error_analysis_present"],
    )
    verdict = compute_verdict(
        k1,
        k2,
        k3,
        empty=label["empty"],
        off_topic=label["off_topic"],
    )

    return {
        "id": record_id,
        "lab_id": 1,
        "student_id": student_id,
        "text": text,
        "verdict": verdict,
        "criteria": {"k1": k1, "k2": k2, "k3": k3},
        "extraction": {
            "density": density,
            "density_unit": "kg/m3",
            "measured_mass": label["measured_mass"],
            "measured_diameter": label["measured_diameter"],
            "measured_height": label["measured_height"],
            "density_calculated": label["density_calculated"],
            "rel_errors": {
                "mass": label["rel_mass"],
                "diameter": label["rel_diameter"],
                "height": label["rel_height"],
            },
            "material_table": material_table,
            "material_student": label["material_student"],
            "material_student_raw": label["material_student_raw"],
            "material_ambiguous": label["material_ambiguous"],
            "dominant_stated": label["dominant_stated"],
            "dominant_calc": dominant_calc,
            "error_analysis_present": label["error_analysis_present"],
        },
        "evidence": label["evidence"],
        "quality": {
            "empty": label["empty"],
            "off_topic": label["off_topic"],
            "too_short": label["too_short"],
            "duplicate_group": label["duplicate_group"],
        },
        "flags": label["flags"],
        "source": source,
        "annotator": "ml_1",
        "reviewed": True,
        "review_notes": label["review_notes"],
        "dataset_version": DATASET_VERSION,
    }


def collect_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for index, (name, text) in enumerate(load_source_pairs(), start=1):
        if name not in SOURCE_LABELS:
            raise KeyError(f"Нет разметки для исходного текста: {name}")
        source = "reference" if name in {"Эталонов", "Эталонный"} else "teacher_example"
        records.append(
            build_record(
                record_id=f"lab1_text_{index:04d}",
                student_id=source_student_id(name),
                text=text,
                label=SOURCE_LABELS[name],
                source=source,
            )
        )

    offset = len(records)
    for index, label in enumerate(
        SYNTHETIC_PASS + SYNTHETIC_REVIEW + SYNTHETIC_FAIL,
        start=1,
    ):
        records.append(
            build_record(
                record_id=f"lab1_text_{offset + index:04d}",
                student_id=f"syn_{index:03d}",
                text=label["text"],
                label=label,
                source="synthetic",
            )
        )

    return records


def validate(records: list[dict[str, Any]]) -> None:
    source_names = set(SOURCE_LABELS)
    ids = set()
    for record in records:
        missing = REQUIRED_KEYS - set(record)
        if missing:
            raise ValueError(f"{record['id']}: нет полей {sorted(missing)}")
        if record["id"] in ids:
            raise ValueError(f"Повторяющийся id: {record['id']}")
        ids.add(record["id"])

        if record["verdict"] not in {"pass", "fail", "needs_review"}:
            raise ValueError(f"{record['id']}: неверный verdict")
        if set(record["criteria"]) != {"k1", "k2", "k3"}:
            raise ValueError(f"{record['id']}: неверный набор критериев")

        for name in source_names:
            if name in record["text"]:
                raise ValueError(f"{record['id']}: в тексте осталось ФИО {name}")
        for name in source_names:
            if name in record["student_id"]:
                raise ValueError(f"{record['id']}: в student_id осталось ФИО {name}")

        for criterion, value in record["criteria"].items():
            if value in (True, None) and not record["evidence"].get(criterion):
                raise ValueError(
                    f"{record['id']}: для {criterion}={value} нужна цитата в evidence"
                )

        k1 = record["criteria"]["k1"]
        k2 = record["criteria"]["k2"]
        k3 = record["criteria"]["k3"]
        extraction = record["extraction"]

        if k1 is True:
            if not (
                extraction["measured_mass"]
                and extraction["measured_diameter"]
                and extraction["measured_height"]
                and extraction["density_calculated"]
                and extraction["density"] is not None
            ):
                raise ValueError(f"{record['id']}: k1=True не согласован с extraction")
        if k2 is True:
            if not (
                extraction["density"] is not None
                and extraction["material_table"] == extraction["material_student"]
                and not extraction["material_ambiguous"]
            ):
                raise ValueError(f"{record['id']}: k2=True не согласован с extraction")
        if k3 is True:
            if not (
                extraction["dominant_calc"] is not None
                and extraction["dominant_stated"] == extraction["dominant_calc"]
            ):
                raise ValueError(f"{record['id']}: k3=True не согласован с extraction")

        expected = compute_verdict(
            k1,
            k2,
            k3,
            empty=record["quality"]["empty"],
            off_topic=record["quality"]["off_topic"],
        )
        if record["verdict"] != expected:
            raise ValueError(f"{record['id']}: verdict не согласован с критериями")


def write_outputs(records: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    source_counts = Counter(record["source"] for record in records)
    verdict_counts = Counter(record["verdict"] for record in records)
    criteria_counts = {
        key: Counter(str(record["criteria"][key]) for record in records)
        for key in ("k1", "k2", "k3")
    }

    manifest = {
        "dataset": "lab1_seed",
        "version": DATASET_VERSION,
        "created_at": DATASET_DATE,
        "lab_id": 1,
        "record_count": len(records),
        "source_counts": dict(sorted(source_counts.items())),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "criteria_counts": {key: dict(value) for key, value in criteria_counts.items()},
        "files": {
            "jsonl": OUT_JSONL.relative_to(ROOT).as_posix(),
            "guideline": "docs/annotation_guideline.md",
        },
        "notes": [
            "Seed-версия; синтетические тексты требуют экспертной проверки.",
            "Исходные тексты взяты из test.json и lab_num1.json.",
            "ФИО заменены на student_id; исходные файлы пока содержат ПД.",
            "Сплиты train/val/test будут добавлены отдельным шагом.",
        ],
    }
    OUT_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    records = collect_records()
    validate(records)
    write_outputs(records)

    verdicts = Counter(record["verdict"] for record in records)
    sources = Counter(record["source"] for record in records)
    print(f"Записано: {OUT_JSONL} ({len(records)} записей)")
    print(f"Манифест: {OUT_MANIFEST}")
    print(f"Источники: {dict(sources)}")
    print(f"Вердикты: {dict(verdicts)}")


if __name__ == "__main__":
    main()
