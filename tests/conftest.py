import logging
from collections import deque
from unittest.mock import Mock

import pytest

from src.crawler.nadarzyn_bip.base_parser import BaseParser
from src.crawler.nadarzyn_bip.crawler import Crawler
from src.models import ContentItem, RedirectItem

BASE_SLEEP_SECONDS = 1.5


@pytest.fixture
def base_url() -> str:
    return "https://bip.nadarzyn.pl"


@pytest.fixture
def parser1() -> Mock:
    return Mock(spec=BaseParser)


@pytest.fixture
def parser2() -> Mock:
    return Mock(spec=BaseParser)


@pytest.fixture
def crawler(base_url: str, parser1: Mock, parser2: Mock) -> Crawler:
    return Crawler(base_url, [parser1, parser2])


@pytest.fixture
def http_client(monkeypatch):  # returns underlying client mock inside context manager
    client = Mock()

    class _Ctx:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc, tb):
            return False

    http_client_cls = Mock(return_value=_Ctx())
    monkeypatch.setattr("src.crawler.nadarzyn_bip.crawler.HttpClient", http_client_cls)
    return client


@pytest.fixture
def sleep_calls(monkeypatch):
    calls: deque[float] = deque()

    def fake_sleep(seconds: float):
        calls.append(seconds)

    monkeypatch.setattr("src.crawler.nadarzyn_bip.crawler.time.sleep", fake_sleep)
    return calls


@pytest.fixture
def make_content(base_url: str):
    def _make(**overrides) -> ContentItem:
        data = {
            "url": base_url,
            "main_title": "Main Title",
            "title": "Sub Title",
            "description": overrides.pop("description", None),
        }
        data.update(overrides)
        return ContentItem(**data)

    return _make


@pytest.fixture
def make_redirect(base_url: str):
    def _make(**overrides) -> RedirectItem:
        data = {"url": base_url, "main_title": overrides.pop("main_title", None)}
        data.update(overrides)
        return RedirectItem(**data)

    return _make


@pytest.fixture
def caplog_info(caplog):  # convenience to default INFO level
    caplog.set_level(logging.INFO)
    return caplog
