# nickname-finder-tgbot
Nickname finder bot for telegram, requires aiogram 2.x

```text.txt``` file contains web sites where bot will search for a nickname


## Request isolation and validation

Set `TOKEN` through the environment or a local `.env` file; never commit credentials. Each nickname search now returns its own result list, so replies do not include earlier users' searches. HTTP requests run off the event loop with a 10-second timeout, and nickname text is URL-encoded. `text.txt` is located relative to `main.py`, independently of the working directory.

Offline regressions mock all HTTP calls and Telegram replies:

```sh
python -m unittest discover -s tests -v
```

A successful HTTP status remains the existing heuristic for a profile match; this does not establish the identity behind an account or guarantee external-site accuracy.
