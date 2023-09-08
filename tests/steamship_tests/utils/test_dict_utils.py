from steamship.utils.dict_utils import remove_none


def test_remove_none():
    d = {"a": 2, "b": "hi", "c": None}
    assert len(d.keys()) == 3
    d2 = remove_none(d)
    assert len(d2.keys()) == 2
    assert "c" not in d2
    assert "c" in d
    assert "a" in d2
    assert "b" in d2
