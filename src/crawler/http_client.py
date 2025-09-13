import httpx

HEADERS = {"User-Agent": "KajetanyWatcher/1.0 (+kajetany.bip.bot@gmail.com)"}


class HttpClient:
    def __init__(self):
        self.client = httpx.Client(follow_redirects=True)

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, *args):
        return self.client.__exit__(*args)

    def fetch(self, url: str) -> httpx.Response:
        r = self.client.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        return r
