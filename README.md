# TV-Tracker

A simple CLI for keeping up-to-date with your favourite shows!

# Prerequisites

- [uv is installed](https://docs.astral.sh/uv/getting-started/installation/)
- [API Key from TheTVDB](https://thetvdb.com/api-information)

# Setup

1. Add your API key
    1. Create a file called `.env` in the same directory as this README
    2. Copy your API key from TheTVDB it should look like this:
        ```
        TVDB_KEY=<your secret key>
        ```
2. Run `uv run src/main.py`

---
[<img src="docs/tvdb-attribution.png" width=50> Metadata provided by TheTVDB. Please consider adding missing information or subscribing.](https://thetvdb.com/subscribe)