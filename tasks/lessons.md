# Lessons Learned — NegotiationCoach AI

Format für neue Einträge:
## [DATUM] — [BUG-ID oder TASK-ID]
**Task:** Was wurde gemacht
**Problem:** Was war falsch oder überraschend
**Ursache:** Warum wurde es nicht sofort erkannt
**Regel:** Was beim nächsten Mal anders machen
**Folge-Risiko:** Welche anderen Stellen könnten dasselbe Problem haben

---

## 2026-06-04 — BUG-20260521-slow-return-from-tool (Regression)
**Task:** Auto-Restore-Logik nach Tool-Navigation repariert — 3–10s Freeze behoben
**Problem:** `_lastActiveSessionId` (module-level) wurde von Effect 1 auf `null` gesetzt, bevor Effect 2 sie lesen konnte. React führt Effects in Deklarationsreihenfolge aus — Effect 1 (Z. 306) feuerte vor Effect 2 (Z. 313) im selben Render-Zyklus.
**Ursache:** Der ursprüngliche Perf-Fix (`d1485f7`) wurde nicht gegen das Effect-Ordering-Verhalten von React geprüft. TypeScript-Check reicht nicht — Runtime-Reihenfolge ist unsichtbar für tsc.
**Regel:** Wenn zwei Effects dieselbe module-level Variable schreiben und lesen, immer prüfen: Welcher feuert zuerst? Werte die vor allen Effects gelesen werden müssen: `useRef(value)` bei Component-Init, nie direkt in Effect lesen.
**Folge-Risiko:** Alle anderen module-level Variablen in `useSessionManager.ts` (`_sessionCache`, `_sessionCacheUserId`) die in Effects gelesen werden — prüfen ob ähnliches Ordering-Problem möglich ist.
