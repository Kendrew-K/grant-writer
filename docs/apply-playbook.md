# Apply playbook

The procedure Claude or Codex follows when the user says "run apply" or "apply to
<grant>". Read all of it before starting.

It has three stop points that stay in place however much of the run is
automated:

1. **Login.** The user signs in. Claude never does.
2. **Missing facts.** Anything not in `profile.md` goes to the user as a
   question. Claude never fills it with a guess.
3. **Submit.** Claude submits only after the user says so for that specific
   grant, having seen the finished application.

## Preflight

1. `profile.md` exists and is filled in. If it still holds the fictional
   example values from `example_profile.md`, stop and interview the user
   instead (see "Building the profile" in `CLAUDE.md`).
2. Run `python grants.py status` to see what is already in progress, so no
   grant is worked twice.
3. If the queue needs refreshing, run `python grants.py scrape`, then sweep
   `sources.md` and `add` whatever is open. See "Finding grants" below.

## Finding grants

- `python grants.py scrape` pulls open federal arts and music opportunities
  from grants.gov. On most days this returns few or none. That is normal: the
  NEA opens its main music deadlines only a couple of times a year.
- Most orchestra and music money is private, regional or state. Work down
  `sources.md`, read each funder's current guidelines, and record every open or
  upcoming program with `python grants.py add ...`.
- Before recording, check eligibility against `profile.md`: applicant type
  (organization, individual, fiscally sponsored), location, budget size,
  membership requirements, years of operating history. Record an ineligible
  program only if the user might want to know about it, with
  `status skipped` and a note saying why.
- `python grants.py top` lists what is worth working, most relevant first.
  Show the user this list and let them choose which grants to apply for. Do
  not start drafting grants they have not picked.

## Per grant

Work in `applications/<grant id>/`. Create the folder when starting.

### 1. Save the guidelines

Fetch the full guidelines and the application questions (available web retrieval first,
the browser only if that fails) and save them as `guidelines.md`. Include
every question verbatim, its word or character limit, required attachments,
the deadline with its time zone, and the eligibility rules.

`python grants.py mark <id> drafting`

### 2. Check eligibility again

Compare the full guidelines with `profile.md`. If the applicant does not
qualify, run `python grants.py mark <id> skipped --note "<reason>"`, tell the
user, and move on.

### 3. Draft every answer from `profile.md` only

Write `draft.md`: one section per application question, headed with the
question text exactly as the funder wrote it, and the limit.

- Every fact must come from `profile.md`. After each answer add a comment
  naming where it came from, which the user can check and the PDF export
  hides:

  ```markdown
  ## Describe the project and its goals. (2,000 characters)

  String Beginnings gives 60 students ages 10 to 13 ...

  <!-- source: profile.md > Programs > String Beginnings -->
  ```

- Mirror the funder's own priorities and wording from `guidelines.md`, but
  never claim something `profile.md` does not say. No invented numbers,
  outcomes, partners, quotes or plans.
- Check every limit. Characters include spaces unless the funder says
  otherwise:
  `python -c "import sys; print(len(open(sys.argv[1], encoding='utf-8').read()))" answer.txt`
- Budget tables go in `budget.md`. Line items and totals come from the user,
  never from Claude's estimate.
- Write plainly: no em dashes, no filler, no stacked adjectives. Reviewers
  score substance.

### 4. Flag everything you could not answer

Anything the grant asks that `profile.md` does not answer, or that sits under
"Always ask the user", goes in `questions.md`:

```markdown
- [ ] Q3 "What is the total project budget?" Not in profile.md. Needed for the budget form.
- [ ] Q7 "Upload a letter of support." Who should write it?
```

Then:

- `python grants.py mark <id> needs-info --note "3 open questions"`
- Post the questions to the user in chat, all at once, numbered. If the
  `PushNotification` tool is available, send one short line as well, e.g.
  `Riverside Community Foundation: 3 questions before I can finish`.
- When the user answers, write each answer into `profile.md` (so the next
  grant has it), tick it off in `questions.md`, and update `draft.md`.

Carry on with other grants while waiting. Do not guess to get unblocked.

### 5. Export attachments

Narratives, budgets and similar uploads:
`python md_to_pdf.py applications/<id>/narrative.md`. It prints the page
count. If a page limit is exceeded, cut the least relevant material and export
again.

### 6. Log in: the user does it

When the portal (Submittable, SmartSimple, Fluxx, Foundant, SurveyMonkey
Apply, grants.gov Workspace, the NEA Applicant Portal and so on) shows a login
or registration page:

- Stop. Tell the user which site needs them, and ask them to sign in or create
  the account themselves in the Chrome window, then say "logged in".
- Never type, store, or ask for a password, security question or one-time
  code. Never create an account for them. Never click through Login.gov or
  SAM.gov steps for them.
- Then continue in the same tab. The browser runs on their own Chrome
  profile, so their session carries over.

### 7. Fill the portal

Use Claude in Chrome and follow `docs/cheap-browser-driving.md`: read fields
with a `javascript_tool` dump, set them in one call, and do not fill forms
through screenshots.

On Codex, follow `docs/codex.md` and the active browser tool's documentation.
Use its supported field controls and uploads; the Claude-specific payloads
in the cheap-browser guide are not required and may not be permitted.
If browser control is unavailable, stop after step 5 and hand the user the
drafts. The stop rules and the no-password, no-submit rules stay the same.

- Paste each answer from `draft.md` into its matching field. Check the portal's
  own character counter where it has one.
- Upload the exported PDFs with the `file_upload` tool and an absolute path.
  If that fails, give the user the absolute paths and ask them to drag the
  files in. Never click an upload button that opens an OS file dialog: the
  browser tools cannot drive it.
- Save as draft after each page if the portal allows it.
- Leave blank anything still open in `questions.md`, and never tick
  certifications, assurances or signature boxes. Those belong to the user.

Stop rules. Hand the grant back with the filled values listed when:

- one grant passes about 40 browser tool calls,
- one widget fails 3 times,
- the portal rejects a save with an error you cannot read, or
- recovering would need a page reload that could lose unsaved work.

### 8. Stop at review and ask for consent

At the portal's final review page:

1. Take one screenshot for the record.
2. Run `python grants.py mark <id> ready-for-review`.
3. Tell the user, in one message: the grant, the deadline, the amount
   requested, where the review page is, anything left blank and why, and the
   boxes only they can tick. Ask them to review it.
4. **Wait.** Submit only when the user replies with an explicit instruction to
   submit this grant, such as "submit gg-363514" or "yes, submit the Copland
   application". Approval of a different grant, an earlier "go ahead", or
   silence does not count. A submitted grant application usually cannot be
   withdrawn or edited.
5. If they ask for changes, make them and repeat this step.

For federal grants on grants.gov, only the registered Authorized
Organization Representative can submit. Hand the user the finished workspace
and let them press submit themselves.

### 9. Record it

After the user confirms submission (or submits it themselves):
`python grants.py mark <id> submitted --note "confirmation <number>"`

Save any confirmation email or number in `applications/<id>/confirmation.md`.

## After the run

Summarize for the user: grants submitted, grants waiting on their review,
open questions per grant, and upcoming deadlines from `python grants.py top`.
