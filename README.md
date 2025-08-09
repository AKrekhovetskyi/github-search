# GitHub Search

Simple GitHub search engine.

## Installation

1. Ensure you have Python 3.13 installed.
1. Clone the repository:
   ```sh
   git clone --recurse-submodules https://github.com/AKrekhovetskyi/github-search.git
   cd github-search
   ```
1. Install dependencies (make sure to install them in your local virtual environment):
   ```sh
   pip install -r requirements.txt
   ```
1. Create an `.env` file from [`.env.sample`](./.env.sample) and set the necessary variables
   ```bash
   cp .env.sample .env
   ```
1. Sometimes it might be necessary to export the following environment variable:
   ```bash
   export PYTHONPATH=${PYTHONPATH}:$(pwd)
   ```

## Usage

Populate the [`input.json`](./input.json) file with the required query parameters (see [`RequestParams`](./src/scraper.py) for details).

To run the search script, use the following command:

```sh
dotenv run -- python -m src.search input.json search_results.json
```

Your can replace both `input.json` and `search_results.json` arguments with the paths to the desirable input and output files.

Add [-O](https://docs.python.org/3/using/cmdline.html#cmdoption-O) flag to the command above if the script is supposed to be run in production.

## Testing

To execute the test suite, run:

```sh
dotenv run -- pytest --show-capture=stdout --showlocals -vv -s -rA --cov-fail-under=90 --cov=src tests
```

This will display detailed output for all tests.

> **NOTE:** To run the [`tests/test_scraper.py::TestGitHub::test_request_page_html`](./tests/test_scraper.py) test, assign a working proxy to the `TEST_PROXY` environment variable.

## Notes

- The project uses [python-dotenv](https://pypi.org/project/python-dotenv/) to manage environment variables.
- For further details, consult the source code and comments.
- Look at the [settings.py](./src/settings.py) file.
- Run the following command before making commits if you decided to contribute to the project:
  ```bash
  pre-commit install --install-hooks
  ```
