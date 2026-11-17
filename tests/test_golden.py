"""Golden vectors frozen from pwdhash.py v0.2.0.

These outputs must never change: users rely on getting the same passwords
as with previous releases and the original pwdhash.js. Do not edit them to
make a failing test pass.
"""

import pytest

import pwdhash

GOLDEN_VECTORS = [
    # short passwords (< 4 characters)
    ("", "example.com", "2MPb"),
    ("a", "example.com", "9FBo"),
    ("abc", "example.com", "LODk9"),
    ("abcd", "example.com", "GnrVD9"),
    # "@@" prefix is stripped
    ("password", "example.com", "4QAIn8SvaW"),
    ("@@password", "example.com", "4QAIn8SvaW"),
    ("@@", "example.com", "2MPb"),
    # non-alphanumeric characters
    ("p@ss w0rd!", "example.com", "KFwBwqsS5+oM"),
    ("~!#$%^&*()", "example.com", "aYKAS1HOK+iA"),
    ("under_score_1", "example.com", "Sa4LKXIowwysN7Q"),
    # non-ASCII (Polish) characters
    ("Zażółć gęślą jaźń", "example.com", "a3o9/S1NiAkwMr6BJzD"),
    ("łódź", "wikipedia.org", "+Q8Mu9"),
    # domains with a suffix from the built-in list
    ("hunter2", "example.co.uk", "KhuVaBms0"),
    ("hunter2", "shop.example.com.pl", "JxU0fsiBT"),
    ("hunter2", "https://login.example.gov.sg/path?q=1", "KB3bFjoJ0"),
    # domains outside the list
    ("hunter2", "github.com", "n1fGXufpJ"),
    ("hunter2", "http://www.amazon.de/", "DFE96iVTx"),
    ("hunter2", "localhost", "t1AH3J2zp"),
    # passwords longer than the hash
    (
        "CorrectHorseBatteryStaple",
        "news.ycombinator.com",
        "FR2VXGvmPl1KdKT74lFAIwAAAA",
    ),
    ("a" * 40, "example.org", "eJBJ9InowRb0F844A3NlvAAAAA"),
]


@pytest.mark.parametrize(("password", "uri", "expected"), GOLDEN_VECTORS)
def test_generate_matches_golden_vector(password, uri, expected):
    assert pwdhash.generate(password, uri) == expected
