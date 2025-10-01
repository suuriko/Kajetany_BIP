#!/usr/bin/env python3
"""
Unit tests for url_manipulation module.

Tests URL parsing and reconstruction functionality used for
manipulating query parameters in web scraping operations.
"""

from urllib.parse import ParseResult

from src.crawler.url_manipulation import parse_url_components, reconstruct_url


class TestUrlManipulation:
    """Test URL parsing and reconstruction functions."""

    def test_parse_url_components_simple_url(self):
        """Test parsing a simple URL without query parameters."""
        url = "https://example.com/path"
        parsed_url, query_params = parse_url_components(url)

        assert isinstance(parsed_url, ParseResult)
        assert parsed_url.scheme == "https"
        assert parsed_url.netloc == "example.com"
        assert parsed_url.path == "/path"
        assert query_params == {}

    def test_parse_url_components_with_query_params(self):
        """Test parsing URL with query parameters."""
        url = "https://example.com/search?q=test&page=2&category=news"
        parsed_url, query_params = parse_url_components(url)

        assert parsed_url.scheme == "https"
        assert parsed_url.netloc == "example.com"
        assert parsed_url.path == "/search"
        assert query_params == {"q": ["test"], "page": ["2"], "category": ["news"]}

    def test_parse_url_components_with_multiple_values(self):
        """Test parsing URL with multiple values for same parameter."""
        url = "https://example.com/search?tag=python&tag=web&tag=scraping"
        parsed_url, query_params = parse_url_components(url)

        assert query_params == {"tag": ["python", "web", "scraping"]}

    def test_parse_url_components_with_fragment(self):
        """Test parsing URL with fragment."""
        url = "https://example.com/page#section1"
        parsed_url, query_params = parse_url_components(url)

        assert parsed_url.fragment == "section1"
        assert query_params == {}

    def test_parse_url_components_with_port(self):
        """Test parsing URL with port number."""
        url = "https://example.com:8080/api/data"
        parsed_url, query_params = parse_url_components(url)

        assert parsed_url.netloc == "example.com:8080"
        assert parsed_url.path == "/api/data"

    def test_parse_url_components_with_empty_query_values(self):
        """Test parsing URL with empty query parameter values."""
        url = "https://example.com/search?q=test&empty=&normal=value"
        parsed_url, query_params = parse_url_components(url)

        # parse_qs by default ignores empty values (keep_blank_values=False by default)
        assert query_params == {
            "q": ["test"],
            "normal": ["value"],
            # 'empty' parameter is omitted because its value is empty
        }

    def test_reconstruct_url_simple(self):
        """Test reconstructing a simple URL without parameters."""
        url = "https://example.com/path"
        parsed_url, query_params = parse_url_components(url)
        reconstructed = reconstruct_url(parsed_url, query_params)

        assert reconstructed == url

    def test_reconstruct_url_with_query_params(self):
        """Test reconstructing URL with query parameters."""
        original_url = "https://example.com/search?q=test&page=2"
        parsed_url, query_params = parse_url_components(original_url)
        reconstructed = reconstruct_url(parsed_url, query_params)

        # Note: order might change, so we check components
        reconstructed_parsed, reconstructed_params = parse_url_components(reconstructed)
        assert reconstructed_parsed.scheme == "https"
        assert reconstructed_parsed.netloc == "example.com"
        assert reconstructed_parsed.path == "/search"
        assert reconstructed_params == query_params

    def test_reconstruct_url_with_multiple_values(self):
        """Test reconstructing URL with multiple values for same parameter."""
        url = "https://example.com/search?tag=python&tag=web"
        parsed_url, query_params = parse_url_components(url)
        reconstructed = reconstruct_url(parsed_url, query_params)

        # Verify the reconstruction preserves multiple values
        _, reconstructed_params = parse_url_components(reconstructed)
        assert reconstructed_params["tag"] == ["python", "web"]

    def test_reconstruct_url_with_modified_params(self):
        """Test reconstructing URL with modified query parameters."""
        url = "https://example.com/search?q=test&page=1"
        parsed_url, query_params = parse_url_components(url)

        # Modify parameters
        query_params["page"] = ["2"]
        query_params["sort"] = ["date"]

        reconstructed = reconstruct_url(parsed_url, query_params)

        # Verify modifications are applied
        _, reconstructed_params = parse_url_components(reconstructed)
        assert reconstructed_params["q"] == ["test"]
        assert reconstructed_params["page"] == ["2"]
        assert reconstructed_params["sort"] == ["date"]

    def test_reconstruct_url_with_fragment(self):
        """Test reconstructing URL with fragment."""
        url = "https://example.com/page?param=value#section1"
        parsed_url, query_params = parse_url_components(url)
        reconstructed = reconstruct_url(parsed_url, query_params)

        assert reconstructed.endswith("#section1")
        assert "param=value" in reconstructed

    def test_reconstruct_url_with_empty_params(self):
        """Test reconstructing URL with empty parameter dictionary."""
        url = "https://example.com/path"
        parsed_url, _ = parse_url_components(url)
        reconstructed = reconstruct_url(parsed_url, {})

        assert reconstructed == url

    def test_round_trip_consistency(self):
        """Test that parse -> reconstruct is consistent for various URLs."""
        test_urls = [
            "https://example.com",
            "https://example.com/path",
            "https://example.com/path?param=value",
            "https://example.com:8080/api?key=123&format=json",
            "http://test.com/search?q=python&sort=date&order=desc#results",
            "https://site.com/page?empty=&multi=1&multi=2&multi=3",
        ]

        for url in test_urls:
            parsed_url, query_params = parse_url_components(url)
            reconstructed = reconstruct_url(parsed_url, query_params)

            # Parse the reconstructed URL to verify consistency
            reconstructed_parsed, reconstructed_params = parse_url_components(reconstructed)

            assert parsed_url.scheme == reconstructed_parsed.scheme
            assert parsed_url.netloc == reconstructed_parsed.netloc
            assert parsed_url.path == reconstructed_parsed.path
            assert parsed_url.fragment == reconstructed_parsed.fragment
            assert query_params == reconstructed_params

    def test_parse_url_components_with_encoded_chars(self):
        """Test parsing URL with encoded characters."""
        url = "https://example.com/search?q=hello%20world&special=%C4%85%C4%99"
        parsed_url, query_params = parse_url_components(url)

        assert parsed_url.scheme == "https"
        assert "q" in query_params
        assert "special" in query_params

    def test_reconstruct_url_preserves_scheme(self):
        """Test that different URL schemes are preserved."""
        schemes = ["http", "https", "ftp"]
        for scheme in schemes:
            url = f"{scheme}://example.com/path?param=value"
            parsed_url, query_params = parse_url_components(url)
            reconstructed = reconstruct_url(parsed_url, query_params)

            assert reconstructed.startswith(f"{scheme}://")

    def test_parse_url_components_malformed_url(self):
        """Test behavior with malformed URLs."""
        # This should not raise an exception, but handle gracefully
        url = "not-a-valid-url"
        parsed_url, query_params = parse_url_components(url)

        assert isinstance(parsed_url, ParseResult)
        assert isinstance(query_params, dict)

    def test_reconstruct_url_with_params_parameter(self):
        """Test reconstruction preserves URL params (semicolon-separated)."""
        url = "https://example.com/path;param=value?query=test"
        parsed_url, query_params = parse_url_components(url)
        reconstructed = reconstruct_url(parsed_url, query_params)

        # Verify params are preserved
        reconstructed_parsed, _ = parse_url_components(reconstructed)
        assert reconstructed_parsed.params == parsed_url.params
