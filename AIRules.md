# AIRules.md — Job Application Agent

Two sections. Section 1 is rules for Claude Code when building this project.
Section 2 is rules for the agent itself at runtime.

---

# Section 1 — Rules for Claude Code

These are standing instructions that apply to every prompt in this project.
Claude Code should follow these without being reminded each time.

---

## Identity and context

**Always read CLAUDE.md first.** Before writing any code, read the project context file. Every session starts fresh — CLAUDE.md is the briefing. Without it you will make wrong assumptions about architecture, naming, and data model.

**Trust the architecture.** The design decisions are finalised. Do not suggest alternative architectures, different databases, or different frameworks unless explicitly asked. The choices — SQLite, python-telegram-bot v20, pydantic-settings, Haiku for scoring, Sonnet for documents — are deliberate. Work within them.

**Update CLAUDE.md's current phase section** at the end of each prompt session. Update "Last completed prompt", "What's working", and "What's next". This keeps future sessions calibrated.

---

## Code quality rules

**Type hints on every function.** Every function signature must have type hints on all parameters and the return type. No `def foo(x, y)` — always `def foo(x: str, y: int) -> dict`.

**Docstrings on every function.** One-line minimum. For complex functions, include what it does, what it returns, and what exceptions it raises.

**No bare `except`.** Never write `except:` or `except Exception:` without logging the error. Always: `except Exception as e: logger.error(f"Context: {e}")`. Catch specific exceptions when possible.

**No hardcoded candidate data.** Never write a name, employer, metric, skill, or country directly in code or in a prompt file. All candidate data comes from `candidate_profile.json` via `core/profile.py`. If you catch yourself writing "Revanth" or "CGI" or "85K req/day" in a code file — stop.

**No hardcoded file paths.** Always use `config.PROFILE_PATH`, `config.RESUME_PATH`, and `Path()` objects. Never write `"data/candidate_profile.json"` as a string literal in code (only in config defaults).

**Print progress for long operations.** Any function that processes more than 10 items should print progress — `"Processing company 3/75: Stripe..."`. Silence during long runs causes confusion.

---

## Security rules

**Check .gitignore before creating any file containing personal data.** If a file will contain API keys, personal information, or candidate data, verify it's in `.gitignore` before creating it. If it's not, add it first.

**Never log API keys.** When printing config confirmations, show only the first 8 characters: `f"API key loaded: {key[:8]}..."`. Never print the full key.

**Never commit .env or CLAUDE.md.** If asked to run `git add .` or `git commit -a`, check the staged files first. If .env or CLAUDE.md appear, stop and explain why they cannot be committed.

**Prompt files are public — zero personal data.** The files in `prompts/` may eventually be committed to git. They must contain only `{template_variables}` — never real names, metrics, or employer names.

---

## Testing rules

**Write the test before saying it's done.** After building any significant function, write a test or a quick validation command and run it. Do not declare a prompt complete without running the code.

**Show the output.** After running any test or validation command, show the actual output in full. Do not summarise it — paste it. The developer needs to see the real output to trust it.

**If a test fails, fix it before moving on.** Do not suggest moving to the next step while a test is failing. Fix the failure first, re-run the test, confirm it passes.

---

## API cost rules

**Haiku for scoring. Sonnet for documents. No exceptions.**
- Scoring prompt → `claude-haiku-4-5-20251001`
- Talking points (pre-approval) → `claude-haiku-4-5-20251001`
- Resume rewrite → `claude-sonnet-4-6`
- Cover letter → `claude-sonnet-4-6`

Never use Sonnet for scoring — even for testing. Use Haiku.
Never use Opus for anything in this project.

**Batch Haiku calls.** When scoring multiple jobs, process in batches of 5 with a 1-second delay between batches. Never fire 50 concurrent API calls.

**Truncate descriptions to 3,000 characters** before sending to any model. Most job descriptions have boilerplate that adds tokens without adding signal.

---

## Telegram rules

**Never send a real Telegram message during development testing** unless the developer explicitly asks for it. Use `--dry-run` mode or `--test-telegram` flag for testing. Do not add test code that fires real messages.

**Never auto-submit an application.** The agent routes jobs to `manual_ready` or `manual_assisted` — both require the developer to manually submit. No code should ever fill a form and click submit without an explicit APPLY tap from Telegram.

---

## Error handling rules

**Enricher must never raise.** The `enrich_company()` function must catch all exceptions and return a Company with `ats_type="unknown"` on any failure. One bad company must never stop the seed loader.

**Poller must never raise.** If one company's ATS API returns an error, log it and continue to the next company. Never let one failure abort the full poll cycle.

**Scorer must never raise.** If Haiku returns invalid JSON, retry once. If it fails twice, log the raw response and mark the job with `status="scored"` and `score=None`. Do not raise.

**Bot must never crash.** The Telegram bot must have a global exception handler that logs errors and keeps the event loop running. A single malformed message must never kill the bot process.

---

## Git rules

**Commit after each working prompt.** After a prompt is validated and working, commit with a meaningful message: `feat: add ATS enricher with Greenhouse/Lever/Ashby detection`. Never let changes accumulate across multiple prompts without committing.

**Commit message format:** `type: description`
Types: `feat` (new feature), `fix` (bug fix), `refactor` (restructure without feature change), `test` (test additions), `chore` (dependencies, config)

**Never commit on a failing test.** Run the validation commands, verify they pass, then commit.

---

# Section 2 — Rules for the agent at runtime

These rules govern how the agent behaves when running. They are the operational constraints of the system.

---

## The human is always the final gate

**Nothing submits without a Telegram APPLY tap.** The agent may scrape, score, generate documents, and prepare packets — but it may not submit an application to any company under any circumstances without an explicit APPLY tap from the developer via Telegram.

This rule has no exceptions. Not for high-scoring jobs. Not for priority_tracked companies. Not when the pipeline is fully automated. The tap is the gate.

---

## Scoring constraints

**Never fabricate metrics.** When generating resume rewrites or cover letters, never invent numbers, percentages, or scale claims that are not present in `base_resume.json`. If a metric is uncertain, omit it rather than estimate.

**Never claim skills not in the profile.** If a job requires a skill that does not appear in `candidate_profile.json`, the resume rewrite must not claim it. The agent may note it as a gap in the red_flags field, but never invent the skill.

**Score conservatively when uncertain.** If the job description is vague or the fit is unclear, score lower rather than higher. A false positive (high score for a weak fit) wastes the developer's time. A false negative (low score for a good fit) is recoverable via the digest.

---

## Company registry rules

**Never mark a company as priority_tracked without earning it.** Promotion to priority_tracked requires 2+ jobs scoring 75+ OR 1 job scoring 85+. Do not manually set a company to priority_tracked except via /fix_ats.

**Auto-ignore is reversible.** A company at `ignored_auto` reactivates automatically when a new job scores 75+. The promoter must check ignored companies on every run.

**Never poll a company with ats_type=unknown.** Unknown ATS companies are in the registry but must not be polled — the poller has nowhere to send the request. Poll only companies with ats_type in (greenhouse, lever, ashby).

---

## Document generation rules

**Talking points must be role-specific.** Before accepting talking points output, verify they reference at least 3 specific terms from the job description. Generic points ("I have experience with AI systems") are not acceptable and should trigger a regeneration with tighter constraints.

**Cover letter must name the company.** Every cover letter must reference the specific company name at least once. A generic cover letter that could apply to any company is a failure condition.

**Resume stays at 1 page.** The docx renderer must enforce 1-page output. If the rewritten resume JSON produces more content than fits, cut lower-priority bullets until it fits. Never produce a 2-page resume.

---

## Duplicate and history rules

**90-day applied block is hard.** If a job's company has an `applied` status record within the last 90 days, hard block silently. Do not surface it to the developer. The developer already decided on that company.

**Skipped is a soft signal, not a block.** A previously skipped company's new role should surface with a "previously seen" flag, but the developer gets to decide again. One skip does not mean permanent rejection.

**Repost detection is a skip, not a block.** A job that appears to be a repost (same title+company+location seen in last 60 days) is skipped to avoid duplicating effort. If the developer specifically wants to apply to a repost, they can do so manually.

---

## Failure modes — what the agent must do when things break

| Failure | Agent behaviour |
|---------|----------------|
| ATS API returns 404 | Log, skip this company, continue polling others |
| Haiku returns invalid JSON | Retry once, log raw response, mark job score=None |
| Sonnet times out | Retry once after 5 seconds, notify via Telegram if second attempt fails |
| Telegram message fails to send | Log, retry once, skip if second attempt fails (do not crash) |
| candidate_profile.json missing | Halt and print clear error: "Run /setup in Telegram or python setup_profile.py" |
| .env missing | Halt immediately with list of missing required keys |
| Database locked | Wait 2 seconds, retry once, raise if still locked |

**When in doubt, fail loudly and continue.** Log the error, notify if possible, and keep the pipeline running for the remaining items. A single failure must never abort the full run.
