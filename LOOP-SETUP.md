# Loop Engineering Setup Guide

Quick start for activating the 5 efficiency patterns in your repos.

---

## ⚡ Quick Start (Copy & Paste)

### 1. Test & CI Loop (1-hour interval)
```bash
/schedule --name "Test & CI Loop" --cron "0 * * * *" --prompt "/loop test-and-ci"
```

### 2. Code Quality Loop (6-hour interval)
```bash
/schedule --name "Code Quality Loop" --cron "0 */6 * * *" --prompt "/loop code-quality"
```

### 3. Dependency Management Loop (Weekly)
```bash
/schedule --name "Dependency Update Loop" --cron "0 0 * * 0" --prompt "/loop dependency-check"
```

### 4. Progress Dashboard Loop (Hourly)
```bash
/schedule --name "Progress Tracking Loop" --cron "0 * * * *" --prompt "/loop progress-dashboard"
```

### 5. Documentation Loop (Every 3 days)
```bash
/schedule --name "Documentation Loop" --cron "0 0 */3 * *" --prompt "/loop documentation-check"
```

---

## 📋 Per-Repository Setup

### blackhawkyama (current)
Suggested loops: Testing (1), Quality (2), Progress (4), Docs (5)

```bash
# Enable these patterns
/loop test-and-ci                  # Pattern 1
/loop code-quality                 # Pattern 2
/loop progress-dashboard           # Pattern 4
/loop documentation-check          # Pattern 5
```

### assay
Framework for evaluations — enable Testing + Dependency

```bash
cd ../assay
/loop test-and-ci                  # Pattern 1
/loop dependency-check             # Pattern 3
```

### gauntlet
LLM security eval — enable Testing + Quality + Dependencies

```bash
cd ../gauntlet
/loop test-and-ci                  # Pattern 1
/loop code-quality                 # Pattern 2
/loop dependency-check             # Pattern 3
```

### recce
Reconnaissance agent — enable Testing + Progress + Docs

```bash
cd ../recce
/loop test-and-ci                  # Pattern 1
/loop progress-dashboard           # Pattern 4
/loop documentation-check          # Pattern 5
```

### immunefi-solidity-track
Solidity learning — enable Testing + Docs

```bash
cd ../immunefi-solidity-track
/loop test-and-ci                  # Pattern 1
/loop documentation-check          # Pattern 5
```

---

## 🚀 Manual Testing Before Scheduling

**Always test a loop manually before scheduling:**

```bash
# Example: Test the "test-and-ci" loop
/goal tests pass + coverage > 80%
/loop test-and-ci --max-iterations 1
```

Watch the output. If successful:
- ✅ Commit the changes
- ✅ Enable in .loop-config.json
- ✅ Schedule via `/schedule`

---

## 🛑 Stop & Disable Loops

**To pause a loop without deleting it:**

```bash
# List all scheduled loops
/schedule --list

# Disable a specific loop
/schedule --disable <loop-id>

# Delete a loop entirely
/schedule --delete <loop-id>
```

---

## 📊 Monitor Loop Progress

Check progress in two ways:

1. **Real-time**: View `.loop-memory.md` in this repo
2. **Dashboard**: Run `/loop progress-dashboard` manually for full metrics

---

## 🔧 Customization

### Adjust Loop Intervals

Edit `.loop-config.json` or re-run `/schedule` with new cron:

```bash
/schedule --update <loop-id> --cron "0 */2 * * *"  # Change to every 2 hours
```

### Change Budget Caps

Edit `.loop-config.json`:

```json
"budget_per_run": 5,        // Tokens per iteration
"budget_weekly_cap": 20     // Max weekly spend
```

### Modify Stop Rules

Update in `CLAUDE.md` the "Stop Rules (Critical)" section, then commit:

```bash
git add CLAUDE.md .loop-memory.md .loop-config.json
git commit -m "Update loop stop rules for faster convergence"
```

---

## ⚠️ Common Pitfalls

1. **Loop runs forever**: Check `max_iterations` in `.loop-config.json`
2. **Budget exhausted**: Increase `budget_per_run` or reduce `schedule` frequency
3. **Tests keep failing**: Add auto-fix steps in loop prompt
4. **Memory file grows huge**: Archive old runs, keep only recent 7 days
5. **Overlap conflicts**: Stagger cron times to avoid concurrent loops

---

## 📈 Success Metrics

After 1 week of loop runs, measure:

- **Test reliability**: % of test loops passing
- **Code quality**: # of auto-fixes applied per week
- **Dependency currency**: # of patches applied
- **Deployment frequency**: Deployments per week
- **Doc freshness**: % of docs updated

---

## 🆘 Troubleshooting

**Loop doesn't start:**
- Check cron syntax: `0 * * * *` = every hour
- Verify `/schedule` registered: `--list`
- Check Claude Code version supports loops

**Loop times out:**
- Reduce `max_iterations` to 1-2
- Split into smaller sub-loops
- Increase timeout: `--timeout 300s`

**Memory file not updating:**
- Ensure loop completes successfully
- Check file permissions: `chmod 644 .loop-memory.md`
- Verify loop appends to memory at end

**High token cost:**
- Reduce `budget_per_run`
- Use subagents with fresh context windows
- Cache CLAUDE.md instructions

---

## 📚 Reference

- **CLAUDE.md**: Frozen loop instructions (read at loop start)
- **.loop-memory.md**: Progress tracking (updated per loop)
- **.loop-config.json**: Configuration (edit to customize)
- **LOOP-SETUP.md**: This guide

---

## Next Steps

1. ✅ Choose 1-2 loops to start with (suggest: Testing + Progress)
2. ✅ Test manually with `/loop <pattern> --max-iterations 1`
3. ✅ Monitor output and results
4. ✅ Schedule via `/schedule` when confident
5. ✅ Check `.loop-memory.md` after first 24h
6. ✅ Adjust intervals/budgets based on actual costs
7. ✅ Roll out to other repos

---

**Questions?** Update this guide as you learn what works best for your workflow.
