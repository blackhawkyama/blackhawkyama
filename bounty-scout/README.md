# BountyScout 🐺

**Autonomous bug bounty program discovery and scoring.**

Monitors HackerOne, Bugcrowd, and Immunefi. Scores programs by ROI, skill match, and saturation. Sends you a daily digest of high-value targets matched to your skills — zero hands-on required.

```
┌──────────────────────────────┐
│  Fetch Programs (All Platforms)  │
└────────────┬─────────────────┘
             │
┌────────────▼──────────────┐
│  Score Each Program       │
│  • Bounty × Skill Match   │
│  • / Saturation Factor    │
└────────────┬──────────────┘
             │
┌────────────▼──────────────────┐
│  Rank & Filter (Top N)        │
│  • Min skill match: 50%       │
│  • Max saturation: 80%        │
└────────────┬──────────────────┘
             │
┌────────────▼──────────────────┐
│  Generate Digest (Daily)      │
│  • Markdown or JSON           │
│  • Send via Email (SES)       │
│  • Store in S3 (optional)     │
└──────────────────────────────┘
```

---

## Features

- **Multi-platform scraping** — HackerOne, Bugcrowd, Immunefi APIs + public fallback
- **Intelligent scoring** — Bounty × skill match / saturation
- **Skill-based filtering** — Matches programs to your expertise (OWASP, API testing, XXE, etc.)
- **Saturation detection** — Favors new/underexplored programs
- **AWS Lambda ready** — Runs daily on schedule, fully serverless
- **Email digests** — Daily/weekly summaries with rank, bounty, skill match
- **S3 history** — Optional digest archival for trending
- **Zero hands-on** — After setup, you only review email recommendations

---

## Installation

### Local (for testing)

```bash
pip install -e bounty-scout/
```

### AWS Lambda (production)

See **[AWS_SETUP.md](AWS_SETUP.md)** for full 30-minute setup guide.

---

## Quick Start (Local)

```python
from bounty_scout import BountyScout

# Create scanner
scout = BountyScout()

# Run full scan
output = scout.run_full_scan(
    period="daily",
    top_n=5,
    output_format="markdown"  # or 'json'
)

print(output)
```

Or with custom skills:

```python
skills = {
    "web_app": 0.95,
    "api_testing": 0.90,
    "xxe": 0.7,
    "deserialization": 0.4,
}

scout = BountyScout(user_skills=skills)
output = scout.run_full_scan()
```

### Testing Locally (with env vars)

```bash
# Create .env
echo "NOTIFY_EMAIL=your-email@gmail.com" > .env
echo "DIGEST_FORMAT=markdown" >> .env

# Run
python -c "from bounty_scout.lambda_handler import local_handler; local_handler()"
```

---

## Architecture

### `schemas.py`
Pydantic models:
- `BountyProgram` — Program metadata (name, platform, bounty, scope)
- `ProgramScore` — Scored program with ranking
- `DailyDigest` — Formatted output for email/storage

### `scraper.py`
Fetches programs from platforms:
- HackerOne GraphQL API (requires key)
- Bugcrowd REST API
- Immunefi public API
- Falls back to public scraping if API keys unavailable

### `scoring.py`
Ranks programs by:
- **Bounty amount** — Base ROI (higher bounty = higher score)
- **Skill match** — 0-1 based on your expertise vs. program's vuln types
- **Saturation** — 0-1 (newer programs scored higher)
- **Formula:** `(bounty × skill_match) / (1 + saturation)`

### `report.py`
Generates output:
- Markdown digest (human-readable, email-friendly)
- JSON digest (programmatic, for webhooks/storage)

### `lambda_handler.py`
AWS Lambda entry point:
- Loads env variables
- Runs scan
- Stores in S3 (optional)
- Sends email via SES
- Logs to CloudWatch

---

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `NOTIFY_EMAIL` | _(required)_ | Email to receive digests |
| `SES_FROM_EMAIL` | noreply@blackhawkyama.dev | Verified SES email |
| `HACKERONE_API_KEY` | _(none)_ | HackerOne API key (optional) |
| `BUGCROWD_API_KEY` | _(none)_ | Bugcrowd API key (optional) |
| `S3_BUCKET` | _(none)_ | S3 bucket for digest history |
| `DIGEST_FORMAT` | markdown | Output format: 'markdown' or 'json' |
| `TOP_N` | 5 | Number of programs per digest |
| `MIN_SKILL_MATCH` | 0.5 | Min skill match (0-1) to include |
| `MAX_SATURATION` | 0.8 | Max saturation (0-1) to include |

### Customize Skill Scores

Edit `scoring.py` `DEFAULT_SKILLS` dict:

```python
DEFAULT_SKILLS = {
    "web_app": 0.9,           # You're strong here
    "api_testing": 0.85,
    "xxe": 0.7,               # Learning
    "deserialization": 0.3,   # New
}
```

Each program's vulnerability types are compared to your skills, weighted by match.

---

## Output Examples

### Markdown Digest

```markdown
# 🐺 BountyScout Digest

**Generated:** 2024-07-18 08:00 UTC
**Period:** Daily
**Programs Scanned:** 412
**New This Period:** 3

---

## Top Targets for You

### 1. TechCorp Bug Bounty
**Platform:** HackerOne
**Score:** 1250 | Skill Match: 92% | Saturation: 35%
**Bounty:** $5,000
**Link:** [Open Program](https://hackerone.com/...)
**Recommendation:** Strong skill match · low saturation · $5,000 avg payout
```

### JSON Digest

```json
{
  "generated_at": "2024-07-18T08:00:00",
  "period": "daily",
  "total_programs_scanned": 412,
  "new_programs": 3,
  "top_programs": [
    {
      "rank": 1,
      "name": "TechCorp Bug Bounty",
      "platform": "hackerone",
      "score": 1250,
      "skill_match": 92,
      "saturation": 35,
      "avg_bounty": 5000
    }
  ]
}
```

---

## Workflow

1. **Setup** (30 min) — AWS Lambda + SES + EventBridge (see [AWS_SETUP.md](AWS_SETUP.md))
2. **Daily run** (automatic) — Lambda triggers at 8 AM UTC
3. **Review** (5 min) — Read email digest, click top program
4. **Test** (hours) — Execute your testing methodology
5. **Report** — Submit findings to platform, collect bounty

---

## Scoring Deep Dive

### Skill Match Calculation

```
skill_match = mean(scores for each vuln_type in program.vulnerability_types)
```

Example: Program accepts XSS + XXE
- Your XSS score: 0.85
- Your XXE score: 0.70
- **Skill match: 0.775** (77.5%)

### Saturation Estimation

- **New program** (<30 days): 20% saturated
- **Established** (<365 days): 60% saturated
- **Mature** (>1 year): 80% saturated
- **Adjustments:** Platform (H1 is 5% more saturated), hunter count

### Final Score

```
raw_score = (bounty × skill_match) / (1 + saturation)
weighted_score = apply_boosts_and_penalties(raw_score)
```

Boosts: New programs (+50%), skill match > 80% (+25%)  
Penalties: Saturated programs (-50%), low skill match (-20%)

---

## Updating Skills

As you learn new attack classes, update your skill scores:

```python
from bounty_scout.scoring import ProgramScorer

scorer = ProgramScorer(user_skills={
    "xxe": 0.8,  # You completed XXE labs
    "deserialization": 0.6,  # You're learning
})
```

Then redeploy Lambda (1 minute).

---

## Troubleshooting

### Programs look low-quality
- Increase `MIN_SKILL_MATCH` to 0.7+
- Decrease `TOP_N` to focus on top 3
- Add API keys (public scraping is limited)

### Not getting new programs
- Platforms update hourly; check again later
- Verify API keys are valid
- Check CloudWatch logs for scraper errors

### Email not arriving
- Check spam folder
- Verify SES email is verified in AWS
- Ensure `NOTIFY_EMAIL` is set

### Lambda timeout (>60s)
- Reduce platform count (edit scraper to skip Immunefi)
- Disable S3 storage
- Increase Lambda timeout to 120s

---

## Future Enhancements

- [ ] Slack webhook support
- [ ] GitHub Issues integration (auto-create issues from top programs)
- [ ] Skill-learning assistant (detect gaps, recommend labs)
- [ ] Program history tracking (detect re-opens, bounty increases)
- [ ] WAF/bot-detection scoring (favor targets you can actually test)
- [ ] Coordinated disclosure tracking (don't repeat tested targets)

---

## Contributing

To add platform support:
1. Add to `scrapers.py` (new `scrape_platform()` method)
2. Update `BountyPlatformScraper.fetch_all_platforms()`
3. Test locally
4. Push and redeploy

---

## License

MIT

---

**Ready to deploy?** See **[AWS_SETUP.md](AWS_SETUP.md)** for step-by-step guide.

Questions? Open an issue.
