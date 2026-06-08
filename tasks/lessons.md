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

---

## 2026-06-08 — BUG-20260521 (Infrastruktur-Grundursache) + BUG-20260608-empty-session-accumulation
**Task:** Fehlenden DB-Index ergänzt + Teufelskreis "leere Session bei jedem Retry" gefixt
**Problem:** `negotiation_sessions` hatte KEINEN Index auf `(user_id, status, updated_at)` — Sequential Scan + Per-Row-RLS killte PostgREST-Threads nach 30s. Zusätzlich entdeckt: ein einzelner Test-Account hatte 1.126 aktive Sessions angesammelt (1.115 davon leere "Neue Verhandlung"-Platzhalter, 985 an einem Nachmittag erstellt) — weil `createSession` bei JEDEM Sende-Versuch eine neue DB-Zeile anlegt, auch wenn die vorherige leer blieb. Während des UI-Freezes wirkte jeder Versuch wie "nichts passiert" → User probierte erneut → neue leere Zeile → Tabelle wuchs → Queries wurden langsamer → mehr Retries. Ein sich selbst verstärkender Teufelskreis.
**Ursache:** Drei Frontend-Regressionsfixes (Effect-Ordering, Cache, AbortController) behoben Symptome, aber nicht die Infrastruktur-Grundursache (fehlender Index) UND nicht die Datenakkumulation, die die Grundursache erst manifestierte. Ohne MCP-Zugriff auf die Produktions-DB (falscher project_ref + abgelaufenes Token) war die Tabellengröße/Indexlage lange unsichtbar.
**Regel:** (1) Bei "Performance wird langsamer über Zeit"-Symptomen IMMER Tabellengröße + Indizes via `pg_indexes`/`EXPLAIN ANALYZE` prüfen, bevor man im Anwendungscode sucht. (2) Schreibende Operationen, die bei Retry/Fehler wiederholt aufgerufen werden können (`createSession`, ähnliche "lazy create on first action"-Patterns), brauchen serverseitige Reuse-/Idempotenz-Logik — nicht nur Frontend-Guards (Refs/State überleben keine Page-Reloads, Browser-Crashes oder mehrere Tabs).
**Folge-Risiko:** Jede andere "create-on-first-use"-Route ohne Reuse-Logik (z. B. Team-Erstellung, Negotiation-Erstellung) kann denselben Akkumulations-Teufelskreis erzeugen, wenn der zugehörige Read-Pfad einmal langsam wird. DB-Migrationen für neue Tabellen sollten Indizes für die erwarteten Hauptabfrage-Patterns von Anfang an enthalten (Checklist-Punkt für Migration-Reviews).
