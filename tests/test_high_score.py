# Stretch feature A — High Score tracker tests.
#
# These exercise the persisted high-score logic in logic_utils.py. Every test
# uses pytest's tmp_path fixture so we read/write a throwaway file and never
# touch the real high_score.json. The key behaviors:
#   - a missing or corrupt file degrades to a zeroed default (never crashes)
#   - a better score is saved and reported as a new record
#   - an equal or worse score leaves the saved best untouched
#
# Authored with Claude Code; see ai_interactions.md for the prompt used.
import json

from logic_utils import (
    load_high_score,
    save_high_score,
    update_high_score,
)


def test_load_missing_file_returns_default(tmp_path):
    path = str(tmp_path / "nope.json")
    data = load_high_score(path)
    assert data == {"score": 0, "difficulty": None, "attempts": None}


def test_load_corrupt_file_returns_default(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("this is not json {{{", encoding="utf-8")
    data = load_high_score(str(path))
    assert data["score"] == 0  # degrades gracefully, no exception


def test_load_wrong_shape_returns_default(tmp_path):
    # Valid JSON but not the expected dict-with-int-score shape.
    path = tmp_path / "shape.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    assert load_high_score(str(path))["score"] == 0


def test_save_then_load_roundtrip(tmp_path):
    path = str(tmp_path / "hs.json")
    record = {"score": 80, "difficulty": "Hard", "attempts": 2}
    save_high_score(record, path)
    assert load_high_score(path) == record


def test_update_sets_first_record(tmp_path):
    path = str(tmp_path / "hs.json")
    is_record, record = update_high_score(50, "Normal", 3, path)
    assert is_record is True
    assert record["score"] == 50
    assert record["difficulty"] == "Normal"
    assert record["attempts"] == 3
    # And it was actually written to disk.
    assert load_high_score(path)["score"] == 50


def test_update_beats_previous(tmp_path):
    path = str(tmp_path / "hs.json")
    update_high_score(40, "Easy", 5, path)
    is_record, record = update_high_score(75, "Hard", 1, path)
    assert is_record is True
    assert record["score"] == 75
    assert load_high_score(path)["score"] == 75


def test_update_does_not_overwrite_lower(tmp_path):
    path = str(tmp_path / "hs.json")
    update_high_score(90, "Normal", 2, path)
    is_record, record = update_high_score(30, "Easy", 6, path)
    assert is_record is False
    assert record["score"] == 90          # unchanged record returned
    assert load_high_score(path)["score"] == 90


def test_update_equal_score_is_not_a_new_record(tmp_path):
    # A tie should not count as a new record (strictly-greater wins only).
    path = str(tmp_path / "hs.json")
    update_high_score(60, "Normal", 3, path)
    is_record, record = update_high_score(60, "Normal", 4, path)
    assert is_record is False
    assert record["attempts"] == 3        # original record preserved
