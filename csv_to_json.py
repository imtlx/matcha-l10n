#!/usr/bin/env python3

import csv
import json
from pathlib import Path
import argparse
import requests
import sys
from collections.abc import Iterable
import re
from typing import TypeAlias

default_spreadsheet_id: str = "1koZhCQuZrVlRfv9vdfWF2huqhYliztvqEruG_0c_Mus"
default_main_sheet_id: int = 1336669961
default_overrides_sheet_id: int = 1300505173

escape_re = re.compile(r'\\u([0-9a-f]{4})', re.I)

Overrides: TypeAlias = dict[str, dict[str, str]]

def fetch_sheet(spreadsheet_id: int, sheet_id: int) -> list[str]:
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export"
    params = {"gid": sheet_id, "format": "csv"}
    print(f'Fetching: {url=!r}, {params=!r}', file=sys.stderr)

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.text.splitlines()

def process_overrides_csv(csv_it: Iterable[str]) -> Overrides:
    result: Overrides = {}
    for lang, key, value in csv.reader(csv_it):
        result.setdefault(lang, {})[key] = value
    return result

def csv_to_json(csv_it: Iterable[str], overrides: Overrides, output_dir: Path) -> None:
    output_dir.mkdir(exist_ok=True)

    rows = list(csv.reader(csv_it))
    if len(rows) < 2:
        raise ValueError("CSV must contain at least 2 rows.")

    # Row 0: language names
    # Row 1: locale IDs
    # Column 0: JSON keys
    # Column 1: reference - skip it
    # Column 2+: actual locales

    locale_row = rows[1]

    for column_index in range(2, len(locale_row)):
        locale = locale_row[column_index].strip()
        if locale == "": continue

        translations = {}

        for row in rows[2:]:
            key = row[0]
            if key.startswith('#'): continue
            if key == "": continue

            original = row[1]

            value = row[column_index] if column_index < len(row) else ""
            if original != "" and value == "": continue

            value = escape_re.sub(lambda m: chr(int(m[1], 16)), value)
            translations[key] = value

        if locale in overrides:
            translations |= overrides[locale]

        output_file = output_dir / f"{locale}.json"
        output = json.dumps(translations, ensure_ascii=False, indent=2)
        output = output.replace("\\\\n", "\\n")
        output = output.replace("\\\\\"", '\"')

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"Created: {output_file}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        epilog=(
            "If 'file' is not provided, automatically fetches from Google "
            "Sheets with either the given spreadsheet and sheet IDs or the "
            "script defaults."
        )
    )
    parser.add_argument(
        "file", type=Path, nargs="?", default=None,
    )
    parser.add_argument(
        "overrides_file", type=Path, nargs="?", default=None,
    )
    parser.add_argument(
        "-S", "--spreadsheet-id", type=str, nargs="?", default=default_spreadsheet_id,
        help=f"default: {default_spreadsheet_id!r}",
    )
    parser.add_argument(
        "-s", "--sheet-id", type=str, nargs="?", default=default_main_sheet_id,
        help=f"default: {default_main_sheet_id!r}",
    )
    parser.add_argument(
        "-O", "--overrides-sheet-id", type=str, nargs="?", default=default_overrides_sheet_id,
        help=f"default: {default_overrides_sheet_id!r}",
    )
    parser.add_argument(
        "-o", "--output-dir", type=Path, nargs="?", default=Path("locales"),
        help="default: ./locales",
    )

    args = parser.parse_args()
    main_file: Path | None = args.file
    overrides_file: Path | None = args.overrides_file
    spreadsheet_id: int = args.spreadsheet_id
    main_sheet_id: int = args.sheet_id
    overrides_sheet_id: int = args.overrides_sheet_id
    output_dir: Path = args.output_dir

    overrides_csv: list[str]
    if overrides_file is None:
        overrides = process_overrides_csv(
            fetch_sheet(spreadsheet_id, overrides_sheet_id)
        )
    else:
        with overrides_file.open("r", encoding="utf-8-sig") as f:
            overrides = process_overrides_csv(f)

    if main_file is None:
        csv_to_json(
            fetch_sheet(spreadsheet_id, main_sheet_id),
            overrides,
            output_dir
        )
    else:
        with main_file.open("r", encoding="utf-8-sig") as f:
            csv_to_json(f, overrides, output_dir)
