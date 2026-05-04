import pytest
from buggy_library import GradeManager, load_from_csv


def test_add_and_average():
    gm = GradeManager()
    gm.add_student("Alice", [12, 14, 16])
    assert gm.get_average("Alice") == 14.0


def test_passing_status():
    gm = GradeManager()
    gm.add_student("Bob", [10, 10, 10])
    assert gm.get_status("Bob") == "Passed"


def test_failing_status():
    gm = GradeManager()
    gm.add_student("Charlie", [5, 6, 7])
    assert gm.get_status("Charlie") == "Failed"


def test_top_student():
    gm = GradeManager()
    gm.add_student("Alice", [12, 14])
    gm.add_student("Bob", [8, 9])
    assert gm.top_student() == "Alice"


def test_remove_existing_student():
    gm = GradeManager()
    gm.add_student("Alice", [12, 14])
    gm.remove_student("Alice")
    assert "Alice" not in gm.students


def test_remove_nonexistent_student():
    gm = GradeManager()
    # Should not raise KeyError
    try:
        gm.remove_student("Nobody")
        assert True
    except KeyError:
        assert False, "remove_student raised KeyError on missing student"


def test_average_empty_grades():
    gm = GradeManager()
    gm.add_student("Empty", [])
    # Should handle empty gracefully, not raise ZeroDivisionError
    try:
        avg = gm.get_average("Empty")
        assert avg == 0 or avg is None
    except ZeroDivisionError:
        assert False, "get_average raised ZeroDivisionError on empty grades"


def test_grade_distribution():
    gm = GradeManager()
    gm.add_student("Alice", [5, 12, 18])
    dist = gm.get_grade_distribution("Alice")
    assert dist["below_10"] == 1
    assert dist["10_to_15"] == 1
    assert dist["above_15"] == 1


def test_export_results(tmp_path):
    gm = GradeManager()
    gm.add_student("Alice", [12, 14])
    out = tmp_path / "results.json"
    gm.export_results(str(out))
    import json
    with open(str(out)) as f:
        data = json.load(f)
    assert "Alice" in data
    assert data["Alice"]["status"] == "Passed"
