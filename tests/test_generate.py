import pytest

import pwdhash

PASSWORD = "password12345"
DOMAIN = "example.com"
TEST_PARAMETERS = (
    pytest.param(
        PASSWORD,
        DOMAIN,
        "0JMBoaKI7NFhObN",
        id="default_password_example_domain",
    ),
    pytest.param(
        PASSWORD,
        "google.com",
        "YzvXOvv3tyZ0PIn",
        id="default_password_google_domain",
    ),
    pytest.param(
        PASSWORD,
        "facebook.com",
        "vYbDjKWA5RoWEWJ",
        id="default_password_facebook_domain",
    ),
    pytest.param(
        "",
        DOMAIN,
        "2MPb",
        id="empty_password",
    ),
    pytest.param(
        "123",
        DOMAIN,
        "7SXmR",
        id="short_password",
    ),
    pytest.param(
        "Zażółć gęślą jaźń",
        DOMAIN,
        "a3o9/S1NiAkwMr6BJzD",
        id="polish_unicode_password",
    ),
    pytest.param(
        "Příliš žluťoučký kůň úpěl ďábelské kódy",
        DOMAIN,
        "ti+BTLNFRbS7vnJ5uFOs2w",
        id="czech_unicode_password",
    ),
    pytest.param(
        "Árvíztűrő tükörfúrógép",
        DOMAIN,
        "jYNNgw1//znH8/aFIU19+g",
        id="hungarian_unicode_password",
    ),
    # outside the BMP (computed with the original pwdhash.js): the password is
    # hashed and its length counted in UTF-16 code units, as in JavaScript
    pytest.param("ab\U0001f600cd", DOMAIN, "EeSo5+zZ", id="emoji_password"),
    pytest.param("\U0001f600" * 3, DOMAIN, "N0+e0cXv", id="only_emoji_password"),
    pytest.param(
        "za\u017c\u00f3\u0142\u0107\U0001f600",
        DOMAIN,
        "iC4+JNpKRa",
        id="polish_and_emoji",
    ),
    pytest.param("\U0001f511\U0001f512", "github.com", "+c2UAj", id="two_emoji"),
    pytest.param(
        "x\U0001f600" * 12 + "!", DOMAIN, "c78ce0gsyf+nD0ReAJPTsQ", id="long_emoji"
    ),
    # pwdhash.js pads passwords of 24+ chars with NUL characters when the hash
    # runs out; they are stripped here (it gives "oXBHg4L654gaL0aU98knRw\0\0\0\0")
    pytest.param("!" * 24, DOMAIN, "oXBHg4L654gaL0aU98knRw", id="nul_padding_stripped"),
    pytest.param(
        pwdhash.PASSWORD_PREFIX + PASSWORD,
        DOMAIN,
        "0JMBoaKI7NFhObN",
        id="password_with_prefix",
    ),
    # check if generate() has extract_domain attached (to work as standalone)
    pytest.param(
        PASSWORD,
        f"http://{DOMAIN}",
        "0JMBoaKI7NFhObN",
        id="default_password_example_domain_with_protocol",
    ),
    pytest.param(
        PASSWORD,
        f"http://bogus.{DOMAIN}",
        "0JMBoaKI7NFhObN",
        id="default_password_example_domain_with_subdomain",
    ),
    pytest.param(
        PASSWORD,
        f"http://bogus.{DOMAIN}/path?test=test",
        "0JMBoaKI7NFhObN",
        id="default_password_example_domain_with_query_params",
    ),
)


@pytest.mark.parametrize(("password", "domain", "expected"), TEST_PARAMETERS)
def test_should_generate_hash_for(password: str, domain: str, expected: str) -> None:
    generated = pwdhash.generate(password, domain)
    assert generated == expected
