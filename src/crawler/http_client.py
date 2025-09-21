from typing import Dict, Optional

import httpx

HttpResponse = httpx.Response

HEADERS = {"User-Agent": "KajetanyWatcher/1.0 (+kajetany.bip.bot@gmail.com)"}


class HttpClient:
    def __init__(self):
        self.client = httpx.Client(follow_redirects=True)

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, *args):
        return self.client.__exit__(*args)

    def fetch(self, url: str, additional_headers: Optional[Dict[str, str]] = None) -> HttpResponse:
        headers = HEADERS.copy()
        if additional_headers:
            headers.update(additional_headers)
        r = self.client.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r
