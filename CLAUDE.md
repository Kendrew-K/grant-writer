# Working in this repo

Notes for Claude Code (or a similar coding agent) opened in this folder. The
project finds music and orchestra grants and fills in their applications for
the user. Everything is plain files: Markdown and one CSV. No server, no
database, no accounts of its own.

## First run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then build `profile.md` (below). It is gitignored because it holds the
applicant's private details.

## Building the profile

`profile.md` is the only source of facts for every application. Copy the shape
of [`example_profile.md`](example_profile.md), whose values are fictional.

When the user describes their organization or themselves in conversation,
write it into `profile.md` yourself, section by section, in their words. Then
list the sections that are still empty or marked ASK and ask about them. A
thin profile makes every application a long list of questions, so it is worth
one thorough interview at the start.

## Commands

```bash
python grants.py scrape            # open federal arts/music grants from grants.gov -> grants.csv
python grants.py add --funder ... --title ... --url ... [--deadline MM/DD/YYYY] [--amount N]
python grants.py top -n 10         # open grants worth working, best first
python grants.py status            # every tracked grant by status
python grants.py mark <id> <status> [--note ...]
python md_to_pdf.py <file>.md      # narrative/budget -> PDF, prints page count
```

Statuses: `new`, `drafting`, `needs-info`, `ready-for-review`, `submitted`,
`skipped`. Change them only through `grants.py mark`, never by editing the CSV.

Most music grants are private, so `scrape` is only a start. Sweep the funders
in [`sources.md`](sources.md) and record open calls with `add`.

## Applying

When the user says "run apply" or names a grant, follow
[`docs/apply-playbook.md`](docs/apply-playbook.md). Read it in full first.

## Rules that are not negotiable

- **Never submit without the user's explicit consent for that grant.** Fill
  the application up to the final review page and stop. Submit only after the
  user has seen it and says to submit that specific grant. A general "go
  ahead", approval of another grant, or silence is not consent. Submitted
  applications usually cannot be withdrawn.
- **Every fact comes from `profile.md`.** No invented numbers, outcomes,
  partners, quotes, budgets or plans. If a question needs something the
  profile does not say, flag it to the user (the playbook's `questions.md`
  step) and wait for their answer. Write the answer into `profile.md` so the
  next grant has it.
- **The user handles all authentication.** When a portal needs a login or a
  new account, stop and ask the user to sign in themselves in the Chrome
  window. Never type, store or ask for passwords, security answers or
  one-time codes, and never create accounts on their behalf.
- **The user owns signatures and certifications.** Never tick an assurance,
  certification, "I agree" or e-signature box, and never fill anything under
  "Always ask the user" in `profile.md`.
- **Never commit personal data.** `profile.md`, `grants.csv` and
  `applications/` are gitignored. Do not add them or paste their contents into
  a commit message.
- **Drive the browser cheaply.** See
  [`docs/cheap-browser-driving.md`](docs/cheap-browser-driving.md). Stop and
  hand a grant back after about 40 browser tool calls, 3 failures on one
  widget, or an unreadable save error.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

The grants.gov calls go through an injectable `fetch` parameter, so the suite
runs offline in under a second. Add a test with any change to scraping,
filtering or the tracker.
