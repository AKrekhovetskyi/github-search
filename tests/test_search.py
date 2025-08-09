from argparse import ArgumentParser
from json import dumps, loads
from pathlib import Path
from unittest.mock import patch

import pytest

from src.logging_config import logging
from src.scraper import GitHub
from src.search import main


def test_main(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    # Prepare a minimal input.json file.
    input_data = {"keywords": ["python"], "proxies": [], "type": "repositories"}
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "output.json"
    input_file.write_text(dumps(input_data))

    class Namespace:
        input_file_path = input_file
        output_file_path = output_file

    search_result = (Path(__file__).parent / "search_result.html").read_text()

    with (
        patch.object(ArgumentParser, "parse_args", return_value=Namespace),
        caplog.at_level(logging.DEBUG),
        patch.object(GitHub, "request_page_html", return_value=search_result),
        patch.object(GitHub, "extract_extra_info", return_value={"owner": ""}),
    ):
        main()

    search_results = loads(output_file.read_bytes())
    assert search_results
    assert isinstance(search_results[0], dict)
    assert "extra" in search_results[0]

    # Assert log contains expected text.
    assert any("Parsed URLs: [{'url': 'https://github.com" in message for message in caplog.messages)
