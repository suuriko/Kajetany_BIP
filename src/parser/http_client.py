import httpx

HEADERS = {"User-Agent": "KajetanyWatcher/1.0 (+kajetany.bip.bot@gmail.com)"}


def fetch(client: httpx.Client, url: str) -> httpx.Response:
    r = client.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r
