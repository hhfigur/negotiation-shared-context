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

---

## 2026-06-05 — BUG-20260521-slow-return-from-tool (Regression 2)
**Task:** `loadSessions` serviert Cache sofort statt nach DB-Query
**Problem:** `hasFreshCache`-Bedingung mit `>= 0` war immer true (Arrays nie negativ), unterdrückte Spinner aber nicht den DB-Wait. `setSessions` wurde erst nach dem Supabase-Round-Trip (~200–500ms) aufgerufen. `useState`-Initializer für sessions konnte Cache nie nutzen da auth beim Mount async (null).
**Ursache:** Cache-Logik wurde nur als Spinner-Guard implementiert, nicht als Daten-Quelle. Die eigentliche Latenz (DB-Query) blieb unverändert.
**Regel:** Wenn ein module-level Cache existiert, muss er sofort als Datenquelle verwendet werden — nicht nur als Spinner-Guard. `setSessions(cache)` VOR dem async Call setzen, nicht danach.
**Folge-Risiko:** Jeder andere Hook mit ähnlichem Pattern (Cache vorhanden, trotzdem async fetch vor setState) hat dasselbe Problem. `loadSessionMessages` prüfen ob ähnliches Muster vorliegt.

---

## 2026-06-08 — BUG-20260521-slow-return-from-tool (Regression 3)
**Task:** AbortController + 6s Timeout in `loadSessions` — verhindert 30s PostgREST-Hang
**Problem:** Supabase PostgREST killt Queries nach 30s. JS Client retried automatisch → zweite 30s-Hang. React StrictMode + rapid dep-changes trigerten 2 simultane Calls. Kein AbortController → UI eingefroren bis zu 60s.
**Ursache:** Jeder Supabase-Query ohne AbortController hängt so lange wie der Server-Timeout (30s+). Niemand hat aktiv einen Timeout gesetzt — es wurde davon ausgegangen dass Supabase "schnell genug" ist.
**Regel:** JEDER Supabase-Query muss ein AbortSignal mit sinnvollem Timeout bekommen. 6s ist ein guter Default (kürzer als PostgREST 30s, länger als normaler DB-Round-Trip). Concurrent-Guard (module-level AbortController) verhindert Race Conditions bei Mehrfach-Aufruf.
**Folge-Risiko:** `loadSessionMessages` (session_history table), `supabase.auth.getSession()` in mehreren Calls, alle anderen Supabase-Queries ohne Timeout — bei Infrastruktur-Problemen hängt jede davon die UI auf.
