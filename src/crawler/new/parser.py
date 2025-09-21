from typing import Generator, Optional
from urllib.parse import urlencode, urlparse, urlunparse

from selectolax.lexbor import LexborHTMLParser, LexborNode

from src.crawler.datetime_extractor import extract_datetime
from src.crawler.new.base_parser import BaseParser
from src.crawler.url_manipulation import parse_url_components, reconstruct_url
from src.models.elements import ContentItem, RedirectItem


class SearchPageConfiguratorParser(BaseParser):
    def can_parse(self, url: str, html_content: str) -> bool:
        return "/redir,szukaj" in url and "_session_antiCSRF" not in url

    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[RedirectItem], None, None]:
        sanitized_url = self._sanitize_query_parameters(url)

        prepared_url = self._prepare_search_url(sanitized_url, dom)
        if prepared_url and prepared_url != sanitized_url:
            # For the second request, include the referer header to maintain session continuity
            # The httpx client automatically maintains cookies between requests
            yield RedirectItem(url=prepared_url)

    def _sanitize_query_parameters(self, url: str) -> str:
        """Remove unnecessary or dynamic query parameters from the URL."""
        parsed_url, query_params = parse_url_components(url)
        query_params.pop("_session_antiCSRF", None)  # Remove anti-CSRF token if present
        return reconstruct_url(parsed_url, query_params)

    def _prepare_search_url(self, url: str, dom: LexborHTMLParser) -> Optional[str]:
        parsed_url, query_params = parse_url_components(url)

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


class SearchPageResultsParser(BaseParser):
    def can_parse(self, url: str, dom: LexborHTMLParser) -> bool:
        return "/redir,szukaj" in url and "_session_antiCSRF" in url

    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[RedirectItem], None, None]:
        for item in dom.css("#PageContent ol.szukaj_wyniki li"):
            yield self._parse_item(item)

    def _parse_item(self, item: LexborNode) -> Optional[RedirectItem]:
        title = self._get_node_text_or_default(item.css_first(".szukaj_tytul > a").first_child) or "Brak tytułu"
        link = self._get_node_text_or_default(item.css_first("cite"))

        if not link:
            self.logger.warning(f"Item missing link, skipping: {title}")
            return None

        self.logger.info(f"Found link in list: \n{title} \n -> {link}")
        description = self._get_node_text_or_default(item.css_first(".szukaj_wyniki_snippet"))

        return RedirectItem(
            main_title=title,
            title=title,
            description=description,
            url=link,
        )


class ArticleParser(BaseParser):
    def can_parse(self, url: str, dom: LexborHTMLParser) -> bool:
        anchor = urlparse(url).fragment
        return "akapit_" in anchor

    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[ContentItem], None, None]:
        anchor = urlparse(url).fragment

        article_node = dom.css_first(f"#{anchor}")
        title = self._get_node_text_or_default(article_node.css_first("h3")) or "Brak tytułu"
        description = None

        published_at = extract_datetime(
            self._get_node_text_or_default(article_node.css_first(".data_publikacji .system_metryka_wartosc"))
        )
        created_at = extract_datetime(
            self._get_node_text_or_default(article_node.css_first(".autor_data .system_metryka_wartosc"))
        )
        last_modified_at = extract_datetime(
            self._get_node_text_or_default(article_node.css_first(".data_mod .system_metryka_wartosc"))
        )

        yield ContentItem(
            main_title=title,
            title=title,
            description=description,
            url=url,
            published_at=published_at,
            created_at=created_at,
            last_modified_at=last_modified_at,
        )


class ArticleAttachmentParser(BaseParser):
    def can_parse(self, url: str, dom: LexborHTMLParser) -> bool:
        anchor = urlparse(url).fragment
        return "plik_" in anchor and dom.css_first(f".obiekt_akapit #{anchor}") is not None

    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[ContentItem], None, None]:
        anchor = urlparse(url).fragment

        article_node = dom.css_first(".obiekt_akapit")
        article_title = self._get_node_text_or_default(article_node.css_first("h3")) or "Brak tytułu"

        attachment_node = article_node.css_first(f"#{anchor}")
        attachment_name = self._get_node_text_or_default(attachment_node.css_first(".pliki_link")) or "Brak nazwy"

        published_at = extract_datetime(
            self._get_node_text_or_default(article_node.css_first(".data_publikacji .system_metryka_wartosc"))
        )
        created_at = extract_datetime(
            self._get_node_text_or_default(article_node.css_first(".autor_data .system_metryka_wartosc"))
        )
        last_modified_at = extract_datetime(
            self._get_node_text_or_default(article_node.css_first(".data_mod .system_metryka_wartosc"))
        )

        yield ContentItem(
            main_title=article_title,
            title=attachment_name,
            description=None,
            url=url,
            published_at=published_at,
            created_at=created_at,
            last_modified_at=last_modified_at,
        )
