# Stretch feature B — Guess History proximity tests.
#
# These verify the "how close was the guess" logic that powers the Guess
# History sidebar: proximity_ratio (a [0,1] closeness score), proximity_bar
# (its text-bar rendering) and proximity_label (the human label). The emphasis
# is on never crashing and never producing an out-of-bounds value, even for
# out-of-range or non-numeric guesses.
#
# Authored with Claude Code; see ai_interactions.md for the prompt used.
from logic_utils import proximity_ratio, proximity_bar, proximity_label


# --- proximity_ratio ---------------------------------------------------------

def test_exact_hit_is_one():
    assert proximity_ratio(50, 50, 1, 100) == 1.0


def test_far_end_of_range_is_near_zero():
    # Guessing 100 when the secret is 1 is as far as the range allows.
    assert proximity_ratio(100, 1, 1, 100) == 0.0


def test_closer_guess_scores_higher():
    near = proximity_ratio(60, 63, 1, 100)
    far = proximity_ratio(20, 63, 1, 100)
    assert near > far
    assert 0.0 <= far <= near <= 1.0


def test_out_of_range_guess_is_clamped_not_negative():
    # 9999 is way past the range; ratio must stay within [0, 1].
    ratio = proximity_ratio(9999, 50, 1, 100)
    assert 0.0 <= ratio <= 1.0


def test_string_guess_is_handled():
    # check_guess passes the secret as a str on even attempts; the proximity
    # helper accepts numeric strings without raising.
    assert proximity_ratio("50", "50", 1, 100) == 1.0


def test_non_numeric_guess_returns_zero():
    assert proximity_ratio("abc", 50, 1, 100) == 0.0


def test_degenerate_range_does_not_divide_by_zero():
    # low == high would be a zero-width span; must not raise ZeroDivisionError.
    assert proximity_ratio(5, 5, 5, 5) == 1.0
    assert proximity_ratio(4, 5, 5, 5) == 0.0


# --- proximity_bar -----------------------------------------------------------

def test_bar_is_fixed_width():
    assert len(proximity_bar(0.0, width=10)) == 10
    assert len(proximity_bar(0.5, width=10)) == 10
    assert len(proximity_bar(1.0, width=10)) == 10


def test_bar_full_and_empty():
    assert proximity_bar(1.0, width=8) == "█" * 8
    assert proximity_bar(0.0, width=8) == "░" * 8


def test_bar_clamps_out_of_bounds_ratio():
    # Ratios outside [0,1] should still render a clean fixed-width bar.
    assert proximity_bar(5.0, width=6) == "█" * 6
    assert proximity_bar(-2.0, width=6) == "░" * 6


# --- proximity_label ---------------------------------------------------------

def test_label_buckets():
    assert "spot on" in proximity_label(1.0)
    assert "very close" in proximity_label(0.9)
    assert proximity_label(0.7) == "warm"
    assert proximity_label(0.4) == "cool"
    assert "far" in proximity_label(0.1)
