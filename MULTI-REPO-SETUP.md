# Multi-Repo Loop Engineering Deployment

Deploy loop engineering across your security/testing repos with optimized patterns for each.

---

## Deployment Plan

### Tier 1: Aggressive (Full Stack) — RCE Bug Hunting

**recce** — Reconnaissance agent for authorized targets

```
Patterns enabled: 1, 2, 3, 4, 5 (ALL)
Schedule: Hourly testing, 6h quality, weekly deps, hourly progress, 3d docs
Budget: 192 tokens/week
Use case: Continuous fuzzing, exploit chain testing, vulnerability tracking
```

**Deploy:**
```bash
# Copy files from blackhawkyama and customize for recce
cp CLAUDE.md ../recce/CLAUDE.md
# Edit CLAUDE.md: enable all 5 patterns
# Edit .loop-config.json: set all to enabled: true
# Commit: "Enable full loop engineering for RCE hunting"
```

---

### Tier 2: Balanced (3 Patterns) — LLM Testing

**assay** — LLM evaluation framework

```
Patterns enabled: 1 (Testing), 3 (Dependencies), 4 (Progress)
Schedule: Hourly testing, weekly deps, hourly progress
Budget: 32 tokens/week
Use case: Evaluate model changes, track eval scores, dependency updates
```

**gauntlet** — Prompt injection eval suite

```
Patterns enabled: 1 (Testing), 2 (Quality), 3 (Dependencies)
Schedule: Hourly testing, 6h quality, weekly deps
Budget: 36 tokens/week
Use case: Run prompt attacks, verify defenses hold, track injection success rates
```

---

### Tier 3: Lean (2 Patterns) — Documentation + Monitoring

**immunefi-solidity-track** — Solidity learning

```
Patterns enabled: 4 (Progress), 5 (Docs)
Schedule: Weekly progress, weekly docs
Budget: 8 tokens/month
Use case: Track learning progress, keep code examples current
```

**blackhawkyama.github.io** — Personal blog site

```
Patterns enabled: 5 (Docs) only
Schedule: Weekly docs check
Budget: 4 tokens/month
Use case: Verify blog links work, examples stay fresh
```

---

## Step-by-Step Deployment

### Step 1: Prepare Template Files

From `blackhawkyama` repo, you have:
- ✅ CLAUDE.md (template with all patterns)
- ✅ .loop-config.json (template configuration)
- ✅ .loop-memory.md (template progress tracker)
- ✅ SESSION-NOTES.md (context reference)
- ✅ ACTIVATION-CHECKLIST.md (activation guide)

### Step 2: Deploy to Each Repo

#### recce (Full Stack)

```bash
cd ../recce
git checkout -b claude/loop-engineering-full

# Copy template files
cp ../blackhawkyama/CLAUDE.md .
cp ../blackhawkyama/.loop-config.json .
cp ../blackhawkyama/.loop-memory.md .

# Edit CLAUDE.md: uncomment all 5 patterns (1-5)
# Edit .loop-config.json: 
#   - testing: enabled=true
#   - quality: enabled=true
#   - dependencies: enabled=true
#   - progress: enabled=true
#   - documentation: enabled=true

# Commit
git add CLAUDE.md .loop-config.json .loop-memory.md
git commit -m "Enable full loop engineering for RCE hunting (all 5 patterns)"
git push -u origin claude/loop-engineering-full
```

#### assay (Testing + Dependencies + Progress)

```bash
cd ../assay
git checkout -b claude/loop-engineering-balanced

# Copy and configure for patterns 1, 3, 4 only
cp ../blackhawkyama/CLAUDE.md .
cp ../blackhawkyama/.loop-config.json .
cp ../blackhawkyama/.loop-memory.md .

# Edit .loop-config.json:
#   - testing: enabled=true
#   - quality: enabled=false (DISABLE)
#   - dependencies: enabled=true
#   - progress: enabled=true
#   - documentation: enabled=false (DISABLE)

git add CLAUDE.md .loop-config.json .loop-memory.md
git commit -m "Enable balanced loop engineering (testing, deps, progress)"
git push -u origin claude/loop-engineering-balanced
```

#### gauntlet (Testing + Quality + Dependencies)

```bash
cd ../gauntlet
git checkout -b claude/loop-engineering-quality

# Copy and configure for patterns 1, 2, 3 only
cp ../blackhawkyama/CLAUDE.md .
cp ../blackhawkyama/.loop-config.json .
cp ../blackhawkyama/.loop-memory.md .

# Edit .loop-config.json:
#   - testing: enabled=true
#   - quality: enabled=true
#   - dependencies: enabled=true
#   - progress: enabled=false (DISABLE)
#   - documentation: enabled=false (DISABLE)

git add CLAUDE.md .loop-config.json .loop-memory.md
git commit -m "Enable quality-focused loop engineering (test, quality, deps)"
git push -u origin claude/loop-engineering-quality
```

#### immunefi-solidity-track (Progress + Docs)

```bash
cd ../immunefi-solidity-track
git checkout -b claude/loop-engineering-lean

# Copy and configure for patterns 4, 5 only
cp ../blackhawkyama/CLAUDE.md .
cp ../blackhawkyama/.loop-config.json .
cp ../blackhawkyama/.loop-memory.md .

# Edit .loop-config.json:
#   - testing: enabled=false (DISABLE)
#   - quality: enabled=false (DISABLE)
#   - dependencies: enabled=false (DISABLE)
#   - progress: enabled=true
#   - documentation: enabled=true

git add CLAUDE.md .loop-config.json .loop-memory.md
git commit -m "Enable lean loop engineering (progress + docs only)"
git push -u origin claude/loop-engineering-lean
```

#### blackhawkyama.github.io (Docs Only)

```bash
cd ../blackhawkyama.github.io
git checkout -b claude/loop-engineering-docs

# Copy and configure for pattern 5 only
cp ../blackhawkyama/CLAUDE.md .
cp ../blackhawkyama/.loop-config.json .
cp ../blackhawkyama/.loop-memory.md .

# Edit .loop-config.json:
#   - testing: enabled=false (DISABLE)
#   - quality: enabled=false (DISABLE)
#   - dependencies: enabled=false (DISABLE)
#   - progress: enabled=false (DISABLE)
#   - documentation: enabled=true

git add CLAUDE.md .loop-config.json .loop-memory.md
git commit -m "Enable docs-only loop engineering for blog"
git push -u origin claude/loop-engineering-docs
```

---

## Step 3: Activate All Loops

Once all branches are pushed, activate in Claude Code CLI/web app:

```bash
# recce (FULL)
/schedule --name "recce: Test & CI" --cron "0 * * * *" --prompt "/loop test-and-ci"
/schedule --name "recce: Code Quality" --cron "0 */6 * * *" --prompt "/loop code-quality"
/schedule --name "recce: Dependencies" --cron "0 0 * * 0" --prompt "/loop dependency-check"
/schedule --name "recce: Progress" --cron "0 * * * *" --prompt "/loop progress-dashboard"
/schedule --name "recce: Documentation" --cron "0 0 */3 * *" --prompt "/loop documentation-check"

# assay (Testing + Deps + Progress)
/schedule --name "assay: Test & CI" --cron "0 * * * *" --prompt "/loop test-and-ci"
/schedule --name "assay: Dependencies" --cron "0 0 * * 0" --prompt "/loop dependency-check"
/schedule --name "assay: Progress" --cron "0 * * * *" --prompt "/loop progress-dashboard"

# gauntlet (Testing + Quality + Deps)
/schedule --name "gauntlet: Test & CI" --cron "0 * * * *" --prompt "/loop test-and-ci"
/schedule --name "gauntlet: Code Quality" --cron "0 */6 * * *" --prompt "/loop code-quality"
/schedule --name "gauntlet: Dependencies" --cron "0 0 * * 0" --prompt "/loop dependency-check"

# immunefi-solidity-track (Progress + Docs)
/schedule --name "immunefi: Progress" --cron "0 0 * * 0" --prompt "/loop progress-dashboard"
/schedule --name "immunefi: Documentation" --cron "0 1 * * 0" --prompt "/loop documentation-check"

# blackhawkyama.github.io (Docs only)
/schedule --name "blog: Documentation" --cron "0 0 * * 0" --prompt "/loop documentation-check"
```

---

## Token Budget Summary

| Repo | Tier | Patterns | Weekly Cost | Monthly Cost |
|------|------|----------|-------------|-------------|
| recce | Aggressive | 1-5 | ~192 tokens | ~768 tokens |
| assay | Balanced | 1,3,4 | ~32 tokens | ~128 tokens |
| gauntlet | Balanced | 1,2,3 | ~36 tokens | ~144 tokens |
| immunefi-track | Lean | 4,5 | ~2 tokens | ~8 tokens |
| blog | Lean | 5 | ~1 token | ~4 tokens |
| **TOTAL** | — | — | **~263 tokens/week** | **~1,052 tokens/month** |

**Cost vs. Benefit:**
- Max plan: Typically 100k-500k tokens/month
- Loop engineering: ~1,052 tokens/month = 0.2-1% of budget
- Savings: Hundreds of hours of manual testing, monitoring, doc updates

---

## Monitoring Dashboard

After activation, check progress with:

```bash
# Each repo updates its own .loop-memory.md
cat recce/.loop-memory.md              # RCE hunting progress
cat assay/.loop-memory.md              # Eval framework metrics
cat gauntlet/.loop-memory.md           # Prompt injection results
cat immunefi-solidity-track/.loop-memory.md  # Learning progress
cat blackhawkyama.github.io/.loop-memory.md  # Blog health
```

---

## Next Steps

1. ✅ Deploy to each repo (use Step 2 above)
2. ✅ Push all branches to GitHub
3. ✅ Activate in Claude Code CLI/web app
4. ⏳ Monitor first week of loop runs
5. ⏳ Adjust cron schedules or patterns based on actual costs

---

**Ready to deploy?** Let me know which repo you want to start with! 🐺
