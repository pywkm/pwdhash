import pytest

import pwdhash

DOMAINS_TO_CHECK = ("a.pl", "example.com", "example.gov.sg", "two-words42.cnt.br")
URI_FORMATS = {
    "already_clean_domain": "{}",
    "domain_with_protocol": "http://{}",
    "domain_with_secure_protocol": "https://{}",
    "domain_with_protocol_and_slash": "http://{}/",
    "domain_with_document": "http://{}/index.html",
    "domain_with_subdomain": "http://subdomain.{}/",
    "domain_with_path": "http://{}/path/to/site/",
    "domain_with_query_params": "http://{}/?age=20",
    "domain_with_path_query_params": "http://{}/path/?age=20",
}


@pytest.mark.parametrize("domain", DOMAINS_TO_CHECK)
@pytest.mark.parametrize("uri_format", URI_FORMATS.values(), ids=URI_FORMATS.keys())
def test_should_extract_domain_from(uri_format: str, domain: str) -> None:
    assert pwdhash.extract_domain(uri_format.format(domain)) == domain


@pytest.mark.parametrize(
    ("uri", "expected"),
    [
        # inputs the original pwdhash.js (and v0.2.0) got wrong
        pytest.param("HTTPS://example.com/x", "example.com", id="uppercase_scheme"),
        pytest.param("Example.com", "example.com", id="uppercase_host"),
        pytest.param("WWW.EXAMPLE.CO.UK", "example.co.uk", id="uppercase_suffix"),
        pytest.param("example.com:8080", "example.com", id="port"),
        pytest.param("http://example.com:8080/x", "example.com", id="url_with_port"),
        pytest.param("localhost:8080", "localhost", id="single_label_with_port"),
        pytest.param("www.example.com.", "example.com", id="trailing_dot"),
        pytest.param("user@mail.example.com", "example.com", id="userinfo"),
        pytest.param("http://user:pw@host.com", "host.com", id="userinfo_password"),
        pytest.param(
            "user:pw@shop.example.co.uk:443/a", "example.co.uk", id="userinfo_suffix"
        ),
        pytest.param("ftp://example.com", "example.com", id="other_scheme"),
        pytest.param("example.com?q=1", "example.com", id="query_without_path"),
        pytest.param("example.com#top", "example.com", id="fragment_without_path"),
        pytest.param("  example.com\n", "example.com", id="surrounding_whitespace"),
        # same as the original
        pytest.param("localhost", "localhost", id="single_label"),
        pytest.param("co.uk", "co.uk", id="bare_suffix"),
        pytest.param("Żółw.PL", "żółw.pl", id="unicode_host"),
        pytest.param("192.168.1.1", "1.1", id="ipv4_cut_like_original"),
        pytest.param("http://10.0.0.1:8080/", "0.1", id="ipv4_with_port"),
        pytest.param("http://[::1]:8080/", "[::1]", id="ipv6_with_port"),
        pytest.param("[2001:DB8::1]", "[2001:db8::1]", id="ipv6_uppercase"),
    ],
)
def test_should_normalize(uri: str, expected: str) -> None:
    assert pwdhash.extract_domain(uri) == expected


@pytest.mark.parametrize(
    "uri", ["", "   ", "/path", "http://", "http:///x", "http://:8080", ".", "[::1"]
)
def test_should_reject_uri_without_host(uri: str) -> None:
    with pytest.raises(ValueError, match="Cannot extract domain"):
        pwdhash.extract_domain(uri)
