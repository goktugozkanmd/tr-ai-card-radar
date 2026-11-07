# Changelog

## Unreleased

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
