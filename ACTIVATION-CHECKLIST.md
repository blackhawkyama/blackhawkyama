# Loop Activation Checklist

**Quick reference for enabling loops in the next session**

---

## ⚡ Quick Start (3 steps, 2 minutes)

### Step 1: Open Claude Code Environment
Choose ONE:
- [ ] Claude Code CLI: Run `claude` in terminal
- [ ] Claude Code Web: Go to https://claude.ai/code
- [ ] IDE Extension: Open VS Code / JetBrains plugin

### Step 2: Run Schedule Commands
Copy & paste these commands into Claude Code:

```bash
/schedule --name "Progress Dashboard" --cron "0 0 * * 0" --prompt "/loop progress-dashboard"
/schedule --name "Documentation Check" --cron "0 1 * * 0" --prompt "/loop documentation-check"
```

### Step 3: Verify
Run this to confirm both loops are scheduled:
```bash
/schedule --list
```

**Expected output**: 2 scheduled routines (Progress Dashboard + Documentation Check)

---

## 📅 What Happens Next

| When | What | Where to Check |
|------|------|-----------------|
| Sunday 00:00 UTC | Progress Dashboard runs | .loop-memory.md |
| Sunday 01:00 UTC | Documentation Check runs | .loop-memory.md |
| Every Sunday after | Automatic repeats | .loop-memory.md |

---

## ✅ Validation Checklist

After running the commands, verify:

- [ ] No errors in Claude Code output
- [ ] `/schedule --list` shows 2 active routines
- [ ] Both routines show correct cron (`0 0 * * 0` and `0 1 * * 0`)
- [ ] Both prompts show `/loop progress-dashboard` and `/loop documentation-check`

---

## 🧪 Optional: Test One Loop First

**Before scheduling (safer approach):**

```bash
/goal metrics generated successfully
/loop progress-dashboard --max-iterations 1
```

Watch the output. If successful → proceed to Step 2 above.

If fails → Check LOOP-SETUP.md troubleshooting section.

---

## 📊 Monitor After Activation

**First Sunday (after scheduling)**:
1. Loops should run automatically
2. Check `.loop-memory.md` for results
3. Look for success status (✅ or error details)

**Weekly after that**:
- Monitor `.loop-memory.md` to see progress
- Check token usage on your Claude plan
- Adjust if needed (see "Customization" below)

---

## 🔧 Customization

### Change Loop Times
If Sunday mornings don't work for you:

```bash
# Reschedule Progress Dashboard to Friday 10:00 UTC
/schedule --update <routine-id> --cron "0 10 * * 5"

# Reschedule Documentation to Saturday 10:00 UTC
/schedule --update <routine-id> --cron "0 10 * * 6"
```

(Get `<routine-id>` from `/schedule --list`)

### Disable Loops Temporarily
```bash
/schedule --disable <routine-id>
```

### Delete Loops
```bash
/schedule --delete <routine-id>
```

---

## ⚠️ Important Reminders

1. **Environment**: Commands ONLY work in Claude Code, not bash
2. **UTC Times**: Cron schedules are in UTC (adjust for your timezone)
3. **Max Plan**: These loops use ~8 tokens/month (negligible)
4. **Manual Patterns**: Patterns 1-3 (Testing, Quality, Deps) are disabled
   - Run them manually when needed
   - Can re-enable if token budget increases

---

## 🆘 Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| `/schedule` not found | You're in bash, not Claude Code. Use CLI/web app |
| "routine already exists" | Delete old one first: `/schedule --delete <id>` |
| Loop didn't run Sunday | Check `/schedule --list` for typos in cron |
| Token overages | Verify budget caps in .loop-config.json |

More details: See LOOP-SETUP.md troubleshooting section.

---

## 📝 Session Tracking

| Session | Date | Action | Status |
|---------|------|--------|--------|
| Session 1 | 2026-07-05 | Created loop setup | ✅ Complete |
| Session 2 | 2026-07-07 | Optimized for max plan | ✅ Complete |
| Session 3 | YYYY-MM-DD | **← You are here** | [ ] Activate loops |
| Session 4+ | YYYY-MM-DD | Monitor & adjust | [ ] Pending |

---

## Next Actions

1. ✅ **NOW**: Follow steps in "Quick Start" above
2. ⏳ **Next Sunday**: Loops auto-run
3. 📊 **After first run**: Check .loop-memory.md
4. 🔄 **Weekly**: Monitor progress

---

**That's it!** 2 minutes of setup, automatic every Sunday after. 🚀
