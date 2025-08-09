from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from secrets import choice
from time import sleep
from typing import Any, Literal
from urllib.parse import urljoin, urlparse

import requests_cache
from bs4 import BeautifulSoup, SoupStrainer, Tag  # pyright: ignore[reportPrivateImportUsage]

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
        return {"q": " ".join(self.keywords), "type": self.type}


class GitHub:
    base_url: str = "https://github.com"

    def __init__(self, proxies: list[str] | None = None) -> None:
        self.session = requests_cache.CachedSession(
            cache_name=CACHE_NAME,
            expire_after=CACHE_TTL_DEV if __debug__ else CACHE_TTL_PROD,
            use_cache_dir=True,
        )
        """NOTE: Remember to close the session at the end."""
        if proxies:
            self.update_session_proxy(proxies)
        self._dont_request_until = datetime.now(UTC)

    def update_session_proxy(self, proxies: list[str]) -> None:
        proxy = choice(proxies)
        proxy = proxy if proxy.startswith("http") else f"http://{proxy}"
        proxy = {"https": proxy} if proxy.startswith("https") else {"http": proxy}
        self.session.proxies.update(proxy)
        logger.debug("Proxy applied: %s", proxy)

    def close(self) -> None:
        self.session.close()

    def request_page_html(self, url: str, params: dict[str, Any] | None = None) -> str:
        """Request GitHub page and return raw HTML."""
        # Simulate human browsing by applying a delay.
        now = datetime.now(UTC)
        if self._dont_request_until > now:
            sleep((self._dont_request_until - now).total_seconds())

        response = self.session.get(url=url, headers=headers, params=params)
        if response.status_code > HTTPStatus.BAD_REQUEST:
            logger.warning("\nURL: %s\nStatus code: %d\nParams: %s", response.request.url, response.status_code, params)

        self._dont_request_until += timedelta(seconds=choice([1, 2, 3]))
        return response.text

    def extract_urls(self, html: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(
            html,
            "lxml",
            parse_only=SoupStrainer("div", attrs={"data-testid": "results-list"}),
        )
        urls = [
            {"url": urljoin(self.base_url, href)}
            for item in soup.find_all("span", attrs={"class": "search-match"})
            if item.parent
            and item.parent.name == "a"
            and (href := item.parent.attrs.get("href"))
            and isinstance(href, str)
        ]
        if urls:
            logger.debug("Parsed URLs: %s", urls)
        else:
            logger.info("No URLs found!")
        return urls

    def extract_extra_info(self, url: str) -> dict[str, Any] | None:
        """Extract owner nic and language statistics."""
        html = self.request_page_html(url=url)
        extra = {"owner": urlparse(url).path.split("/")[1], "language_stats": {}}
        soup = BeautifulSoup(
            html,
            "lxml",
            parse_only=SoupStrainer("div", attrs={"class": "Layout-sidebar"}),
        )
        languages = soup.find(string="Languages")
        if not languages or not isinstance(languages.parent, Tag) or not isinstance(languages.parent.parent, Tag):
            return None
        language_and_percentage = 2
        for li in languages.parent.parent.find_all("li"):
            if (
                not li
                or not isinstance(li, Tag)
                or not (spans := li.find_all("span"))
                or len(spans) < language_and_percentage
            ):
                continue
            extra["language_stats"][spans[0].text] = spans[1].text

        logger.info("Extra info: %s", extra)
        return extra
