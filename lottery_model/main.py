from __future__ import annotations

import csv
import itertools
from dataclasses import dataclass
from pathlib import Path


TARGET_HITS = 9
TOP_N = 20
RESULT_LABELS = {
    "3": "主胜",
    "1": "平",
    "0": "主负",
}


@dataclass(frozen=True)
class Match:
    match_id: int
    home: str
    away: str
    probabilities: dict[str, float]
    manual_lock: str | None
    manual_exclude: bool

    @property
    def best_result(self) -> str:
        if self.manual_lock is not None:
            return self.manual_lock
        return max(self.probabilities, key=self.probabilities.get)

    @property
    def best_probability(self) -> float:
        return self.probabilities[self.best_result]


def read_matches(csv_path: Path) -> list[Match]:
    matches: list[Match] = []
    with csv_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            manual_lock = (row.get("manual_lock") or "").strip()
            if manual_lock == "":
                manual_lock = None
            if manual_lock is not None and manual_lock not in RESULT_LABELS:
                raise ValueError(f"match_id={row['match_id']} has invalid manual_lock: {manual_lock}")

            probabilities = {
                "3": float(row["p3"]),
                "1": float(row["p1"]),
                "0": float(row["p0"]),
            }
            probability_sum = sum(probabilities.values())
            if abs(probability_sum - 1.0) > 0.001:
                raise ValueError(
                    f"match_id={row['match_id']} probabilities must sum to 1.0, got {probability_sum:.4f}"
                )

            matches.append(
                Match(
                    match_id=int(row["match_id"]),
                    home=row["home"].strip(),
                    away=row["away"].strip(),
                    probabilities=probabilities,
                    manual_lock=manual_lock,
                    manual_exclude=(row.get("manual_exclude") or "0").strip() == "1",
                )
            )
    return matches


def combination_probability(matches: tuple[Match, ...]) -> float:
    probability = 1.0
    for match in matches:
        probability *= match.best_probability
    return probability


def format_match(match: Match) -> str:
    result = match.best_result
    lock_mark = "*" if match.manual_lock is not None else ""
    return (
        f"{match.match_id}.{match.home} vs {match.away}:"
        f"{result}({RESULT_LABELS[result]}, {match.best_probability:.1%}){lock_mark}"
    )


def main() -> None:
    csv_path = Path(__file__).parent / "data" / "matches.csv"
    matches = read_matches(csv_path)

    excluded_matches = [match for match in matches if match.manual_exclude]
    active_matches = [match for match in matches if not match.manual_exclude]
    locked_matches = [match for match in active_matches if match.manual_lock is not None]
    candidate_matches = [match for match in active_matches if match.manual_lock is None]

    need_from_candidates = TARGET_HITS - len(locked_matches)
    if need_from_candidates < 0:
        raise ValueError(f"locked matches exceed target hits: {len(locked_matches)} > {TARGET_HITS}")
    if need_from_candidates > len(candidate_matches):
        raise ValueError(
            f"not enough candidate matches: need {need_from_candidates}, got {len(candidate_matches)}"
        )

    ranked_groups = []
    for combo in itertools.combinations(candidate_matches, need_from_candidates):
        group = tuple(locked_matches) + combo
        ranked_groups.append((combination_probability(group), group))

    ranked_groups.sort(key=lambda item: item[0], reverse=True)

    print(f"Loaded matches: {len(matches)}")
    print(f"Active matches: {len(active_matches)}")
    print(f"Excluded matches: {len(excluded_matches)}")
    print(f"Locked matches: {len(locked_matches)}")
    print(f"Mode: {len(candidate_matches)} choose {need_from_candidates}")
    print(f"Total groups: {len(ranked_groups)}")
    print()
    print(f"Top {min(TOP_N, len(ranked_groups))} groups by hit probability")

    for rank, (probability, group) in enumerate(ranked_groups[:TOP_N], start=1):
        picks = " | ".join(format_match(match) for match in group)
        print(f"{rank:02d}. probability={probability:.6%} | {picks}")


if __name__ == "__main__":
    main()
