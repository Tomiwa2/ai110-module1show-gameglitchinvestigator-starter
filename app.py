import random
import streamlit as st

#Done
# FIX: Moved check_guess and parse_guess into logic_utils.py and imported them
# here, instead of defining them inline — refactor done with Claude Code in
# agent mode.
from logic_utils import (
    check_guess,
    parse_guess,
    load_high_score,
    update_high_score,
    proximity_ratio,
    proximity_bar,
    proximity_label,
    proximity_state,
    build_session_summary,
)

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

# FIX: Corrected attempt limits so they decrease as difficulty rises
# (was Easy=6, Normal=8, Hard=5 — non-monotonic) — diagnosed and fixed
# with Claude Code in agent mode.
attempt_limit_map = {
    "Easy": 10,    # most attempts — easiest
    "Normal": 7,   # standard
    "Hard": 4,     # fewest attempts — hardest
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# --- Stretch feature A: High Score (persisted to disk) ---
st.sidebar.divider()
record = load_high_score()
if record["score"] > 0:
    detail = ""
    if record.get("difficulty"):
        detail = f" · {record['difficulty']}"
        if record.get("attempts") is not None:
            detail += f", {record['attempts']} attempt(s)"
    st.sidebar.metric("🏆 High Score", record["score"], help="Your best score, saved between sessions.")
    if detail:
        st.sidebar.caption(f"Set on{detail}")
else:
    st.sidebar.metric("🏆 High Score", "—", help="Win a game to set your first high score!")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# Structured per-guess log powering the Guess History visualization. Each entry
# is {"guess", "outcome", "ratio"} for a valid numeric guess.
if "guess_log" not in st.session_state:
    st.session_state.guess_log = []

st.subheader("Make a guess")

st.info(
    f"Guess a number between 1 and 100. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # Full reset so a finished round (won or lost) can actually replay without
    # a browser refresh. The high score is intentionally NOT cleared — it lives
    # on disk and should survive across games.
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.score = 0
    st.session_state.history = []
    st.session_state.guess_log = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        if st.session_state.attempts % 2 == 0:
            secret = str(st.session_state.secret)
        else:
            secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        # Record this guess for the Guess History visualization. proximity_ratio
        # always uses the real (int) secret and the current difficulty range.
        ratio = proximity_ratio(guess_int, st.session_state.secret, low, high)
        st.session_state.guess_log.append({
            "guess": guess_int,
            "outcome": outcome,
            "ratio": ratio,
        })

        if show_hint:
            st.warning(message)

        # UI enhancement: color-coded Hot/Cold readout for the latest guess.
        # proximity_state maps closeness to an emoji + Streamlit colour so the
        # feedback turns red when you're hot and blue when you're cold.
        if outcome != "Win":
            state = proximity_state(ratio)
            st.markdown(
                f"### {state['emoji']} "
                f":{state['color']}[{state['label']}] "
                f"· `{proximity_bar(ratio)}` {round(ratio * 100)}% close"
            )

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )

            # Stretch feature A: persist the score if it's a new personal best.
            is_record, record = update_high_score(
                score=st.session_state.score,
                difficulty=difficulty,
                attempts=st.session_state.attempts,
            )
            if is_record:
                st.success(f"🏆 NEW HIGH SCORE: {record['score']}!")
            else:
                st.info(f"🏆 High score to beat: {record['score']}")
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# --- Stretch feature B: Guess History visualization (sidebar) ---
# Placed at the bottom so it renders AFTER the submit handler has appended the
# latest guess — Streamlit sidebar calls land in the sidebar regardless of where
# they appear in the script.
st.sidebar.divider()
st.sidebar.header("Guess History")
if not st.session_state.guess_log:
    st.sidebar.caption("No guesses yet. Each guess shows how close you got.")
else:
    icon = {"Win": "🎉", "Too High": "📉", "Too Low": "📈"}
    # Most recent guess first.
    for i, entry in enumerate(reversed(st.session_state.guess_log), start=1):
        bar = proximity_bar(entry["ratio"])
        label = proximity_label(entry["ratio"])
        mark = icon.get(entry["outcome"], "•")
        st.sidebar.markdown(
            f"`{bar}` {mark} **{entry['guess']}** — {label}"
        )

# --- UI enhancement: Session Summary table ---
# A structured recap of the whole session rendered from build_session_summary.
# Shown once at least one guess exists, and always once the round ends so the
# player gets a clean scorecard of their run.
if st.session_state.guess_log:
    st.divider()
    st.subheader("📋 Session Summary")
    summary_rows = build_session_summary(st.session_state.guess_log)
    st.table(summary_rows)

    total = len(summary_rows)
    best_ratio = max(e["ratio"] for e in st.session_state.guess_log)
    best = proximity_state(best_ratio)
    c1, c2, c3 = st.columns(3)
    c1.metric("Guesses", total)
    c2.metric("Score", st.session_state.score)
    c3.metric("Closest", f"{best['emoji']} {round(best_ratio * 100)}%")

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
