Research how the following works in this codebase today: $ARGUMENTS

Rules:
- Describe only what exists now. Do not suggest changes, fixes or new features.
- Back every statement with a file reference in the form path/to/file.py:12-30.
- Read files the request mentions in full before exploring further.

Steps:
1. Split the question into a short checklist of areas (endpoints, models, services, tests, config).
2. Explore each area. Follow imports; read the tests to see intended behaviour; check git log if history matters.
3. If a third-party library matters, check its documentation for the version in requirements.txt.
4. Trust the code over existing docs. Note any doc that disagrees with the code.

Write the result to research/<short-topic>.md with:
- Summary (3-6 sentences answering the question)
- Findings by component, with code references
- Data flow: how a request moves through the components
- Tests that cover this area today, and gaps in coverage (as facts, not advice)
