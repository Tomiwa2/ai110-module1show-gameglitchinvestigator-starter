import json
import os


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive guessing range for a difficulty level.

    Args:
        difficulty: The chosen difficulty label (e.g. ``"Easy"``).

    Returns:
        tuple[int, int]: The ``(low, high)`` bounds, both inclusive.

    Raises:
        NotImplementedError: This helper still needs to be refactored
            out of ``app.py`` into this module.
    """
    raise NotImplementedError(
        "Refactor this function from app.py into logic_utils.py"
    )


def parse_guess(raw: str):
    """Parse raw user input into an integer guess.

    Decimal strings are accepted and truncated toward zero (e.g.
    ``"3.99"`` becomes ``3``) because Streamlit hands input over as
    free-form text. Empty, ``None``, and non-numeric input are reported
    as errors rather than raising.

    Args:
        raw: The unprocessed text entered by the player.

    Returns:
        tuple[bool, int | None, str | None]: A triple of
        ``(ok, guess, error_message)``. On success ``ok`` is ``True``,
        ``guess`` is the parsed int, and ``error_message`` is ``None``.
        On failure ``ok`` is ``False``, ``guess`` is ``None``, and
        ``error_message`` explains what went wrong.
    """
    # FIX: Refactored parse_guess out of app.py into logic_utils.py so the
    # input handling can be unit-tested directly (app.py runs Streamlit on
    # import) — done with Claude Code in agent mode.
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """Compare a guess against the secret number.

    Falls back to a string comparison if the two values cannot be
    compared numerically, so a mistyped secret can never raise a
    ``TypeError`` to the caller.

    Args:
        guess: The player's parsed guess.
        secret: The number the player is trying to find.

    Returns:
        tuple[str, str]: An ``(outcome, message)`` pair where ``outcome``
        is one of ``"Win"``, ``"Too High"``, or ``"Too Low"`` and
        ``message`` is a player-facing hint.
    """
    # FIX: Refactored check_guess out of app.py into logic_utils.py and fixed
    # the reversed hint bug (Too High now says "Go LOWER", Too Low says
    # "Go HIGHER") — done with Claude Code in agent mode.
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        else:
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Compute the new score after a guess.

    Args:
        current_score: The player's score before this guess.
        outcome: The result of the guess, as returned by
            :func:`check_guess` (e.g. ``"Win"``).
        attempt_number: The 1-based index of the current attempt.

    Returns:
        int: The updated score.

    Raises:
        NotImplementedError: This helper still needs to be refactored
            out of ``app.py`` into this module.
    """
    raise NotImplementedError(
        "Refactor this function from app.py into logic_utils.py"
    )


# ---------------------------------------------------------------------------
# STRETCH FEATURE A: High Score tracker
#
# Persists the best score to a JSON file next to this module so it survives
# Streamlit reruns AND full app restarts. All disk access is defensive: a
# missing or corrupt file degrades to a zeroed default instead of crashing.
# ---------------------------------------------------------------------------

# Default location for the saved high score (alongside this module).
HIGH_SCORE_PATH = os.path.join(os.path.dirname(__file__), "high_score.json")

# Shape of an "empty" high score, used as a safe fallback everywhere.
_DEFAULT_HIGH_SCORE = {"score": 0, "difficulty": None, "attempts": None}


def load_high_score(path: str = HIGH_SCORE_PATH):
    """Load the saved high score from disk.

    All failure modes degrade gracefully: a missing, unreadable, or
    malformed file (and any payload that is not a dict with an integer
    ``score``) yields a fresh zeroed default rather than raising, so a
    bad file can never take the game down.

    Args:
        path: Path to the high-score JSON file. Defaults to
            :data:`HIGH_SCORE_PATH`.

    Returns:
        dict: A mapping with the keys ``score``, ``difficulty``, and
        ``attempts``. Unknown keys in the file are dropped and missing
        keys are backfilled from the default.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return dict(_DEFAULT_HIGH_SCORE)

    # Be defensive about shape — only trust a dict with an int score.
    if not isinstance(data, dict) or not isinstance(data.get("score"), int):
        return dict(_DEFAULT_HIGH_SCORE)

    merged = dict(_DEFAULT_HIGH_SCORE)
    for key in _DEFAULT_HIGH_SCORE:
        if key in data:
            merged[key] = data[key]
    return merged


def save_high_score(data: dict, path: str = HIGH_SCORE_PATH):
    """Write a high-score record to disk as JSON.

    Args:
        data: The high-score mapping to persist (typically with
            ``score``, ``difficulty``, and ``attempts`` keys).
        path: Destination path for the JSON file. Defaults to
            :data:`HIGH_SCORE_PATH`.

    Returns:
        None
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def update_high_score(score: int, difficulty, attempts,
                      path: str = HIGH_SCORE_PATH):
    """Persist ``score`` only if it beats the saved best.

    Args:
        score: The score just achieved by the player.
        difficulty: The difficulty the score was achieved on.
        attempts: The number of attempts the score took.
        path: Path to the high-score JSON file. Defaults to
            :data:`HIGH_SCORE_PATH`.

    Returns:
        tuple[bool, dict]: An ``(is_new_record, high_score_data)`` pair.
        On a new record the file is rewritten and the returned dict
        reflects the new best; otherwise the existing record is returned
        unchanged and ``is_new_record`` is ``False``.
    """
    current = load_high_score(path)
    if score > current["score"]:
        new_record = {
            "score": score,
            "difficulty": difficulty,
            "attempts": attempts,
        }
        save_high_score(new_record, path)
        return True, new_record
    return False, current


# ---------------------------------------------------------------------------
# STRETCH FEATURE B: Guess History proximity
#
# Turns each past guess into a "how close were you" signal so the Guess History
# sidebar can show the player narrowing in on the secret.
# ---------------------------------------------------------------------------

def proximity_ratio(guess, secret, low: int, high: int) -> float:
    """Measure how close a guess is to the secret as a ratio.

    The guess is clamped into ``[low, high]`` before measuring, so an
    out-of-range guess reads as "far" instead of producing a nonsensical
    negative ratio. Non-numeric input is treated as maximally far.

    Args:
        guess: The player's guess (coerced to ``int`` if possible).
        secret: The number being guessed (coerced to ``int``).
        low: The inclusive lower bound of the active range.
        high: The inclusive upper bound of the active range.

    Returns:
        float: Closeness in ``[0.0, 1.0]`` where ``1.0`` is an exact hit
        and ``0.0`` is as far as the range allows. A degenerate range
        (``high <= low``) returns ``1.0`` only on an exact match.
    """
    try:
        guess = int(guess)
        secret = int(secret)
    except (TypeError, ValueError):
        return 0.0

    span = high - low
    if span <= 0:
        return 1.0 if guess == secret else 0.0

    clamped = max(low, min(high, guess))
    distance = abs(clamped - secret)
    ratio = 1.0 - distance / span
    return max(0.0, min(1.0, ratio))


def proximity_bar(ratio: float, width: int = 10) -> str:
    """Render a closeness ratio as a fixed-width text bar.

    Args:
        ratio: A closeness value; clamped into ``[0.0, 1.0]``.
        width: Total number of cells in the bar. Coerced to at least 1.

    Returns:
        str: A bar of ``width`` characters such as ``"███████░░░"``,
        where filled cells (``█``) are proportional to ``ratio`` and the
        remainder are empty cells (``░``).
    """
    width = max(1, int(width))
    ratio = max(0.0, min(1.0, ratio))
    filled = int(round(ratio * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def proximity_label(ratio: float) -> str:
    """Map a closeness ratio to a short, human-friendly label.

    Args:
        ratio: A closeness value in ``[0.0, 1.0]``.

    Returns:
        str: A label describing the closeness, ranging from
        ``"🎯 spot on"`` for a near-exact hit down to ``"❄️ far"``.
    """
    if ratio >= 0.99:
        return "🎯 spot on"
    if ratio >= 0.85:
        return "🔥 very close"
    if ratio >= 0.6:
        return "warm"
    if ratio >= 0.3:
        return "cool"
    return "❄️ far"


# ---------------------------------------------------------------------------
# STRETCH FEATURE C: Hot/Cold state + session summary (UI enhancement)
#
# proximity_state turns a closeness ratio into a Hot/Cold readout (emoji +
# label + a Streamlit color name) so feedback can be color-coded. The colour
# is returned as data — logic_utils stays UI-framework-free, and app.py decides
# how to render it. build_session_summary shapes the raw guess log into table
# rows for an end-of-game recap.
# ---------------------------------------------------------------------------

def proximity_state(ratio: float) -> dict:
    """Classify a closeness ratio into a Hot/Cold state.

    This drives the color-coded "Hot/Cold" feedback: each band carries an
    emoji, a short label, and a Streamlit colour name (usable in markdown as
    ``:color[text]``). Bands line up with :func:`proximity_label`.

    Args:
        ratio: A closeness value; clamped into ``[0.0, 1.0]``.

    Returns:
        dict: ``{"emoji", "label", "color"}`` describing the state, from
        ``🎯 Bullseye`` (violet) down to ``🧊 Freezing`` (blue).
    """
    ratio = max(0.0, min(1.0, ratio))
    if ratio >= 0.99:
        return {"emoji": "🎯", "label": "Bullseye", "color": "violet"}
    if ratio >= 0.85:
        return {"emoji": "🔥", "label": "Hot", "color": "red"}
    if ratio >= 0.6:
        return {"emoji": "♨️", "label": "Warm", "color": "orange"}
    if ratio >= 0.3:
        return {"emoji": "💧", "label": "Cool", "color": "blue"}
    return {"emoji": "🧊", "label": "Freezing", "color": "blue"}


def build_session_summary(guess_log: list) -> list:
    """Shape the raw guess log into rows for an end-of-game summary table.

    Args:
        guess_log: The per-guess log, where each entry is a mapping with
            ``"guess"``, ``"outcome"`` and ``"ratio"`` keys (as appended in
            ``app.py``). A missing or empty log yields an empty list.

    Returns:
        list[dict]: One row per guess with display-ready columns:
        ``"#"`` (1-based attempt), ``"Guess"``, ``"Result"`` (outcome with an
        emoji), ``"Closeness"`` (percentage string) and ``"State"`` (the
        Hot/Cold label with emoji).
    """
    outcome_icon = {"Win": "🎉", "Too High": "📉", "Too Low": "📈"}
    rows = []
    for i, entry in enumerate(guess_log or [], start=1):
        ratio = entry.get("ratio", 0.0)
        state = proximity_state(ratio)
        outcome = entry.get("outcome", "")
        rows.append({
            "#": i,
            "Guess": entry.get("guess", ""),
            "Result": f"{outcome_icon.get(outcome, '•')} {outcome}",
            "Closeness": f"{round(ratio * 100)}%",
            "State": f"{state['emoji']} {state['label']}",
        })
    return rows
