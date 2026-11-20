# Changelog

## Unreleased

- Removed the deprecated `local_dir_use_symlinks` argument from `hf_hub_download` calls in `hf_client.py` to prevent runtime deprecation warnings and keep compatibility with newer `huggingface-hub` releases.
- Replaced raw Python tracebacks in `tr-card-radar audit` and `tr-card-radar audit-list` with clear single-line errors when a resource YAML file is missing, empty, malformed, or a Hub snapshot cannot be fetched.
- Added offline unit tests covering the CLI, Hugging Face client fallback logic, `examples/resources.yaml`, and `examples/local_cards/`.
- Fixed package metadata URLs in pyproject.toml, which still pointed to a placeholder repository address (REPLACE_WITH_USERNAME) instead of the real repository.
- Added a packaging metadata regression test that fails if the placeholder address comes back.
- Fixed license prose scan matching short license ids as substrings, which hid the missing-license blocker on cards that merely contained words such as "submit" or "permit".
- Added stable check ids to every warning in report.json, reuse_warnings.tsv, and report.md; v0.1 checks now use uppercase ids such as LICENSE_MISSING (previously missing_license).

## 0.1.0

- Initial CLI skeleton.
- Added single repository audit command.
- Added resource list audit command.
- Added JSON, Markdown, and TSV report writers.
- Added conservative card metadata checks.
- Added mocked tests.
- Added Turkish AI resource list example based on checked public metadata sources from 2026 06 23.
