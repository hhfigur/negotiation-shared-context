---
name: session-start
description: Run at the start of every session in shared-context. Orients to current repo state, loads lessons, and confirms cross-repo readiness before any work begins.
trigger: Zu Beginn jeder Session in shared-context — vor jeder Änderung ausführen
---

# Skill: session-start

Run this at the start of every working session in shared-context.

## Checklist

Work through each item in order. Report status for each.

### 1. Lessons Review
- Read `tasks/lessons.md`
- Note any patterns relevant to today's task
- Surface any warnings that apply to what's being attempted

### 2. Branch & Diff Status

```bash
git -C . log --oneline -3
git -C . status --short
git -C ../negotiation-buddy log --oneline -3 2>/dev/null \
  || echo "negotiation-buddy nicht erreichbar"
git -C ../negotiation-buddy status --short 2>/dev/null
git -C ../negotiationcoach-backend log --oneline -3 2>/dev/null \
  || echo "negotiationcoach-backend nicht erreichbar"
git -C ../negotiationcoach-backend status --short 2>/dev/null
```

- Gibt es uncommitted changes? Was betreffen sie?
- Gibt es untracked files die gestaged werden sollten?
- Sind Repos ahead of origin?

### 3. Current Release State
- Read `product/releases/current.md`
- Note: welche Items sind In Delivery, welche Blocked
- Note: aktive Exit Criteria

### 4. Active Tasks
- Read `tasks/todo.md`
- Gibt es offene Items aus der vorherigen Session?
- BLOCKED-Items die eine User-Entscheidung brauchen, flaggen

### 5. Offene Bugs

```bash
grep -rl "Status:.*OPEN" docs/delivery/bugs/ 2>/dev/null
```

Für jeden offenen Bug: ID, Priorität (P0/P1/P2), aktueller Stand.
P0/P1 Bugs sind immer zuerst zu nennen.

### 6. Cross-Repo Readiness
- Confirm TARGET REPO ist deklariert (Pflicht für jede Dateiänderung)
- Wenn cross-repo gearbeitet wird: confirm `--add-dir` ist aktiv für relevante Repos
- Reminder: keine Dateien außerhalb shared-context ohne expliziten TARGET REPO Header

## Output Format

```
SESSION START — [DATUM]
─────────────────────────────
Repos:
  shared-context:           [branch, clean/dirty, ahead?]
  negotiation-buddy:        [branch, clean/dirty, ahead?]
  negotiationcoach-backend: [branch, clean/dirty, ahead?]

Lessons:      [relevante Muster oder: keine]
Tasks:        [offene Items oder: keine]
Offene Bugs:  [ID + Priorität oder: keine]
In Delivery:  [Items oder: keine]
Cross-repo:   [TARGET REPO oder: nicht gesetzt — read-only mode]
─────────────────────────────
Bereit für: [was heute angegangen werden kann]

STOP — warte auf Aufgabe vom User.
```
