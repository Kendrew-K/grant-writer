# Grant Writer

Finds music and orchestra grants and fills in the applications with Claude
Code or Codex, using only facts you have given it. It asks you whenever it is unsure,
you log in to every portal yourself, and it never submits until you say so for
that grant.

## What you need

- Python 3.10 or newer
- [Claude Code](https://claude.com/claude-code)
- Google Chrome with the Claude in Chrome extension connected, for filling
  online portals (`claude --chrome`)
- Or Codex instead of Claude Code. It reads `AGENTS.md`, which points it at the
  same rules. See [Using Grant Writer in Codex](docs/codex.md) for setup,
  browser tool equivalents and verification limits.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate           # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
claude
```

Then tell Claude about the organization (or yourself, if you apply as an
individual musician): mission, history, programs, people, audience, budget,
past grants, work samples. It writes this into `profile.md`, following
`example_profile.md`, and asks about anything missing. Every application is
built from that file, so the more complete it is the fewer questions you get
later. You can also edit `profile.md` by hand at any time.

## Everyday use

Say it to Claude or Codex in plain words:

| You say | The agent does |
|---|---|
| "find grants" | Runs `python grants.py scrape`, checks the funders in `sources.md`, and shows you the open ones |
| "apply to &lt;grant&gt;" or "run apply" | Follows `docs/apply-playbook.md`: saves the guidelines, drafts every answer, asks you what it does not know, fills the portal, stops at review |
| "what's the status" | Runs `python grants.py status` |

Where your approval is needed:

1. **Questions.** Anything not in `profile.md` is listed in
   `applications/<grant id>/questions.md` and asked in chat. Your answers are
   saved into `profile.md` for next time.
2. **Login.** When a portal needs you to sign in, Claude stops and asks you to
   do it in Chrome. It never sees or types your passwords.
3. **Submit.** Claude stops at the portal's review page and tells you what is
   there. Look it over, tick the certification boxes yourself, and reply
   "submit &lt;grant id&gt;". Nothing is submitted before that.

## Files

| File | What it is |
|---|---|
| `profile.md` | Your facts. The only source for applications. Private, not committed. |
| `example_profile.md` | The template profile, filled with a fictional orchestra |
| `grants.csv` | Every grant found and where each one stands. Private. |
| `applications/<id>/` | Per grant: `guidelines.md`, `draft.md`, `questions.md`, exported PDFs. Private. |
| `sources.md` | Music funders to check by hand, since most have no API |
| `grants.py` | Command-line tool: scrape, add, top, status, mark |
| `md_to_pdf.py` | Turns a narrative or budget into a PDF and prints its page count |
| `docs/apply-playbook.md` | The step-by-step procedure Claude follows for each application |
| `docs/cheap-browser-driving.md` | How Claude fills web forms without wasting usage |
| `CLAUDE.md` | Rules Claude reads at the start of every session |

## Commands

```bash
python grants.py scrape                 # open federal arts/music grants from grants.gov
python grants.py add --funder "Copland Fund" --title "Performance Program" \
  --url https://www.coplandfund.org --deadline 02/15/2027 --amount 20000
python grants.py top -n 10
python grants.py status
python grants.py mark <id> submitted --note "confirmation 12345"
python md_to_pdf.py applications/<id>/narrative.md
```

`GRANTS_TRACKER` changes where the tracker CSV lives (default `grants.csv`).
`CHROME_PATH` points `md_to_pdf.py` at Chrome if it is not found automatically.

## Things to know

- **Federal grants need registration first.** NEA and other federal grants
  require a UEI and an active SAM.gov registration, plus a grants.gov account
  with the Authorized Organization Representative role. Registration can take
  several weeks, so start it well before a deadline. On grants.gov only that
  representative can press submit.
- **Most music money is private.** `scrape` often finds nothing on a given day
  because federal music deadlines come only a few times a year. The funders in
  `sources.md`, plus your state arts agency and local community foundation,
  are where most orchestra grants are.
- **Programs change every year.** Treat `sources.md` as a starting list and
  have Claude read each funder's current guidelines before applying.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```
