# plan.md — Job Application Agent
### Build plan · April 2026 · Revanth Gollapudi

---

## Phase overview

| Phase | What it delivers | Status |
|-------|-----------------|--------|
| Phase 1 — Foundation | Skeleton, security, database, config, profile system | ⬜ Not started |
| Phase 2 — Company registry | Enricher, seed loader, /add_company, 75 companies tracked | ⬜ Not started |
| Phase 3 — Poller + scorer | Daily ATS polling, hard rules, Haiku scoring | ⬜ Not started |
| Phase 4 — Telegram bot | Approval gate, /setup onboarding, all commands | ⬜ Not started |
| Phase 5 — Writer + pipeline | Sonnet docs, full pipeline run, calibration | ⬜ Not started |
| Phase 6 — Form filling | Playwright for Greenhouse/Lever/Ashby (auto_apply) | ⬜ Future |

Update status as you go: ⬜ Not started · 🔄 In progress · ✅ Done · ❌ Blocked

---

## Phase 1 — Foundation
**Goal:** Secure, working project skeleton with database and profile system.
**Definition of done:** `python main.py` prints database ready. `git status` shows no sensitive files. Profile loads and renders correctly.

| Prompt | What it builds | Done? |
|--------|---------------|-------|
| 1.1 | Project skeleton, .gitignore, CLAUDE.md, folder structure | ⬜ |
| 1.2 | Real .env and CLAUDE.md with actual keys and context | ⬜ |
| 1.3 | Database schema (Observation, Company, Job), config loader, main.py | ⬜ |

**Phase 1 validation checklist:**
- [ ] `python main.py` prints "Database ready" without errors
- [ ] `git status` shows no .env, no CLAUDE.md, no candidate_profile.json
- [ ] `data/jobs.db` exists and has three tables
- [ ] `python setup_profile.py` runs and saves candidate_profile.json
- [ ] Scoring context renders correctly with real data

---

## Phase 2 — Company registry
**Goal:** 75 companies enriched with ATS detection, daily poll queue populated.
**Definition of done:** `python main.py --load-seeds` runs cleanly. 75 companies in DB with at least 50 having detected ATS type.

| Prompt | What it builds | Done? |
|--------|---------------|-------|
| 2.1 | Profile loader, setup_profile.py CLI, profile_to_scoring_context() | ⬜ |
| 2.2 | Enricher: careers page finder, ATS detector, fallback to unknown | ⬜ |
| 2.3 | Seed list loader (75 companies), validation report, /add_company skeleton | ⬜ |

**Phase 2 validation checklist:**
- [ ] `python main.py --load-seeds` shows 75 companies processed
- [ ] At least 50 companies have ats_type != unknown
- [ ] enrich_company("Stripe") returns greenhouse correctly
- [ ] Unknown companies listed clearly for manual /fix_ats
- [ ] /add_company command works in Telegram

---

## Phase 3 — Poller and scorer
**Goal:** Real jobs flowing in, scored, routed to approved/digest/dropped.
**Definition of done:** `python main.py --poll && python main.py --score` ingests real jobs and produces a score breakdown that feels calibrated.

| Prompt | What it builds | Done? |
|--------|---------------|-------|
| 3.1 | ATS poller (Greenhouse/Lever/Ashby JSON APIs), supplemental boards, deduplication | ⬜ |
| 3.2 | Hard rules filter (8 rules, -10 penalty for thin stack match) | ⬜ |
| 3.3 | Haiku scorer, score routing, calibration test scaffold | ⬜ |

**Phase 3 validation checklist:**
- [ ] `python main.py --poll` ingests at least 20 real jobs from tracked companies
- [ ] Job records show correct age_days, country, title
- [ ] Hard rules filter catches expected categories (too_old, wrong_country, etc.)
- [ ] Haiku scorer returns valid JSON for every job
- [ ] Score distribution feels realistic (not 90% approved or 90% dropped)
- [ ] Calibration test skips gracefully if validation_30.csv not yet created

---

## Phase 4 — Telegram bot
**Goal:** Phone receives real job notifications. APPLY/SKIP/EDIT works. /setup onboarding works end to end.
**Definition of done:** Tap APPLY on a real job notification. Bot acknowledges. /status shows correct counts.

| Prompt | What it builds | Done? |
|--------|---------------|-------|
| 4.1 | Telegram sending functions (approval message, digest, priority alert, manual packet) | ⬜ |
| 4.2 | Command handlers (APPLY/SKIP/EDIT callbacks, reply parser, /add_company, /fix_ats, /status) | ⬜ |
| 4.3 | /setup ConversationHandler (full onboarding + section edit mode) | ⬜ |

**Phase 4 validation checklist:**
- [ ] `python main.py --test-telegram` message arrives on phone within 10 seconds
- [ ] Tap APPLY on a notification → bot acknowledges
- [ ] Reply "done" → bot says "Logged as applied"
- [ ] /status shows correct numbers
- [ ] /setup runs full onboarding, saves profile correctly
- [ ] /setup second run shows section menu (edit mode)
- [ ] /add_company Stripe → bot finds Greenhouse, confirms

---

## Phase 5 — Writer and full pipeline
**Goal:** Tap APPLY → receive tailored resume + cover letter on phone. Full pipeline runs end to end with one command.
**Definition of done:** ./run.sh runs without errors. APPLY tap delivers .docx resume and cover letter. Calibration test passes.

| Prompt | What it builds | Done? |
|--------|---------------|-------|
| 5.1 | Sonnet writer (resume rewrite + cover letter + talking points, parallel calls) | ⬜ |
| 5.2 | Promoter agent, --run pipeline, --dry-run mode | ⬜ |
| 5.3 | Calibration test, health check, run.sh, final validation | ⬜ |

**Phase 5 validation checklist:**
- [ ] `python main.py --dry-run` shows what would be sent without sending
- [ ] `python main.py --run` sends real Telegram notifications
- [ ] APPLY tap → resume .docx arrives on phone within 60 seconds
- [ ] Resume is formatted correctly (1 page, Arial, not garbled)
- [ ] Cover letter references company name specifically
- [ ] Talking points reference JD language (not generic)
- [ ] `python main.py --health` shows all green
- [ ] `python -m pytest tests/ -v` passes all tests
- [ ] `./run.sh` runs cleanly

---

## Phase 6 — Form filling (future, Week 7+)
**Goal:** Tap APPLY on a Greenhouse/Lever/Ashby role → form fills and submits automatically.
**Prerequisite:** Phase 1–5 proven stable. Pipeline running for at least 2 weeks with no data quality issues.

| What to build | Notes |
|--------------|-------|
| Playwright integration | Greenhouse first — most common |
| Greenhouse form filler | Name, email, phone, LinkedIn, resume upload, cover letter upload, work auth |
| Lever form filler | Different selectors, same flow |
| Ashby form filler | Fastest-growing, similar to Greenhouse |
| route change | manual_ready → auto_apply after Playwright proven |

---

## Week-by-week schedule

### Week 1 (April 12–18)
**Evening 1 (Mon):** Phase 1 Prompt 1.1 — skeleton and security
**Evening 2 (Tue):** Phase 1 Prompt 1.2 — .env and CLAUDE.md
**Evening 3 (Wed):** Phase 1 Prompt 1.3 — database and config
**Evening 4 (Thu):** Phase 2 Prompt 2.1 — profile loader and setup_profile.py
**Evening 5 (Fri):** Buffer — fix anything from the week, run Phase 1 validation checklist
**Weekend:** Manual calibration exercise — score 30 jobs by hand, save validation_30.csv

### Week 2 (April 19–25)
**Evening 1:** Phase 2 Prompt 2.2 — enricher
**Evening 2:** Phase 2 Prompt 2.3 — seed loader, 75 companies
**Evening 3:** Phase 3 Prompt 3.1 — ATS poller
**Evening 4:** Phase 3 Prompt 3.2 — hard rules
**Evening 5:** Phase 3 Prompt 3.3 — Haiku scorer
**Weekend:** Run Phase 3 validation checklist, review score distribution

### Week 3 (April 26 – May 2)
**Evening 1:** Phase 4 Prompt 4.1 — Telegram sending functions
**Evening 2:** Phase 4 Prompt 4.2 — command handlers
**Evening 3:** Phase 4 Prompt 4.3 — /setup ConversationHandler (full evening)
**Evening 4:** Phase 4 validation — run full bot test on phone
**Evening 5:** Buffer / fix issues
**Weekend:** Run Phase 4 checklist. Start seeing real notifications.

### Week 4 (May 3–9)
**Evening 1:** Phase 5 Prompt 5.1 — Sonnet writer
**Evening 2:** Phase 5 Prompt 5.2 — promoter and --run pipeline
**Evening 3:** Phase 5 Prompt 5.3 — health check, run.sh, calibration
**Evening 4:** Phase 5 validation — end-to-end test, APPLY tap test
**Evening 5:** Buffer — tune scoring prompt if calibration test fails
**Weekend:** Full pipeline live. Start applying. Ramp from 3–5/day.

### Week 5 (May 10–16)
**Focus:** Running the system, not building it
**Daily:** Run ./run.sh each evening
**Applications:** 8–10/day
**Countries:** Add Singapore and Netherlands to target_countries
**Tune:** If score distribution feels off, adjust scoring prompt
**Add companies:** /add_company any promising companies you spot

### Week 6+ (May 17+)
**Volume:** 12–15 applications/day max
**Countries:** Add Germany, Sweden
**Switzerland:** Begin Jan–Feb 2027 (quota timing)
**Phase 6:** Begin planning Playwright form filling if pipeline is stable
**Ryder project completes mid-June:** Update resume metrics immediately

---

## Application volume targets

| Period | Apps/day | Countries active |
|--------|----------|-----------------|
| Week 1–2 (build) | 0 — building only | — |
| Week 3 (partial) | 3–5 manual | USA |
| Week 4 | 5–8 | USA |
| Week 5 | 8–10 | USA, SG, NL |
| Week 6+ | 12–15 max | USA, SG, NL, DE, SE |
| Jan–Feb 2027 | +1–2/day | Add CH |

---

## Cost tracking

| Phase | Est. cost | Actual |
|-------|-----------|--------|
| Build (weeks 1–3) | ~$3–8 | |
| Ramp (weeks 4–5) | ~$15–25 | |
| Full pace (week 6+) | ~$15–20/month | |

Haiku: ~$0.25/1,000 jobs scored
Sonnet: ~$3 per resume+CL pair (fires only post-APPLY)
ATS polling: $0 (public APIs)
Supplemental boards: $0

---

## Known risks and mitigations

| Risk | Mitigation |
|------|-----------|
| Calibration off > 10 points | Tune scoring prompt before going live — hard gate |
| ATS detection wrong for many companies | Fix with /fix_ats after seed load, before first poll |
| Telegram bot crashes during operation | Add global exception handler that logs and continues |
| Ryder project delays beyond mid-June | Don't wait — apply now, update resume metrics when delivered |
| Swiss quota exhausted before applying | CH targeting starts Jan 2027 — not urgent |
