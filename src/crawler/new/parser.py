from typing import Generator, Optional
from urllib.parse import urlencode, urljoin, urlparse, urlunparse

from selectolax.lexbor import LexborHTMLParser, LexborNode

from src.crawler.new.base_parser import BaseParser
from src.crawler.url_manipulation import parse_url_components, reconstruct_url
from src.models.elements import ContentItem, RedirectItem


class CSSSelectors:
    """CSS selectors used throughout the parsers."""

    PUBLICATION_DATE = ".data_publikacji .system_metryka_wartosc"
    CREATION_DATE = ".autor_data .system_metryka_wartosc"
    MODIFICATION_DATE = ".data_mod .system_metryka_wartosc"
    ARTICLE_TITLE = "h3"
    ARTICLE_NODE = ".obiekt_akapit"
    CONTAINER_NODE = ".obiekt_pliki"
    FILE_LINK = ".pliki_link"
    SEARCH_RESULTS = "#PageContent ol.szukaj_wyniki li"
    SEARCH_TITLE = ".szukaj_tytul > a"
    SEARCH_SNIPPET = ".szukaj_wyniki_snippet"
    MORE_LINK = "a.wyswietl_wiecej_link"
    BRIEF_ARTICLE = ".akapit_skrot"
    ANTI_CSRF_INPUT = "input[name='_session_antiCSRF']"


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

        token_input = dom.css_first(CSSSelectors.ANTI_CSRF_INPUT)
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
        for item in dom.css(CSSSelectors.SEARCH_RESULTS):
            yield self._parse_item(item)

    def _parse_item(self, item: LexborNode) -> Optional[RedirectItem]:
        title_node = self._safe_get_node(item, CSSSelectors.SEARCH_TITLE)
        title = self._get_node_text_or_default(title_node.first_child if title_node else None) or "Brak tytułu"
        link = self._get_node_text_or_default(item.css_first("cite"))

        if not link:
            self.logger.warning(f"Item missing link, skipping: {title}")
            return None

        self.logger.info(f"Found link in list: \n{title} \n -> {link}")
        description = self._get_node_text_or_default(self._safe_get_node(item, CSSSelectors.SEARCH_SNIPPET))

        return RedirectItem(
            main_title=title,
            title=title,
            description=description,
            url=link,
        )


class ArticleParser(BaseParser):
    def can_parse(self, url: str, dom: LexborHTMLParser) -> bool:
        anchor = self._get_anchor_from_url(url)
        return "akapit_" in anchor

    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[ContentItem], None, None]:
        anchor = self._get_anchor_from_url(url)
        article_node = dom.css_first(f"#{anchor}")

        if not article_node:
            self.logger.warning(f"Article node not found for anchor: {anchor}")
            return

        title = self._extract_title(article_node)
        published_at, created_at, last_modified_at = self._extract_metadata(article_node)

        yield ContentItem(
            main_title=title,
            title=title,
            description=None,
            url=url,
            published_at=published_at,
            created_at=created_at,
            last_modified_at=last_modified_at,
        )


class ArticleAttachmentParser(BaseParser):
    def can_parse(self, url: str, dom: LexborHTMLParser) -> bool:
        anchor = self._get_anchor_from_url(url)
        return "plik_" in anchor and dom.css_first(f"{CSSSelectors.ARTICLE_NODE} #{anchor}") is not None

    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[ContentItem], None, None]:
        anchor = self._get_anchor_from_url(url)
        article_node = dom.css_first(CSSSelectors.ARTICLE_NODE)

        if not article_node:
            self.logger.warning(f"Article node not found for attachment: {anchor}")
            return

        article_title = self._extract_title(article_node)
        attachment_node = self._safe_get_node(article_node, f"#{anchor}")
        attachment_name = (
            self._get_node_text_or_default(self._safe_get_node(attachment_node, CSSSelectors.FILE_LINK)) or "Brak nazwy"
        )

        published_at, created_at, last_modified_at = self._extract_metadata(article_node)

        yield ContentItem(
            main_title=article_title,
            title=attachment_name,
            description=None,
            url=url,
            published_at=published_at,
            created_at=created_at,
            last_modified_at=last_modified_at,
        )


class ListAttachmentParser(BaseParser):
    def can_parse(self, url: str, dom: LexborHTMLParser) -> bool:
        anchor = self._get_anchor_from_url(url)
        return "plik_" in anchor and dom.css_first(f"{CSSSelectors.ARTICLE_NODE} #{anchor}") is None

    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[ContentItem], None, None]:
        anchor = self._get_anchor_from_url(url)
        container_node = dom.css_first(f"{CSSSelectors.CONTAINER_NODE}:has(#{anchor})")

        if not container_node:
            self.logger.warning(f"Container node not found for attachment: {anchor}")
            return

        article_title = self._extract_title(container_node)
        attachment_node = self._safe_get_node(container_node, f"#{anchor}")
        attachment_name = (
            self._get_node_text_or_default(self._safe_get_node(attachment_node, CSSSelectors.FILE_LINK)) or "Brak nazwy"
        )

        published_at, created_at, last_modified_at = self._extract_metadata(container_node)

        yield ContentItem(
            main_title=article_title,
            title=attachment_name,
            description=None,
            url=url,
            published_at=published_at,
            created_at=created_at,
            last_modified_at=last_modified_at,
        )


class ArticleBriefParser(BaseParser):
    def can_parse(self, url: str, dom: LexborHTMLParser) -> bool:
        anchor = self._get_anchor_from_url(url)
        brief_selector = f"{CSSSelectors.ARTICLE_NODE}#{anchor} {CSSSelectors.BRIEF_ARTICLE}"
        return "akapit_" in anchor and dom.css_first(brief_selector) is not None

    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[RedirectItem], None, None]:
        parsed_url = urlparse(url)
        anchor = parsed_url.fragment
        base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))  # URL base
        article_node = dom.css_first(f"{CSSSelectors.ARTICLE_NODE}#{anchor} {CSSSelectors.BRIEF_ARTICLE}")

        if not article_node:
            self.logger.warning(f"Brief article node not found for anchor: {anchor}")
            return

        more_link = self._safe_get_node(article_node, CSSSelectors.MORE_LINK)
        more_link_url = more_link.attributes.get("href") if more_link else None
        if not more_link_url:
            self.logger.warning(f"Item missing 'read more' link, skipping: {url}")
            return

        title = self._extract_title(article_node)

        yield RedirectItem(
            main_title=title,
            title=title,
            description=None,
            url=urljoin(base_url, more_link_url),
            published_at=None,
            created_at=None,
            last_modified_at=None,
        )


class FullArticleParser(BaseParser):
    def can_parse(self, url: str, dom: LexborHTMLParser) -> bool:
        return True

    def parse(self, url: str, dom: LexborHTMLParser) -> Generator[Optional[ContentItem], None, None]:
        article_node = dom.css_first(CSSSelectors.ARTICLE_NODE)

        if not article_node:
            self.logger.warning("Article node not found in full article parser")
            return

        title = self._extract_title(article_node)
        published_at, created_at, last_modified_at = self._extract_metadata(article_node)

        yield ContentItem(
            main_title=title,
            title=title,
            description=None,
            url=url,
            published_at=published_at,
            created_at=created_at,
            last_modified_at=last_modified_at,
        )
