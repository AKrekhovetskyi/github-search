import argparse
from json import loads
from pathlib import Path

from src.scraper import GitHub, RequestParams


class NoInputFileFoundError(Exception): ...


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub Search CLI")
    parser.add_argument("input_file_path", type=str, help="A path to the file with input data.")
    args = parser.parse_args()
    input_file_path = Path(args.input_file_path)
    if not input_file_path.exists():
        raise NoInputFileFoundError

    input_data = loads(input_file_path.read_bytes())
    params = RequestParams(
        keywords=input_data["keywords"],
        proxies=input_data["proxies"],
        type=input_data["type"],
    )
    github = GitHub()
    html = github.search(params)
    github.extract_urls(html)
    github.close()


if __name__ == "__main__":
    main()
