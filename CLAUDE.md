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

### 1. Recurring Testing & CI Checks
**Goal**: Run tests, detect failures, fix common issues autonomously.

**Loop Prompt**:
```
/loop 1h
/goal all tests pass + coverage > 80%
Run: npm test && npm run coverage
If failures: auto-fix linting issues, run tests again.
Stop if: tests green, coverage > 80%, or 5 iterations.
Memory: .loop-memory.md tracks test runs + fixes applied.
```

**Config**:
- Trigger: Every 1 hour
- Verifier: test output + coverage report
- Stop Rule: success (tests green + 80% coverage) OR 5 iterations
- Budget: $5 per loop (allow small fixes)

---

### 2. Code Quality Loops
**Goal**: Continuous code review, linting, refactoring.

**Loop Prompt**:
```
/loop 6h
/goal code passes linting + no high-severity issues
Run: npm run lint && npm run type-check
Find: unused variables, dead code, complexity hotspots
Fix: apply auto-fixable issues, suggest refactors
Memory: .loop-memory.md tracks files modified + improvements
Stop if: all checks pass, no improvements found, or 3 iterations
```

**Config**:
- Trigger: Every 6 hours
- Verifier: lint results, type-check, complexity metrics
- Stop Rule: success (lint green + type-check green) OR 3 iterations OR no new issues
- Budget: $3 per loop

---

### 3. Dependency Management
**Goal**: Regular updates, security scans, compatibility checks.

**Loop Prompt**:
```
/loop 7d
/goal all dependencies current + no security vulnerabilities
Run: npm audit && npm outdated
Check: semver compatibility, breaking changes
Update: patch + minor versions, test after each
Memory: .loop-memory.md tracks dependency updates + audit results
Stop if: audit clean + all patches applied, or 2 iterations
```

**Config**:
- Trigger: Every 7 days
- Verifier: npm audit output, test suite
- Stop Rule: success (audit clean) OR 2 iterations OR breaking changes found (manual review)
- Budget: $8 per loop

---

### 4. Progress Tracking & Dashboards
**Goal**: Automated status dashboards, burndown charts, deployment monitoring.

**Loop Prompt**:
```
/loop 1h
/goal generate updated progress metrics + deployment status
Run: extract from .loop-memory.md files across all repos
Generate: 
  - Test pass rate (24h, 7d)
  - Deployment success rate
  - Issue resolution velocity
  - Code quality trend
Output: progress.md with metrics + charts
Memory: progress.md appends historical records
Stop if: metrics generated successfully
```

**Config**:
- Trigger: Every 1 hour
- Verifier: progress.md exists + has recent data
- Stop Rule: success (metrics generated) OR 1 iteration
- Budget: $2 per loop

---

### 5. Documentation Maintenance
**Goal**: Keep docs in sync with code changes, detect outdated sections.

**Loop Prompt**:
```
/loop 3d
/goal README + API docs match current code
Check: function signatures, endpoints, examples
Find: outdated sections, missing docstrings
Update: docs to match implementation, suggest refactors
Memory: .loop-memory.md tracks doc updates + issues
Stop if: all docs current, no mismatches, or 1 iteration
```

**Config**:
- Trigger: Every 3 days
- Verifier: code-to-doc diff, docstring coverage
- Stop Rule: success (docs match code) OR 1 iteration
- Budget: $2 per loop

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

**Token Budget Examples**:
- Pattern 1 (Testing): $5 per run, $20 weekly cap
- Pattern 2 (Quality): $3 per run, $15 weekly cap
- Pattern 3 (Dependencies): $8 per run, $16 weekly cap
- Pattern 4 (Progress): $2 per run, $14 weekly cap
- Pattern 5 (Docs): $2 per run, $6 weekly cap

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
