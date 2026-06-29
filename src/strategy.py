from __future__ import annotations

from models import Match


def choose_best_result(match: Match) -> str:
    return match.best_result


def choose_best_probability(match: Match) -> float:
    return match.best_probability


def choose_best_odds(match: Match) -> float:
    return match.best_odds


def choose_best_ev(match: Match) -> float:
    return match.best_ev


def is_locked(match: Match) -> bool:
    return match.manual_lock is not None or match.auto_locked


def lock_reason(match: Match) -> str:
    if match.manual_lock is not None:
        return "manual"
    if match.auto_locked:
        return "auto"
    return ""
