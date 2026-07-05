# Loop Engineering for Repo Efficiency

This document enables autonomous loops via `/loop` and `/schedule` for recurring efficiency tasks.

## Loop Anatomy

**6 components:**
1. **Trigger**: `/schedule` + `/loop`; runs on interval or self-spaces
2. **Execution**: Claude reads state, acts, outputs. No manual iteration
3. **Verifier**: tests/build/screenshot, `/goal` grades
4. **Stop Rules**: success + failure stops + token budget
5. **Memory**: `.loop-memory.md` tracks progress, roll-back checkpoints
6. **Skills**: This CLAUDE.md (frozen instructions, keep short)

---

## Loop Patterns (5 Efficiency Workflows)

### 1. Recurring Testing & CI Checks ~~[DISABLED - Manual Only]~~
**Goal**: Run tests, detect failures, fix common issues autonomously.

~~Run manually during development. Too token-expensive for max plan.~~

---

### 2. Code Quality Loops ~~[DISABLED - Manual Only]~~
**Goal**: Continuous code review, linting, refactoring.

~~Run manually during development. Too token-expensive for max plan.~~

---

### 3. Dependency Management ~~[DISABLED - Manual Only]~~
**Goal**: Regular updates, security scans, compatibility checks.

~~Run manually or quarterly. Too token-expensive for max plan.~~

---

### 4. Progress Tracking & Dashboards ✅ [ENABLED]
**Goal**: Automated status dashboards, burndown charts, deployment monitoring.

**Loop Prompt**:
```
/loop progress-dashboard
/goal generate updated progress metrics
Run: extract from .loop-memory.md files across all repos
Generate: 
  - Test pass rate (7d)
  - Issue resolution velocity
  - Code quality snapshot
Output: progress.md with latest metrics
Stop if: metrics generated successfully (1 iteration max)
```

**Config**:
- Trigger: Every Sunday @ midnight (0 0 * * 0)
- Verifier: progress.md exists + recent timestamp
- Stop Rule: success (metrics generated) OR 1 iteration
- Budget: $1 per run, $4/month cap
- Max iterations: 1

---

### 5. Documentation Maintenance ✅ [ENABLED]
**Goal**: Keep docs in sync with code changes, detect outdated sections.

**Loop Prompt**:
```
/loop documentation-check
/goal README + docs match current code
Check: function signatures, examples, outdated sections
Find: missing docstrings, broken links
Suggest: refactors if found
Stop if: docs current or 1 iteration (1 shot only)
```

**Config**:
- Trigger: Every Sunday @ 1am (0 1 * * 0)
- Verifier: code-to-doc diff check
- Stop Rule: success (docs match) OR 1 iteration
- Budget: $1 per run, $4/month cap
- Max iterations: 1

---

## Memory File Format (.loop-memory.md)

Track each loop iteration:

```markdown
# Loop Memory for [Repo Name]

## Test Loop (Pattern 1)
- 2026-07-05 10:00: Tests run, 2 failures
  - Fixed linting issues in src/auth.ts
  - Coverage: 78% → 82%
  - Status: ✅ PASS

## Quality Loop (Pattern 2)
- 2026-07-05 16:00: Lint scan, 3 issues
  - Removed unused imports in handlers/
  - Complexity reduced in parser.ts
  - Status: ✅ PASS

## Dependency Loop (Pattern 3)
- 2026-07-05 12:00: Audit scan
  - npm audit: 0 vulnerabilities
  - Updated @types/node 18 → 20 (compatible)
  - Status: ✅ PASS

[Continue appending runs...]
```

---

## Stop Rules (Critical)

**Success**: Goal met (tests pass, lints clean, audit passes, etc.)
**Failure**: 
- Max iterations reached (varies by pattern: 1-5)
- Budget exhausted (set per loop)
- Manual error found (e.g., breaking change in dependency)
- Token budget exceeded

**Token Budget Examples** (Lean Setup - Max Plan Optimized):
- ~~Pattern 1 (Testing): DISABLED~~
- ~~Pattern 2 (Quality): DISABLED~~
- ~~Pattern 3 (Dependencies): DISABLED~~
- Pattern 4 (Progress): $1 per run, $4/month cap (weekly)
- Pattern 5 (Docs): $1 per run, $4/month cap (weekly)
- **Total**: ~8 tokens/month (~0.2% of typical max plan)

---

## Implementation Checklist

- [ ] Create `.loop-memory.md` in each repo
- [ ] Set up `/schedule` triggers (one per pattern per repo)
- [ ] Configure stop rules in each loop prompt
- [ ] Test 1 loop iteration manually before scheduling
- [ ] Monitor first 24h of automated runs
- [ ] Adjust intervals/budgets based on actual execution

---

## Loop Pro Tips

1. **Start with `/goal` before `/loop`** — Define verifiable end state first
2. **Keep memory files compact** — Append only latest runs, archive old entries
3. **Cap iterations aggressively** — Prevent runaway loops (max 3-5 per pattern)
4. **Use subagents for heavy lifting** — Agent() calls get fresh context windows
5. **Budget early** — Always set `token budget: $X` to prevent costly loops
6. **Test manually first** — Run the loop once by hand before scheduling
7. **Monitor dashboards** — Spot runaway loops via progress.md metrics
8. **Compact sessions regularly** — Loop memory can grow; roll back monthly
9. **No breaking changes in loops** — Loops should fix, not redesign

---

## Repos Using Loop Engineering

- blackhawkyama (this repo) — Profile + docs loop
- assay — Test + quality loops
- gauntlet — Test + dependency loops  
- recce — Test + progress loops
- immunefi-solidity-track — Test + doc loops
- [Add more as needed...]

---

## Example: Full Loop Lifecycle

```
T+0:00   /schedule run test-loop every 1h
T+1:00   TRIGGER: loop starts
T+1:05   EXECUTION: npm test runs, 2 failures
T+1:10   VERIFIER: detects failures, grades as FAIL
T+1:15   AUTO-FIX: fixes linting, reruns tests
T+1:20   VERIFIER: all pass, coverage 83%
T+1:21   MEMORY: appends success record
T+1:22   STOP: goal met, loop ends
T+2:00   TRIGGER: next iteration (repeats)
```

---

## Questions?

This is a living document. Update `.loop-memory.md` with learnings, add new patterns as workflows emerge, and adjust budgets based on actual costs.
