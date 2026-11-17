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


@pytest.mark.parametrize("uri", ["", "/path"])
def test_should_reject_uri_without_host(uri: str) -> None:
    with pytest.raises(ValueError, match="Cannot extract domain"):
        pwdhash.extract_domain(uri)
