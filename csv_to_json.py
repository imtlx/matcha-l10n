import csv
import json
from pathlib import Path


def csv_to_json(csv_file, output_dir="locales"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    if len(rows) < 2:
        raise ValueError("CSV must contain at least 2 rows.")

    """
    Row 0: language names
    Row 1: locale IDs
    Column 0: JSON keys
    Column 1: reference - skip it
    Column 2+: actual locales
    """

    locale_row = rows[1]

    for column_index in range(2, len(locale_row)):
        locale = locale_row[column_index].strip()

        if not locale:
            continue

        translations = {}

        for row in rows[2:]:
            if not row:
                continue

            key = row[0]

            if not key:
                continue

            value = row[column_index] if column_index < len(row) else ""

            translations[key] = value

        output_file = output_dir / f"{locale}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                translations,
                f,
                ensure_ascii=False,
                indent=2
            )

        print(f"Created: {output_file}")


if __name__ == "__main__":
    csv_to_json("locales.csv")
