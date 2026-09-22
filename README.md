# YNAB LLM analysis

The planned iPhone-to-YNAB batch receipt workflow is in [PLAN.md](PLAN.md).

## List tracking accounts

Run on macOS with the saved `ynab_token.rtf` file beside the script:

```sh
python3 list_tracking_accounts.py
```

The script lists open tracking accounts in the last-used YNAB plan. To select a
specific plan, pass `--plan PLAN_ID`. Add `--include-closed` to show closed
tracking accounts. You can also supply the token through the `YNAB_TOKEN`
environment variable instead of the RTF file.

The token file is ignored by Git. Keep it private and never commit it.
