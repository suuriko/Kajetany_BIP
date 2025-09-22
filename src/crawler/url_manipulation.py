from urllib.parse import ParseResult, parse_qs, urlencode, urlparse, urlunparse


def parse_url_components(url: str) -> tuple[ParseResult, dict]:
    """Parse URL and return parsed URL object and query parameters dictionary."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return parsed_url, query_params


def reconstruct_url(parsed_url: ParseResult, query_params: dict) -> str:
    """Reconstruct URL from parsed components and query parameters."""
    new_query = urlencode(query_params, doseq=True)
    return urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment)
    )
