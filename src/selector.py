from __future__ import annotations

import itertools
from dataclasses import dataclass

from config import TARGET_HITS, TOP_N
from models import Match
from scoring import GroupScore, score_group
from strategy import is_locked


@dataclass(frozen=True)
class SelectionResult:
    loaded_count: int
    active_count: int
    excluded_count: int
    locked_count: int
    manual_locked_count: int
    auto_locked_count: int
    candidate_count: int
    need_from_candidates: int
    total_groups: int
    ranked_groups: list[GroupScore]


def rank_groups(matches: list[Match]) -> SelectionResult:
    excluded_matches = [match for match in matches if match.manual_exclude]
    active_matches = [match for match in matches if not match.manual_exclude]
    locked_matches = [match for match in active_matches if is_locked(match)]
    candidate_matches = [match for match in active_matches if not is_locked(match)]

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
        ranked_groups.append(score_group(group))

    ranked_groups.sort(key=lambda item: item.score, reverse=True)

    return SelectionResult(
        loaded_count=len(matches),
        active_count=len(active_matches),
        excluded_count=len(excluded_matches),
        locked_count=len(locked_matches),
        manual_locked_count=sum(1 for match in locked_matches if match.manual_lock is not None),
        auto_locked_count=sum(1 for match in locked_matches if match.auto_locked),
        candidate_count=len(candidate_matches),
        need_from_candidates=need_from_candidates,
        total_groups=len(ranked_groups),
        ranked_groups=ranked_groups[:TOP_N],
    )
