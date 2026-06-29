from __future__ import annotations

from config import MATCHES_CSV_PATH, RANK_MODE, RECOMMENDATIONS_CSV_PATH, TOP_N
from data_loader import read_matches
from output_writer import save_recommendations
from selector import rank_groups


def main() -> None:
    matches = read_matches(MATCHES_CSV_PATH)
    selection = rank_groups(matches)
    save_recommendations(selection.ranked_groups, RECOMMENDATIONS_CSV_PATH)

    print(f"Loaded matches: {selection.loaded_count}")
    print(f"Active matches: {selection.active_count}")
    print(f"Excluded matches: {selection.excluded_count}")
    print(
        "Locked matches: "
        f"{selection.locked_count} "
        f"(manual={selection.manual_locked_count}, auto={selection.auto_locked_count})"
    )
    print(f"Mode: {selection.candidate_count} choose {selection.need_from_candidates}")
    print(f"Total groups: {selection.total_groups}")
    print(f"Rank mode: {RANK_MODE}")
    print(f"Saved: {RECOMMENDATIONS_CSV_PATH}")
    print()
    print(f"Top {min(TOP_N, len(selection.ranked_groups))} groups")

    for rank, group_score in enumerate(selection.ranked_groups, start=1):
        picks = " | ".join(
            f"{match.match_id}:{match.best_result}"
            f"(p={match.best_probability:.1%},odds={match.best_odds:.2f},ev={match.best_ev:.3f})"
            for match in group_score.group
        )
        print(
            f"{rank:02d}. score={group_score.score:.6f} "
            f"probability={group_score.probability:.6%} "
            f"ev={group_score.ev:.6f} | {picks}"
        )


if __name__ == "__main__":
    main()
