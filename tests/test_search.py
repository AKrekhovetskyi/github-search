from argparse import ArgumentParser
from json import dumps
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
        caplog.at_level(logging.INFO),
        patch.object(GitHub, "request_page_html", return_value=search_result),
        patch.object(GitHub, "extract_extra_info", return_value={"owner": ""}),
    ):
        main()

    # Assert log contains expected text.
    assert any("Parsed URLs: [{'url': 'https://github.com" in message for message in caplog.messages)
