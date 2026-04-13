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
