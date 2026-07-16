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

---

## 2026-06-19 — BUG-20260529-batna-extraction (Regression Fix v2)
**Task:** EF extract-mode auf user-only messages umgestellt — BATNA-Extraktion endgültig gefixt
**Problem:** Nach Fix v1 (3-tier Regex) gab die EF immer noch all-null zurück. Ursache: Der Anthropic-Call erhielt das vollständige messages-Array (user + assistant). Lange strukturierte Coaching-Antworten (Szenarien, Strategieblöcke) im Assistenten-Kontext verursachten, dass Claude beim Extrahieren all-null zurückgab — obwohl der Nutzer BATNA explizit genannt hatte. curl-Bisection: user-only messages → korrekte Extraktion. Full conversation → all-null.
**Ursache:** Fix v1 löste das Parsing-Problem, aber nicht das Interferenz-Problem: Assistenten-Nachrichten mit reichen Coaching-Inhalten dominieren den LLM-Kontext und lassen den User-Content in den Hintergrund treten. Das Problem war nur mit dem realen Conversation-Payload sichtbar — synthetische Tests (kurze Konversationen ohne lange Strategie-Blöcke) passierten den Gate.
**Regel:** Bei LLM-Extraction aus Chat-History: IMMER nur User-Messages an den Extraction-Call übergeben. Assistenten-Nachrichten enthalten Paraphrasierungen, Coaching-Blöcke und Strategie-Outputs die das Signal-zu-Rausch-Verhältnis für strukturierte Extraktion massiv verschlechtern. user-only filter ist Standard-Pattern für Extraction-Calls.
**Folge-Risiko:** Alle anderen Extraction-Calls (analyze-progress EF, runExtractInputs im Backend) prüfen ob sie ebenfalls den vollen Messages-Array erhalten. analyze-progress EF ist besonders verdächtig — gleiche Architektur.

---

## 2026-07-02 — NC-L3-OPPONENT-UI (apiClient Path Bug)
**Task:** OpponentSimulator apiClient-Pfade korrigiert
**Problem:** Brief spezifizierte `/opponent-simulation/start` ohne `/api/`-Prefix — alle anderen apiClient-Funktionen nutzen `/api/...`. Fehler: `Cannot POST /opponent-simulation/start` im Frontend.
**Ursache:** Plan-Code-Block wurde ohne Abgleich mit bestehenden apiClient-Beispielen geschrieben.
**Regel:** Wenn neue apiClient-Funktionen im Plan spezifiziert werden, immer ein bestehendes Beispiel (z.B. `analyzeOnly`, `enrich`) aus der Datei zitieren, damit der Implementer das exakte Pfad-Pattern erkennt — nicht nur `/path` schreiben, wenn alle anderen `/api/path` nutzen.
**Folge-Risiko:** Jede neue apiClient-Funktion ohne expliziten `/api/`-Prefix-Hinweis im Plan.

## 2026-07-02 — NC-L3-OPPONENT-UI
**Task:** OpponentSimulator Frontend-Plan + Implementierung
**Problem:** Plan spezifizierte marker "06" für BottomTabBar/SessionSidebar, aber "06" war bereits von "Team" belegt. Implementer nutzte korrekt "07".
**Ursache:** Marker-Nummer wurde aus Annahme "nächste nach 05" ohne Codebase-Check vergeben.
**Regel:** Vor jeder Plan-Spezifikation von Marker-Nummern, Enum-Werten oder anderen sequential IDs: grep oder direkten Dateicheck durchführen. Keine sequenziellen IDs aus dem Kopf vergeben.
**Folge-Risiko:** Alle Pläne die neue BottomTabBar/Sidebar-Einträge spezifizieren — immer aktuellen Stand der TOOLS-Arrays prüfen vor Nummerierung.

## 2026-06-30 — BUG-20260630-tool-nav-404-perf
**Task:** Tool-Navigation 404 + langsames Laden nach Tool-Rückkehr behoben
**Problem:** Nach NC-NAV (Route-Umbenennung /zopa → /app/zopa) navigierten SessionSidebar und Landing.tsx weiterhin zu /zopa. React Router traf den catch-all → NotFound (404). Parallel: Index unmountete bei jedem Tool-Wechsel (Flat Routing) → Sessions/Profile re-fetch, N×ReactMarkdown-Parse → spürbare Verzögerung beim Zurücknavigieren.
**Ursache:** Route-Strings wurden an 2 von 4 Stellen aktualisiert (BottomTabBar ✓, App.tsx ✓), aber SessionSidebar und Landing.tsx wurden übersehen. Keine zentrale Routen-Konstante → Silent Divergence. Das Nested-Routing-Problem (Index remountet) war bekannt aber die 404-Symptome überdeckten es.
**Regel:** (1) Nach jeder Route-Umbenennung: `grep -r '"/zopa"\|"/canvas"\|"/what-if"'` über ALLE Dateien — nicht nur App.tsx und BottomTabBar. (2) Tool-Routen als Konstante exportieren (`TOOL_ROUTES` in einem zentralen File) statt als Strings an mehreren Stellen. (3) Nested Routing ist die korrekte Lösung für "Keep Parent Mounted" — aber vor Einführung alle navigate() / route strings im gesamten Repo auflisten (grep-Pflicht).
**Folge-Risiko:** Wenn weitere Route-Umbenennungen kommen, dieselbe grep-Pflicht anwenden. Alle Dateien mit hardcodierten Pfaden: SessionSidebar, Landing, BottomTabBar, StrategyGenerator, DebriefDashboard, TeamDashboard.

---

## 2026-06-10 — BUG-20260521-batna-lost-after-nav + BUG-20260529-batna-extraction
**Task:** Supabase EF `chat` (`mode: 'extract'`) JSON-Parsing robust gemacht — BATNA-Extraktion repariert
**Problem:** Die EF entfernte mit `content.replace(/```json\s*/g,"").replace(/```\s*/g,"").trim()` nur die Markdown-Fence-Marker und versuchte dann den GESAMTEN String zu `JSON.parse`en. Claude (Haiku 4.5) hält sich bei früh-/generischen Konversationen NICHT an "Antworte NUR mit validem JSON" — es antwortet im normalen Coaching-Ton (Prosa) mit einem eingebetteten ` ```json `-Block. Nach dem Fence-Strip beginnt der String mit Prosa-Text → `JSON.parse` wirft → Catch-Fallback liefert `alternatives: null` → BATNA wird nie aus `extractedInputs` extrahiert, geht aber durch die `??`-Merge-Logik bei jeder Navigation als "verschwunden" wahr.
**Ursache:** Die robuste 3-Tier-Regex-Extraktion existierte bereits im Backend (`chatHelpers.ts::parseChatResponse`), wurde aber nie auf die parallele Supabase-EF-Extraktion (NC-CONTEXT A) übertragen. Zwei parallele Extraktionspfade mit unterschiedlicher Parsing-Robustheit — der schwächere wurde nicht erkannt, weil er silent auf All-Null fällt (kein Error sichtbar).
**Regel:** Wenn ein LLM-Call eine "Antworte NUR mit JSON"-Anweisung enthält, IMMER mit 3-Tier-Regex-Fallback parsen (1. ` ```json ` Block egal wo im Text, 2. Objekt mit erwartetem Schlüssel auch ohne Fence, 3. irgendein `{...}`), NIEMALS naives `replace()` + direktes `JSON.parse()` auf den Rohtext. Bei zwei parallelen Implementierungen derselben Funktionalität (Backend vs. EF) IMMER auf identische Robustheit prüfen — nicht nur auf identisches Antwortformat.
**Folge-Risiko:** Andere `mode: '...'`-Branches in Supabase Edge Functions mit ähnlichem "JSON-only"-Prompt (falls vorhanden) könnten dasselbe naive Parsing nutzen. Bei jeder neuen EF mit strukturierter LLM-Antwort: 3-Tier-Parser aus `chatHelpers.ts` als Standard-Pattern verwenden.

---

## 2026-07-08 — NC-L3-SIM Phase 1 (/close-task-dev Format-Mismatch)
**Task:** Nach erfolgreichem Phase-1-Review (smlParser.ts + promptBuilder.ts, commit `c00e719`) `/close-task-dev` für NC-L3-SIM aufgerufen.
**Problem:** Zwei Probleme entdeckt statt eines sauberen Abschlusses: (1) `/close-task-dev` erwartet in Schritt A/B/F `### <ITEM_ID>`-Entry-Body-Überschriften plus eine separate `## Summary Index`-Tabelle mit `✅`-Stempeln — das ist das Format von `docs/audits/refactor-backlog.md` (RFB-xxx-Items). `product/feature-register.md`, wo alle `NC-`-Items inkl. NC-L3-SIM leben, nutzt seit der `product/README.md`-Umstellung ein flaches `## Register`-Tabellenformat ohne Item-Überschriften und ohne separate Summary-Index-Tabelle — Skill-Schritt B würde also literal HALTen. (2) Selbst mit angepasstem Format wäre ein "Status: DONE"-Stempel inhaltlich falsch gewesen: NC-L3-SIM ist ein Mehrphasen-Item (7 Phasen laut Design-Doc Abschnitt 11), Phase 1 war erst der erste von sieben Schritten.
**Ursache:** `/close-task-dev` wurde offenbar vor der Umstellung von `refactor-backlog.md` (### + Summary Index) auf `feature-register.md` (flache Tabelle) geschrieben und nie für das neue Format aktualisiert. Zusätzlich unterscheidet der Skill nicht zwischen "ganzes Item fertig" und "eine von mehreren Phasen fertig".
**Regel:** `/close-task-dev` NUR für vollständig abgeschlossene Items aufrufen (alle Phasen/Teilschritte fertig), nicht nach jedem Teilschritt eines Mehrphasen-Feature. Für `NC-`-Items in `feature-register.md`: der Skill braucht ein Update auf das flache Tabellenformat, bevor er für diese Items nutzbar ist — bis dahin bei `NC-`-Items manuell prüfen (Format + Vollständigkeit) statt den Skill blind laufen zu lassen. Zwischenstände von Mehrphasen-Items gehören in den Brief (`## Implement`-Abschnitt) und die `Notes`-Spalte des Registers, nicht in einen "Status: DONE"-Stempel.
**Folge-Risiko:** Jedes andere `NC-`-Item mit `/close-task-dev` würde denselben Format-Mismatch treffen. Der Skill selbst (`shared-context/.claude/skills/close-task-dev/`) sollte aktualisiert werden, um sowohl `refactor-backlog.md` (### + Summary Index) als auch `feature-register.md` (flache Tabelle, `Notes`-Spalte statt Entry-Body) zu unterstützen.

---

## 2026-07-16 — Loop-Coding-Integration PROMPT 1 (/close-task auf item-loses Governance-Delivery)

**Task:** Nach Governance-Delivery (verify-loop-Skill, feature-plan/feature-implement/bug-fix-Erweiterungen, ADR-011, verify-harness.md, Commit `2cd0285`) wurde `/close-task` aufgerufen.
**Problem:** `/close-task` verlangt zwingend eine `### <ITEM_ID>`-Entry-Body in `docs/audits/refactor-backlog.md` (Step B: HALT falls nicht gefunden) sowie `wiki/index.md`/`wiki/session-log.md` (Step J). Beides passt strukturell nicht: (1) dieses Delivery ist ein cross-cutting Engineering-Prozess-Item ohne RFB-/NC-ID — im Plan (`docs/features/loop-coding-integration.md` Abschnitt 6.6) explizit als offene Frage markiert, ob es überhaupt getrackt werden soll; (2) `wiki/` existiert in diesem Repo nicht mehr (durch `product/` + `tasks/` ersetzt) — der Skill referenziert eine veraltete Repo-Struktur.
**Ursache:** `/close-task` wurde vor der Umstellung von `wiki/` auf `product/`/`tasks/` geschrieben (ähnlich wie der bereits bekannte `/close-task-dev`-Formatmismatch vom 2026-07-08) und nie für item-lose Governance-Deliveries (kein RFB-/NC-Item) vorgesehen.
**Regel:** Vor jedem `/close-task`-Aufruf prüfen: (a) existiert `wiki/` überhaupt noch im Repo? (b) hat das Item ein RFB-ID in `refactor-backlog.md`? Falls eine der beiden Fragen "nein" ist: Skill NICHT blind durchlaufen, sondern manuell im Sinne des Skills abschließen (Verifikation, Staff-Engineer-Frage, Lessons-Eintrag) und dies explizit so berichten statt einen falschen ITEM_ID zu erfinden.
**Folge-Risiko:** Jedes weitere item-lose Governance-/Prozess-Delivery (kein RFB-/NC-Item) trifft denselben Mismatch. `/close-task` und `/close-task-dev` sollten langfristig auf die aktuelle Repo-Struktur (kein `wiki/`, `feature-register.md` statt RFB-Backlog für Produkt-Items, kein Träger für reine Governance-Items) aktualisiert werden.
