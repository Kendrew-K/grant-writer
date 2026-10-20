# Using Grant Writer in Codex

Open this folder as a local project in Codex. `AGENTS.md` points to
`CLAUDE.md`, which remains the shared source of project rules. Codex uses the
same Python scripts, profile, tracker, application files and apply playbook.
No model API key or rewrite of the project is required.

## Start here

Install the dependencies from `requirements.txt` if they are missing. In
PowerShell, you can use the virtual environment without activating it:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q --basetemp .pytest_cache/codex-temp
```

The local pytest temporary directory avoids restricted system temporary
directories. It contains test fixtures only and is already gitignored.

Tell Codex "help me build my profile", "find grants", "what's the status",
or "apply to <grant>". These are chat instructions, not slash commands.
If `profile.md` is missing, build it from the user's answers using the shape
of `example_profile.md`. Never copy its fictional facts into a real profile.
Research can begin without a profile, but applicant eligibility and drafting
require the user's facts.

## Tool equivalents

| Workflow | Codex approach |
|---|---|
| Research funders and guidelines | Available web search and page retrieval tools; use current funder sources. |
| Track grants | Run `grants.py` from this folder; change status only with `mark`. |
| Draft answers and budgets | Read `profile.md`, save Markdown under `applications/<id>/`, and follow the playbook. |
| Export PDFs | Run `md_to_pdf.py`; Chrome/Chromium and the `markdown` package are required. |
| Fill portals | Use an available browser-control tool with its documented field, navigation and upload operations. |
| Review and submit | Stop at review; follow the playbook's grant-specific consent and user-owned certification rules. |

## Browser adaptation

When the computer-use skill is available, read it before operating a portal.
This Codex session exposes browser controls through `cua_repl`. Follow that
tool's initialization instructions and returned API documentation. Use
supported DOM or accessibility controls when available. Do not translate
Claude's `javascript_tool`, `find`, `computer`, or `file_upload` calls
literally, inject the payloads from the cheap-browser guide, or assume
arbitrary page JavaScript is permitted.

Create a dedicated tab for each grant. Respect a browser or tab the user
explicitly chooses. Ask the user to authenticate in the selected browser and
continue in the same tab after they confirm; do not assume separate browser
surfaces share login sessions. Never inspect or enter credentials.

Use supported file uploads if exposed. If uploads or a portal widget cannot
be controlled, hand the user the saved answers and absolute attachment paths.
If there is no browser-control tool, complete research and drafts and hand
off the portal steps. Web search alone cannot fill an application.

Keep the cheap-browser guide's call budget and recovery limits. Follow the
active browser tool's restrictions wherever its supported operations differ
from that guide. User certifications, signatures and final consent still
belong to the user.

## Verification scope

The offline tests cover grant filtering and tracker behavior. Passing them
does not establish that a live funder portal accepts uploads or saves fields,
or that the grants.gov API is currently reachable. Verify those during the
user's chosen grant workflow. PDF export should also be checked on an actual
document before it is uploaded.
