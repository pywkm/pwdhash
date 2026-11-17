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
def test_should_generate_hash_for(password, domain, expected):
    generated = pwdhash.generate(password, domain)
    assert generated == expected
