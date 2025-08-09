import os
import re
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.scraper import GitHub, GitHubSearchTypes, RequestParams

TEST_PROXY = os.getenv("TEST_PROXY")


@pytest.fixture(scope="module")
def github() -> Iterator[GitHub]:
    github_instance = GitHub(proxies=[TEST_PROXY] if TEST_PROXY else None)
    yield github_instance
    github_instance.close()


@pytest.fixture(scope="module")
def request_params() -> RequestParams:
    return RequestParams(keywords=["python", "django-rest-framework", "jwt"], proxies=[])


class TestGitHub:
    @pytest.mark.skipif(
        not TEST_PROXY,
        reason="The test performs real requests which require proxy. Set the `TEST_PROXY` environment variable first.",
    )
    @pytest.mark.parametrize("type_", ["repositories", "issues", "wikis"])
    def test_request_page_html(self, type_: GitHubSearchTypes, github: GitHub, request_params: RequestParams) -> None:
        request_params.type = type_
        html = github.request_page_html(url=f"{github.base_url}/search", params=request_params.to_dict())
        soup = BeautifulSoup(html, "lxml")
        # Look for all text that matches the pattern like: "12 results".
        match = soup.find(string=re.compile(r"\b(\d+)\s+results\b", re.IGNORECASE))
        assert match is not None, "Expected text like 'X results' not found. Make sure the set proxy isn't blocked."
        number = int(re.search(r"\d+", match).group())  # pyright: ignore[reportCallIssue,reportArgumentType]
        assert number > 1, f"Expected number > 1, got {number}"

    @pytest.mark.parametrize(
        ("proxy", "set_proxy"),
        [
            (["194.126.37.94:8080"], {"http": "http://194.126.37.94:8080"}),
            (["http://194.126.37.94:8080"], {"http": "http://194.126.37.94:8080"}),
            (["https://194.126.37.94:8080"], {"https": "https://194.126.37.94:8080"}),
        ],
    )
    def test_update_session_proxy(self, proxy: list[str], set_proxy: dict[str, str], github: GitHub) -> None:
        github.update_session_proxy(proxies=proxy)
        assert github.session.proxies == set_proxy
        github.session.proxies = {}

    def test_extract_urls(self, github: GitHub) -> None:
        html = (Path(__file__).parent / "search_result.html").read_text()
        urls = github.extract_urls(html)
        expected_result = [
            {"url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage"},
            {"url": "https://github.com/michealbalogun/Horizon-dashboard"},
        ]
        for url, expected_url in zip(urls, expected_result, strict=True):
            assert url == expected_url

    def test_extract_extra_info(self, github: GitHub) -> None:
        html = (Path(__file__).parent / "repository_sidebar.html").read_text()
        with patch.object(GitHub, "request_page_html", return_value=html):
            extra_info = github.extract_extra_info("https://github.com/AKrekhovetskyi/github-search")
            assert extra_info == {
                "owner": "AKrekhovetskyi",
                "language_stats": {"CSS": "52.0%", "JavaScript": "47.2%", "HTML": "0.8%"},
            }
