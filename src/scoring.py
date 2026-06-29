from __future__ import annotations

from dataclasses import dataclass

from config import RANK_MODE
from models import Match
from strategy import choose_best_ev, choose_best_probability


@dataclass(frozen=True)
class GroupScore:
    score: float
    probability: float
    ev: float
    group: tuple[Match, ...]


def score_group(group: tuple[Match, ...]) -> GroupScore:
    probability = combination_probability(group)
    ev = combination_ev(group)
    score = _rank_score(probability, ev)
    return GroupScore(score=score, probability=probability, ev=ev, group=group)


def combination_probability(group: tuple[Match, ...]) -> float:
    probability = 1.0
    for match in group:
        probability *= choose_best_probability(match)
    return probability


def combination_ev(group: tuple[Match, ...]) -> float:
    ev = 1.0
    for match in group:
        ev *= choose_best_ev(match)
    return ev


def _rank_score(probability: float, ev: float) -> float:
    if RANK_MODE == "probability":
        return probability
    if RANK_MODE == "ev":
        return ev
    raise ValueError(f"unsupported RANK_MODE: {RANK_MODE}")
