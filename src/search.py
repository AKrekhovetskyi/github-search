import argparse
from json import dumps, loads
from pathlib import Path

from src.scraper import GitHub, RequestParams


class NoInputFileFoundError(Exception): ...


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub Search CLI")
    parser.add_argument("input_file_path", type=str, help="A path to the file with input data (JSON).")
    parser.add_argument("output_file_path", type=str, help="A path to the file with parsed data (JSON).")
    args = parser.parse_args()
    input_file_path = Path(args.input_file_path)
    if not input_file_path.exists():
        raise NoInputFileFoundError

    input_data = loads(input_file_path.read_bytes())
    params = RequestParams(keywords=input_data["keywords"], proxies=input_data["proxies"], type=input_data["type"])
    github = GitHub(proxies=params.proxies)
    html = github.request_page_html(url=f"{github.base_url}/search", params=params.to_dict())
    urls = github.extract_urls(html)
    for url in urls:
        extra_info = github.extract_extra_info(url["url"])
        if extra_info:
            url["extra"] = extra_info  # pyright: ignore[reportArgumentType]
    github.close()
    output_file_path = Path(args.output_file_path)
    output_file_path.write_text(dumps(urls))


if __name__ == "__main__":
    main()
