from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATCHES_CSV_PATH = PROJECT_ROOT / "data" / "matches.csv"
RECOMMENDATIONS_CSV_PATH = PROJECT_ROOT / "output" / "recommendations.csv"

TARGET_HITS = 9
TOP_N = 20

AUTO_LOCK_ENABLED = True
AUTO_LOCK_THRESHOLD = 0.90

# Supported values: "probability", "ev"
RANK_MODE = "probability"

RESULT_LABELS = {
    "3": "home_win",
    "1": "draw",
    "0": "away_win",
}
