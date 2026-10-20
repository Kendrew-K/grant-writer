# Codex workflow validation

Checked October 2, 2026 in the local Codex desktop session.

| Check | Result |
|---|---|
| Existing automated suite | 6 tests passed. Used a workspace-local pytest temporary directory. |
| Tracker CLI | Add, top, status, mark, unknown-ID rejection and invalid-date rejection passed using an isolated tracker. |
| Live grants.gov scrape | Completed successfully outside the network-restricted sandbox; returned zero matching open grants. |
| Funder research | Retrieved the current NEA grants page with the web tool. |
| PDF export | Headless Chrome generated a one-page PDF outside the sandbox. Verified extracted text, hidden source comment and rendered layout. |
| Browser form controls | Filled text, multiline answer and dropdown on a local test portal. Verified local draft save. |
| PDF upload | Blocked by Chrome extension setup: ChatGPT extension requires Allow access to file URLs. No upload completed. |
| GitHub connection | Repository listing succeeded and included private repositories. No writes were attempted. |
| Private-data exclusion | Smoke-test tracker and PDF are gitignored under applications/. |

## Remaining prerequisites

- `profile.md` is absent. Build it from the user's facts before drafting or
  determining applicant eligibility. The fictional example is not an applicant.
- In Chrome's extension settings, open ChatGPT's Details and enable
  **Allow access to file URLs** to support attachment uploads. Re-test uploads
  after enabling it. Reference:
  https://developers.openai.com/codex/app/chrome-extension#upload-files
- A chosen live portal still needs its own verification of fields, uploads,
  validation messages and draft persistence. The local test establishes browser
  control, not compatibility with every portal.

Test artifacts are under `applications/codex-smoke/`. The local test server was
stopped after validation. No applicant facts were invented, no real portal
application was created, and nothing was submitted or published to GitHub.
