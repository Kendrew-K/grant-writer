# Music grant sources

grants.gov is the only source here with an API, and `python grants.py scrape`
covers it. Everything below has to be checked by hand: open the funder's page
(WebFetch first, browser only if that fails), find any call that is open now or
opens within 90 days, check the applicant type against `profile.md`, and record
it:

```bash
python grants.py add --funder "Chamber Music America" --title "Classical Commissioning" \
  --url "<the program page>" --deadline 03/01/2027 --amount 20000 \
  --eligibility "CMA ensemble members" --notes "commission for chamber ensemble"
```

Programs change names and cycles every year. Read the current guidelines
before recording anything, and never record a program from memory.

"Bot-walled" means the site refused a plain HTTP request on 2026-09-25. Use
WebSearch for the program name or open it in the browser instead.

## Federal

| Funder | URL | Funds | Notes |
|---|---|---|---|
| National Endowment for the Arts | https://www.arts.gov/grants | Grants for Arts Projects (Music, Opera, Arts Education), Challenge America | Organizations only, usually a 3-year programming history required. Two parts: grants.gov, then the NEA Applicant Portal. Needs a UEI and active SAM.gov registration, which take weeks. |
| grants.gov | https://www.grants.gov | Everything federal | Covered by `grants.py scrape`. |

## Service organizations (often member-only)

| Funder | URL | Funds | Notes |
|---|---|---|---|
| League of American Orchestras | https://americanorchestras.org | Grant and fellowship programs for orchestras | Most require League membership. |
| Chamber Music America | https://www.chambermusicamerica.org | Commissioning and ensemble grants, classical and jazz | Member ensembles. |
| New Music USA | https://www.newmusicusa.org | Project grants for creators and for organizations | Individuals and organizations. |
| OPERA America | https://www.operaamerica.org | Grants for opera companies and creators | Member companies. |
| Chorus America | https://www.chorusamerica.org | Choral sector programs | Member choruses. |

## Private foundations: new music, commissioning, performance

| Funder | URL | Funds | Notes |
|---|---|---|---|
| Aaron Copland Fund for Music | https://www.coplandfund.org | Performance and recording of contemporary American music | Organizations. |
| Amphion Foundation | https://www.amphionfoundation.org | Contemporary music performance | Small ensembles and presenters. |
| Koussevitzky Music Foundation | https://www.koussevitzky.org | Commissions by performing organizations | Joint application with a composer. |
| Fromm Music Foundation | https://frommfoundation.fas.harvard.edu | Composer commissions | Bot-walled. |
| BMI Foundation | https://www.bmifoundation.org | Awards and scholarships for composers | Individuals. |
| ASCAP Foundation | https://www.ascapfoundation.org | Composer awards and music education | Bot-walled. |

## Music education

| Funder | URL | Funds | Notes |
|---|---|---|---|
| Mockingbird Foundation | https://www.mockingbirdfoundation.org | Music education for children | Small grants, organizations. |
| Save The Music Foundation | https://www.savethemusic.org | Instruments and programs for schools | Schools and districts. Bot-walled. |
| D'Addario Foundation | https://www.daddariofoundation.org | Community music instruction programs | Organizations. |
| NAMM Foundation | https://www.nammfoundation.org | Music education programs and research | Organizations. |

## Regional arts organizations (touring and presenting)

| Funder | URL | Region |
|---|---|---|
| South Arts | https://www.southarts.org | Southeast |
| Mid-America Arts Alliance | https://www.maaa.org | AR, KS, MO, NE, OK, TX. Bot-walled. |
| WESTAF | https://www.westaf.org | West |
| New England Foundation for the Arts | https://www.nefa.org | New England |
| Arts Midwest | https://www.artsmidwest.org | Midwest |
| Mid Atlantic Arts | https://www.midatlanticarts.org | Mid-Atlantic |

## State and local

- **State arts agency.** Nearly every state arts agency funds orchestras and
  music organizations yearly. Directory: https://nasaa-arts.org (pick the
  state from `profile.md`).
- **City or county arts and culture office.** WebSearch
  `"<city from profile.md>" arts and culture grants`.
- **Community foundations** for the applicant's city. WebSearch
  `"<city>" community foundation grants arts`.

## Large or invitation-only

- Andrew W. Mellon Foundation, https://www.mellon.org. Mostly by invitation.
  Record only if the funder publishes an open call.

## Paid databases

Candid Foundation Directory (https://candid.org) and Instrumentl
(https://www.instrumentl.com) list thousands of private funders. Use one only if
the user already has an account and has logged in themselves. Never sign up or
start a trial on their behalf.
