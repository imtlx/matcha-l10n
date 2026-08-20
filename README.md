# Matcha l10n

Localization repository containing locale files and the tooling used to generate them from a CSV translation table.

## How it works

The localization data is maintained in a Google Sheet and exported as a CSV table. The repository contains a script that takes this CSV file and generates the locale files used by the datapack.

The general flow is:

**Google Sheet → CSV → locale generation script → locale files**

## Repository contents

- [Locale files](locales/) - generated localization files for all supported locales.
- [Generation script](csv_to_json.py) - converts the CSV translation table into locale files.
- [GitHub Actions](.github/workflows/) - periodically checks for changes in the source data and commits updated locale files automatically.

## Automatic updates

A GitHub Action runs every hour and checks the source localization data from the Google Sheet.

When the source data has changed:

1. The latest CSV data is retrieved.
2. Locale files are regenerated.
3. Changes are committed to the repository.

This keeps the locale files in sync with the translation table without requiring manual updates.

## Source of truth

The **Google Sheet is the source of truth for localization data**. Locale files in this repository are generated artifacts and should generally not be edited manually.

## Notes

The generated locale files should be treated as build output derived from the localization table. Changes made directly to generated files may be overwritten by the next generation run.
