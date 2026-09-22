#!/usr/bin/env python3
"""List open tracking accounts in a YNAB plan."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def get_token() -> str:
    token = os.environ.get("YNAB_TOKEN", "").strip()
    if not token:
        token_file = Path(__file__).with_name("ynab_token.rtf")
        try:
            token = subprocess.check_output(
                ["textutil", "-convert", "txt", "-stdout", str(token_file)],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            raise ValueError(
                "Set YNAB_TOKEN or put ynab_token.rtf next to this script "
                "(reading RTF requires macOS textutil)."
            ) from exc
    if not token or any(character.isspace() for character in token):
        raise ValueError("The YNAB token must be a single nonempty value.")
    return token


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan", default="last-used", help="YNAB plan ID (default: last-used)"
    )
    parser.add_argument(
        "--include-closed", action="store_true", help="Include closed tracking accounts"
    )
    args = parser.parse_args()

    try:
        token = get_token()
        url = f"https://api.ynab.com/v1/plans/{quote(args.plan, safe='')}/accounts"
        request = Request(url, headers={"Authorization": f"Bearer {token}"})
        with urlopen(request, timeout=20) as response:
            accounts = json.load(response)["data"]["accounts"]
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except HTTPError as exc:
        print(f"YNAB API returned HTTP {exc.code}.", file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"Could not reach YNAB: {exc.reason if isinstance(exc, URLError) else 'timed out'}", file=sys.stderr)
        return 1
    except (KeyError, json.JSONDecodeError):
        print("YNAB returned an unexpected response.", file=sys.stderr)
        return 1

    tracking = [
        account
        for account in accounts
        if account.get("on_budget") is False
        and not account.get("deleted")
        and (args.include_closed or not account.get("closed"))
    ]
    if not tracking:
        print("No tracking accounts found.")
    else:
        for account in tracking:
            status = " [closed]" if account.get("closed") else ""
            print(f"{account['name']} ({account['type']}){status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
