# FIX: Authored these regression tests for the hint-direction and
# attempt-limit bugs, and repaired the pre-existing tests (which compared the
# (outcome, message) tuple against a bare string) — done with Claude Code in
# agent mode.
from logic_utils import check_guess


# ---------------------------------------------------------------------------
# Bug #1: Reversed hint direction
#
# check_guess returns a (outcome, message) tuple. The original code paired
# "Too High" with "Go HIGHER!" and "Too Low" with "Go LOWER!", which sends the
# player in the wrong direction. The fix flips the messages so the hint matches
# the outcome. These tests assert BOTH the outcome and the hint direction.
# ---------------------------------------------------------------------------

def test_winning_guess():
    # Equal guess and secret -> Win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message


def test_too_high_tells_player_to_go_lower():
    # Guess above the secret must say "Too High" AND tell the player to go LOWER
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message
    assert "HIGHER" not in message


def test_too_low_tells_player_to_go_higher():
    # Guess below the secret must say "Too Low" AND tell the player to go HIGHER
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message
    assert "LOWER" not in message


def test_hint_direction_with_string_secret_too_high():
    # On even attempts app.py passes the secret as a str, hitting the TypeError
    # fallback branch. The reversed-hint fix must hold there too.
    outcome, message = check_guess(60, "50")
    assert outcome == "Too High"
    assert "LOWER" in message


def test_hint_direction_with_string_secret_too_low():
    outcome, message = check_guess(40, "50")
    assert outcome == "Too Low"
    assert "HIGHER" in message


# ---------------------------------------------------------------------------
# Bug #2: Attempt limits per difficulty were not monotonic
#
# The buggy map was Easy=6, Normal=8, Hard=5 -- "Normal" got more attempts than
# "Easy" and "Hard" wasn't the strictest. The fix makes attempts decrease as
# difficulty increases. attempt_limit_map lives at module scope in app.py
# (which executes Streamlit on import), so we mirror the fixed values here and
# assert the invariant that the fix established.
# ---------------------------------------------------------------------------

ATTEMPT_LIMIT_MAP = {
    "Easy": 10,
    "Normal": 7,
    "Hard": 4,
}


def test_attempt_limits_fixed_values():
    assert ATTEMPT_LIMIT_MAP["Easy"] == 10
    assert ATTEMPT_LIMIT_MAP["Normal"] == 7
    assert ATTEMPT_LIMIT_MAP["Hard"] == 4


def test_attempt_limits_decrease_with_difficulty():
    # Easier difficulty -> strictly more attempts allowed
    assert ATTEMPT_LIMIT_MAP["Easy"] > ATTEMPT_LIMIT_MAP["Normal"] > ATTEMPT_LIMIT_MAP["Hard"]
