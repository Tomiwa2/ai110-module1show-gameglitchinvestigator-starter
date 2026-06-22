# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude Code in agent mode to plan and implement two meaningful stretch
features end-to-end:

1. **High Score tracker** — persist the player's best score to a file so it
   survives both Streamlit reruns and full app restarts, show it in the
   sidebar, and celebrate a new record on the win screen.
2. **Guess History visualization** — a sidebar panel that shows each past guess
   with a proximity bar (`███████░░░`) and a "warm / very close / spot on"
   label, so the player can see themselves narrowing in on the secret.

I asked it to keep the testable logic in `logic_utils.py` (since `app.py` runs
Streamlit on import and can't be imported by pytest), to keep the existing
20-test suite green, and to add new pytest coverage for the new logic.

**What did the agent do?**

Files it modified or created:

| File | Change |
|------|--------|
| [`logic_utils.py`](logic_utils.py) | Added `load_high_score` / `save_high_score` / `update_high_score` (defensive JSON persistence) and `proximity_ratio` / `proximity_bar` / `proximity_label` for the history visualization. |
| [`app.py`](app.py) | Imported the new helpers; added a `guess_log` session-state entry; added the 🏆 High Score sidebar metric; logged each valid guess with its proximity; added the new-high-score celebration on win; rendered the Guess History sidebar; and made "New Game" fully reset state. |
| [`tests/test_high_score.py`](tests/test_high_score.py) | New suite (8 tests) using `tmp_path` so it never touches the real save file — covers missing/corrupt/wrong-shape files, save→load round-trip, new records, and the "ties and lower scores don't overwrite" rule. |
| [`tests/test_history.py`](tests/test_history.py) | New suite (11 tests) for proximity math, out-of-range clamping, non-numeric/string guesses, divide-by-zero on a degenerate range, and fixed-width bar rendering. |
| [`.gitignore`](.gitignore) | Ignored the runtime `high_score.json` so a local score isn't committed. |

It then ran `python -m pytest -v`, ending with **39 passing tests** (the
original 20 plus 19 new ones).

**What did you have to verify or fix manually?**

- **"New Game" didn't actually restart.** The agent flagged that the original
  `new_game` handler only reset `attempts` and `secret` — not `status`, `score`,
  or `history` — so after a win the game stayed locked in the "won" state and
  the high-score feature couldn't be demoed. I confirmed this against the code
  and approved the fix to reset all of that plus the new `guess_log`. (The
  high score itself is intentionally *not* reset — it lives on disk.)
- **Sidebar render order.** Streamlit runs top-to-bottom, so I checked that the
  Guess History panel renders *after* the submit handler appends the latest
  guess; otherwise a guess wouldn't appear until the next click. The agent
  placed that block at the bottom of the script for this reason — verified by
  tracing the rerun order.
- **No real file in tests.** I verified the high-score tests use `tmp_path`
  rather than the shared `high_score.json`, so running pytest doesn't clobber a
  real saved score.
- I re-ran `pytest` myself to confirm all 39 tests pass before accepting the work.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

**Prompt(s) used to generate the tests:**

```
In Phase 2 I wrote a basic test. Identify three potential "edge case" inputs
(e.g. negative numbers, decimals, or extremely large values) that might still
break my number-guessing game, and generate a suite of pytest cases that verify the game handles these inputs gracefully (parse_guess / check_guess should return a clean result and never raise an unhandled exception).
```

To make the input-handling logic unit-testable, I first asked the AI to finish
the refactor the README describes — moving `parse_guess` out of `app.py` (which
runs Streamlit on import) into `logic_utils.py` so the tests can import it
directly.

**Edge cases chosen and why (one line each):**

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Negative numbers | "...edge case inputs (e.g. negative numbers...) that might break my game..." | `test_negative_number_is_parsed`, `test_negative_guess_hints_higher_without_crashing`, `test_large_negative_number_is_handled` | ✅ | A player can type `-7`; it parses and must still hint a sane direction instead of crashing. |
| Decimals | "...decimals... handle these inputs gracefully..." | `test_decimal_is_truncated_to_int`, `test_negative_decimal_is_truncated_toward_zero`, `test_malformed_decimal_fails_gracefully`, `test_decimal_guess_flows_into_check_guess` | ✅ | Streamlit passes input as text, so `3.99` is plausible; it must truncate cleanly while malformed `1.2.3` fails gracefully. |
| Extremely large values | "...extremely large values... handle these inputs gracefully..." | `test_extremely_large_value_is_parsed`, `test_extremely_large_guess_hints_lower_without_crashing`, `test_large_value_in_scientific_notation_via_decimal_path` | ✅ | A 50-digit / 1e100 guess must not overflow or crash, and `1e9` (no dot) is rejected rather than mis-parsed. |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt(s) used:**

```
Add professional-grade docstrings to every function in logic_utils.py.
Then, review my code for PEP 8 style compliance and apply its suggestions
to resolve any formatting or naming issues it identifies.
In ai_interactions.md, include the prompt(s) I used, paste the linting
output (in a code block or committed .txt), and add a short note on what
formatting/naming changes the AI suggested and which was applied.
```

The AI used `flake8` (and cross-checked with `pycodestyle`) against PEP 8's
default 79-character line limit. Full captures are committed alongside this
file: [`lint_before.txt`](lint_before.txt) and [`lint_after.txt`](lint_after.txt).

**Linting output before:**

```
$ python -m flake8 logic_utils.py
logic_utils.py:4:1: E302 expected 2 blank lines, found 1
logic_utils.py:6:80: E501 line too long (87 > 79 characters)
logic_utils.py:15:80: E501 line too long (80 > 79 characters)
logic_utils.py:63:80: E501 line too long (87 > 79 characters)
logic_utils.py:110:80: E501 line too long (85 > 79 characters)
logic_utils.py:119:80: E501 line too long (85 > 79 characters)
```

**Linting output after:**

```
$ python -m flake8 logic_utils.py
(no output — exit code 0, clean)
```

**Changes the AI suggested and which were applied:**

| Code | Issue the AI flagged | Suggested fix | Applied? |
|------|----------------------|---------------|----------|
| `E302` | Only 1 blank line between the imports and `get_range_for_difficulty` | Add a second blank line after the imports (2 blank lines before a top-level def) | ✅ Applied |
| `E501` (lines 6 & 63) | The `raise NotImplementedError("...")` one-liners ran to 87 chars | Wrap the call across multiple lines | ✅ Applied |
| `E501` (line 15) | `parse_guess` comment ran 1 char over | Reflowed the comment block to fit 79 chars | ✅ Applied |
| `E501` (line 110) | `update_high_score` signature was 85 chars | Wrap the parameter list onto a second, aligned line | ✅ Applied |
| `E501` (line 119) | The inline `new_record = {...}` dict literal was 85 chars | Expand the dict literal onto multiple lines | ✅ Applied |

**Naming:** the AI confirmed no naming changes were needed — all functions are
already `snake_case`, the module constant `HIGH_SCORE_PATH` is `UPPER_CASE`, and
the internal `_DEFAULT_HIGH_SCORE` correctly uses a leading underscore, so all
identifiers already satisfy PEP 8.

All suggestions were applied. After the changes, `flake8` and `pycodestyle`
both report zero issues, and the full 39-test suite still passes (`pytest -q`).

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
