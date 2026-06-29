from __future__ import annotations

from dataclasses import dataclass

from config import AUTO_LOCK_ENABLED, AUTO_LOCK_THRESHOLD


@dataclass(frozen=True)
class Match:
    match_id: int
    home: str
    away: str
    probabilities: dict[str, float]
    odds: dict[str, float]
    manual_lock: str | None
    manual_exclude: bool

    @property
    def raw_best_result(self) -> str:
        return max(self.probabilities, key=self.probabilities.get)

    @property
    def raw_best_probability(self) -> float:
        return self.probabilities[self.raw_best_result]

    @property
    def best_result(self) -> str:
        if self.manual_lock is not None:
            return self.manual_lock
        return self.raw_best_result

    @property
    def best_probability(self) -> float:
        return self.probabilities[self.best_result]

    @property
    def best_odds(self) -> float:
        return self.odds[self.best_result]

    @property
    def best_ev(self) -> float:
        return self.best_probability * self.best_odds

    @property
    def auto_locked(self) -> bool:
        if not AUTO_LOCK_ENABLED or self.manual_lock is not None:
            return False
        return self.raw_best_probability >= AUTO_LOCK_THRESHOLD
