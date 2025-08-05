import re
from collections.abc import Iterator
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from src.scraper import GitHub, GitHubSearchTypes, RequestParams


@pytest.fixture(scope="module")
def github() -> Iterator[GitHub]:
    github_instance = GitHub()
    yield github_instance
    github_instance.close()


@pytest.fixture(scope="module")
def request_params() -> RequestParams:
    return RequestParams(keywords=["python", "django-rest-framework", "jwt"], proxies=[])


class TestGitHub:
    @pytest.mark.parametrize("type_", ["repositories", "issues", "wikis"])
    def test_search(self, type_: GitHubSearchTypes, github: GitHub, request_params: RequestParams) -> None:
        request_params.type = type_
        html = github.search(request_params)
        soup = BeautifulSoup(html, "lxml")

        # Look for all text that matches the pattern like: "12 results".
        match = soup.find(string=re.compile(r"\b(\d+)\s+results\b", re.IGNORECASE))
        assert match is not None, "Expected text like 'X results' not found"
        number = int(re.search(r"\d+", match).group())  # pyright: ignore[reportCallIssue,reportArgumentType]
        assert number > 1, f"Expected number > 1, got {number}"

    def test_extract_urls(self, github: GitHub) -> None:
        html = (Path(__file__).parent / "search_result.html").read_text()
        urls = github.extract_urls(html)
        expected_result = [
            {"url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage"},
            {"url": "https://github.com/michealbalogun/Horizon-dashboard"},
        ]
        for url, expected_url in zip(urls, expected_result, strict=True):
            assert url == expected_url
