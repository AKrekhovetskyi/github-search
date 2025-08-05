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
   mv .env.sample .env
   ```
1. Sometimes it might be necessary to export the following environment variable:
   ```bash
   export PYTHONPATH=${PYTHONPATH}:$(pwd)
   ```

## Usage

To run the search script, use the following command:

```sh
dotenv run -- python -m src.search input.json
```

Replace `input.json` with the path to your input file containing search parameters.

Add [-O](https://docs.python.org/3/using/cmdline.html#cmdoption-O) flag to the command above if the script is supposed to be run in production.

## Testing

To execute the test suite, run:

```sh
dotenv run -- pytest --show-capture=stdout --showlocals -vv -s -rA --cov-fail-under=90 --cov=src tests
```

This will display detailed output for all tests.

## Notes

- The project uses [python-dotenv](https://pypi.org/project/python-dotenv/) to manage environment variables.
- For further details, consult the source code and comments.
- Look at the [settings.py](./src/settings.py) file.
- Run the following command before making commits if you decided to contribute to the project:
  ```bash
  pre-commit install --install-hooks
  ```
