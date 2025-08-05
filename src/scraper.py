from dataclasses import dataclass, field
from http import HTTPStatus
from secrets import choice
from typing import Any, Literal
from urllib.parse import quote_plus

import requests_cache
from bs4 import BeautifulSoup, SoupStrainer  # pyright: ignore[reportPrivateImportUsage]

from src.logging_config import logging
from src.settings import CACHE_NAME, CACHE_TTL_DEV, CACHE_TTL_PROD

logger = logging.getLogger(__name__)
headers = {
    "accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
        "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    ),
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,uk;q=0.8,ru;q=0.7",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://github.com/",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
    ),
}

type GitHubSearchTypes = Literal["repositories", "issues", "wikis"]


@dataclass
class RequestParams:
    keywords: list[str]
    """List of keywords separated by space."""
    proxies: list[str]
    type: GitHubSearchTypes = field(default="repositories")

    def to_dict(self) -> dict[str, Any]:
        return {"q": quote_plus(" ".join(self.keywords)), "type": self.type}


class GitHub:
    _base_url: str = "https://github.com"

    def __init__(self) -> None:
        # NOTE: Remember to close the session at the end.
        self.session = requests_cache.CachedSession(
            cache_name=CACHE_NAME,
            expire_after=CACHE_TTL_DEV if __debug__ else CACHE_TTL_PROD,
            use_cache_dir=True,
        )

    def close(self) -> None:
        self.session.close()

    def search(self, params: RequestParams) -> str:
        """Perform GitHub search and return raw HTML."""
        if params.proxies:
            proxy = choice(params.proxies)
            prefix = f"http{'s' if proxy.startswith('https') else ''}"
            self.session.proxies = {prefix: f"{prefix}://{proxy}"}
            logger.debug("Proxy applied: %s", self.session.proxies)
        response = self.session.get(
            url=f"{self._base_url}/search",
            headers=headers,
            params=params.to_dict(),
        )

        if response.status_code > HTTPStatus.BAD_REQUEST:
            logger.warning(
                "\nURL: %s\nStatus code: %d\nParams: %s", response.request.url, response.status_code, params.to_dict()
            )

        return response.text

    def extract_urls(self, html: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(
            html,
            "lxml",
            parse_only=SoupStrainer("div", attrs={"data-testid": "results-list"}),
        )
        urls = [
            {"url": f"{self._base_url}{item.parent.attrs['href']}"}
            for item in soup.find_all("span", attrs={"class": "search-match"})
            if item.parent and item.parent.name == "a"
        ]
        logger.info("Parsed URLs: %s", urls)
        return urls
