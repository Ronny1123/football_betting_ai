from __future__ import annotations

import csv
from pathlib import Path

from config import RESULT_LABELS
from models import Match


REQUIRED_COLUMNS = {
    "match_id",
    "home",
    "away",
    "p3",
    "p1",
    "p0",
    "odds3",
    "odds1",
    "odds0",
    "manual_lock",
    "manual_exclude",
}


def read_matches(csv_path: Path) -> list[Match]:
    matches: list[Match] = []
    with csv_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError(f"{csv_path} is empty")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{csv_path} missing required columns: {missing}")

        for row in reader:
            matches.append(_row_to_match(row))

    return matches


def _row_to_match(row: dict[str, str]) -> Match:
    match_id = int(row["match_id"])
    manual_lock = _parse_manual_lock(row.get("manual_lock"), match_id)

    probabilities = {
        "3": _parse_float(row["p3"], "p3", match_id),
        "1": _parse_float(row["p1"], "p1", match_id),
        "0": _parse_float(row["p0"], "p0", match_id),
    }
    probability_sum = sum(probabilities.values())
    if abs(probability_sum - 1.0) > 0.001:
        raise ValueError(
            f"match_id={match_id} probabilities must sum to 1.0, got {probability_sum:.4f}"
        )

    odds = {
        "3": _parse_positive_float(row["odds3"], "odds3", match_id),
        "1": _parse_positive_float(row["odds1"], "odds1", match_id),
        "0": _parse_positive_float(row["odds0"], "odds0", match_id),
    }

    return Match(
        match_id=match_id,
        home=row["home"].strip(),
        away=row["away"].strip(),
        probabilities=probabilities,
        odds=odds,
        manual_lock=manual_lock,
        manual_exclude=_parse_bool(row.get("manual_exclude")),
    )


def _parse_manual_lock(value: str | None, match_id: int) -> str | None:
    manual_lock = (value or "").strip()
    if manual_lock == "":
        return None
    if manual_lock not in RESULT_LABELS:
        raise ValueError(f"match_id={match_id} has invalid manual_lock: {manual_lock}")
    return manual_lock


def _parse_bool(value: str | None) -> bool:
    return (value or "0").strip().lower() in {"1", "true", "yes", "y"}


def _parse_float(value: str, column: str, match_id: int) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise ValueError(f"match_id={match_id} has invalid {column}: {value}") from error
    if parsed < 0:
        raise ValueError(f"match_id={match_id} {column} must be >= 0")
    return parsed


def _parse_positive_float(value: str, column: str, match_id: int) -> float:
    parsed = _parse_float(value, column, match_id)
    if parsed <= 0:
        raise ValueError(f"match_id={match_id} {column} must be > 0")
    return parsed
