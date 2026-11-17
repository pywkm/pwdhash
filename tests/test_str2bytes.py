import pytest

import pwdhash

TEST_PARAMETERS = (
    pytest.param(
        "some simple ascii",
        b"some simple ascii",
        id="ascii_string",
    ),
    pytest.param(
        "Zażółć gęślą jaźń",
        b"Za|\xf3B\x07 g\x19[l\x05 jazD",
        id="polish_unicode_string",
    ),
    pytest.param(
        "Příliš žluťoučký kůň úpěl ďábelské",
        b"PY\xedlia ~lueou\rk\xfd koH \xfap\x1bl \x0f\xe1belsk\xe9",
        id="czech_unicode_string",
    ),
    pytest.param(
        "Árvíztűrő tükörfúrógép",
        b"\xc1rv\xedztqrQ t\xfck\xf6rf\xfar\xf3g\xe9p",
        id="hungarian_unicode_string",
    ),
)


@pytest.mark.parametrize(("string_to_encode", "expected_bytes"), TEST_PARAMETERS)
def test_should_encode(string_to_encode, expected_bytes):
    assert pwdhash.str2bytes(string_to_encode) == expected_bytes
