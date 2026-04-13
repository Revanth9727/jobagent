# Claude Code Guide — Updated
### Job Application Agent · Mac · Windsurf + Claude Code · Full workflow

---

## How to read this guide

Every phase has three layers:

**Phase level:** What to do before starting the phase, what to watch during it, and what to verify before moving on.

**Prompt level:** What to do before running each prompt, what to watch while Claude Code works, and what to confirm after it finishes.

This is not a guide you skim. Read each section before you act on it. The "before" steps are not optional — skipping them is how you end up debugging problems that would have taken 30 seconds to prevent.

---

## Your workspace setup — do this once

Open two windows side by side on your Mac:

**Left: Windsurf** — pointed at your `job-agent/` folder. You will watch files appear here in real time as Claude Code writes them. This is your early warning system. If something looks wrong in Windsurf, catch it before running the code.

**Right: Terminal** — with Claude Code running (`claude` command inside the project folder). This is where you paste prompts and read responses.

When you need to run shell commands (like `python main.py`), open a second terminal tab. Keep the Claude Code session in its own tab — do not close it between prompts within a phase.

---

## Before you ever open Claude Code

These steps happen once, before Phase 1. Do not skip them.

**1. Create your Telegram bot**
- Open Telegram on your phone
- Search for `@BotFather`
- Send `/newbot`
- Follow the prompts — give it a name and a username
- Copy the token it gives you (looks like `1234567890:ABCdef...`)
- Message `@userinfobot` — it replies with your chat ID
- Write both down somewhere safe

**2. Get your Anthropic API key**
- Go to console.anthropic.com
- Create an API key
- Copy it — you will only see it once

**3. Install prerequisites**
```bash
# Check Python — needs 3.11 or 3.12
python3 --version

# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

**4. Create the project folder and open Claude Code**
```bash
mkdir job-agent
cd job-agent
claude
```

Claude Code is now running inside your project folder. Keep this terminal tab open for the entire guide.

**5. Open Windsurf**
Point it at the `job-agent/` folder. You should see an empty folder. Files will appear here as Claude Code creates them.

---

## PHASE 1 — Foundation

### Before starting Phase 1

Read these before touching Claude Code:

- You have your Telegram bot token and chat ID written down
- You have your Anthropic API key written down
- Claude Code is running in terminal inside `job-agent/`
- Windsurf is open and pointing at `job-agent/`
- You have 2 hours of uninterrupted time — do not start this phase if you have 30 minutes

**Mental model for this phase:** You are building the container, not the content. No features at the end. Just a clean, secure, working foundation. Resist the urge to start scoring jobs or writing agents. That comes later.

**What you'll have at the end of Phase 1:**
- Project structure with all folders and empty files
- `.gitignore` protecting all sensitive files
- `CLAUDE.md` giving Claude Code full project context for every future session
- Working SQLite database with all three tables
- Config loader that reads from `.env` and fails clearly if anything is missing
- `python main.py` prints success without errors

---

### Prompt 1.1 — Project skeleton and security

**Before running this prompt:**
- Confirm Claude Code is running (`claude` in terminal, inside `job-agent/`)
- Confirm Windsurf shows an empty folder
- Read the prompt fully before pasting — understand what it's asking for
- Note: `.gitignore` is created first deliberately. This is not negotiable.

**Why this prompt is worded this way:**
Claude Code has no memory of your project — the folder is empty. So the prompt must give it everything: what to build, in what order, and why the order matters. The `.gitignore`-first instruction is explicit because the most common beginner mistake is creating files with personal data and then forgetting to protect them. By making it step 1, you guarantee nothing sensitive ever reaches git.

The `CLAUDE.example.md` file is important — it's the template that goes into git. The real `CLAUDE.md` (with your actual data) gets created in Prompt 1.2 and stays in `.gitignore` forever.

**The prompt:**
```
I'm building a job application agent in Python on Mac.
Do these steps in this exact order:

1. Create .gitignore first, before anything else:
   .env
   CLAUDE.md
   data/candidate_profile.json
   data/base_resume.json
   data/jobs.db
   data/outputs/
   data/calibration/
   __pycache__/
   *.pyc
   venv/
   .venv/
   .DS_Store

2. Create this folder structure with empty files (just a docstring
   in each .py file, empty for .txt files):
   agents/__init__.py
   agents/enricher.py
   agents/poller.py
   agents/scorer.py
   agents/writer.py
   agents/promoter.py
   core/__init__.py
   core/database.py
   core/config.py
   core/deduper.py
   core/router.py
   core/profile.py
   core/telegram_bot.py
   prompts/score_jd.txt
   prompts/rewrite_resume.txt
   prompts/cover_letter.txt
   prompts/talking_points.txt
   data/outputs/.gitkeep
   data/calibration/.gitkeep
   tests/__init__.py
   tests/test_scorer.py
   tests/test_deduper.py
   main.py
   requirements.txt
   setup_profile.py

3. Create .env.example with these placeholder lines:
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   TELEGRAM_BOT_TOKEN=your-bot-token-here
   TELEGRAM_CHAT_ID=your-chat-id-here
   PROFILE_PATH=data/candidate_profile.json
   RESUME_PATH=data/base_resume.json

4. Create CLAUDE.example.md with this exact content:
   # Job Application Agent
   ## What this is
   Monitoring agent. You add companies. Agent watches and scores.
   Nothing submits without Telegram APPLY tap.
   ## The loop
   company registry → enrich once → poll daily → score → Telegram gate
   ## Score thresholds
   75+: immediate alert · 65-74: daily digest · <65: drop
   ## Company tiers
   candidate → tracked → priority_tracked → ignored_auto
   ## Security
   .env and CLAUDE.md are in .gitignore — never commit them

5. Run: git init
   Run: git add .gitignore
   Run: git commit -m "init: gitignore first"

Show me the complete folder tree when done.
```

**While Claude Code works:**
- Watch Windsurf — you should see folders and files appearing
- If Claude Code asks you a clarifying question, answer it directly — do not let it proceed with assumptions on security-related steps
- If you see it creating `.env` (not `.env.example`), stop it immediately with Ctrl+C

**After — confirm these before moving on:**

```bash
# Run this — .env and CLAUDE.md must NOT appear
git status

# Run this — should show the full folder tree
find . -not -path './.git/*' | sort

# Run this — verify .gitignore exists and has the right content
cat .gitignore
```

Expected output from `git status`: `nothing to commit, working tree clean`

If `.env` or `CLAUDE.md` appear in `git status`, stop. Fix `.gitignore` before continuing.

---

### Prompt 1.2 — Real .env and CLAUDE.md

**Before running this prompt:**
- Have your Anthropic API key ready to paste
- Have your Telegram bot token ready to paste
- Have your Telegram chat ID ready to paste
- Confirm `git status` is clean from Prompt 1.1
- Know that these files will contain real personal data — they are already protected by `.gitignore`

**Why this prompt is worded this way:**
This prompt creates the two files that give the project its identity. `CLAUDE.md` is read by Claude Code at the start of every future session — it's the briefing document that means you never have to re-explain the project. The more accurate and complete it is now, the shorter every future prompt can be.

The verification step at the end (running `git status` and confirming neither file appears) is the most important part of this prompt. Do not skip it.

**The prompt:**
```
Create two files with my actual credentials and project context.
Both are already in .gitignore so they are safe.

1. Create .env with these values:
   ANTHROPIC_API_KEY=[paste your actual key here]
   TELEGRAM_BOT_TOKEN=[paste your actual bot token here]
   TELEGRAM_CHAT_ID=[paste your actual chat ID here]
   PROFILE_PATH=data/candidate_profile.json
   RESUME_PATH=data/base_resume.json

2. Create CLAUDE.md with this content — this is your project briefing
   that you will read at the start of every future session:

   # CLAUDE.md — Job Application Agent
   # In .gitignore — never commit

   ## Candidate
   Name: Revanth Gollapudi
   Role: Consultant AI Engineer at CGI, West Lafayette IN
   Target: Senior AI Engineer / AI Systems Architect
   Stack: RAG, LLM fine-tuning (LoRA/PEFT/DPO), EvalOps, Azure, AWS,
          Kubernetes, LangGraph, multimodal computer vision
   Metrics: 85K req/day platform, 6K-user RAG, 30% cost cut, hallucination 45→30%
   Countries: USA (primary), SG, NL, DE, SE, CH
   Visa: Indian passport, US-based, needs international sponsorship

   ## Architecture
   Single loop: company registry → enrich once → poll daily
   Enricher: /add_company → careers page → ATS detect → save → poll
   Poller: Greenhouse/Lever/Ashby JSON APIs (primary)
           Arbeitnow/MyCareersFuture/RSS (supplemental, weak)
   Scorer: hard rules first → Haiku → route by threshold
   Writer: Sonnet, post-APPLY tap only, resume + CL in parallel
   Bot: Telegram, approval gate + /setup + all commands

   ## Models
   Haiku (claude-haiku-4-5-20251001): scoring, talking points
   Sonnet (claude-sonnet-4-6): resume rewrite, cover letter
   Never swap these.

   ## Thresholds (from candidate_profile.json at runtime)
   75+: immediate Telegram · 65-74: daily digest · <65: drop

   ## Security rules
   Never hardcode candidate data in code or prompts
   All prompts use {profile_context} variable only
   .env, CLAUDE.md, candidate_profile.json never in git

   ## Current phase
   Phase 1 — Prompt 1.2 just completed
   Next: Prompt 1.3 — database schema and config

After creating both files:
- Run: git status
- Confirm neither .env nor CLAUDE.md appears in the output
- Show me the git status output in full
```

**While Claude Code works:**
- Do not paste your API key in the chat if you can avoid it — ask Claude Code to create the `.env` file and then edit it yourself in Windsurf after
- Watch that it creates `CLAUDE.md` not `CLAUDE.example.md` — the example already exists, this is the real one

**After — confirm these before moving on:**

```bash
# This is the critical check — both files must be invisible to git
git status
# Expected: nothing to commit, working tree clean

# Verify .env has your keys (values will show — that's fine, it's local)
cat .env

# Open CLAUDE.md in Windsurf and read it
# Does it accurately describe YOUR project and YOUR profile?
```

If `git status` shows `.env` or `CLAUDE.md` — stop everything. Your `.gitignore` is not working. Fix it before continuing.

---

### Prompt 1.3 — Database, config, and main.py

**Before running this prompt:**
- Confirm Prompt 1.2 is done and `git status` is clean
- Install dependencies first — Claude Code will need these:
```bash
pip install sqlalchemy pydantic-settings python-dotenv anthropic \
            python-telegram-bot python-docx aiohttp requests feedparser \
            pytest
pip freeze > requirements.txt
```
- Open `core/database.py` in Windsurf so you can watch it being written

**Why this prompt is worded this way:**
The database is the memory of the entire system. Every agent reads from and writes to it. Getting the schema right now means you never have to migrate it later. The prompt specifies all three tables with all fields because Claude Code needs the full picture to create correct foreign keys and relationships.

The config loader is in the same prompt because they're tightly coupled — database init needs the file path, which comes from config. The test at the end is non-negotiable: you need to know the database actually creates tables before building anything on top of it.

**The prompt:**
```
Read CLAUDE.md first to understand the project.

Now build the database layer and config. Three things:

1. Create core/config.py:
   Use pydantic-settings to load from .env.
   Fields:
     ANTHROPIC_API_KEY: str (required)
     TELEGRAM_BOT_TOKEN: str (required)
     TELEGRAM_CHAT_ID: str (required)
     PROFILE_PATH: str = "data/candidate_profile.json"
     RESUME_PATH: str = "data/base_resume.json"
   On missing required field: raise ValueError with a clear message
   listing exactly which key is missing and where to find it.
   Add a settings singleton: settings = Settings()

2. Create core/database.py with these exact SQLAlchemy models:

class Observation(Base):
   id, run_id (str), source (str), source_type (str),
   company_id (Integer FK to companies.id nullable),
   job_id (Integer FK to jobs.id nullable),
   raw_url, raw_title, raw_company, raw_location,
   raw_payload (JSON), observed_at (DateTime default utcnow)

class Company(Base):
   id, name (str, not null), canonical_name (str),
   careers_url, ats_type (str default "unknown"),
   ats_board_url, ats_confirmed (bool default False),
   discovery_source, tracking_status (str default "candidate"),
   first_seen_at (DateTime), last_seen_at (DateTime),
   times_seen (int default 1), best_role_score (float nullable),
   roles_above_75 (int default 0),
   ignored_at (DateTime nullable), reactivated_at (DateTime nullable),
   notes (Text)

class Job(Base):
   id, company_id (Integer FK to companies.id, not null),
   canonical_url (str unique not null),
   normalized_hash (str unique not null),
   title (str), location (str), country (str),
   description (Text), posted_at (DateTime),
   first_seen_at (DateTime), last_seen_at (DateTime),
   age_days (int), is_repost (bool default False),
   source_type (str), source_confidence (str),
   hard_filtered (bool default False), hard_filter_reason (str),
   source_deduped (bool default False),
   history_status (str nullable),
   score (float nullable), score_reason (Text),
   key_matches (JSON), red_flags (JSON), talking_points (JSON),
   status (str default "scraped"),
   ats_type (str nullable), route (str nullable),
   resume_path (str nullable), cover_letter_path (str nullable),
   approved_at (DateTime nullable), applied_at (DateTime nullable),
   confirmed_at (DateTime nullable),
   telegram_message_id (str nullable)

Add these CRUD helpers with full type hints and docstrings:
- get_db() — context manager yielding a Session
- create_observation(session, run_id, source, source_type, raw_data) -> Observation
- upsert_company(session, name, discovery_source) -> tuple[Company, bool]
- upsert_job(session, canonical_url, company_id, data) -> tuple[Job, bool]
- get_jobs_for_scoring(session) -> list[Job]
  (status="scraped", hard_filtered=False, score is None)
- update_job_status(session, job_id, status, **kwargs)

3. Update main.py:
   Import config and database.
   Create all tables on startup.
   Print:
     "✅ Config loaded"
     "✅ Database ready — tables: observations, companies, jobs"
     "Run with a flag: --health --load-seeds --poll --score --run --bot"
   If .env is missing, print a clear error and exit(1).

Then run: python main.py
Show me the exact output.
```

**While Claude Code works:**
- Watch `core/database.py` appear in Windsurf — it should be substantial (80-120 lines)
- If you see Claude Code importing something you didn't install, let it finish and then install the missing package
- Check that the foreign keys look right: `company_id` on Job points to `companies.id`, not to `company.id`

**After — confirm these before moving on:**

```bash
# Should print the two success lines
python main.py

# Should show jobs.db was created
ls data/

# Verify all three tables exist
python3 -c "
from core.database import get_db, Observation, Company, Job
db = next(get_db())
print('Tables created:', db.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())
"

# Commit this phase
git add -A
git commit -m "feat: phase 1 complete — skeleton, database, config"
```

Expected output from `python main.py`:
```
✅ Config loaded
✅ Database ready — tables: observations, companies, jobs
Run with a flag: --health --load-seeds --poll --score --run --bot
```

If you get `ModuleNotFoundError`: run `pip install [missing module]` and retry.
If you get `sqlalchemy` errors: paste the full error to Claude Code and ask it to fix.

### After Phase 1 — before moving to Phase 2

**Phase 1 exit checklist:**
- [ ] `python main.py` runs without errors
- [ ] `git status` is clean (no untracked sensitive files)
- [ ] `data/jobs.db` exists
- [ ] All three tables created (verified above)
- [ ] `CLAUDE.md` is complete and accurate
- [ ] Phase committed to git

**Update CLAUDE.md:** Change "Current phase" to "Phase 2 — starting Prompt 2.1"

**Do the manual calibration exercise now — before Phase 2.** This is the most important non-coding task in the project. Find 30 real job postings on LinkedIn or Glassdoor. Score each one yourself (0-100) and record your reasoning. Save to a spreadsheet — you will need this in Phase 3 to validate Claude's scoring.

```
Columns: title, company, location, description, your_score, your_reason, would_apply
```

Do not skip this. It is the only way to know if the scorer is calibrated correctly.

---

## PHASE 2 — Company registry and enricher

### Before starting Phase 2

- Phase 1 exit checklist is complete
- You have done the manual calibration exercise (30 jobs scored)
- `CLAUDE.md` current phase is updated
- You have 10-15 minutes to review the seed list and customise it before running Prompt 2.3

**What you'll have at the end of Phase 2:**
- `core/profile.py` loading candidate data from JSON at runtime
- `data/candidate_profile.json` written with your real profile
- `agents/enricher.py` finding careers pages and detecting ATS
- 75 companies in the database with ATS types detected
- `/add_company` command skeleton working

---

### Prompt 2.1 — Profile loader and CLI setup

**Before running this prompt:**
- Open `core/profile.py` in Windsurf so you can watch it being written
- Know that this prompt creates `setup_profile.py` — a command-line script that asks you questions and writes your profile to disk
- After Claude Code finishes, you will run `python setup_profile.py` and answer real questions about yourself

**Why this prompt is worded this way:**
The profile system is what makes the agent generic — no hardcoded candidate data anywhere. Every prompt template, every scoring call, every resume rewrite loads the profile at runtime via `profile_to_scoring_context()`. This function is the bridge between your personal data and Claude's prompt templates.

The CLI setup script is simpler than the Telegram onboarding (which comes in Phase 4). Use it now to get a working profile quickly. You can re-run it any time to update your profile.

**The prompt:**
```
Read CLAUDE.md first.

Build the profile system. Two things:

1. Create core/profile.py:

PROFILE_PATH comes from core/config.settings.PROFILE_PATH

def load_profile() -> dict:
   Load data/candidate_profile.json.
   If missing: raise FileNotFoundError with message:
   "No profile found. Run: python setup_profile.py"

def save_profile(profile: dict) -> None:
   Create data/ if needed.
   Write with json.dumps(profile, indent=2)

def profile_to_scoring_context(profile: dict) -> str:
   Render profile to a prompt-injectable string.
   Use first 10 items from skills.core and skills.stack
   (ordering matters — most differentiating skills first).
   Format:
   CANDIDATE: {name}, {current_title}
   EXPERIENCE: {years_total}+ years. {summary}
   KEY METRICS:
   {each metric on its own line with a dash}
   CORE SKILLS: {top 10 core, comma-separated}
   STACK: {top 10 stack, comma-separated}
   EMPLOYER: {current_employer}, {location}
   VISA: {visa_status} — needs sponsorship: {needs_sponsorship}
   TARGET COUNTRIES: {target_countries comma-separated}

2. Create setup_profile.py in the project root:
   Command-line script, one question at a time.
   Ask for:
   - Full name
   - Current job title
   - Current employer
   - Location (city and country)
   - Years of total experience (integer)
   - One-paragraph background summary
   - Up to 5 key metrics (press Enter alone to stop)
   - Core AI/ML skills (comma-separated)
   - Tech stack (comma-separated)
   - Cloud platforms (comma-separated)
   - Target countries (comma-separated, e.g. USA,SG,NL,DE,SE,CH)
   - Visa status
   - Needs sponsorship for international roles? (y/n)
   - Min score for immediate Telegram alert (default 75)
   - Min score for daily digest (default 65)
   - Max daily applications (default 15)
   - Work mode preferences (e.g. remote,hybrid)
   - Target cities per country (e.g. USA:remote,San Francisco NL:Amsterdam)

   Save to data/candidate_profile.json as structured JSON.
   Print "✅ Profile saved to data/candidate_profile.json"

Run: python setup_profile.py
Fill in your real details.
Then run:
python3 -c "
from core.profile import load_profile, profile_to_scoring_context
p = load_profile()
print(profile_to_scoring_context(p))
"
Show me the scoring context output.
```

**While Claude Code works:**
- Watch `core/profile.py` in Windsurf — the `profile_to_scoring_context()` function should produce a clean multi-line string
- When `python setup_profile.py` runs, answer every question with real data — this will be injected into every Claude API call

**After — confirm these before moving on:**

```bash
# Scoring context should show YOUR real data — not placeholders
python3 -c "
from core.profile import load_profile, profile_to_scoring_context
print(profile_to_scoring_context(load_profile()))
"

# Profile file exists and is not in git
ls data/candidate_profile.json
git status  # must not show candidate_profile.json
```

Read the scoring context output carefully. This exact text is what Claude will see when scoring jobs. If anything is missing or wrong, edit `data/candidate_profile.json` directly in Windsurf and re-run the test.

---

### Prompt 2.2 — ATS enricher

**Before running this prompt:**
- Confirm `core/profile.py` works from Prompt 2.1
- Know that this prompt builds the most "intelligent" part of Phase 2 — the enricher tries multiple strategies to find a company's ATS
- Read the fallback rule: if nothing works, save as unknown. Never raise.

**Why this prompt is worded this way:**
The enricher tries strategies in order from fastest (known URL patterns) to slowest (fetching the actual HTML). The slug generation — converting "Scale AI" to "scale-ai" — works for most companies because Greenhouse, Lever, and Ashby all use company slugs in their board URLs. Expect ~65-70% accuracy on first pass. The rest get fixed manually with `/fix_ats`.

The "never raise" rule is critical. One company failing must never stop the rest from being processed.

**The prompt:**
```
Read CLAUDE.md first.

Build agents/enricher.py. Two responsibilities:

1. enrich_company(company_name: str, hint_url: str = None) -> Company:
   Find the careers page and detect ATS type.
   Import get_db and upsert_company from core.database.

   Strategy (try in order, stop at first success):
   a. If hint_url: send HEAD request (timeout=5s). If responds:
      check if URL contains "greenhouse", "lever", "ashby",
      "workday" → set ats_type accordingly. Save ats_board_url.
   b. Generate slug: name.lower().strip()
      .replace(" ", "-").replace("'","").replace(".", "")
      Try HEAD requests (timeout=5s, allow_redirects=True):
      - https://boards.greenhouse.io/{slug} → greenhouse
      - https://jobs.lever.co/{slug} → lever
      - https://jobs.ashbyhq.com/{slug} → ashby
   c. Try fetching HTML from these URLs (GET, timeout=5s):
      - https://{slug}.com/careers
      - https://www.{slug}.com/careers
      - https://{slug}.com/jobs
      Scan raw HTML for: "greenhouse.io", "lever.co",
      "ashbyhq", "myworkdayjobs", "workday.com"
      First match wins. Save careers_url.
   d. Fallback: ats_type="unknown", save whatever careers_url
      was found (or None), ats_confirmed=False.

   ALWAYS: catch all exceptions per step (never raise to caller).
   ALWAYS: call upsert_company() and save results to DB.
   ALWAYS: log what was tried and what was found.
   Return the Company object.

2. load_seed_list() -> None:
   Read data/company_seed_list.json.
   For each company:
     Call upsert_company(name, discovery_source="seed")
     Set tracking_status="tracked" (seed companies trusted from day one)
     Call enrich_company(name, hint_url) if ats_type not yet set
     Print: "  {name}: {ats_type found or unknown}"
   At end, print summary:
     Total: X
     Detected (greenhouse/lever/ashby): X
     Unknown: X — fix with /fix_ats
     Errors: X

Create data/company_seed_list.json with these 10 starter companies:
[
  {"name": "Anthropic", "country": "USA",
   "hint_url": "https://boards.greenhouse.io/anthropic"},
  {"name": "Databricks", "country": "USA",
   "hint_url": "https://boards.greenhouse.io/databricks"},
  {"name": "Cohere", "country": "USA",
   "hint_url": "https://jobs.lever.co/cohere"},
  {"name": "Grab", "country": "SG",
   "hint_url": "https://boards.greenhouse.io/grab"},
  {"name": "Adyen", "country": "NL",
   "hint_url": "https://boards.greenhouse.io/adyen"},
  {"name": "N26", "country": "DE",
   "hint_url": "https://boards.greenhouse.io/n26"},
  {"name": "Spotify", "country": "SE", "hint_url": null},
  {"name": "Klarna", "country": "SE", "hint_url": null},
  {"name": "Stripe", "country": "USA", "hint_url": null},
  {"name": "Scale AI", "country": "USA", "hint_url": null}
]

Then test with:
python3 -c "
from agents.enricher import enrich_company
result = enrich_company('Stripe')
print(f'Name: {result.name}')
print(f'ATS: {result.ats_type}')
print(f'Board URL: {result.ats_board_url}')
print(f'Confirmed: {result.ats_confirmed}')
"
Show me the output.
```

**While Claude Code works:**
- Watch `agents/enricher.py` being written in Windsurf
- The file should be 80-120 lines
- Check that every strategy step has its own try/except block
- If you see `requests` not imported, it's fine — you'll install it

**After — confirm these before moving on:**

```bash
# Install requests if not already installed
pip install requests

# Run the test
python3 -c "
from agents.enricher import enrich_company
r = enrich_company('Stripe')
print(r.name, r.ats_type, r.ats_board_url)
"
# Expected: Stripe greenhouse boards.greenhouse.io/stripe

# Verify Stripe is in the database
python3 -c "
from core.database import get_db, Company
db = next(get_db())
c = db.query(Company).filter(Company.name=='Stripe').first()
print(c.name, c.ats_type, c.tracking_status)
"
```

---

### Prompt 2.3 — Full seed list and /add_company

**Before running this prompt:**
- Open `data/company_seed_list.json` in Windsurf
- Customise the 10-company starter list — remove any companies you know aren't relevant, add any you already have in mind
- This prompt will expand it to 75 companies and wire up the `--load-seeds` CLI flag

**Why this prompt is worded this way:**
The seed list is the single most impactful thing you can do to improve coverage without adding complexity. 75 well-chosen companies polled daily is more valuable than algorithmic discovery across thousands of companies. The `/add_company` command built here is deliberately simple — just the Telegram handler structure, no full bot yet. The full bot comes in Phase 4.

**The prompt:**
```
Read CLAUDE.md first.

Two things:

1. Update data/company_seed_list.json to include all 75 companies.
   Add these to the existing 10, keeping the same JSON structure:

   USA: OpenAI (hint: jobs.ashbyhq.com/openai), Google DeepMind,
        Meta AI, Microsoft AI, Hugging Face, Weights & Biases,
        Together AI, Mistral, Perplexity, Harvey, Glean, Pinecone,
        Weaviate, LangChain, Palantir, Salesforce, ServiceNow,
        Snowflake, Elastic, Datadog, Confluent,
        JPMorgan Chase, Goldman Sachs, BlackRock, Accenture,
        McKinsey QuantumBlack, BCG X

   SG: Sea Group, Gojek, Google Singapore, Meta Singapore,
       ByteDance Singapore, Shopee, DBS Bank, OKX

   NL: Booking.com, ASML, Uber Amsterdam, Netflix Amsterdam,
       Elastic Amsterdam, Optiver, IMC Trading, Mollie

   DE: SAP, Siemens AI, Aleph Alpha, DeepL, Celonis, Helsing,
       Flixbus, Zalando, Bosch AI

   SE: Ericsson, King, Lovable, Einride

   CH (Jan-Feb window only):
       Google Zurich, UBS, Julius Baer, Microsoft Zurich, ABB

2. Add --load-seeds to main.py:
   if "--load-seeds" in sys.argv:
       from agents.enricher import load_seed_list
       load_seed_list()
       sys.exit(0)

3. Add a /add_company command stub to core/telegram_bot.py.
   For now, just a function that:
   - Takes company_name and optional hint_url
   - Calls enrich_company()
   - Returns a formatted string describing what was found:
     If detected: "✅ {name} — ATS: {ats_type}\nBoard: {url}\nAdded to tracked."
     If unknown: "⚠️ {name} added — ATS unknown.\nUse /fix_ats to correct."
   (Full Telegram integration comes in Phase 4)

Run: python main.py --load-seeds
Show me the full summary report.
```

**While Claude Code works:**
- The seed loader will make network requests for each company — it will take 3-5 minutes for 75 companies
- Watch the progress output as it runs
- Some will fail or show unknown — this is expected and normal

**After — confirm these before moving on:**

```bash
# Check company count in database
python3 -c "
from core.database import get_db, Company
db = next(get_db())
total = db.query(Company).count()
detected = db.query(Company).filter(Company.ats_type != 'unknown').count()
print(f'Total: {total}, Detected: {detected}, Unknown: {total-detected}')
"
# Expected: Total: 75, Detected: 45-55, Unknown: 20-30

# Commit Phase 2
git add -A
git commit -m "feat: phase 2 complete — enricher and 75-company registry"
```

### After Phase 2 — before moving to Phase 3

**Phase 2 exit checklist:**
- [ ] `python main.py --load-seeds` runs without crashing
- [ ] 75 companies in database
- [ ] At least 45 companies have a detected ATS type
- [ ] Unknown companies listed clearly in the summary
- [ ] `profile_to_scoring_context()` produces correct output with your real data
- [ ] Phase committed to git

**Update CLAUDE.md:** Change current phase to "Phase 3 — starting Prompt 3.1"

**Manual fix-up task:** For any company showing as unknown that you know uses Greenhouse/Lever/Ashby, make a list. You will fix these with `/fix_ats` once the bot is running in Phase 4. For now, just note them down.

---

## PHASE 3 — Poller and scorer

### Before starting Phase 3

- Phase 2 exit checklist is complete
- `CLAUDE.md` current phase updated
- Have your `data/calibration/validation_30.csv` ready — you will need it to validate the scorer at the end of this phase
- Format: `title,company,location,description,your_score,your_reason,would_apply`

**What you'll have at the end of Phase 3:**
- Daily ATS polling working — real jobs in the database
- Hard rules filtering obvious mismatches before Claude runs
- Haiku scoring routing jobs to approved/digest/dropped
- Calibration test validating Claude's scores against your judgement

---

### Prompt 3.1 — ATS poller

**Before running this prompt:**
- Open `agents/poller.py` in Windsurf
- Know that this prompt makes real HTTP requests to Greenhouse, Lever, and Ashby — your 75 companies will actually be polled
- This is the first prompt that generates real job data

**Why this prompt is worded this way:**
Greenhouse, Lever, and Ashby expose public JSON APIs — no login, no API key, no rate limits. This makes them far more reliable than any scraping approach. The deduplication logic runs before writing any job to the database, keeping the data clean from the start.

The supplemental boards (Arbeitnow, MyCareersFuture) are included but clearly labelled as weak — they run after the primary ATS polling and their results are treated as discovery hints, not confirmed postings.

**The prompt:**
```
Read CLAUDE.md first.

Build agents/poller.py. Daily ATS polling for all tracked companies.

Import uuid, hashlib, datetime from standard library.
Import requests.
Import get_db, upsert_job, create_observation, Company, Job from core.database.

def run_poll() -> dict:
   Generate run_id = str(uuid.uuid4())[:8]
   stats = {companies: 0, new_jobs: 0, duplicates: 0, errors: 0}

   Query all companies where:
   tracking_status in ("tracked", "priority_tracked")
   AND ats_type in ("greenhouse", "lever", "ashby")

   For each company:
     Try to poll based on ats_type:

     GREENHOUSE:
     slug = extract last path segment from ats_board_url
     url = f"https://boards.greenhouse.io/v1/boards/{slug}/jobs?content=true"
     r = requests.get(url, timeout=10)
     jobs_data = r.json().get("jobs", [])
     For each job:
       title = job["title"]
       location = job.get("location", {}).get("name", "Unknown")
       description = job.get("content", "")
       canonical_url = job["absolute_url"]
       posted_at = parse job["updated_at"]

     LEVER:
     slug = extract last path segment from ats_board_url
     url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
     r = requests.get(url, timeout=10)
     jobs_data = r.json() (it's a list)
     For each job:
       title = job["text"]
       location = job.get("categories", {}).get("location", "Unknown")
       description = job.get("descriptionPlain", "")
       canonical_url = job["hostedUrl"]
       posted_at = datetime.fromtimestamp(job["createdAt"]/1000)

     ASHBY:
     slug = extract last path segment from ats_board_url
     url = f"https://jobs.ashbyhq.com/api/posting-api/job-board/{slug}"
     r = requests.get(url, timeout=10)
     jobs_data = r.json().get("jobPostings", [])
     For each job:
       title = job["title"]
       location = job.get("location", "Unknown")
       description = job.get("descriptionHtml", "")
       canonical_url = job["jobUrl"]
       posted_at = parse job["publishedDate"]

   For each job across all ATS types:
     normalized_hash = hashlib.sha256(
       f"{title}{company.name}{location}".lower().encode()
     ).hexdigest()[:16]

     Check existing: query Job where canonical_url = canonical_url
     If exists: update last_seen_at, stats["duplicates"]++, skip

     Check hash: query Job where normalized_hash = hash
     If exists: mark source_deduped=True, stats["duplicates"]++, skip

     Calculate age_days = (today - posted_at).days
     If age_days > 21: skip (hard age filter)

     Create job record: status="scraped", source_type="ats_api",
     source_confidence="confirmed", country=company's country
     Write observation: source=company.ats_type, run_id=run_id
     stats["new_jobs"]++

   Print for each company:
   "  {company.name}: {new} new, {dup} duplicates"

   After primary polling, run supplemental boards:
   def _poll_arbeitnow(): fetch arbeitnow.com/api/job-board-api,
     filter for AI/ML roles, write with source_type="free_board"
   def _poll_mycareersfuture(): fetch
     api.mycareersfuture.gov.sg/v2/jobs?search=AI+engineer&limit=20,
     write similarly

   Print final summary:
   "Poll complete: {new_jobs} new jobs from {companies} companies"

Add to main.py:
   if "--poll" in sys.argv:
       from agents.poller import run_poll
       run_poll()
       sys.exit(0)

Run: python main.py --poll
Show me the full output.
```

**While Claude Code works:**
- Watch for any HTTP errors in the output — 404 means the slug is wrong for that company
- The poll will take 2-5 minutes for 75 companies
- Some companies will return 0 jobs (they have no open AI/ML roles right now — this is fine)

**After — confirm these before moving on:**

```bash
# Check how many jobs were ingested
python3 -c "
from core.database import get_db, Job
db = next(get_db())
total = db.query(Job).count()
print(f'Total jobs: {total}')

# Show a sample
j = db.query(Job).first()
if j:
    print(f'Sample: {j.title} at company_id={j.company_id}')
    print(f'  Status: {j.status}, Age: {j.age_days} days')
    print(f'  Country: {j.country}')
"
# Expected: 20-100+ jobs depending on current openings
```

---

### Prompt 3.2 — Hard rules filter

**Before running this prompt:**
- You should have real jobs in the database from Prompt 3.1
- Know that this prompt adds the filtering layer that runs before any Claude API call
- The stack-match rule is a penalty (-10), not a skip — read this carefully before running

**Why this prompt is worded this way:**
Hard rules catch the obvious wrong jobs before spending any money on Claude. Age, country, sponsorship language, seniority — these are binary. The stack-match is deliberately softer because many senior roles underspecify the tech stack, and a hard skip would mean missing good jobs. A -10 penalty lets Claude still see the job but ranks it lower.

**The prompt:**
```
Read CLAUDE.md first.

Build the hard rules layer in agents/scorer.py.

Import get_db, Job, Company from core.database.
Import load_profile from core.profile.

def apply_hard_rules(job: Job, company: Company, profile: dict
                     ) -> tuple[bool, str]:
   """
   Returns (should_skip: bool, reason: str).
   Run checks in order, stop at first True.
   """
   sc = profile["search_config"]

   # 1. Age filter
   if job.age_days and job.age_days > sc.get("age_hard_filter_days", 21):
       return True, "too_old"

   # 2. Country filter
   targets = [c.upper() for c in sc.get("target_countries", [])]
   if job.country and job.country.upper() not in targets:
       return True, "wrong_country"

   # 3. Sponsorship language
   desc_lower = (job.description or "").lower()
   sponsorship_blocks = [
       "no sponsorship", "must be authorized", "us citizen only",
       "must be a us citizen", "must be eu citizen",
       "eu citizen required", "citizens only", "no visa",
       "must have authorization to work"
   ]
   if any(phrase in desc_lower for phrase in sponsorship_blocks):
       return True, "sponsorship_blocked"

   # 4. Seniority mismatch
   title_lower = (job.title or "").lower()
   junior_signals = [
       "junior", "intern", "internship", "entry level",
       "entry-level", "associate", "graduate", "jr."
   ]
   if any(s in title_lower for s in junior_signals):
       return True, "seniority_mismatch"

   # 5. Source duplicate
   if job.source_deduped:
       return True, "source_duplicate"

   # 6. Application history — applied recently
   from core.database import get_db, Job as JobModel
   from datetime import datetime, timedelta
   db = next(get_db())
   cutoff = datetime.utcnow() - timedelta(days=90)
   recent_apply = db.query(JobModel).filter(
       JobModel.company_id == job.company_id,
       JobModel.status == "applied",
       JobModel.applied_at >= cutoff
   ).first()
   if recent_apply:
       return True, "applied_recently"

   # 7. Previously skipped (soft warn — do not skip, just flag)
   prev_skip = db.query(JobModel).filter(
       JobModel.company_id == job.company_id,
       JobModel.status == "skipped"
   ).first()
   if prev_skip:
       job.history_status = "skipped_warn"
       # Do not return True — continue to scoring

   # 8. Thin stack match (penalty, not skip)
   core_skills = [s.lower() for s in profile["skills"]["core"][:10]]
   matches = sum(1 for skill in core_skills if skill in desc_lower)
   if matches < 2:
       if not hasattr(job, "_score_penalty"):
           job._score_penalty = 0
       job._score_penalty -= 10

   return False, ""

def run_hard_rules() -> dict:
   profile = load_profile()
   db = next(get_db())
   jobs = db.query(Job).filter(
       Job.status == "scraped",
       Job.hard_filtered == False
   ).all()

   stats = {}
   for job in jobs:
       company = db.query(Company).get(job.company_id)
       should_skip, reason = apply_hard_rules(job, company, profile)
       if should_skip:
           job.hard_filtered = True
           job.hard_filter_reason = reason
           job.status = "hard_filtered"
           stats[reason] = stats.get(reason, 0) + 1
       db.commit()

   passed = len(jobs) - sum(stats.values())
   print(f"Hard rules: {passed} passed, {sum(stats.values())} skipped")
   for reason, count in sorted(stats.items()):
       print(f"  {reason}: {count}")
   return stats

Add to main.py --score flag (stub for now, Haiku added in 3.3):
   if "--score" in sys.argv:
       from agents.scorer import run_hard_rules
       run_hard_rules()
       sys.exit(0)

Run: python main.py --score
Show me the output.
```

**While Claude Code works:**
- Watch `agents/scorer.py` in Windsurf
- Make sure there are 8 numbered checks matching what you specified
- The stack-match check (rule 8) must not return `True` — it only sets a penalty

**After — confirm these before moving on:**

```bash
python main.py --score
# Should show a breakdown like:
# Hard rules: 35 passed, 12 skipped
#   too_old: 3
#   wrong_country: 5
#   sponsorship_blocked: 2
#   seniority_mismatch: 2

# If 100% passed or 100% skipped, something is wrong
# Check that job.country matches your target_countries list format
python3 -c "
from core.database import get_db, Job
db = next(get_db())
j = db.query(Job).first()
print('Country stored as:', repr(j.country))
"
# Compare this to what's in candidate_profile.json target_countries
```

---

### Prompt 3.3 — Haiku scorer

**Before running this prompt:**
- Hard rules must be working from Prompt 3.2
- You must have at least some jobs with `status="scraped"` (passed hard rules)
- This is the first prompt that calls the Anthropic API — have your API key in `.env`

**Why this prompt is worded this way:**
Haiku is the cheapest Claude model. At $0.00025 per job, you can score thousands of jobs for pennies. The prompt includes the calibration test specifically because you need to validate the scorer before trusting it with real applications. If the calibration test shows Claude is consistently off from your judgement, you tune the prompt — not the code.

**The prompt:**
```
Read CLAUDE.md first.

Add Haiku scoring to agents/scorer.py.

First, create prompts/score_jd.txt with this content:
---
Score this job for the following candidate.

{profile_context}

JOB: {title} at {company}, {location}
POSTED: {age_days} days ago
PREVIOUSLY SEEN: {previously_seen}
DESCRIPTION:
{description}

Return JSON only — no prose, no markdown, no code blocks:
{{
  "score": <integer 0-100>,
  "reason": "<exactly 2 sentences>",
  "key_matches": ["<match1>", "<match2>"],
  "red_flags": ["<flag1>"],
  "sponsorship_friendly": <true or false>,
  "seniority_match": <true or false>
}}

Scoring:
85-100: exceptional — nearly every requirement matches
75-84: strong — most requirements match, minor gaps
65-74: good — worth applying with some stretch
50-64: partial — missing key requirements
0-49: poor fit — do not apply
---

Add to agents/scorer.py:

import json
import asyncio
import anthropic
from pathlib import Path
from core.profile import load_profile, profile_to_scoring_context
from core.config import settings

async def score_job_haiku(job, company_name: str, profile: dict,
                          client) -> dict:
   context = profile_to_scoring_context(profile)
   penalty = getattr(job, "_score_penalty", 0)
   previously_seen = (
       "Yes — previously skipped by candidate"
       if job.history_status == "skipped_warn"
       else "No"
   )
   template = Path("prompts/score_jd.txt").read_text()
   prompt = template.format(
       profile_context=context,
       title=job.title or "Unknown",
       company=company_name,
       location=job.location or "Unknown",
       age_days=job.age_days or 0,
       previously_seen=previously_seen,
       description=(job.description or "")[:3000]
   )
   try:
       response = await client.messages.create(
           model="claude-haiku-4-5-20251001",
           max_tokens=300,
           messages=[{"role": "user", "content": prompt}]
       )
       result = json.loads(response.content[0].text)
       result["score"] = max(0, min(100, result["score"] + penalty))
       return result
   except json.JSONDecodeError as e:
       # Retry once
       try:
           response2 = await client.messages.create(
               model="claude-haiku-4-5-20251001",
               max_tokens=300,
               messages=[{"role": "user", "content": prompt + "\n\nReturn valid JSON only."}]
           )
           return json.loads(response2.content[0].text)
       except Exception:
           return {"score": 0, "reason": "Scoring failed", "key_matches": [],
                   "red_flags": ["scoring error"], "sponsorship_friendly": False,
                   "seniority_match": False}

async def run_haiku_scoring():
   profile = load_profile()
   client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
   db = next(get_db())

   jobs = db.query(Job).filter(
       Job.status == "scraped",
       Job.hard_filtered == False
   ).all()

   print(f"Scoring {len(jobs)} jobs with Haiku...")
   stats = {"approved": 0, "digest": 0, "dropped": 0}
   min_immediate = profile["search_config"].get("min_score_immediate", 75)
   min_digest = profile["search_config"].get("min_score_digest", 65)

   for i in range(0, len(jobs), 5):
       batch = jobs[i:i+5]
       tasks = []
       for job in batch:
           company = db.query(Company).get(job.company_id)
           company_name = company.name if company else "Unknown"
           tasks.append(score_job_haiku(job, company_name, profile, client))
       results = await asyncio.gather(*tasks)
       for job, result in zip(batch, results):
           job.score = result["score"]
           job.score_reason = result["reason"]
           job.key_matches = result["key_matches"]
           job.red_flags = result["red_flags"]
           if job.score >= min_immediate:
               job.status = "approved"
               stats["approved"] += 1
           elif job.score >= min_digest:
               job.status = "digest"
               stats["digest"] += 1
           else:
               job.status = "dropped"
               stats["dropped"] += 1
       db.commit()
       if i + 5 < len(jobs):
           await asyncio.sleep(1)

   print(f"Haiku scoring: {stats['approved']} approved (75+), "
         f"{stats['digest']} digest (65-74), {stats['dropped']} dropped (<65)")

Update run_hard_rules() to call run_haiku_scoring() after filtering.
Update --score in main.py to run both.

Also write tests/test_scorer.py:
def test_calibration():
   csv_path = Path("data/calibration/validation_30.csv")
   if not csv_path.exists():
       import pytest; pytest.skip("validation_30.csv not found")
   import csv, asyncio
   rows = list(csv.DictReader(csv_path.open()))
   profile = load_profile()
   client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
   deltas = []
   disagreements = []
   for row in rows:
       # Create a minimal Job-like object for scoring
       class FakeJob:
           title=row["title"]; location=row["location"]
           description=row["description"]; age_days=7
           history_status=None; _score_penalty=0
       result = asyncio.run(
           score_job_haiku(FakeJob(), row["company"], profile, client))
       delta = abs(result["score"] - int(row["your_score"]))
       deltas.append(delta)
       if delta > 15:
           disagreements.append(
               f"{row['company']}: you={row['your_score']}, claude={result['score']}"
           )
   avg = sum(deltas) / len(deltas)
   print(f"Average delta: {avg:.1f} points")
   if disagreements:
       print("Disagreements (>15 pts):")
       for d in disagreements: print(f"  {d}")
   assert avg < 10, f"Average delta {avg:.1f} too high — tune scoring prompt"

Run: python main.py --score
Then: python -m pytest tests/test_scorer.py -v
Show me both outputs.
```

**While Claude Code works:**
- This prompt makes real Anthropic API calls — small cost (~$0.01 for a few jobs)
- Watch the output for any JSON parsing errors
- If the distribution looks wrong (all 90+, or all below 50), the prompt needs tuning

**After — confirm these before moving on:**

```bash
# Check score distribution
python3 -c "
from core.database import get_db, Job
db = next(get_db())
approved = db.query(Job).filter(Job.status=='approved').count()
digest = db.query(Job).filter(Job.status=='digest').count()
dropped = db.query(Job).filter(Job.status=='dropped').count()
print(f'Approved: {approved}, Digest: {digest}, Dropped: {dropped}')

# Read one approved job's reason
j = db.query(Job).filter(Job.status=='approved').first()
if j: print(f'Top job: {j.title}, score={j.score}, reason={j.score_reason}')
"

# If you have validation_30.csv, run calibration
python -m pytest tests/test_scorer.py -v

# Commit
git add -A
git commit -m "feat: phase 3 complete — poller, hard rules, Haiku scorer"
```

### After Phase 3 — before moving to Phase 4

**Phase 3 exit checklist:**
- [ ] `python main.py --poll` ingests real jobs
- [ ] `python main.py --score` produces a reasonable distribution (not all one status)
- [ ] If `validation_30.csv` exists: calibration test average delta < 10 points
- [ ] Score reason for an approved job makes sense and feels relevant
- [ ] Phase committed to git

**Update CLAUDE.md:** Change current phase to "Phase 4 — starting Prompt 4.1"

---

## PHASE 4 — Telegram bot

### Before starting Phase 4

- Phase 3 exit checklist is complete
- Your Telegram bot token and chat ID are in `.env`
- You have Telegram open on your phone — you will receive real messages during this phase
- Know that Phase 4 Prompt 4.3 (the `/setup` ConversationHandler) is a full evening on its own — do not underestimate it

**What you'll have at the end of Phase 4:**
- Real job notifications arriving on your phone
- APPLY/SKIP/EDIT buttons working
- Reply "done" closing the tracking loop
- `/setup` running full onboarding or section editing
- `/add_company`, `/fix_ats`, `/status` all working

---

### Prompt 4.1 — Telegram sending functions

**Before running this prompt:**
- Run `pip install python-telegram-bot` if not already installed
- Open `core/telegram_bot.py` in Windsurf — it should currently be empty
- Know that this prompt only builds the sending functions — not the handlers that receive your taps

**Why this prompt is worded this way:**
Building the sending side first means you can test immediately by running `--test-telegram` and checking your phone. If the message arrives, the bot token and chat ID are correct. If not, you know the problem before building the more complex handler side.

**The prompt:**
```
Read CLAUDE.md first.

Build the sending functions in core/telegram_bot.py.
Use python-telegram-bot v20 (async).

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application
from core.config import settings

async def send_approval_message(job, bot: Bot) -> str:
   """Send immediate 75+ notification. Returns telegram_message_id."""
   matches_str = ", ".join(job.key_matches or []) or "None detected"
   flags_str = ", ".join(job.red_flags or []) or "None"
   pts = job.talking_points
   if pts and isinstance(pts, list):
       pts_str = "\n".join(f"{i+1}. {p}" for i, p in enumerate(pts))
   else:
       pts_str = "[Generating on APPLY tap]"

   text = (
       f"🎯 New role — Score: {job.score}/100\n\n"
       f"*{job.title}*\n"
       f"📍 {job.location} · {job.country}\n"
       f"📅 Posted {job.age_days} days ago\n\n"
       f"*Why {job.score}:* {job.score_reason}\n\n"
       f"✅ *Matches:* {matches_str}\n"
       f"⚠️ *Flags:* {flags_str}\n\n"
       f"💡 *Talking points:*\n{pts_str}\n\n"
       f"🔗 {job.canonical_url}"
   )
   keyboard = InlineKeyboardMarkup([[
       InlineKeyboardButton("✅ APPLY", callback_data=f"apply_{job.id}"),
       InlineKeyboardButton("❌ SKIP", callback_data=f"skip_{job.id}"),
       InlineKeyboardButton("✏️ EDIT", callback_data=f"edit_{job.id}")
   ]])
   msg = await bot.send_message(
       chat_id=settings.TELEGRAM_CHAT_ID,
       text=text,
       parse_mode="Markdown",
       reply_markup=keyboard
   )
   return str(msg.message_id)

async def send_daily_digest(jobs: list, promotions: dict, bot: Bot):
   """Send batched digest for 65-74 jobs plus registry updates."""
   if not jobs and not any(promotions.values()):
       return
   lines = [f"📋 *Daily digest — {__import__('datetime').date.today()}*\n"]
   if jobs:
       lines.append(f"*{len(jobs)} roles in your queue:*\n")
       for j in sorted(jobs, key=lambda x: x.score, reverse=True):
           lines.append(
               f"[{j.score}] {j.title}\n"
               f"     → /request_docs {j.id}\n"
           )
   if promotions.get("tracked"):
       lines.append(f"\n🏢 *New tracked:* {', '.join(promotions['tracked'])}")
   if promotions.get("priority"):
       lines.append(f"\n⭐ *New priority:* {', '.join(promotions['priority'])}")
   await bot.send_message(
       chat_id=settings.TELEGRAM_CHAT_ID,
       text="\n".join(lines),
       parse_mode="Markdown"
   )

async def send_priority_alert(job, bot: Bot) -> str:
   """Fast-path alert for priority_tracked company new roles."""
   text = f"⚡ *Priority alert* — new role at tracked company\n\n"
   return await send_approval_message(job, bot)

async def send_manual_assisted_packet(job, resume_path: str,
                                       cover_letter_path: str, bot: Bot):
   """Send prepped packet for Workday/unknown ATS."""
   pts = job.talking_points or []
   pts_str = "\n".join(f"{i+1}. {p}" for i,p in enumerate(pts)) if pts else ""
   text = (
       f"🔧 *Manual submit needed*\n\n"
       f"*{job.title}*\n"
       f"ATS: {job.ats_type or 'unknown'}\n"
       f"🔗 {job.canonical_url}\n\n"
       f"*Talking points:*\n{pts_str}\n\n"
       f"Resume + cover letter attached. Est. 5 min to submit."
   )
   await bot.send_message(
       chat_id=settings.TELEGRAM_CHAT_ID,
       text=text, parse_mode="Markdown"
   )
   if resume_path:
       await bot.send_document(
           chat_id=settings.TELEGRAM_CHAT_ID,
           document=open(resume_path, "rb")
       )

Add to main.py:
   if "--test-telegram" in sys.argv:
       import asyncio
       from telegram import Bot
       async def _test():
           bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
           await bot.send_message(
               chat_id=settings.TELEGRAM_CHAT_ID,
               text="✅ Bot connected. Job agent ready."
           )
           print("Test message sent. Check your Telegram.")
       asyncio.run(_test())
       sys.exit(0)

Run: python main.py --test-telegram
Check your phone. Show me what you see (describe the message).
```

**While Claude Code works:**
- Watch `core/telegram_bot.py` being written in Windsurf
- The file should be 80-120 lines
- Check that `send_approval_message` returns the message_id — this is needed for reply parsing

**After — confirm these before moving on:**

```bash
python main.py --test-telegram
# Check your phone — message should arrive within 10 seconds
# If nothing arrives after 30 seconds: check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env
```

---

### Prompt 4.2 — Command handlers and reply parser

**Before running this prompt:**
- Test message must have arrived on your phone from Prompt 4.1
- Open your Telegram app — you will be interacting with the bot during testing
- Know that this prompt adds the interactive handlers

**Why this prompt is worded this way:**
The reply parser is the subtlest piece — it matches your "done" reply to a specific job using `telegram_message_id`. Without this, the tracking loop has no closure. The handler builds are straightforward but the reply logic needs careful implementation.

**The prompt:**
```
Read CLAUDE.md first.

Add command handlers to core/telegram_bot.py.
Build run_bot() that starts the Application with all handlers.

from telegram.ext import (Application, CallbackQueryHandler,
    MessageHandler, CommandHandler, filters)

async def handle_apply(update, context):
   query = update.callback_query
   await query.answer()
   job_id = int(query.data.split("_")[1])
   db = next(get_db())
   job = db.query(Job).get(job_id)
   if not job: return
   job.status = "approved"
   job.approved_at = datetime.utcnow()
   db.commit()
   from core.router import route_application
   route = route_application(job)
   job.route = route
   db.commit()
   if route == "manual_ready":
       await query.edit_message_text(
           f"✅ Approved — generating docs...\n🔗 {job.canonical_url}"
       )
   else:
       await query.edit_message_text(
           f"🔧 Manual submit — preparing packet...\n🔗 {job.canonical_url}"
       )
   # Trigger writer (stub — full writer in Phase 5)
   print(f"[stub] Would generate docs for job {job_id}")

async def handle_skip(update, context):
   query = update.callback_query
   await query.answer()
   job_id = int(query.data.split("_")[1])
   db = next(get_db())
   job = db.query(Job).get(job_id)
   if not job: return
   job.status = "skipped"
   db.commit()
   await query.edit_message_text("❌ Skipped.")

async def handle_edit(update, context):
   query = update.callback_query
   await query.answer()
   await query.message.reply_text(
       "✏️ What should change? Reply to this message with feedback."
   )

async def handle_reply(update, context):
   msg = update.message
   if not msg.reply_to_message: return
   replied_id = str(msg.reply_to_message.message_id)
   db = next(get_db())
   job = db.query(Job).filter(
       Job.telegram_message_id == replied_id
   ).first()
   if not job: return
   text_lower = msg.text.lower()
   confirmation_words = ["done", "applied", "submitted", "sent", "in"]
   if any(w in text_lower for w in confirmation_words):
       job.confirmed_at = datetime.utcnow()
       job.status = "applied"
       db.commit()
       await msg.reply_text("✅ Logged as applied. Good luck!")

async def cmd_status(update, context):
   from datetime import date
   db = next(get_db())
   today = date.today()
   scraped = db.query(Job).filter(Job.status=="scraped").count()
   approved = db.query(Job).filter(Job.status=="approved").count()
   digest = db.query(Job).filter(Job.status=="digest").count()
   applied = db.query(Job).filter(Job.status=="applied").count()
   from core.database import Company
   tracked = db.query(Company).filter(
       Company.tracking_status=="tracked").count()
   priority = db.query(Company).filter(
       Company.tracking_status=="priority_tracked").count()
   await update.message.reply_text(
       f"📊 *Pipeline status*\n"
       f"Scraped: {scraped} · Approved: {approved} · "
       f"Digest: {digest} · Applied: {applied}\n"
       f"Companies: {tracked} tracked · {priority} priority",
       parse_mode="Markdown"
   )

async def cmd_add_company(update, context):
   args = context.args
   if not args:
       await update.message.reply_text("Usage: /add_company CompanyName [hint_url]")
       return
   name = args[0]
   hint = args[1] if len(args) > 1 else None
   from agents.enricher import enrich_company
   company = enrich_company(name, hint)
   if company.ats_type != "unknown":
       await update.message.reply_text(
           f"✅ {company.name} — ATS: {company.ats_type}\n"
           f"Board: {company.ats_board_url}\nAdded to tracked."
       )
   else:
       await update.message.reply_text(
           f"⚠️ {company.name} added — ATS unknown.\n"
           f"Use /fix_ats {company.id} greenhouse (or lever/ashby)"
       )

async def cmd_fix_ats(update, context):
   if len(context.args) < 2:
       await update.message.reply_text("Usage: /fix_ats company_id type")
       return
   company_id, ats_type = int(context.args[0]), context.args[1]
   db = next(get_db())
   company = db.query(Company).get(company_id)
   if not company:
       await update.message.reply_text("Company not found.")
       return
   company.ats_type = ats_type
   company.ats_confirmed = True
   db.commit()
   await update.message.reply_text(f"✅ {company.name} → {ats_type}")

async def cmd_applied(update, context):
   if not context.args:
       await update.message.reply_text("Usage: /applied job_id")
       return
   job_id = int(context.args[0])
   db = next(get_db())
   job = db.query(Job).get(job_id)
   if not job:
       await update.message.reply_text("Job not found.")
       return
   job.confirmed_at = datetime.utcnow()
   job.status = "applied"
   db.commit()
   await update.message.reply_text("✅ Logged as applied.")

def run_bot():
   app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
   app.add_handler(CallbackQueryHandler(handle_apply, pattern="^apply_"))
   app.add_handler(CallbackQueryHandler(handle_skip, pattern="^skip_"))
   app.add_handler(CallbackQueryHandler(handle_edit, pattern="^edit_"))
   app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, handle_reply))
   app.add_handler(CommandHandler("status", cmd_status))
   app.add_handler(CommandHandler("add_company", cmd_add_company))
   app.add_handler(CommandHandler("fix_ats", cmd_fix_ats))
   app.add_handler(CommandHandler("applied", cmd_applied))
   print("Bot running. Ctrl+C to stop.")
   app.run_polling()

Add to main.py:
   if "--bot" in sys.argv:
       from core.telegram_bot import run_bot
       run_bot()
       sys.exit(0)

Also create core/router.py:
   def classify_ats(url: str) -> str:
       patterns = {
           "greenhouse": ["greenhouse.io", "boards.greenhouse"],
           "lever": ["jobs.lever.co", "lever.co"],
           "ashby": ["jobs.ashbyhq.com"],
           "workday": ["myworkdayjobs.com", "wd1.myworkdayjobs"],
       }
       for ats, urls in patterns.items():
           if any(p in (url or "") for p in urls):
               return ats
       return "unknown"

   def route_application(job) -> str:
       ats = classify_ats(job.canonical_url)
       if ats in ("greenhouse", "lever", "ashby"):
           return "manual_ready"
       return "manual_assisted"

Run: python main.py --bot
Then from Telegram send: /status
Show me what the bot replies.
```

**While Claude Code works:**
- Keep a second terminal tab open for running the bot separately from other commands
- The bot blocks the terminal while running — use Ctrl+C to stop it

**After — confirm these before moving on:**

Open your Telegram app and test:
```
Send: /status           → should show real numbers from your database
Send: /add_company Stripe  → should detect Greenhouse and confirm
Send: /fix_ats 1 lever  → should update that company (use a real company_id)
```

---

### Prompt 4.3 — /setup ConversationHandler

**Before running this prompt:**
- Budget a full evening for this prompt — it is the most complex single piece in the project
- All previous Telegram commands must be working from Prompt 4.2
- Know that this replaces `setup_profile.py` for future profile edits — the CLI script still works as a fallback

**Why this prompt is worded this way:**
A ConversationHandler has states, transitions, and branching paths. It's substantially more complex than a simple command handler. The one-question-at-a-time flow with section menus requires careful state management. Take your time reading the output in Windsurf before running it.

**The prompt:**
```
Read CLAUDE.md first.

Add /setup as a ConversationHandler in core/telegram_bot.py.

This is complex — implement carefully.

from telegram.ext import ConversationHandler

Define state constants at module level:
SECTION_MENU = 0
ID_NAME, ID_TITLE, ID_EMPLOYER, ID_LOCATION = 1, 2, 3, 4
EXP_YEARS, EXP_SUMMARY, EXP_METRICS_START, EXP_METRICS_MORE = 5, 6, 7, 8
SK_CORE, SK_STACK, SK_CLOUD = 9, 10, 11
SC_COUNTRIES, SC_CITIES, SC_WORKMODE = 12, 13, 14
SC_ROLES, SC_VISA, SC_SPONSORSHIP, SC_THRESHOLDS = 15, 16, 17, 18
CONFIRM_SECTION = 19

Implement these handlers:

async def cmd_setup(update, context):
   from core.profile import load_profile
   try:
       profile = load_profile()
       context.user_data["profile_draft"] = dict(profile)
       keyboard = InlineKeyboardMarkup([[
           InlineKeyboardButton("Identity", callback_data="section_identity"),
           InlineKeyboardButton("Experience", callback_data="section_experience"),
       ],[
           InlineKeyboardButton("Skills", callback_data="section_skills"),
           InlineKeyboardButton("Search config", callback_data="section_search"),
       ],[
           InlineKeyboardButton("✅ Done", callback_data="section_done"),
       ]])
       await update.message.reply_text(
           "Profile loaded. Which section to update?",
           reply_markup=keyboard
       )
       return SECTION_MENU
   except FileNotFoundError:
       context.user_data["profile_draft"] = {}
       await update.message.reply_text("Let's set up your profile. One question at a time.\n\nFirst: What's your full name?")
       return ID_NAME

async def received_name(update, context):
   context.user_data["profile_draft"].setdefault("identity", {})
   context.user_data["profile_draft"]["identity"]["name"] = update.message.text
   await update.message.reply_text("Current job title?")
   return ID_TITLE

async def received_title(update, context):
   context.user_data["profile_draft"]["identity"]["current_title"] = update.message.text
   await update.message.reply_text("Current employer?")
   return ID_EMPLOYER

async def received_employer(update, context):
   context.user_data["profile_draft"]["identity"]["current_employer"] = update.message.text
   await update.message.reply_text("Location? (e.g. West Lafayette, IN)")
   return ID_LOCATION

async def received_location(update, context):
   context.user_data["profile_draft"]["identity"]["location"] = update.message.text
   await update.message.reply_text("Years of total experience? (number)")
   return EXP_YEARS

async def received_years(update, context):
   context.user_data["profile_draft"].setdefault("experience", {})
   context.user_data["profile_draft"]["experience"]["years_total"] = int(update.message.text)
   await update.message.reply_text("One-paragraph background summary:")
   return EXP_SUMMARY

async def received_summary(update, context):
   context.user_data["profile_draft"]["experience"]["summary"] = update.message.text
   context.user_data["profile_draft"]["experience"]["key_metrics"] = []
   await update.message.reply_text("Key metrics — one at a time. (Send each metric, then send 'done' when finished)\nFirst metric:")
   return EXP_METRICS_START

async def received_metric(update, context):
   text = update.message.text.strip()
   if text.lower() == "done":
       await update.message.reply_text("Core AI/ML skills (comma-separated):")
       return SK_CORE
   context.user_data["profile_draft"]["experience"]["key_metrics"].append(text)
   count = len(context.user_data["profile_draft"]["experience"]["key_metrics"])
   if count >= 5:
       await update.message.reply_text("5 metrics saved. Core AI/ML skills (comma-separated):")
       return SK_CORE
   await update.message.reply_text(f"Metric {count} saved. Next metric (or 'done'):")
   return EXP_METRICS_MORE

async def received_core_skills(update, context):
   context.user_data["profile_draft"].setdefault("skills", {})
   context.user_data["profile_draft"]["skills"]["core"] = [
       s.strip() for s in update.message.text.split(",")
   ]
   await update.message.reply_text("Tech stack (comma-separated):")
   return SK_STACK

async def received_stack(update, context):
   context.user_data["profile_draft"]["skills"]["stack"] = [
       s.strip() for s in update.message.text.split(",")
   ]
   await update.message.reply_text("Cloud platforms (comma-separated):")
   return SK_CLOUD

async def received_cloud(update, context):
   context.user_data["profile_draft"]["skills"]["cloud"] = [
       s.strip() for s in update.message.text.split(",")
   ]
   keyboard = InlineKeyboardMarkup([[
       InlineKeyboardButton("🇺🇸 USA", callback_data="country_USA"),
       InlineKeyboardButton("🇸🇬 SG", callback_data="country_SG"),
       InlineKeyboardButton("🇳🇱 NL", callback_data="country_NL"),
   ],[
       InlineKeyboardButton("🇩🇪 DE", callback_data="country_DE"),
       InlineKeyboardButton("🇸🇪 SE", callback_data="country_SE"),
       InlineKeyboardButton("🇨🇭 CH", callback_data="country_CH"),
   ],[
       InlineKeyboardButton("✅ Done selecting", callback_data="countries_done"),
   ]])
   context.user_data["profile_draft"].setdefault("search_config", {})
   context.user_data["profile_draft"]["search_config"]["target_countries"] = []
   await update.message.reply_text(
       "Target countries (tap all that apply, then Done):",
       reply_markup=keyboard
   )
   return SC_COUNTRIES

async def country_toggle(update, context):
   query = update.callback_query
   await query.answer()
   if query.data == "countries_done":
       await query.edit_message_text(
           "Work mode preferences (tap all that apply):",
           reply_markup=InlineKeyboardMarkup([[
               InlineKeyboardButton("Remote", callback_data="wm_remote"),
               InlineKeyboardButton("Hybrid", callback_data="wm_hybrid"),
               InlineKeyboardButton("On-site", callback_data="wm_onsite"),
           ],[
               InlineKeyboardButton("✅ Done", callback_data="wm_done"),
           ]])
       )
       context.user_data["profile_draft"]["search_config"]["work_mode_preferences"] = []
       return SC_WORKMODE
   country = query.data.split("_")[1]
   countries = context.user_data["profile_draft"]["search_config"]["target_countries"]
   if country in countries:
       countries.remove(country)
   else:
       countries.append(country)
   await query.answer(f"{'Added' if country in countries else 'Removed'} {country}")
   return SC_COUNTRIES

async def workmode_toggle(update, context):
   query = update.callback_query
   await query.answer()
   if query.data == "wm_done":
       keyboard = InlineKeyboardMarkup([[
           InlineKeyboardButton("H-1B", callback_data="visa_H1B"),
           InlineKeyboardButton("EAD", callback_data="visa_EAD"),
           InlineKeyboardButton("OPT", callback_data="visa_OPT"),
       ],[
           InlineKeyboardButton("Green Card", callback_data="visa_GC"),
           InlineKeyboardButton("Citizen", callback_data="visa_Citizen"),
           InlineKeyboardButton("Other", callback_data="visa_Other"),
       ]])
       await query.edit_message_text("Visa status:", reply_markup=keyboard)
       return SC_VISA
   mode = query.data.split("_")[1]
   modes = context.user_data["profile_draft"]["search_config"].setdefault(
       "work_mode_preferences", [])
   if mode in modes: modes.remove(mode)
   else: modes.append(mode)
   return SC_WORKMODE

async def received_visa(update, context):
   query = update.callback_query
   await query.answer()
   visa = query.data.split("_")[1]
   context.user_data["profile_draft"]["search_config"]["visa_status"] = visa
   keyboard = InlineKeyboardMarkup([[
       InlineKeyboardButton("Yes", callback_data="sponsor_yes"),
       InlineKeyboardButton("No", callback_data="sponsor_no"),
   ]])
   await query.edit_message_text(
       "Needs employer sponsorship for international roles?",
       reply_markup=keyboard
   )
   return SC_SPONSORSHIP

async def received_sponsorship(update, context):
   query = update.callback_query
   await query.answer()
   context.user_data["profile_draft"]["search_config"]["needs_sponsorship"] = (
       query.data == "sponsor_yes"
   )
   keyboard = InlineKeyboardMarkup([[
       InlineKeyboardButton("75", callback_data="thresh_75_imm"),
       InlineKeyboardButton("80", callback_data="thresh_80_imm"),
       InlineKeyboardButton("Type instead", callback_data="thresh_type_imm"),
   ]])
   await query.edit_message_text(
       "Min score for immediate Telegram alert:", reply_markup=keyboard
   )
   return SC_THRESHOLDS

async def received_thresholds(update, context):
   query = update.callback_query
   await query.answer()
   val = int(query.data.split("_")[1])
   context.user_data["profile_draft"]["search_config"]["min_score_immediate"] = val
   context.user_data["profile_draft"]["search_config"]["min_score_digest"] = val - 10
   context.user_data["profile_draft"]["search_config"]["max_daily_apps"] = 15
   context.user_data["profile_draft"]["search_config"]["age_hard_filter_days"] = 21
   context.user_data["profile_draft"]["search_config"]["history_block_days"] = 90
   context.user_data["profile_draft"]["search_config"]["auto_ignore_days"] = 60
   await _finish_setup(update.callback_query.message, context)
   return ConversationHandler.END

async def _finish_setup(message, context):
   from core.profile import save_profile, profile_to_scoring_context
   profile = context.user_data.get("profile_draft", {})
   save_profile(profile)
   preview = profile_to_scoring_context(profile)
   await message.reply_text(
       f"✅ Profile saved!\n\n*Scoring context preview:*\n```\n{preview[:800]}\n```",
       parse_mode="Markdown"
   )

async def cmd_cancel(update, context):
   context.user_data.clear()
   await update.message.reply_text("Setup cancelled.")
   return ConversationHandler.END

async def section_done(update, context):
   query = update.callback_query
   await query.answer()
   await _finish_setup(query.message, context)
   return ConversationHandler.END

setup_handler = ConversationHandler(
   entry_points=[CommandHandler("setup", cmd_setup)],
   states={
       SECTION_MENU: [CallbackQueryHandler(section_done, pattern="^section_done$"),
                      CallbackQueryHandler(lambda u,c: ID_NAME, pattern="^section_")],
       ID_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_name)],
       ID_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_title)],
       ID_EMPLOYER: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_employer)],
       ID_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_location)],
       EXP_YEARS: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_years)],
       EXP_SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_summary)],
       EXP_METRICS_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_metric)],
       EXP_METRICS_MORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_metric)],
       SK_CORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_core_skills)],
       SK_STACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_stack)],
       SK_CLOUD: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_cloud)],
       SC_COUNTRIES: [CallbackQueryHandler(country_toggle)],
       SC_WORKMODE: [CallbackQueryHandler(workmode_toggle)],
       SC_VISA: [CallbackQueryHandler(received_visa, pattern="^visa_")],
       SC_SPONSORSHIP: [CallbackQueryHandler(received_sponsorship, pattern="^sponsor_")],
       SC_THRESHOLDS: [CallbackQueryHandler(received_thresholds, pattern="^thresh_")],
   },
   fallbacks=[CommandHandler("cancel", cmd_cancel)],
)

Add setup_handler to run_bot() before app.run_polling().

Run: python main.py --bot
Then send /setup to your bot. Walk through the full flow.
Show me the scoring context preview the bot sends at the end.
```

**While Claude Code works:**
- This is a large file — watch it appear in Windsurf section by section
- Check that every state in the `states` dict has a corresponding handler function
- Check that `ConversationHandler.END` is returned at the end of the flow

**After — confirm these before moving on:**

```bash
# Run the bot and test /setup end to end on your phone
python main.py --bot

# After /setup completes, verify the profile was updated
python3 -c "
from core.profile import load_profile, profile_to_scoring_context
print(profile_to_scoring_context(load_profile()))
"

# Try /setup a second time — should show section menu, not restart
# Tap one section, update one field, tap Done
# Verify only that field changed

git add -A
git commit -m "feat: phase 4 complete — Telegram bot, /setup, all commands"
```

### After Phase 4 — before moving to Phase 5

**Phase 4 exit checklist:**
- [ ] Test message arrives on phone with `--test-telegram`
- [ ] `/status` shows real numbers
- [ ] `/add_company` detects and saves a company
- [ ] `/setup` runs full onboarding, saves profile correctly
- [ ] `/setup` second run shows section menu (edit mode)
- [ ] APPLY/SKIP/EDIT buttons tap correctly
- [ ] Reply "done" → bot says "Logged as applied"
- [ ] Phase committed to git

**Update CLAUDE.md:** Change current phase to "Phase 5 — starting Prompt 5.1"

---

## PHASE 5 — Writer and full pipeline

### Before starting Phase 5

- Phase 4 exit checklist is complete
- You have approved jobs in the database (status="approved") — if not, run `--poll` and `--score`
- Know that this phase makes your first Sonnet API calls — cost is ~$3 per resume+cover letter pair
- `CLAUDE.md` current phase updated

**What you'll have at the end of Phase 5:**
- Sonnet generating tailored resume and cover letter after APPLY tap
- Company promotion evaluator running automatically
- Full `./run.sh` pipeline command
- Health check, calibration test, all tests passing

---

### Prompt 5.1 — Sonnet writer

**Before running this prompt:**
- Have at least one job with `status="approved"` in the database
- Have `data/base_resume.json` — either written by `/setup` or manually created
- Know that this prompt generates real documents you will use for real applications

**Why this prompt is worded this way:**
Sonnet runs two calls in parallel using `asyncio.gather`. This halves the generation time. The resume rewrite returns JSON which then gets rendered to `.docx` by python-docx. The cover letter is plain text saved to `.txt`. Both arrive in your Telegram message after the APPLY tap.

**The prompt:**
```
Read CLAUDE.md first.

Build agents/writer.py — Sonnet document generator.

Create these prompt files first:

prompts/rewrite_resume.txt:
---
Rewrite this resume for the following job.

CANDIDATE:
{profile_context}

BASE RESUME (JSON):
{base_resume_json}

JOB: {title} at {company}, {location} ({country})
DESCRIPTION:
{description}

INSTRUCTIONS:
- Reorder bullets so the most JD-relevant ones appear first
- Rewrite the summary (2-3 sentences) using this company's language
- Emphasise skills the JD explicitly mentions that the candidate has
- Tone: {tone}
- Keep to 1 page — cut lower-priority bullets if needed
- Never fabricate or exaggerate metrics
Return the same JSON structure as the base resume. JSON only.
---

prompts/cover_letter.txt:
---
Write a cover letter for {candidate_name} applying to {company} for {title}.

CANDIDATE:
{profile_context}

JOB DESCRIPTION:
{description}

TONE: {tone}

FORMAT — 3 paragraphs, max 300 words:
Para 1: compelling hook + why this specific company + strongest achievement
Para 2: 2 specific skill matches, each with a metric
Para 3: why this location/market + confident call to action
Company name must appear at least once.
Return plain text only.
---

prompts/talking_points.txt:
---
Generate 3 talking points for {candidate_name} for this role.

CANDIDATE:
{profile_context}

JOB DESCRIPTION:
{description}
KEY JD TERMS: {top_5_jd_keywords}

RULES:
- Each point: 2 sentences — specific claim, then specific evidence
- Must reference at least 3 of the KEY JD TERMS listed above
- Generic statements are not acceptable — be role-specific
Return numbered list (1. 2. 3.). Plain text only.
---

Build agents/writer.py:

import asyncio, json
from pathlib import Path
import anthropic
from docx import Document
from docx.shared import Pt
from core.config import settings
from core.profile import load_profile, profile_to_scoring_context

TONE_BY_COUNTRY = {
   "USA": "direct and achievement-focused",
   "SG": "achievement-focused with enthusiasm for the Singapore tech ecosystem",
   "NL": "warm but professional",
   "DE": "formal and precision-focused",
   "SE": "collaborative and values-aligned",
   "CH": "precise and quality-focused",
}

def extract_jd_keywords(description: str, profile: dict) -> list[str]:
   """Find top 5 distinctive technical terms from JD that match profile skills."""
   all_skills = (
       profile["skills"]["core"] +
       profile["skills"]["stack"] +
       profile["skills"].get("cloud", [])
   )
   desc_lower = description.lower()
   matches = [s for s in all_skills if s.lower() in desc_lower]
   return matches[:5]

async def generate_documents(job, profile: dict, client) -> tuple[str, str, list]:
   """
   Generate resume (.docx), cover letter (.txt), and talking points.
   Returns (resume_path, cover_letter_path, talking_points_list).
   """
   context = profile_to_scoring_context(profile)
   tone = TONE_BY_COUNTRY.get(job.country or "USA", "professional")
   base_resume = json.loads(Path(settings.RESUME_PATH).read_text())
   keywords = extract_jd_keywords(job.description or "", profile)
   keywords_str = ", ".join(keywords)
   candidate_name = profile["identity"]["name"]

   # Load prompt templates
   resume_tmpl = Path("prompts/rewrite_resume.txt").read_text()
   cl_tmpl = Path("prompts/cover_letter.txt").read_text()
   tp_tmpl = Path("prompts/talking_points.txt").read_text()

   # Parallel Sonnet calls (resume + cover letter)
   # Talking points use Haiku (cheaper, pre-approval already done)
   resume_prompt = resume_tmpl.format(
       profile_context=context,
       base_resume_json=json.dumps(base_resume, indent=2),
       title=job.title, company="[Company]",
       location=job.location or "", country=job.country or "",
       description=(job.description or "")[:3000],
       tone=tone
   )
   cl_prompt = cl_tmpl.format(
       candidate_name=candidate_name, company="[Company]",
       title=job.title, profile_context=context,
       description=(job.description or "")[:3000], tone=tone
   )
   tp_prompt = tp_tmpl.format(
       candidate_name=candidate_name,
       profile_context=context,
       description=(job.description or "")[:2000],
       top_5_jd_keywords=keywords_str
   )

   # Run resume + cover letter in parallel, talking points with Haiku
   resume_coro = client.messages.create(
       model="claude-sonnet-4-6", max_tokens=2000,
       messages=[{"role": "user", "content": resume_prompt}]
   )
   cl_coro = client.messages.create(
       model="claude-sonnet-4-6", max_tokens=800,
       messages=[{"role": "user", "content": cl_prompt}]
   )
   tp_coro = client.messages.create(
       model="claude-haiku-4-5-20251001", max_tokens=400,
       messages=[{"role": "user", "content": tp_prompt}]
   )
   resume_resp, cl_resp, tp_resp = await asyncio.gather(
       resume_coro, cl_coro, tp_coro
   )

   # Parse resume JSON and render to docx
   resume_json = json.loads(resume_resp.content[0].text)
   safe_name = f"{job.id}_{(job.title or 'role').replace(' ','_')[:20]}"
   Path("data/outputs").mkdir(exist_ok=True)
   resume_path = f"data/outputs/{safe_name}_resume.docx"
   _render_resume_docx(resume_json, profile, resume_path)

   # Save cover letter
   cl_text = cl_resp.content[0].text
   cl_path = f"data/outputs/{safe_name}_cover_letter.txt"
   Path(cl_path).write_text(cl_text)

   # Parse talking points
   tp_text = tp_resp.content[0].text
   tp_list = [line.strip() for line in tp_text.split("\n")
              if line.strip() and line.strip()[0].isdigit()]

   return resume_path, cl_path, tp_list

def _render_resume_docx(resume_data: dict, profile: dict, output_path: str):
   """Render resume JSON to a clean 1-page .docx."""
   doc = Document()
   style = doc.styles["Normal"]
   style.font.name = "Arial"
   style.font.size = Pt(10)

   identity = profile.get("identity", {})
   # Name
   title = doc.add_heading(identity.get("name", ""), level=1)
   title.alignment = 1  # centre

   # Contact line
   contact = doc.add_paragraph()
   contact.alignment = 1
   contact.add_run(
       f"{identity.get('email','')} | {identity.get('phone','')} | "
       f"{identity.get('linkedin_url','')} | {identity.get('portfolio_url','')}"
   ).font.size = Pt(9)

   # Summary
   if resume_data.get("summary"):
       doc.add_heading("Summary", level=2)
       doc.add_paragraph(resume_data["summary"])

   # Experience
   if resume_data.get("experience"):
       doc.add_heading("Experience", level=2)
       for job in resume_data["experience"]:
           p = doc.add_paragraph()
           p.add_run(f"{job['title']} | {job['company']}").bold = True
           p.add_run(f"  {job.get('dates','')}")
           for bullet in job.get("bullets", []):
               bp = doc.add_paragraph(style="List Bullet")
               if isinstance(bullet, dict):
                   bp.add_run(bullet.get("text", str(bullet)))
               else:
                   bp.add_run(str(bullet))

   doc.save(output_path)

Wire generate_documents() into handle_apply() in telegram_bot.py.
Replace the stub with:
   import asyncio, anthropic
   client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
   profile = load_profile()
   resume_path, cl_path, tp_list = await generate_documents(job, profile, client)
   job.resume_path = resume_path
   job.cover_letter_path = cl_path
   job.talking_points = tp_list
   job.status = "applying"
   db.commit()
   # Send packet based on route
   if route == "manual_ready":
       await bot.send_document(chat_id=settings.TELEGRAM_CHAT_ID,
                               document=open(resume_path, "rb"),
                               caption=f"Resume for {job.title}")
       await bot.send_document(chat_id=settings.TELEGRAM_CHAT_ID,
                               document=open(cl_path, "rb"),
                               caption="Cover letter")
   else:
       await send_manual_assisted_packet(job, resume_path, cl_path, bot)

Test:
python3 -c "
import asyncio, anthropic
from core.database import get_db, Job
from core.profile import load_profile
from agents.writer import generate_documents
from core.config import settings

db = next(get_db())
job = db.query(Job).filter(Job.status=='approved').first()
profile = load_profile()
client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
resume, cl, pts = asyncio.run(generate_documents(job, profile, client))
print('Resume:', resume)
print('Cover letter:', cl)
print('Talking points:')
for p in pts: print(' ', p)
"
Show me the output, especially the talking points.
```

**While Claude Code works:**
- The test will make real Sonnet API calls — cost ~$3
- Watch `data/outputs/` in Windsurf — the `.docx` and `.txt` files should appear
- Open the `.docx` in Pages or Word immediately — check it's readable

**After — confirm these before moving on:**

```bash
# Check the outputs folder
ls data/outputs/

# Open the .docx — is it readable? 1 page? Formatted correctly?
# Read the cover letter .txt — does it mention the company?
# Read the talking points — do they reference JD language specifically?

# If talking points feel generic, ask Claude Code:
# "The talking points are too generic — add a constraint that forces
#  them to reference the company's specific product or domain"
```

---

### Prompt 5.2 — Promoter and full pipeline run

**Before running this prompt:**
- Writer must be working from Prompt 5.1
- Have both the bot and the pipeline tested individually

**Why this prompt is worded this way:**
The promoter closes the learning loop — companies that repeatedly surface strong matches get elevated to `priority_tracked` automatically. The `--run` flag wires everything into a single command. `--dry-run` lets you see what would happen without firing Telegram messages.

**The prompt:**
```
Read CLAUDE.md first.

Two things:

1. Build agents/promoter.py:

def run_promoter():
   db = next(get_db())
   companies = db.query(Company).all()
   promotions = {"tracked": [], "priority": []}

   for company in companies:
       obs_runs = db.execute(
           "SELECT COUNT(DISTINCT run_id) FROM observations WHERE company_id=?",
           (company.id,)
       ).scalar()
       jobs_75 = db.query(Job).filter(
           Job.company_id==company.id, Job.score>=75
       ).count()
       best = db.execute(
           "SELECT MAX(score) FROM jobs WHERE company_id=?",
           (company.id,)
       ).scalar() or 0
       company.best_role_score = best
       company.roles_above_75 = jobs_75

       prev_status = company.tracking_status

       if company.tracking_status == "candidate":
           if obs_runs >= 2 or jobs_75 >= 1:
               company.tracking_status = "tracked"
               promotions["tracked"].append(company.name)

       elif company.tracking_status == "tracked":
           if jobs_75 >= 2 or best >= 85:
               company.tracking_status = "priority_tracked"
               promotions["priority"].append(company.name)

       elif company.tracking_status == "ignored_auto":
           new_75 = db.query(Job).filter(
               Job.company_id==company.id,
               Job.score>=75,
               Job.first_seen_at >= company.ignored_at
           ).first()
           if new_75:
               company.tracking_status = "candidate"
               company.reactivated_at = datetime.utcnow()
               print(f"  Reactivated: {company.name}")

       from datetime import datetime, timedelta
       if company.tracking_status in ("candidate","tracked"):
           cutoff = datetime.utcnow() - timedelta(
               days=profile["search_config"].get("auto_ignore_days",60))
           if company.last_seen_at and company.last_seen_at < cutoff:
               no_65 = not db.query(Job).filter(
                   Job.company_id==company.id, Job.score>=65
               ).first()
               if no_65:
                   company.tracking_status = "ignored_auto"
                   company.ignored_at = datetime.utcnow()
                   print(f"  Auto-ignored: {company.name}")

       if company.tracking_status != prev_status:
           print(f"  Promoted: {company.name} {prev_status}→{company.tracking_status}")

   db.commit()
   return promotions

2. Update main.py with --run and --dry-run:

async def run_full_pipeline(dry_run: bool = False):
   from datetime import datetime
   start = datetime.utcnow()
   print(f"Pipeline starting {start.strftime('%H:%M:%S')} "
         f"{'(DRY RUN)' if dry_run else ''}")

   print("\n1. Polling...")
   from agents.poller import run_poll
   run_poll()

   print("\n2. Scoring...")
   from agents.scorer import run_hard_rules, run_haiku_scoring
   run_hard_rules()
   await run_haiku_scoring()

   print("\n3. Promoting companies...")
   from agents.promoter import run_promoter
   promotions = run_promoter()

   if not dry_run:
       print("\n4. Sending Telegram notifications...")
       from telegram import Bot
       bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
       db = next(get_db())

       # Approved jobs
       approved = db.query(Job).filter(
           Job.status=="approved",
           Job.telegram_message_id==None
       ).all()
       for job in approved:
           from core.telegram_bot import send_approval_message
           msg_id = await send_approval_message(job, bot)
           job.telegram_message_id = msg_id
       db.commit()
       print(f"  Sent {len(approved)} approval notifications")

       # Daily digest
       digest_jobs = db.query(Job).filter(Job.status=="digest").all()
       if digest_jobs or any(promotions.values()):
           from core.telegram_bot import send_daily_digest
           await send_daily_digest(digest_jobs, promotions, bot)
           print(f"  Sent digest: {len(digest_jobs)} jobs")
   else:
       db = next(get_db())
       approved_count = db.query(Job).filter(
           Job.status=="approved", Job.telegram_message_id==None).count()
       digest_count = db.query(Job).filter(Job.status=="digest").count()
       print(f"\n[DRY RUN] Would send:")
       print(f"  {approved_count} approval notifications")
       print(f"  {digest_count} digest jobs")
       if promotions["tracked"]:
           print(f"  New tracked: {', '.join(promotions['tracked'])}")
       if promotions["priority"]:
           print(f"  New priority: {', '.join(promotions['priority'])}")

   elapsed = (datetime.utcnow() - start).seconds
   print(f"\nPipeline complete in {elapsed}s")

if "--run" in sys.argv:
   import asyncio
   asyncio.run(run_full_pipeline(dry_run=False))
   sys.exit(0)
if "--dry-run" in sys.argv:
   import asyncio
   asyncio.run(run_full_pipeline(dry_run=True))
   sys.exit(0)

Run: python main.py --dry-run
Show me the full output.
Then run: python main.py --run
Check your phone. Describe what arrived.
```

**After — confirm these before moving on:**

```bash
# Dry run should show what would be sent without sending
python main.py --dry-run

# Real run — check phone for notifications
python main.py --run

# Tap APPLY on one notification
# Within 60 seconds, resume and cover letter should arrive on phone
# Reply "done" — bot should reply "Logged as applied"
# Run /status — applied count should be 1
```

---

### Prompt 5.3 — Health check, run.sh, and final validation

**Before running this prompt:**
- Full pipeline must be working from Prompt 5.2
- APPLY → documents → "done" → logged must all work end to end
- This is the final prompt — after it, you are operational

**Why this prompt is worded this way:**
The health check is what you run when something feels off — it checks every component in one command. `run.sh` is the evening command you'll run every day. The calibration test validates that Claude's scoring matches your judgement before you trust it with real applications.

**The prompt:**
```
Read CLAUDE.md first.

Final validation setup. Three things:

1. Add --health to main.py:

async def run_health_check():
   from telegram import Bot
   import anthropic
   checks = []

   # Config
   try:
       _ = settings.ANTHROPIC_API_KEY
       _ = settings.TELEGRAM_BOT_TOKEN
       checks.append(("Config loaded", True, ""))
   except Exception as e:
       checks.append(("Config loaded", False, str(e)))

   # Profile
   try:
       from core.profile import load_profile, profile_to_scoring_context
       p = load_profile()
       ctx = profile_to_scoring_context(p)
       checks.append(("Candidate profile", True, p["identity"]["name"]))
   except Exception as e:
       checks.append(("Candidate profile", False, str(e)))

   # Database
   try:
       db = next(get_db())
       from core.database import Company, Job, Observation
       c = db.query(Company).count()
       j = db.query(Job).count()
       checks.append(("Database", True, f"{c} companies, {j} jobs"))
   except Exception as e:
       checks.append(("Database", False, str(e)))

   # Telegram
   try:
       bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
       me = await bot.get_me()
       checks.append(("Telegram bot", True, f"@{me.username}"))
   except Exception as e:
       checks.append(("Telegram bot", False, str(e)))

   # Anthropic API
   try:
       client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
       r = await client.messages.create(
           model="claude-haiku-4-5-20251001", max_tokens=10,
           messages=[{"role": "user", "content": "ping"}]
       )
       checks.append(("Anthropic API", True, "Haiku responding"))
   except Exception as e:
       checks.append(("Anthropic API", False, str(e)))

   # DB stats
   db = next(get_db())
   tracked = db.query(Company).filter(Company.tracking_status=="tracked").count()
   priority = db.query(Company).filter(Company.tracking_status=="priority_tracked").count()
   applied = db.query(Job).filter(Job.status=="applied").count()

   print("\n🏥 Health check\n")
   for name, ok, detail in checks:
       icon = "✅" if ok else "❌"
       print(f"{icon} {name}: {detail}")
   print(f"\n📊 Registry: {tracked} tracked · {priority} priority")
   print(f"📊 Applied total: {applied}")

if "--health" in sys.argv:
   import asyncio
   asyncio.run(run_health_check())
   sys.exit(0)

2. Create run.sh in the project root:
#!/bin/bash
set -e
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting pipeline: $(date)"
python main.py --run
echo "Done: $(date)"

Make it executable: chmod +x run.sh

3. Complete tests/test_scorer.py with the full calibration test:
(Use the version from Prompt 3.3 — it should already exist)
Make sure it skips gracefully if validation_30.csv is missing.

Also add tests/test_deduper.py with basic unit tests:
- Test that source_dedupe returns existing job_id for same URL
- Test that source_dedupe returns None for new URL
- Test that hash dedup works for same title+company+location

Run: python main.py --health
Show me the health check output.
Then run: python -m pytest tests/ -v
Show me the test results.
Then run: ./run.sh
Show me it runs without errors.
```

**After — confirm these before moving on:**

```bash
# All health checks should be green
python main.py --health

# All tests should pass (calibration skips if no CSV — that's fine)
python -m pytest tests/ -v

# run.sh should execute cleanly
./run.sh

# Final commit
git add -A
git commit -m "feat: phase 5 complete — writer, full pipeline, health check"
```

### After Phase 5 — you are operational

**Phase 5 exit checklist:**
- [ ] `python main.py --health` shows all green
- [ ] `python -m pytest tests/ -v` passes
- [ ] `./run.sh` runs without errors
- [ ] APPLY tap → resume and cover letter arrive on phone
- [ ] Reply "done" → logged as applied
- [ ] All phases committed to git

**Update CLAUDE.md:** Change current phase to "Operational — running ./run.sh daily"

---

## Daily operating procedure

Once Phase 5 is complete, your daily workflow is:

**Evening (5-10 minutes active, 5 minutes passive):**
```bash
# Keep this running in background (separate terminal)
python main.py --bot

# Run the pipeline once each evening
./run.sh
```

Check your phone. For each notification:
- Review score, reason, matches, flags, talking points
- Tap APPLY if it looks right
- Receive resume and cover letter
- Navigate to the application URL
- Upload resume, paste cover letter, fill remaining fields, submit
- Reply "done" to the Telegram message

**Weekly (10 minutes):**
```bash
# Check calibration — if average delta > 10, tune the scoring prompt
python -m pytest tests/test_scorer.py -v

# Check health
python main.py --health

# Review which companies promoted to priority_tracked this week
# via /status
```

**When you spot a new company:**
```
/add_company CompanyName
```
That's it. The enricher handles the rest.

---

## Quick reference — all commands

| Command | What it does |
|---------|-------------|
| `python main.py` | Show available flags |
| `python main.py --health` | Full health check |
| `python main.py --load-seeds` | Load 75-company seed list |
| `python main.py --poll` | Fetch new jobs |
| `python main.py --score` | Hard rules + Haiku scoring |
| `python main.py --dry-run` | Full pipeline, no Telegram |
| `python main.py --run` | Full pipeline with Telegram |
| `python main.py --bot` | Start Telegram bot |
| `python main.py --test-telegram` | Send test ping to phone |
| `./run.sh` | Evening pipeline command |
| `python -m pytest tests/ -v` | Run all tests |
| `python setup_profile.py` | CLI profile setup fallback |

| Telegram command | What it does |
|-----------------|-------------|
| `/setup` | Onboard or edit profile sections |
| `/status` | Today's pipeline summary |
| `/add_company Name` | Add a company to registry |
| `/fix_ats id type` | Correct ATS detection |
| `/request_docs id` | Generate docs for digest job |
| `/applied id` | Manual confirmation fallback |
| `/cancel` | Cancel any in-progress conversation |
| Reply "done" | Confirm you submitted an application |
