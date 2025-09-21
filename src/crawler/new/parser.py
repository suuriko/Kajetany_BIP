from typing import Generator, Optional
from urllib.parse import urlencode, urljoin, urlunparse

from selectolax.lexbor import LexborHTMLParser, LexborNode

from src.crawler.datetime_extractor import extract_datetime
from src.crawler.http_client import HttpResponse
from src.crawler.new.base_parser import BaseParser
from src.crawler.url_manipulation import parse_url_components, reconstruct_url
from src.models.elements import Elements


class BipNadarzynSearchResultsParser(BaseParser):
    """Parser for BIP Nadarzyn website content, specialized in parsing search results.

    Assumes that the BIP search results page returns only relevant items, doesn't search for keywords.
    """

    def fetch(self, url: str) -> HttpResponse:
        """Fetch the URL using the provided HTTP client.
        Handles dynamic query parameters and prepares the search URL.
        """
        sanitized_url = self._sanitize_query_parameters(url)
        response = self.http_client.fetch(sanitized_url)

        prepared_url = self._prepare_search_url(sanitized_url, response.text)
        if prepared_url and prepared_url != sanitized_url:
            # For the second request, include the referer header to maintain session continuity
            # The httpx client automatically maintains cookies between requests
            additional_headers = {"Referer": sanitized_url}
            response = self.http_client.fetch(prepared_url, additional_headers)
        return response

    def _sanitize_query_parameters(self, url: str) -> str:
        """Remove unnecessary or dynamic query parameters from the URL."""
        parsed_url, query_params = parse_url_components(url)
        query_params.pop("_session_antiCSRF", None)  # Remove anti-CSRF token if present
        return reconstruct_url(parsed_url, query_params)

    def _prepare_search_url(self, url: str, page_html: str) -> Optional[str]:
        parsed_url, query_params = parse_url_components(url)

        dom = LexborHTMLParser(page_html)
        token_input = dom.css_first("input[name='_session_antiCSRF']")
        if token_input:
            token_value = token_input.attributes.get("value")
            if token_value:
                # Add the token to the query parameters
                query_params["_session_antiCSRF"] = [token_value]

        # Reconstruct the URL with the new parameters
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(
            (parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment)
        )

    def parse_list(self, html: str) -> Generator[Optional[Elements], None, None]:
        """Parse the main list page for relevant items."""
        dom = LexborHTMLParser(html)
        for item in dom.css("#PageContent ol.szukaj_wyniki li"):
            yield self.parse_item(item)

    def parse_item(self, item: LexborNode) -> Optional[Elements]:
        """Parse a single item node into an Elements object."""
        title = self._get_node_text_or_default(item.css_first("div.szukaj_tytul > a")) or "Brak tytułu"
        published_at = extract_datetime(
            self._get_node_text_or_default(item.css_first(".data_publikacji .system_metryka_wartosc"))
        )
        created_at = extract_datetime(
            self._get_node_text_or_default(item.css_first(".autor_data .system_metryka_wartosc"))
        )
        last_modified_at = extract_datetime(
            self._get_node_text_or_default(item.css_first(".data_mod .system_metryka_wartosc"))
        )

        for a in item.css("cite"):
            link_text = (a.text() or "").strip()
            if not link_text:
                continue
            full_url = urljoin(self.base_url, link_text)
            self.logger.info(f"Found link in list: \n{title} \n -> {link_text} \n  -> {full_url}")

            return Elements(
                main_title=title,
                title=link_text,
                url=full_url,
                published_at=published_at,
                created_at=created_at,
                last_modified_at=last_modified_at,
            )
        return None

    def _get_node_text_or_default(self, node: Optional[LexborNode], default: Optional[str] = None) -> Optional[str]:
        """Helper to get text from a node or return default."""
        return node.text(strip=True) if node else default

    def _get_node_text_content_or_default(
        self, node: Optional[LexborNode], default: Optional[str] = None
    ) -> Optional[str]:
        """Helper to get text content from a node or return default."""
        return node.text_content.strip() if node and node.text_content else default
