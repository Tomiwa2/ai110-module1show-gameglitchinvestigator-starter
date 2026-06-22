# Phase 2 — Edge-case test suite.
#
# Phase 2's basic tests covered the "happy path" (normal in-range guesses).
# These tests probe three categories of unusual input that could still break
# the game, and assert the game handles each GRACEFULLY — i.e. parse_guess and
# check_guess return a clean result and never raise an unhandled exception.
#
# Authored with Claude Code; see ai_interactions.md for the prompts used and the
# one-line rationale for each edge case.
from logic_utils import check_guess, parse_guess


# ---------------------------------------------------------------------------
# Edge case #1: Negative numbers
#
# A player can type "-7". int("-7") succeeds, so parse_guess should accept it,
# and check_guess must still give a sane direction hint instead of crashing.
# ---------------------------------------------------------------------------

def test_negative_number_is_parsed():
    ok, value, err = parse_guess("-7")
    assert ok is True
    assert value == -7
    assert err is None


def test_negative_guess_hints_higher_without_crashing():
    # -7 is below any positive secret, so the game should say "Too Low".
    outcome, message = check_guess(-7, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


def test_large_negative_number_is_handled():
    ok, value, err = parse_guess("-999999")
    assert ok is True
    assert value == -999999
    outcome, _ = check_guess(value, 50)
    assert outcome == "Too Low"


# ---------------------------------------------------------------------------
# Edge case #2: Decimals
#
# Streamlit hands every guess over as text, so "3.99" is a plausible entry.
# parse_guess truncates via int(float(...)); it must not raise, and malformed
# decimals like "1.2.3" must fail gracefully with an error message.
# ---------------------------------------------------------------------------

def test_decimal_is_truncated_to_int():
    ok, value, err = parse_guess("3.99")
    assert ok is True
    assert value == 3            # truncated, not rounded
    assert err is None


def test_negative_decimal_is_truncated_toward_zero():
    ok, value, err = parse_guess("-3.99")
    assert ok is True
    assert value == -3           # int(float("-3.99")) == -3
    assert err is None


def test_malformed_decimal_fails_gracefully():
    # "1.2.3" is not a valid number; the game should reject it, not crash.
    ok, value, err = parse_guess("1.2.3")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_decimal_guess_flows_into_check_guess():
    ok, value, _ = parse_guess("49.9")
    assert ok is True
    outcome, message = check_guess(value, 50)   # 49 vs 50
    assert outcome == "Too Low"
    assert "HIGHER" in message


# ---------------------------------------------------------------------------
# Edge case #3: Extremely large values
#
# Python ints are arbitrary-precision, so a value far beyond any game range
# must not overflow or crash. parse_guess should accept it and check_guess
# should report "Too High".
# ---------------------------------------------------------------------------

def test_extremely_large_value_is_parsed():
    big = "9" * 50  # a 50-digit number
    ok, value, err = parse_guess(big)
    assert ok is True
    assert value == int(big)
    assert err is None


def test_extremely_large_guess_hints_lower_without_crashing():
    huge = 10 ** 100
    outcome, message = check_guess(huge, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_large_value_in_scientific_notation_via_decimal_path():
    # "1e9" contains no ".", so int("1e9") raises and is rejected gracefully.
    ok, value, err = parse_guess("1e9")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


# ---------------------------------------------------------------------------
# Bonus: non-numeric / empty inputs should also be handled gracefully.
# ---------------------------------------------------------------------------

def test_empty_input_is_rejected():
    ok, value, err = parse_guess("")
    assert ok is False
    assert err == "Enter a guess."


def test_none_input_is_rejected():
    ok, value, err = parse_guess(None)
    assert ok is False
    assert err == "Enter a guess."


def test_alphabetic_input_is_rejected():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert err == "That is not a number."
