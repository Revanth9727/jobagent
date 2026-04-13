# Job Application Agent — Complete Final Guide
### Revanth Gollapudi · Claude Code + Copilot + Windsurf · April 2026

---

## What this is

A monitoring agent built on a curated company registry.

**The loop:** company registry → enrich once (find careers page, detect ATS) → poll daily. The enricher is a one-time step per company, not a recurring loop. The poller is what runs every day.

**How companies enter the registry:** You add them — either upfront via the seed list or on the fly with `/add_company`. The agent never discovers companies autonomously.

**Supplemental inputs:** Arbeitnow (DE), MyCareersFuture (SG), and RSS feeds are weak secondary inputs that occasionally surface roles at companies you haven't seeded. They are not core discovery. Don't rely on them — treat anything they return as a bonus.

**You are the discovery layer. The agent is the monitoring layer.**

---

## All decisions — final

| Decision | Answer |
|----------|--------|
| Phase 1 scope | Scraper + scorer + resume/CL writer + Telegram gate |
| Daily time budget | 2+ hrs/evening |
| Hosting | Your laptop, Phase 1 |
| Countries week 1–2 | USA only |
| Countries week 5+ | Add Singapore + Netherlands |
| Volume week 1–2 | 3–5/day |
| Volume week 3–4 | 8–10/day |
| Volume week 5+ | 12–15/day max |
| Manual validation gate | 30 jobs scored by hand before scoring code touches real data |
| Validation job source | You find them on LinkedIn/Glassdoor |
| Primary scraping | ATS JSON APIs (Greenhouse/Lever/Ashby) — core, reliable, daily |
| Supplemental inputs | Arbeitnow (DE), MyCareersFuture (SG), RSS — weak secondary layer, not core discovery |
| SerpAPI | Cut entirely — not needed |
| Company seed list | 75 companies curated upfront · /add_company command for on-the-fly adds |
| Company add flow | /add_company [name] → enricher finds careers page → detects ATS → marks tracked → polls daily |
| LinkedIn | Saved cookies only if at all — never automate login |
| Source dedupe | URL first → title+company+location hash fallback |
| Application-history dupe (applied) | Hard block, silent drop, 90-day window |
| Application-history dupe (skipped) | Soft warn — surfaces with "previously seen" flag |
| Hard rules (before Claude) | Age >21 days, wrong geography, sponsorship mismatch, seniority mismatch, source duplicate, history duplicate → hard skip · thin stack match → -10 score penalty |
| Age filter band | 10–21 days = deprioritize · >21 days = hard skip |
| Repost detection | Same title+company seen in last 60 days = skip |
| Scoring model | Haiku for scoring (cheap) · Sonnet only post-approval |
| Score routing — immediate | 75+ → Telegram immediately |
| Score routing — digest | 65–74 → daily digest batch |
| Score routing — drop | <65 → silent drop |
| Tailored docs fire when | 75+ only, after APPLY tap |
| 65–74 docs | Not generated automatically · `/request_docs [job_id]` on demand |
| Telegram packet (pre-approval) | Score + reason · key matches + red flags · 3 role-specific talking points |
| Post-approval | Sonnet generates resume + cover letter bundled |
| Closed loop | Reply to Telegram message → `confirmed_at` logged, status → applied |
| Company tiers | `candidate` → `tracked` → `priority_tracked` → `ignored_auto` |
| Candidate → tracked | Seen in 2+ separate runs OR any 75+ role |
| Tracked → priority_tracked | 2+ roles score 75+ OR any single role scores 85+ |
| Auto-ignore | 60 days with no 65+ role → `ignored_auto` |
| Auto-reactivate | New 75+ role at ignored company → `ignored_auto → candidate` · must re-earn tracked normally |
| Priority fast-path | New role only, first-seen, 75+, at priority_tracked company → immediate alert outside digest |
| ATS detection | Auto-detect via HTTP fingerprinting · you correct if wrong |
| Workday / unknown ATS | `manual_assisted` permanently — Telegram sends prepped packet |
| Greenhouse/Lever/Ashby/direct | `manual_ready` (Phase 1) → `auto_apply` (Phase 2 when Playwright exists) · Phase 1: docs pre-generated, you submit manually |
| Monitoring cadence | Daily poll for all tracked companies |
| Digest includes | Company registry updates: new tracked + priority_tracked promotions |
| Security | CLAUDE.example.md + .env.example in git · real files in .gitignore · no secrets ever committed |

---

## Data model — three entities

### `observations` — the foundation

Every time a company or job is seen, write a row. This is what makes "seen 2+ times" rules implementable and debugging possible.

```python
class Observation(Base):
    __tablename__ = "observations"

    id            = Column(Integer, primary_key=True)
    run_id        = Column(String, nullable=False)   # UUID per pipeline run
    source        = Column(String, nullable=False)   # greenhouse | lever | ashby | arbeitnow | mycareersfuture | rss | manual_add
    source_type   = Column(String, nullable=False)   # discovery | monitoring | hybrid
    company_id    = Column(Integer, ForeignKey("companies.id"), nullable=True)
    job_id        = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    raw_url       = Column(String)
    raw_title     = Column(String)
    raw_company   = Column(String)
    raw_location  = Column(String)
    raw_payload   = Column(JSON)                     # full source response
    observed_at   = Column(DateTime, default=datetime.utcnow)
```

### `companies` — the registry

```python
class Company(Base):
    __tablename__ = "companies"

    id                  = Column(Integer, primary_key=True)
    name                = Column(String, nullable=False)
    canonical_name      = Column(String)             # normalized for dedup
    careers_url         = Column(String)
    ats_type            = Column(String)             # greenhouse | lever | ashby | workday | direct | unknown
    ats_board_url       = Column(String)             # e.g. boards.greenhouse.io/anthropic
    ats_confirmed       = Column(Boolean, default=False)   # True after you verify auto-detect
    discovery_source    = Column(String)
    tracking_status     = Column(String, default="candidate")
    # candidate | tracked | priority_tracked | ignored_auto | ignored_manual
    first_seen_at       = Column(DateTime)
    last_seen_at        = Column(DateTime)
    times_seen          = Column(Integer, default=1)
    best_role_score     = Column(Float, nullable=True)
    roles_above_75      = Column(Integer, default=0)
    ignored_at          = Column(DateTime, nullable=True)
    reactivated_at      = Column(DateTime, nullable=True)
    notes               = Column(Text)
```

### `jobs` — canonical records

```python
class Job(Base):
    __tablename__ = "jobs"

    id                  = Column(Integer, primary_key=True)
    company_id          = Column(Integer, ForeignKey("companies.id"))
    canonical_url       = Column(String, unique=True, nullable=False)
    source_urls         = Column(JSON)               # all URLs that resolve to this job
    normalized_hash     = Column(String, unique=True) # title+company+location hash
    title               = Column(String)
    location            = Column(String)
    country             = Column(String)             # USA | SG | NL | DE | SE | CH
    description         = Column(Text)
    posted_at           = Column(DateTime)
    first_seen_at       = Column(DateTime)
    last_seen_at        = Column(DateTime)
    age_days            = Column(Integer)
    is_repost           = Column(Boolean, default=False)
    source_type         = Column(String)             # ats_api | free_board | manual_add
    source_confidence   = Column(String)             # discovery | confirmed

    # Hard filter result
    hard_filtered       = Column(Boolean, default=False)
    hard_filter_reason  = Column(String, nullable=True)

    # Duplicate checks
    source_deduped      = Column(Boolean, default=False)  # collapsed from multiple sources
    history_status      = Column(String, nullable=True)   # None | applied_block | skipped_warn

    # Scoring
    score               = Column(Float, nullable=True)
    score_reason        = Column(Text, nullable=True)
    key_matches         = Column(JSON, nullable=True)
    red_flags           = Column(JSON, nullable=True)
    talking_points      = Column(JSON, nullable=True)

    # Status flow
    status = Column(String, default="scraped")
    # scraped → hard_filtered | scored → approved | digest | dropped
    # approved → applying → applied | skipped
    # applied → interviewing | ghosted | rejected | offered

    # ATS routing
    ats_type            = Column(String, nullable=True)  # greenhouse | lever | ashby | workday | unknown — set by router
    route               = Column(String, nullable=True)  # manual_ready | manual_assisted (Phase 1) · auto_apply added Phase 2

    # Documents — generated post-approval only
    resume_path         = Column(String, nullable=True)
    cover_letter_path   = Column(String, nullable=True)

    # Tracking
    approved_at         = Column(DateTime, nullable=True)
    applied_at          = Column(DateTime, nullable=True)
    confirmed_at        = Column(DateTime, nullable=True)  # set on Telegram reply
    telegram_message_id = Column(String, nullable=True)    # for reply parsing
```

---

## Project structure

```
job-agent/
├── agents/
│   ├── enricher.py         # Careers page finder + ATS detector + /add_company handler
│   ├── poller.py           # Daily ATS polling (Greenhouse/Lever/Ashby) + supplemental boards
│   ├── enricher.py         # ATS detection + company registry update
│   ├── promoter.py         # Company promotion evaluator
│   ├── scorer.py           # Hard rules → Haiku → routing
│   └── writer.py           # Resume + CL (Sonnet, post-approval)
├── core/
│   ├── database.py         # SQLAlchemy models + CRUD
│   ├── config.py           # .env loader (pydantic-settings)
│   ├── deduper.py          # Source dedupe + history duplicate check
│   ├── router.py           # ATS classifier + manual_ready/manual_assisted routing (auto_apply Phase 2)
│   ├── profile.py          # Profile loader — reads candidate_profile.json
│   └── telegram_bot.py     # Gate: APPLY/SKIP/EDIT + reply parser + /request_docs + /setup onboarding
├── prompts/
│   ├── score_jd.txt        # Template — {profile.summary} injected at runtime
│   ├── rewrite_resume.txt  # Template — {profile} injected at runtime
│   ├── cover_letter.txt    # Template — {profile} injected at runtime
│   └── talking_points.txt  # Template — {profile} injected at runtime
├── data/
│   ├── candidate_profile.json   # Written by Telegram /setup — never in git
│   ├── candidate_profile.example.json  # Placeholder template — in git
│   ├── base_resume.json         # Written by Telegram /setup — never in git
│   ├── company_seed_list.json   # Curated starter companies
│   ├── jobs.db                  # never in git
│   ├── outputs/                 # never in git
│   └── calibration/
│       └── validation_30.csv    # never in git
├── tests/
│   ├── test_deduper.py
│   ├── test_scorer.py
│   ├── test_promoter.py
│   └── test_enricher.py
├── .env                    # never in git
├── .env.example            # in git — placeholders only
├── CLAUDE.md               # never in git
├── CLAUDE.example.md       # in git — placeholders only
├── .gitignore
├── requirements.txt
└── main.py
```

---

## .gitignore — set before first commit

```gitignore
.env
CLAUDE.md

# Candidate data — never commit personal information
data/candidate_profile.json
data/base_resume.json
data/jobs.db
data/outputs/
data/calibration/

# Python
__pycache__/
*.pyc
venv/
.venv/

# OS
.DS_Store
```

---
## Candidate profile system

The agent is fully generic. No candidate data lives in code or prompts. Everything is loaded at runtime from `data/candidate_profile.json`, written by the Telegram `/setup` onboarding flow. Swap the profile file and the whole system adapts to any candidate.

### Profile schema (data/candidate_profile.example.json)

```json
{
  "identity": {
    "name": "",
    "current_title": "",
    "current_employer": "",
    "location": "",
    "email": "",
    "phone": "",
    "linkedin_url": "",
    "portfolio_url": "",
    "github_url": ""
  },
  "experience": {
    "years_total": 0,
    "summary": "",
    "key_metrics": [],
    "employers": []
  },
  "skills": {
    "core": [],
    "stack": [],
    "cloud": [],
    "frameworks": []
  },
  "search_config": {
    "target_countries": [],
    "target_cities": {},
    "work_mode_preferences": ["remote", "hybrid"],
    "target_roles": [],
    "visa_status": "",
    "needs_sponsorship": true,
    "min_score_immediate": 75,
    "min_score_digest": 65,
    "max_daily_apps": 15,
    "age_hard_filter_days": 21,
    "history_block_days": 90,
    "auto_ignore_days": 60
  },
  "tone_preferences": {
    "USA": "direct and achievement-focused",
    "SG": "achievement-focused with enthusiasm for local ecosystem",
    "NL": "warm but professional",
    "DE": "formal and precision-focused",
    "SE": "collaborative and values-aligned",
    "CH": "precise and quality-focused"
  },
  "profile_version": 1,
  "created_at": "",
  "updated_at": ""
}
```

### Profile loader (core/profile.py)

```python
import json
from pathlib import Path

PROFILE_PATH = Path("data/candidate_profile.json")

def load_profile() -> dict:
    """Load candidate profile. Raises clear error if not found."""
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            "No candidate profile found. Run /setup in Telegram to create one."
        )
    return json.loads(PROFILE_PATH.read_text())

def save_profile(profile: dict) -> None:
    PROFILE_PATH.parent.mkdir(exist_ok=True)
    PROFILE_PATH.write_text(json.dumps(profile, indent=2))

def profile_to_scoring_context(profile: dict) -> str:
    """
    Render profile into a prompt-injectable string.
    This is what replaces all hardcoded candidate details in every prompt.

    Note on skill ordering: skills are taken in list order.
    Put your most differentiating skills first in the profile —
    the prompt context is token-limited so ordering matters.
    """
    p = profile
    skills_str  = ", ".join(p["skills"]["core"][:10])   # top 10 — put most differentiating first
    stack_str   = ", ".join(p["skills"]["stack"][:10])  # top 10 — order intentionally
    metrics_str = "\n".join(f"- {m}" for m in p["experience"]["key_metrics"])
    countries   = ", ".join(p["search_config"]["target_countries"])
    return f"""
CANDIDATE: {p["identity"]["name"]}, {p["identity"]["current_title"]}
EXPERIENCE: {p["experience"]["years_total"]}+ years. {p["experience"]["summary"]}
KEY METRICS:
{metrics_str}
CORE SKILLS: {skills_str}
STACK: {stack_str}
EMPLOYER: {p["identity"]["current_employer"]}, {p["identity"]["location"]}
VISA: {p["search_config"]["visa_status"]} — needs sponsorship: {p["search_config"]["needs_sponsorship"]}
TARGET COUNTRIES: {countries}
""".strip()
```

### How prompts use the profile

Every prompt template uses `{profile_context}` as the single candidate-specific variable. Nothing else is hardcoded anywhere in the codebase.

**prompts/score_jd.txt:**
```
Score this job for the following candidate.

{profile_context}

JOB: {title} at {company}, {location}
POSTED: {age_days} days ago
PREVIOUSLY SEEN: {previously_seen}
DESCRIPTION:
{description}

Return JSON only — no prose, no markdown:
{{
  "score": <int 0-100>,
  "reason": "<2 sentences>",
  "key_matches": ["<match>"],
  "red_flags": ["<flag>"],
  "sponsorship_friendly": <bool>,
  "seniority_match": <bool>
}}

Scoring: 85-100=exceptional, 75-84=strong, 65-74=good, <65=skip
```

**prompts/rewrite_resume.txt:**
```
Rewrite the following resume for this specific job.

CANDIDATE PROFILE:
{profile_context}

BASE RESUME (JSON):
{base_resume_json}

TARGET JOB: {title} at {company}, {location} ({country})
JOB DESCRIPTION:
{description}

INSTRUCTIONS:
- Reorder bullets by relevance to this role
- Rewrite summary (2-3 sentences) using this company's language
- Emphasise skills the JD explicitly mentions that the candidate has
- Tone: {tone}
- Keep to 1 page — cut lower-priority bullets if needed
- Never fabricate or exaggerate metrics
Return same JSON structure as base resume.
```

**prompts/cover_letter.txt:**
```
Write a cover letter for {candidate_name} applying to {company} for {title}.

CANDIDATE:
{profile_context}

JOB DESCRIPTION:
{description}

TONE: {tone}

FORMAT:
- 3 paragraphs, max 300 words total
- Para 1: hook + why this specific company + strongest relevant achievement
- Para 2: 2 skill matches with a metric each
- Para 3: why this location/market + call to action
Return plain text only.
```

**prompts/talking_points.txt:**
```
Generate 3 role-specific talking points for {candidate_name} for this job.

CANDIDATE:
{profile_context}

JOB DESCRIPTION:
{description}
KEY JD TERMS: {top_5_jd_keywords}

RULES:
- Each point: 2 sentences — the claim, then the specific evidence
- Must reference at least 3 of the key JD terms above
- Generic statements that could apply to any AI role are not acceptable
Return as numbered list, plain text.
```

### Telegram /setup onboarding

Runs on `/setup`. One question at a time. Constrained fields use inline buttons with a "Type instead" option. On re-run with existing profile, shows a section menu and re-asks only the chosen section.

```
Prompt for Claude Code:
"Build a Telegram ConversationHandler for /setup using python-telegram-bot v20.

SECTIONS (in order):

IDENTITY — free text, one question at a time:
  full name, current title, employer, location (city + country),
  email, phone, LinkedIn URL, portfolio URL, GitHub URL

EXPERIENCE — free text:
  years of experience, one-paragraph background summary,
  key metrics (up to 5, one at a time — e.g. '85K req/day platform')

SKILLS — free text, comma-separated:
  core AI/ML skills, tech stack, cloud platforms, frameworks

SEARCH CONFIG — inline buttons + 'Type instead' option:
  target countries (multi-select: USA / SG / NL / DE / SE / CH / Other)
  target cities per country (free text per selected country — e.g. USA: remote,San Francisco,New York)
  work mode preferences (multi-select buttons: Remote / Hybrid / On-site — select all that apply)
  target role titles (free text)
  visa status (buttons: H-1B / EAD / OPT / Green Card / Citizen / Other)
  needs sponsorship (Yes / No)
  min score immediate (buttons: 70 / 75 / 80 + type option)
  min score digest (buttons: 60 / 65 / 70 + type option)
  max daily applications (buttons: 10 / 15 / 20 + type option)

After each section: show summary, ask 'Looks good? (Yes / Edit)'.
At end: write data/candidate_profile.json, confirm to user.

On /setup with existing profile:
  show section menu as buttons (Identity / Experience / Skills / Search config)
  user picks → re-ask only that section → save updated profile

The 'Type instead' button on any constrained field switches
that single field to free text input."
```

---

## CLAUDE.example.md

```markdown
# Job Application Agent

## What this is
Monitoring agent built on a curated company registry. No SerpAPI.
You add companies. The agent enriches them once and polls them daily.
Nothing submits without my Telegram tap.

## Candidate profile
- Name: [YOUR NAME]
- Current role: [ROLE], [EMPLOYER], [LOCATION]
- Stack: [YOUR STACK]
- Key metrics: [YOUR METRICS]
- Target countries: USA (primary), SG, NL, DE, SE, CH
- Work auth: [YOUR VISA STATUS]

## Architecture
The loop: company registry → enrich once (careers page + ATS detect) → poll daily
Enricher: /add_company → detect ATS → save → tracked → poll next run
          If ATS unknown: save anyway, user fixes with /fix_ats later
Poller: daily Greenhouse/Lever/Ashby JSON APIs + supplemental boards (Arbeitnow DE, MyCareersFuture SG, RSS)
Shared: company registry → promotion evaluator → scoring → Telegram gate
Output: post-approval Sonnet generates resume + cover letter

## Score thresholds
- 75+ : immediate Telegram · talking points pre-approval · docs post-approval
- 65–74: daily digest · /request_docs [id] on demand
- <65  : silent drop

## Company tiers
- candidate: first seen
- tracked: 2+ runs OR any 75+ role
- priority_tracked: 2+ roles 75+ OR 1 role 85+ → fast-path new-role alerts
- ignored_auto: 60 days no 65+ → reactivates only on new 75+ role

## Duplicate rules
- Source dedupe: URL → hash (collapses copies before scoring)
- Applied in last 90 days: hard block
- Previously skipped: soft warn ("previously seen" flag in Telegram)
```

---
## 75-company seed list (data/company_seed_list.json)

Start with this list. Edit before using — remove companies you know aren't relevant, add any you already have in mind. The enricher will find the careers page and ATS for each one automatically when you run Week 2 Night 1.

```json
{
  "companies": [
    
    // ── USA · AI-native (Tier 1) ──────────────────────────────────────────
    {"name": "Anthropic",         "country": "USA", "hint_url": "https://boards.greenhouse.io/anthropic"},
    {"name": "OpenAI",            "country": "USA", "hint_url": "https://jobs.ashbyhq.com/openai"},
    {"name": "Google DeepMind",   "country": "USA", "hint_url": null},
    {"name": "Meta AI",           "country": "USA", "hint_url": null},
    {"name": "Microsoft AI",      "country": "USA", "hint_url": null},

    // ── USA · AI infrastructure & tooling (Tier 2) ───────────────────────
    {"name": "Databricks",        "country": "USA", "hint_url": "https://boards.greenhouse.io/databricks"},
    {"name": "Cohere",            "country": "USA", "hint_url": "https://jobs.lever.co/cohere"},
    {"name": "Scale AI",          "country": "USA", "hint_url": "https://boards.greenhouse.io/scaleai"},
    {"name": "Hugging Face",      "country": "USA", "hint_url": null},
    {"name": "Weights & Biases",  "country": "USA", "hint_url": null},
    {"name": "Together AI",       "country": "USA", "hint_url": null},
    {"name": "Mistral",           "country": "USA", "hint_url": null},
    {"name": "Perplexity",        "country": "USA", "hint_url": null},
    {"name": "Harvey",            "country": "USA", "hint_url": null},
    {"name": "Glean",             "country": "USA", "hint_url": null},
    {"name": "Pinecone",          "country": "USA", "hint_url": null},
    {"name": "Weaviate",          "country": "USA", "hint_url": null},
    {"name": "LangChain",         "country": "USA", "hint_url": null},

    // ── USA · Enterprise AI (Tier 3) ─────────────────────────────────────
    {"name": "Palantir",          "country": "USA", "hint_url": null},
    {"name": "Salesforce",        "country": "USA", "hint_url": null},
    {"name": "ServiceNow",        "country": "USA", "hint_url": null},
    {"name": "Snowflake",         "country": "USA", "hint_url": null},
    {"name": "Elastic",           "country": "USA", "hint_url": null},
    {"name": "Datadog",           "country": "USA", "hint_url": null},
    {"name": "Stripe",            "country": "USA", "hint_url": "https://boards.greenhouse.io/stripe"},
    {"name": "Confluent",         "country": "USA", "hint_url": null},

    // ── USA · Finance AI ─────────────────────────────────────────────────
    {"name": "JPMorgan Chase",    "country": "USA", "hint_url": null},
    {"name": "Goldman Sachs",     "country": "USA", "hint_url": null},
    {"name": "BlackRock",         "country": "USA", "hint_url": null},
    {"name": "Accenture",         "country": "USA", "hint_url": null},
    {"name": "McKinsey QuantumBlack", "country": "USA", "hint_url": null},
    {"name": "BCG X",             "country": "USA", "hint_url": null},

    // ── Singapore ────────────────────────────────────────────────────────
    {"name": "Grab",              "country": "SG",  "hint_url": "https://boards.greenhouse.io/grab"},
    {"name": "Sea Group",         "country": "SG",  "hint_url": null},
    {"name": "Gojek",             "country": "SG",  "hint_url": null},
    {"name": "Stripe Singapore",  "country": "SG",  "hint_url": null},
    {"name": "Google Singapore",  "country": "SG",  "hint_url": null},
    {"name": "Meta Singapore",    "country": "SG",  "hint_url": null},
    {"name": "ByteDance Singapore","country": "SG", "hint_url": null},
    {"name": "Shopee",            "country": "SG",  "hint_url": null},
    {"name": "DBS Bank",          "country": "SG",  "hint_url": null},
    {"name": "OKX",               "country": "SG",  "hint_url": null},

    // ── Netherlands ──────────────────────────────────────────────────────
    {"name": "Booking.com",       "country": "NL",  "hint_url": null},
    {"name": "ASML",              "country": "NL",  "hint_url": null},
    {"name": "Adyen",             "country": "NL",  "hint_url": "https://boards.greenhouse.io/adyen"},
    {"name": "Uber Amsterdam",    "country": "NL",  "hint_url": null},
    {"name": "Netflix Amsterdam", "country": "NL",  "hint_url": null},
    {"name": "Elastic Amsterdam", "country": "NL",  "hint_url": null},
    {"name": "Optiver",           "country": "NL",  "hint_url": null},
    {"name": "IMC Trading",       "country": "NL",  "hint_url": null},
    {"name": "Mollie",            "country": "NL",  "hint_url": null},

    // ── Germany ──────────────────────────────────────────────────────────
    {"name": "SAP",               "country": "DE",  "hint_url": null},
    {"name": "Siemens AI",        "country": "DE",  "hint_url": null},
    {"name": "Aleph Alpha",       "country": "DE",  "hint_url": null},
    {"name": "DeepL",             "country": "DE",  "hint_url": null},
    {"name": "N26",               "country": "DE",  "hint_url": "https://boards.greenhouse.io/n26"},
    {"name": "Celonis",           "country": "DE",  "hint_url": null},
    {"name": "Helsing",           "country": "DE",  "hint_url": null},
    {"name": "Flixbus",           "country": "DE",  "hint_url": null},
    {"name": "Zalando",           "country": "DE",  "hint_url": null},
    {"name": "Bosch AI",          "country": "DE",  "hint_url": null},

    // ── Sweden ───────────────────────────────────────────────────────────
    {"name": "Spotify",           "country": "SE",  "hint_url": null},
    {"name": "Klarna",            "country": "SE",  "hint_url": null},
    {"name": "Ericsson",          "country": "SE",  "hint_url": null},
    {"name": "King",              "country": "SE",  "hint_url": null},
    {"name": "Lovable",           "country": "SE",  "hint_url": null},
    {"name": "Einride",           "country": "SE",  "hint_url": null},

    // ── Switzerland ──────────────────────────────────────────────────────
    // Apply Jan-Feb only (non-EU quota runs out mid-year)
    {"name": "Google Zurich",     "country": "CH",  "hint_url": null},
    {"name": "UBS",               "country": "CH",  "hint_url": null},
    {"name": "Julius Baer",       "country": "CH",  "hint_url": null},
    {"name": "Microsoft Zurich",  "country": "CH",  "hint_url": null},
    {"name": "ABB",               "country": "CH",  "hint_url": null}
  ]
}
```

**How to use this list:**
- Edit it before running the enricher — remove companies you know aren't relevant
- `hint_url` is optional but speeds up ATS detection — fill it in when you know the board URL
- Add any companies not on this list using `/add_company` at any time
- Swiss companies: the enricher will find their ATS but the poller respects your country filter — only active during your Jan–Feb CH window

---

## Week-by-week build plan (2+ hrs/evening)

### Week 1 — Calibration + skeleton

**Nights 1–2: Manual scoring (hard gate)**

Find 30 real jobs yourself on LinkedIn/Glassdoor. Open a spreadsheet:

```
title | company | location | url | your_score | your_reason
| key_matches | red_flags | would_apply | claude_score
| claude_reason | delta | disagreement_reason
```

Score all 30 yourself first without Claude. Then for each one paste the JD into Claude.ai using the scoring context generated from your profile:

```
# Generate your calibration prompt by running this in Python:
# from core.profile import load_profile, profile_to_scoring_context
# print(profile_to_scoring_context(load_profile()))
# Paste the output below, then add the JD at the end.

Score this job for the following candidate:

[paste output of profile_to_scoring_context() here]

Return JSON: score (0-100), reason (2 sentences), key_matches [],
red_flags [], sponsorship_friendly (bool), seniority_match (bool)

JD: [paste]
```

If you haven't built the profile loader yet in Week 1, write your context manually using your actual details — but keep it in the same format so the comparison against the scorer is valid.

Record delta. If Claude is consistently >10 points off in either direction, note the pattern — that pattern becomes a prompt fix before you write a line of code.

**Nights 3–4: Skeleton + database**

Prompt for Claude Code:
```
Read CLAUDE.md. Create the project skeleton as described.
Start with core/database.py — three SQLAlchemy models:
Observation, Company, Job with all fields in the guide.
Add CRUD helpers: create_observation, upsert_company,
upsert_job, get_unscored_jobs, update_job_status.
Use proper type hints throughout.
```

**Night 5: Config + security**

```
Create core/config.py loading .env variables with pydantic-settings.

API keys and infrastructure only — no candidate data here.
Scoring thresholds, visa status, employer all live in
candidate_profile.json (written by /setup). Do not duplicate
them in .env — two sources of truth causes drift.

Fields:
  ANTHROPIC_API_KEY   (required)
  TELEGRAM_BOT_TOKEN  (required)
  TELEGRAM_CHAT_ID    (required)
  PROFILE_PATH        (default: "data/candidate_profile.json")
  RESUME_PATH         (default: "data/base_resume.json")

Raise a clear error on missing required fields.
```

---

### Week 2 — Enricher + seed loader + /add_company

**Night 1–2: Seed list loader + enricher**

```
Create agents/enricher.py. Two responsibilities:

1. load_seed_list(): reads data/company_seed_list.json, upserts
   each company into the registry with tracking_status="tracked"
   (seed companies are trusted from day one), then runs enrichment.

2. enrich_company(company_name, hint_url=None): given a name,
   find the careers page and detect ATS.
   Try in order:
   a. hint_url if provided — check directly
   b. boards.greenhouse.io/{slug} (slug = slugified name)
   c. jobs.lever.co/{slug}
   d. jobs.ashbyhq.com/{slug}
   e. HTTP GET {company}.com/careers — scan HTML for ATS signatures
      ("greenhouse", "lever", "ashby", "workday" in page source)
   f. Google search fallback: "{company name} jobs greenhouse OR lever"
      using requests + basic HTML parse (no SerpAPI)

   Save: ats_type, ats_board_url, ats_confirmed=False.
   Log all detections — you'll correct misdetections via /fix_ats.
```

**Night 3: Deduper**

```
Create core/deduper.py with two functions:
1. source_dedupe(job_data): URL match first, then
   title+company+location hash. Returns existing job_id or None.
2. history_duplicate_check(company_id, title): query jobs table.
   If status=applied and applied_at within the last 90 days: return "hard_block".
   If status=skipped: return "soft_warn". Else None.
```

**Night 4: /add_company Telegram command**

```
Add /add_company command to telegram_bot.py.

Flow:
  User sends: /add_company Stripe
  Enricher runs: tries greenhouse → lever → ashby slugs,
                 then fetches careers page and scans HTML.

  IF ATS detected:
    Bot replies: "Found Stripe — ATS: Greenhouse
                 Board: boards.greenhouse.io/stripe
                 Add to tracked? (Yes / No / Fix ATS)"
    Yes → save company, tracking_status=tracked, poll on next run.
    Fix ATS → bot sends buttons: Greenhouse/Lever/Ashby/Workday/Direct/Unknown

  IF ATS not detected:
    Bot replies: "Added Stripe — ATS unknown.
                 Careers URL saved: stripe.com/careers (if found)
                 Use /fix_ats [id] [type] when you know the ATS."
    Company saved with ats_type=unknown, ats_confirmed=False.
    Will not be polled until ATS is fixed — poller skips unknown ATS.

  Also handle hint URL:
    /add_company Stripe https://stripe.com/jobs
    Skips detection, saves URL directly, confirms with user.
```

**Night 5: Test + review**

Load the seed list. Run enricher on all 75 companies. Check detection accuracy — expect ~70% correct auto-detection. Correct the failures with /fix_ats. Review which companies couldn't be detected and add hint_urls manually for those.

---

### Week 3 — Scorer + Telegram notifier

**Nights 1–2: Hard rules filter**

```
Create the hard rules layer in agents/scorer.py.
Implement in order — stop at first failure:
1. age_days > 21: hard skip
2. country not in target list: hard skip
3. "no sponsorship" / "must be EU citizen" / "citizens only" in description: hard skip
4. title contains junior/intern/entry-level: hard skip
5. description has <2 of candidate's core skills after fuzzy matching: deprioritize (score penalty of -10 before Claude), not hard skip — many good roles underspecify stack or phrase it differently
6. source_dedupe returns existing job_id: hard skip (source dupe)
7. history_duplicate_check returns hard_block: hard skip
8. history_duplicate_check returns soft_warn: flag job with previously_seen=True, continue
Store hard_filtered=True and hard_filter_reason on skipped jobs.
Log counts per reason after each run.
```

**Night 3: Haiku scorer**

```
Create Haiku scoring in agents/scorer.py.
Load prompts/score_jd.txt. Use claude-haiku-4-5-20251001.
Max tokens: 300. Parse JSON response.
Store: score, score_reason, key_matches, red_flags.
Route: >=75 → status=approved, >=65 → status=digest, <65 → status=dropped.
Batch jobs in groups of 5 with 1 second delay between batches.
```

**Score prompt (prompts/score_jd.txt):**

See the Candidate profile system section above — the full template is defined there.
At runtime, `profile_to_scoring_context(load_profile())` is called and injected
as `{profile_context}`. No candidate data is hardcoded here.

**Nights 4–5: Telegram bot — core approval flow**

```
Create core/telegram_bot.py using python-telegram-bot v20.
Implement:
1. send_approval_message(job): immediate 75+ notification.
   Include: company, title, location, score, reason, key_matches,
   red_flags, 3 talking points, direct URL.
   Inline keyboard: APPLY / SKIP / EDIT.
   Store telegram_message_id on job record.
2. send_daily_digest(): 65-74 jobs + registry updates at 8am.
   Include /request_docs [job_id] instructions.
3. handle_apply_callback(): status=approved, trigger writer.
4. handle_skip_callback(): status=skipped.
5. handle_reply(message): "done"/"applied"/"submitted" →
   confirmed_at=now, status=applied.
6. handle_request_docs(job_id): trigger writer for 65-74 jobs.
7. send_priority_alert(job): priority_tracked companies,
   first-seen roles only — fires outside normal digest.
```

**Night 6 (dedicated): /setup onboarding ConversationHandler**

This is non-trivial — budget a full evening. A ConversationHandler with section menus, inline buttons, "Type instead" fallback, and a re-run edit flow is real work.

```
Add /setup ConversationHandler to telegram_bot.py.
Sections in order:
  IDENTITY: name, title, employer, location, email, phone,
            LinkedIn, portfolio, GitHub (free text, one at a time)
  EXPERIENCE: years, summary paragraph, up to 5 key metrics
              (one at a time — user sends each metric, bot asks "another? Yes/Done")
  SKILLS: core skills, stack, cloud platforms, frameworks (comma-separated)
  SEARCH CONFIG (buttons + 'Type instead'):
    countries (multi-select: USA/SG/NL/DE/SE/CH/Other)
    cities per country (free text per selected country)
    work mode (Remote / Hybrid / On-site / Any)
    role titles (free text)
    visa status (H-1B / EAD / OPT / Green Card / Citizen / Other)
    needs sponsorship (Yes / No)
    score thresholds + daily cap (buttons with type option)

After each section: summary + "Looks good? (Yes / Edit)"
End: write data/candidate_profile.json, confirm.

On /setup with existing profile:
  show section menu as buttons → user picks → re-ask only that section.
```

**Night 7: ATS router + manual_assisted packet**

```
Create core/router.py. This runs inside handle_apply_callback(),
after APPLY tap, before the writer fires.

def classify_ats(url: str) -> str:
    patterns = {
        "greenhouse": ["greenhouse.io", "boards.greenhouse"],
        "lever":      ["jobs.lever.co", "lever.co"],
        "ashby":      ["jobs.ashbyhq.com"],
        "workday":    ["myworkdayjobs.com", "wd1.myworkdayjobs", "wd3.myworkdayjobs"],
    }
    for ats, urls in patterns.items():
        if any(p in url for p in urls):
            return ats
    return "unknown"

def route_application(job: Job) -> str:
    ats = classify_ats(job.canonical_url)
    if ats in ("greenhouse", "lever", "ashby"):
        return "manual_ready"    # Phase 1: docs generated, you submit. Phase 2: Playwright takes over.
    else:
        return "manual_assisted" # Workday + unknown: prepped packet, you click through.

After routing, handle_apply_callback() branches:
- manual_ready: trigger writer, send docs + direct link to Telegram, you submit
- manual_assisted: trigger writer AND send_manual_assisted_packet()

def send_manual_assisted_packet(job, resume_path, cover_letter_path):
    """
    Telegram message with everything pre-prepared for a 5-minute manual submit.
    Fires for Workday and unknown ATS after APPLY tap.
    """
    message = (
        f"🔧 Manual submit needed\n\n"
        f"{job.company} — {job.title}\n"
        f"ATS: {classify_ats(job.canonical_url)}\n"
        f"Link: {job.canonical_url}\n\n"
        f"Top 3 talking points:\n"
        f"{job.talking_points}\n\n"
        f"Docs attached. Est. 5 minutes to submit."
    )
    send_with_files(message, [resume_path, cover_letter_path])
    update_job_status(job.id, "applying")

Store ats_type on job record when router runs — useful for
tracking which ATS your applications go through.
```

---

### Week 4 — Resume + cover letter writer

**Nights 1–2: Company promotion evaluator**

```
Create agents/promoter.py. Run after each scrape+score cycle.
For each company:
  - Count observations across separate run_ids
  - Count jobs with score >= 75
  - Check best_role_score

Promotion logic:
  candidate → tracked: observations.run_ids distinct count >= 2 OR any score >= 75
  tracked → priority_tracked: jobs with score >= 75 count >= 2 OR any score >= 85
  tracked/candidate → ignored_auto: last_seen_at > 60 days AND no job score >= 65
  ignored_auto → candidate: new job appears with score >= 75 (reactivation)

Update company.tracking_status, company.best_role_score, company.roles_above_75.
Add promotions to daily digest queue.
```

**Nights 3–5: Writer (Sonnet)**

```
Create agents/writer.py. Called only after APPLY tap.
Two Sonnet calls per job: resume rewrite + cover letter.
Run in parallel (asyncio.gather). Output: .docx resume, .txt cover letter.
Store paths on job record.

Resume prompt (prompts/rewrite_resume.txt):
Load base_resume.json. Rewrite for this specific JD.
Reorder bullets by relevance. Rewrite summary (2-3 sentences).
Emphasise: EU AI Act for DE/NL/CH, RAG+fintech for SG/NL,
computer vision for DE/CH industrial, agent systems for USA startups.
Keep 1 page. Never fabricate metrics. Return same JSON structure.

Cover letter prompt (prompts/cover_letter.txt):
3 paragraphs max 300 words. Para 1: hook + why this company.
Para 2: 2 specific skill matches + metric each.
Para 3: why this location + call to action.
Tone by country: USA=direct, SG=achievement-focused,
NL=warm-professional, DE=formal-precise, SE=collaborative, CH=precision-quality.

Talking points prompt (prompts/talking_points.txt):
Generate 3 role-specific talking points. These must reference
specific language from the JD, not generic resume bullets.
Each point: 2 sentences — the claim, then the specific evidence from the candidate's background.
If points feel generic after generation, regenerate with this flag:
"Make these more specific to {company}'s stated priorities: {jd_keywords}"
```

---

### Week 5 — Integration + international expansion

**Night 1–2: ATS pollers + supplemental boards**

```
Create agents/poller.py. For each tracked company with known ATS:
- Greenhouse: GET boards.greenhouse.io/v1/boards/{slug}/jobs?content=true
- Lever: GET api.lever.co/v0/postings/{slug}?mode=json
- Ashby: GET jobs.ashbyhq.com/api/posting-api/job-board/{slug}
All are public JSON APIs, no auth.
For each job returned: dedupe, write observation with source=ats_api,
upsert canonical job, link to company.
```

**Night 3: Hybrid sources**

```
Add to agents/poller.py:
- Arbeitnow: GET arbeitnow.com/api/job-board-api (free, no key, German market)
- MyCareersFuture: GET api.mycareersfuture.gov.sg/api/search (free public API, SG)
- LinkedIn RSS: feedparser on job search RSS URLs (no login, no ban risk)
These are source_type=hybrid — write observations, route through same pipeline.
```

**Nights 4–5: End-to-end test**

Run full pipeline on real data. Validate:
- Observations table correctly records all sightings
- Company promotion is firing correctly
- Score distribution looks right (compare against validation_30.csv calibration)
- Telegram messages are well-formatted and actionable
- Reply parsing correctly sets confirmed_at
- /request_docs works for a 65-74 job

Fix everything before ramping volume.

---

## Scoring prompt test — the calibration check

Before trusting Claude on real applications, run this test after building the scorer:

```python
# tests/test_scorer.py
def test_calibration():
    """
    Load validation_30.csv. Run each JD through score_job().
    Assert: average delta < 10 points.
    Assert: no single job delta > 20 points.
    Log disagreements for manual review.
    """
    df = pd.read_csv("data/calibration/validation_30.csv")
    deltas = []
    for _, row in df.iterrows():
        result = score_job(row["description"], row["title"], row["company"])
        delta = abs(result["score"] - row["your_score"])
        deltas.append(delta)
        if delta > 15:
            print(f"DISAGREEMENT: {row['company']} — you:{row['your_score']} claude:{result['score']}")
    assert sum(deltas) / len(deltas) < 10, "Average delta too high — tune prompt"
```

---

## Talking points quality check

The most important prompt to get right. Before trusting it, test it manually:

Take 5 jobs from your validation set. Generate talking points for each. Ask yourself:
- Do these reference language from the JD specifically?
- Could these talking points have been written for any senior AI role, or just this one?
- If the answer to the second question is "any role" — the prompt needs tightening.

The fix: extract 5 keywords from the JD before generating talking points and inject them as a constraint:

```python
# In talking_points.txt prompt:
"These talking points must reference at least 3 of these specific terms
from the job description: {top_5_jd_keywords}. Generic AI experience
statements are not acceptable."
```

---

## Cost breakdown — keeping it minimal

| Component | Model | When it fires | Cost |
|-----------|-------|--------------|------|
| Scoring | Haiku | Every job that passes hard rules | ~$0.25 / 1,000 jobs |
| Talking points | Haiku | Every 75+ job (pre-approval) | ~$0.01 / job |
| Resume rewrite | Sonnet | After APPLY tap only | ~$1.50 / job |
| Cover letter | Sonnet | After APPLY tap only (bundled) | ~$1.50 / job |
| ATS polling | — | Free JSON APIs — Greenhouse/Lever/Ashby | $0 |
| Free boards | — | Arbeitnow, MyCareersFuture, RSS | $0 |

**Monthly estimate at full pace (15 apps/day):**
- Haiku scoring ~200 jobs/day × 30 days = 6,000 jobs → ~$1.50
- Haiku talking points ~20 per day × 30 = 600 → ~$6
- Sonnet resume+CL ~10 approvals/day × 30 = 300 → ~$90
- **Total: ~$15–20/month at full pace** (down from $55–65 with SerpAPI)
- **During build (weeks 1–3): ~$3–8** (minimal Sonnet, Haiku testing only)

---

## What breaks and how to fix it

| Problem | Cause | Fix |
|---------|-------|-----|
| Greenhouse board returns 404 | Company changed slug | Re-run enricher, update ats_board_url |
| Enricher can't find ATS | Custom subdomain or obscure careers page | Add hint_url manually: /add_company Name https://company.com/jobs |
| Claude scores too generously | Prompt undersells hard requirements | Add "penalise 15 points if role requires X which candidate lacks" |
| Telegram reply not parsed | Message wasn't a direct reply | Add fallback: `/applied [job_id]` command |
| Company name variants | "JPMorgan" vs "JP Morgan Chase" | canonical_name field + fuzzy match on upsert |
| ATS detection wrong | Company uses custom subdomain | Manual correction via `/fix_ats [company_id] [type]` command |
| Observations table grows fast | Expected — it's an append-only log | Archive rows older than 180 days to observations_archive |

---

## The first prompt to give Claude Code

```
Read CLAUDE.md in this repo. I'm building the job application agent
described there. Start with the data model.

Create core/database.py with three SQLAlchemy models:
Observation, Company, Job — all fields as documented.
Add these CRUD helpers:
- create_observation(run_id, source, source_type, raw_data) -> Observation
- upsert_company(name, discovery_source) -> (Company, created: bool)
- upsert_job(canonical_url, company_id, data) -> (Job, created: bool)
- get_jobs_for_scoring() -> list[Job] where status=scraped and hard_filtered=False
- update_job_status(job_id, status, **kwargs)

Use proper type hints. Add a get_db() context manager.
Create the tables on first run.

Show me database.py first, then we'll build from there.
```

This gives you a working database in one session. Every other agent builds on top of it.
