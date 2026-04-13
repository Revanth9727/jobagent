# architecture.md — Job Application Agent
### System design reference · April 2026

---

## The core idea in one sentence

You add companies. The agent watches them, scores what they post, and asks your permission before doing anything consequential.

---

## The loop

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPANY REGISTRY                          │
│   candidate → tracked → priority_tracked → ignored_auto     │
└──────────────────────┬──────────────────────────────────────┘
                       │ enrich once per company
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    ATS ENRICHER                              │
│   careers page finder → Greenhouse/Lever/Ashby detection     │
│   unknown fallback → user corrects with /fix_ats             │
└──────────────────────┬──────────────────────────────────────┘
                       │ daily
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    POLLER (daily)                            │
│   Primary: Greenhouse/Lever/Ashby JSON APIs (no auth)        │
│   Supplemental: Arbeitnow (DE), MyCareersFuture (SG), RSS   │
│   Output: Job records + Observation rows                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    DEDUPLICATION                             │
│   Source dedupe: URL match → title+company+location hash    │
│   History check: applied (90d) → block · skipped → warn     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    HARD RULES FILTER                         │
│   1. age > 21 days → skip                                   │
│   2. wrong country → skip                                    │
│   3. sponsorship blocked language → skip                     │
│   4. junior/intern in title → skip                          │
│   5. source duplicate → skip                                 │
│   6. applied same company < 90 days → skip                  │
│   7. previously skipped → soft warn, continue               │
│   8. thin stack match → -10 penalty, continue               │
└──────────────────────┬──────────────────────────────────────┘
                       │ jobs that pass
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    HAIKU SCORER                              │
│   Model: claude-haiku-4-5-20251001                          │
│   Input: profile_context + job description (3,000 char max) │
│   Output: score 0-100, reason, key_matches, red_flags       │
│   Cost: ~$0.00025 per job                                   │
└──────────┬──────────────────┬───────────────────────────────┘
           │ 75+              │ 65-74              │ <65
           ▼                  ▼                    ▼
    Immediate          Daily digest           Silently
    Telegram           batch (8am)            dropped
    alert
           │                  │
           ▼                  ▼
┌──────────────────┐  ┌──────────────────────────────────────┐
│ COMPANY PROMOTER │  │ /request_docs [id] on demand         │
│ Run after each   │  └──────────────────────────────────────┘
│ poll+score cycle │
│ candidate→tracked│
│ tracked→priority │
│ →ignored_auto    │
└──────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                 TELEGRAM APPROVAL GATE                       │
│   Pre-approval message contains:                            │
│   - Score + 2-sentence reason                               │
│   - Key matches + red flags                                 │
│   - 3 role-specific talking points (Haiku)                  │
│   - Direct application URL                                  │
│   Buttons: [✅ APPLY] [❌ SKIP] [✏️ EDIT]                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ APPLY tap
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    ATS ROUTER                                │
│   Greenhouse / Lever / Ashby / direct → manual_ready        │
│   Workday / unknown → manual_assisted                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 SONNET WRITER (post-approval)                │
│   Model: claude-sonnet-4-6                                  │
│   Two parallel calls (asyncio.gather):                      │
│   1. Resume rewrite → .docx via python-docx                 │
│   2. Cover letter → .txt                                    │
│   Tone: adjusted by country (USA/SG/NL/DE/SE/CH)           │
│   Cost: ~$3 per pair                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
  manual_ready                manual_assisted
  Docs + link sent            Docs + talking points
  to Telegram                 + link sent to Telegram
  You submit the form         5-minute Workday paste-in
          │                         │
          └────────────┬────────────┘
                       │ You reply "done"
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 CLOSED-LOOP CONFIRMATION                     │
│   Reply parser matches reply to telegram_message_id         │
│   Sets confirmed_at, status → applied                       │
│   Updates daily digest funnel metrics                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Data model

### Three tables

```
observations                    companies                       jobs
────────────                    ─────────                       ────
id (PK)                         id (PK)                         id (PK)
run_id                          name                            company_id (FK)
source                          canonical_name                  canonical_url (unique)
source_type                     careers_url                     normalized_hash (unique)
company_id (FK nullable)        ats_type                        title
job_id (FK nullable)            ats_board_url                   location
raw_url                         ats_confirmed                   country
raw_title                       discovery_source                description
raw_company                     tracking_status                 posted_at
raw_location                    first_seen_at                   first_seen_at
raw_payload (JSON)              last_seen_at                    last_seen_at
observed_at                     times_seen                      age_days
                                best_role_score                 is_repost
                                roles_above_75                  source_type
                                ignored_at                      source_confidence
                                reactivated_at                  hard_filtered
                                notes                           hard_filter_reason
                                                                history_status
                                                                score
                                                                score_reason
                                                                key_matches (JSON)
                                                                red_flags (JSON)
                                                                talking_points (JSON)
                                                                status
                                                                ats_type
                                                                route
                                                                resume_path
                                                                cover_letter_path
                                                                approved_at
                                                                applied_at
                                                                confirmed_at
                                                                telegram_message_id
```

### Company status flow
```
          /add_company or seed load
                    │
                    ▼
              [candidate]
                    │
        seen 2+ runs OR any 75+ job
                    │
                    ▼
              [tracked] ◄──────────── auto-reactivation
                    │                 (new 75+ job)
         2+ jobs 75+ OR any 85+          │
                    │                    │
                    ▼                    │
          [priority_tracked]       [ignored_auto]
                                         ▲
                               60 days, no 65+ job
```

### Job status flow
```
scraped ──hard rules──► hard_filtered
   │
   └──Haiku score──► approved (75+) ──APPLY──► applying ──reply "done"──► applied
                  ├─► digest (65-74)                                    ├─► interviewing
                  └─► dropped (<65)            SKIP ──────────────────► skipped
                                                                        ├─► ghosted
                                                                        ├─► rejected
                                                                        └─► offered
```

---

## File structure

```
job-agent/
├── agents/
│   ├── enricher.py      One-time per company: careers page → ATS detection
│   ├── poller.py        Daily: ATS JSON APIs + supplemental boards
│   ├── promoter.py      Company tier promotion after each poll+score
│   ├── scorer.py        Hard rules + Haiku scoring
│   └── writer.py        Sonnet resume + cover letter (post-approval only)
├── core/
│   ├── config.py        .env loader via pydantic-settings
│   ├── database.py      SQLAlchemy models + CRUD helpers
│   ├── deduper.py       Source dedupe + application history check
│   ├── profile.py       Profile loader + profile_to_scoring_context()
│   ├── router.py        ATS classifier → manual_ready | manual_assisted
│   └── telegram_bot.py  Approval gate + /setup + all commands
├── prompts/
│   ├── score_jd.txt     Haiku scoring template (uses {profile_context})
│   ├── rewrite_resume.txt  Sonnet resume template
│   ├── cover_letter.txt    Sonnet cover letter template
│   └── talking_points.txt  Haiku talking points template
├── data/
│   ├── candidate_profile.json  ← .gitignore (written by /setup)
│   ├── base_resume.json        ← .gitignore (written by /setup)
│   ├── company_seed_list.json  ← in git (no personal data)
│   ├── jobs.db                 ← .gitignore
│   ├── outputs/                ← .gitignore (generated docs)
│   └── calibration/
│       └── validation_30.csv   ← .gitignore (your 30-job scores)
├── tests/
│   ├── test_scorer.py   Calibration test: your scores vs Claude scores
│   └── test_deduper.py  Dedup logic unit tests
├── .env                 ← .gitignore (API keys)
├── .env.example         ← in git (placeholders)
├── CLAUDE.md            ← .gitignore (personal context)
├── CLAUDE.example.md    ← in git (template)
├── AIRules.md           ← in git (no personal data)
├── architecture.md      ← in git (no personal data)
├── plan.md              ← in git (no personal data)
├── setup_profile.py     CLI onboarding fallback
├── requirements.txt
├── run.sh               Evening cron command
└── main.py              Entry point + CLI flags
```

---

## Scraping sources

| Source | Type | Countries | Method | Cost | Reliability |
|--------|------|-----------|--------|------|-------------|
| Greenhouse JSON API | Primary | All | `boards.greenhouse.io/v1/boards/{slug}/jobs` | Free | High |
| Lever JSON API | Primary | All | `api.lever.co/v0/postings/{slug}` | Free | High |
| Ashby JSON API | Primary | All | `jobs.ashbyhq.com/api/posting-api/job-board/{slug}` | Free | High |
| Arbeitnow | Supplemental | DE | `arbeitnow.com/api/job-board-api` | Free | Medium |
| MyCareersFuture | Supplemental | SG | `api.mycareersfuture.gov.sg/v2/jobs` | Free | Medium |
| LinkedIn RSS | Supplemental | All | Feedparser, no auth | Free | Low |

**Note:** Supplemental sources are weak bonus inputs. Never rely on them as primary coverage. They occasionally surface roles at companies not in the seed list.

---

## AI models

| Model | Used for | When | Cost |
|-------|---------|------|------|
| `claude-haiku-4-5-20251001` | Job scoring | Every job passing hard rules | ~$0.00025/job |
| `claude-haiku-4-5-20251001` | Talking points | Every 75+ job (pre-approval) | ~$0.01/job |
| `claude-sonnet-4-6` | Resume rewrite | Post-APPLY tap only | ~$1.50/call |
| `claude-sonnet-4-6` | Cover letter | Post-APPLY tap only (parallel) | ~$1.50/call |

Monthly estimate at 15 apps/day: ~$15–20

---

## Telegram commands

| Command | When | What it does |
|---------|------|-------------|
| `/setup` | First run or edit | Onboarding ConversationHandler |
| `/status` | Any time | Today's pipeline summary |
| `/add_company Name` | Spot a new company | Enriches and adds to registry |
| `/fix_ats id type` | ATS misdetected | Corrects ATS type, marks confirmed |
| `/request_docs id` | 65-74 digest job | Generates resume + CL on demand |
| `/applied id` | Forgot to reply | Fallback confirmation |
| `/cancel` | Mid-conversation | Clears state, ends conversation |
| APPLY button | Job notification | Triggers Sonnet writer |
| SKIP button | Job notification | Marks skipped, notes company |
| EDIT button | Job notification | Re-generates talking points |
| Reply "done" | After submitting | Closes loop, sets confirmed_at |

---

## ATS detection strategy

The enricher tries these in order, stopping at first success:

```
1. hint_url provided → check directly, detect from URL pattern
2. Try boards.greenhouse.io/{slug}     → if 200: greenhouse
3. Try jobs.lever.co/{slug}            → if 200: lever
4. Try jobs.ashbyhq.com/{slug}         → if 200: ashby
5. Try {slug}.com/careers              → fetch HTML, scan for ATS signatures
6. Try {slug}.com/jobs                 → same
7. Fallback: save as unknown, store careers_url if found
```

Slug generation: `name.lower().replace(" ", "-").replace("'", "")`
Accuracy: ~65-70% correct on first pass for well-known companies
Manual correction: `/fix_ats [company_id] [type]`

---

## Scoring prompt design

All scoring prompts are templates in `prompts/`. They use `{profile_context}` — never hardcoded candidate data.

`profile_to_scoring_context()` renders the profile into a standardised string:
```
CANDIDATE: {name}, {title}
EXPERIENCE: {years}+ years. {summary}
KEY METRICS:
- {metric1}
- {metric2}
CORE SKILLS: {top 10 core skills, ordered by importance}
STACK: {top 10 stack skills, ordered by importance}
EMPLOYER: {current_employer}, {location}
VISA: {visa_status} — needs sponsorship: {bool}
TARGET COUNTRIES: {countries}
```

**Skill ordering matters.** The first 10 skills in `candidate_profile.json` are what Claude sees. Put the most differentiating skills first — not alphabetically, not by frequency, but by how much they differentiate this candidate from other senior AI engineers.

---

## Cost model

```
Daily at 15 apps/day:
  Haiku scoring:        ~100 jobs × $0.00025 = $0.025/day
  Haiku talking points: ~20 jobs × $0.01    = $0.20/day
  Sonnet resume:        ~10 approvals × $1.50 = $15/day
  Sonnet cover letter:  ~10 approvals × $1.50 = $15/day (parallel, not additive to time)

Monthly:
  Haiku:  ~$7
  Sonnet: ~$90 (at 10 approvals/day)
  APIs:   $0
  Total:  ~$15-20/month
```

The Sonnet cost dominates. It is controlled by the APPLY tap rate — you only pay for documents on jobs you explicitly choose to apply to.

---

## Security model

```
What's in git (safe to commit):
  All .py files
  All .txt prompt templates (zero personal data — only {variables})
  company_seed_list.json
  .env.example
  CLAUDE.example.md
  AIRules.md, architecture.md, plan.md
  requirements.txt, run.sh

What's in .gitignore (never commit):
  .env                   ← API keys
  CLAUDE.md              ← personal context + project state
  data/candidate_profile.json  ← all personal data
  data/base_resume.json        ← resume content
  data/jobs.db                 ← all job and application data
  data/outputs/                ← generated resumes and cover letters
  data/calibration/            ← your manual scoring data
```

**The rule:** If a file contains your name, your employer, your metrics, your API keys, or your application history — it does not go in git. Everything that goes in git could be read by anyone.
