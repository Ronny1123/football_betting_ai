from __future__ import annotations

import csv
from pathlib import Path

from config import RESULT_LABELS
from models import Match
from scoring import GroupScore
from strategy import choose_best_result, lock_reason


def save_recommendations(ranked_groups: list[GroupScore], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "rank",
                "score",
                "probability",
                "probability_pct",
                "ev",
                "picks",
                "details",
            ],
        )
        writer.writeheader()
        for rank, group_score in enumerate(ranked_groups, start=1):
            writer.writerow(
                {
                    "rank": rank,
                    "score": f"{group_score.score:.8f}",
                    "probability": f"{group_score.probability:.8f}",
                    "probability_pct": f"{group_score.probability:.4%}",
                    "ev": f"{group_score.ev:.8f}",
                    "picks": _format_picks(group_score.group),
                    "details": _format_details(group_score.group),
                }
            )


def _format_picks(group: tuple[Match, ...]) -> str:
    return "|".join(f"{match.match_id}:{choose_best_result(match)}" for match in group)


def _format_details(group: tuple[Match, ...]) -> str:
    return " | ".join(_format_match(match) for match in group)


def _format_match(match: Match) -> str:
    result = choose_best_result(match)
    reason = lock_reason(match)
    suffix = f",{reason}_lock" if reason else ""
    return (
        f"{match.match_id}.{match.home} vs {match.away}:"
        f"{result}({RESULT_LABELS[result]},p={match.probabilities[result]:.1%},"
        f"odds={match.odds[result]:.2f},ev={match.probabilities[result] * match.odds[result]:.3f}"
        f"{suffix})"
    )
