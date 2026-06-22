# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Describe the game's purpose.**
  This is a Streamlit number-guessing game. The app picks a secret number within a range that depends on the chosen difficulty (Easy 1–20, Normal 1–100, Hard 1–50). The player types a guess and submits it; the game responds "Too High" or "Too Low" with a hint pointing in the right direction, tracks attempts and score, and ends the round on a correct guess or when attempts run out.

- [x] **Detail which bugs you found.**
  1. **Reversed hints** — guessing above the secret told the player to "Go HIGHER" and vice versa, sending them the wrong way.
  2. **Non-monotonic attempt limits** — the difficulty map (Easy 6, Normal 8, Hard 5) gave "Normal" more attempts than "Easy," so harder difficulties weren't actually harder.
  3. **Broken pre-existing tests** — the starter tests compared the `(outcome, message)` tuple returned by `check_guess` against a bare string, so they could never pass.
  4. **Off-by-one attempts** — "Attempts left" displayed one fewer than the allowed limit before any guess was made.
  5. **Out-of-range guesses failed silently** — entering a number outside the valid range produced no error or feedback.
  6. **Reset friction** — "New Game" (and winning) didn't cleanly restart the round without state confusion.

- [x] **Explain what fixes you applied.**
  - **Hint logic:** Refactored `check_guess` out of `app.py` into [`logic_utils.py`](logic_utils.py) and corrected the messages so "Too High" → "📉 Go LOWER!" and "Too Low" → "📈 Go HIGHER!". The fix also holds in the `TypeError` fallback branch (when the secret is passed as a string on even attempts).
  - **Attempt limits:** Corrected `attempt_limit_map` in `app.py` to Easy 10, Normal 7, Hard 4 so attempts strictly decrease as difficulty rises.
  - **Tests:** Repaired the pre-existing tests to unpack the returned tuple, and authored regression tests in [`tests/test_game_logic.py`](tests/test_game_logic.py) for both the hint-direction bug and the attempt-limit invariant. All 7 tests pass.

## 🎬 Demo Walkthrough

A step-by-step record of a sample game so anyone can follow the fixed behavior end-to-end without running it. Settings: **Normal** difficulty (range 1–100, 7 attempts allowed). For this run the secret number is **63**.

1. **Game loads.** The board shows "Attempts left: 7" and an empty guess input. The Developer Debug Info expander reveals the secret (63) for verification.
2. **User enters 40 → "Too Low".** Because 40 is below the secret, the game now correctly hints **📈 Go HIGHER!** (before the fix it pointed the wrong way). The guess is recorded in history and the score updates.
3. **User enters 70 → "Too High".** 70 is above 63, so the game hints **📉 Go LOWER!** — the hint direction matches the outcome, confirming the reversed-hint bug is repaired.
4. **User enters 60 → "Too Low".** Still below the secret, so the hint stays **📈 Go HIGHER!**, narrowing the range to 61–69. Attempts left ticks down and the score continues to update after each guess.
5. **User enters 63 → Win! 🎉** The game shows "Correct!", triggers balloons, and ends the round with a message like "You won! The secret was 63. Final score: 25". The game locks to the "won" state.
6. **User clicks "New Game 🔁".** The board resets with a fresh secret number and attempts, ready for another round — no browser refresh required.

## 🧪 Test Results

Phase 2 added an edge-case suite ([`tests/test_edge_cases.py`](tests/test_edge_cases.py)) probing
three input categories that could still break the game — **negative numbers**, **decimals**, and
**extremely large values** — plus a few non-numeric guards. All tests pass:

```
$ python -m pytest -v
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.13.0
collecting ... collected 20 items

tests/test_edge_cases.py::test_negative_number_is_parsed PASSED          [  5%]
tests/test_edge_cases.py::test_negative_guess_hints_higher_without_crashing PASSED [ 10%]
tests/test_edge_cases.py::test_large_negative_number_is_handled PASSED   [ 15%]
tests/test_edge_cases.py::test_decimal_is_truncated_to_int PASSED        [ 20%]
tests/test_edge_cases.py::test_negative_decimal_is_truncated_toward_zero PASSED [ 25%]
tests/test_edge_cases.py::test_malformed_decimal_fails_gracefully PASSED [ 30%]
tests/test_edge_cases.py::test_decimal_guess_flows_into_check_guess PASSED [ 35%]
tests/test_edge_cases.py::test_extremely_large_value_is_parsed PASSED    [ 40%]
tests/test_edge_cases.py::test_extremely_large_guess_hints_lower_without_crashing PASSED [ 45%]
tests/test_edge_cases.py::test_large_value_in_scientific_notation_via_decimal_path PASSED [ 50%]
tests/test_edge_cases.py::test_empty_input_is_rejected PASSED            [ 55%]
tests/test_edge_cases.py::test_none_input_is_rejected PASSED             [ 60%]
tests/test_edge_cases.py::test_alphabetic_input_is_rejected PASSED       [ 65%]
tests/test_game_logic.py::test_winning_guess PASSED                      [ 70%]
tests/test_game_logic.py::test_too_high_tells_player_to_go_lower PASSED  [ 75%]
tests/test_game_logic.py::test_too_low_tells_player_to_go_higher PASSED  [ 80%]
tests/test_game_logic.py::test_hint_direction_with_string_secret_too_high PASSED [ 85%]
tests/test_game_logic.py::test_hint_direction_with_string_secret_too_low PASSED [ 90%]
tests/test_game_logic.py::test_attempt_limits_fixed_values PASSED        [ 95%]
tests/test_game_logic.py::test_attempt_limits_decrease_with_difficulty PASSED [100%]

============================= 20 passed in 0.41s ==============================
```

## 🚀 Stretch Features

- [x] **Enhanced UI: color-coded Hot/Cold feedback + session summary table.**
  Built on the existing proximity helpers in [`logic_utils.py`](logic_utils.py), this
  adds structured, user-friendly output without touching the core guess/score logic.

  **What was added**

  - **`proximity_state(ratio)` in [`logic_utils.py`](logic_utils.py)** — a new helper that
    classifies a closeness ratio into a Hot/Cold band and returns it as data:
    `{"emoji", "label", "color"}`. The bands run 🎯 *Bullseye* (violet) → 🔥 *Hot* (red)
    → ♨️ *Warm* (orange) → 💧 *Cool* (blue) → 🧊 *Freezing* (blue). The colour is a
    Streamlit colour name so `logic_utils` stays UI-framework-free and `app.py` decides
    how to render it.
  - **`build_session_summary(guess_log)` in [`logic_utils.py`](logic_utils.py)** — shapes the
    raw per-guess log into display-ready table rows with columns
    `#`, `Guess`, `Result` (outcome + emoji), `Closeness` (a percentage), and
    `State` (Hot/Cold label + emoji). Returns an empty list for an empty log.

  **Where the UI changed in [`app.py`](app.py)**

  - **Color-coded Hot/Cold readout (submit handler).** After each non-winning guess,
    `app.py` now calls `proximity_state(ratio)` and renders a colored markdown line —
    e.g. `🔥 :red[Hot] · ███████░░░ 78% close` — combining the emoji, the
    color-coded label, the existing `proximity_bar`, and a percentage. Feedback turns
    red as you near the secret and blue when you're far.
  - **Session Summary table (bottom of page).** A new `📋 Session Summary` section calls
    `build_session_summary(st.session_state.guess_log)` and renders it with `st.table`,
    followed by three `st.metric` cards (total **Guesses**, current **Score**, and
    **Closest** approach). It appears once at least one guess has been made and gives the
    player a clean end-of-round scorecard.

  Core game logic (`check_guess`, `update_score`, state handling) was left untouched, and
  all 39 tests still pass.
