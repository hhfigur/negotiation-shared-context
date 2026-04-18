# WIKI — Governance Baseline: NegotiationCoach AI

**Klassifikation:** Observed | Inferred | Missing | Proposed
**Erstellt:** 2026-04-17
**Ablageort:** `shared-context/docs/wiki/`
**Basis:** ADR-001–007, Delivery-Controller-Erfahrung, initial-setup-baseline.md, Wave-1-Completion-Gate
**Verwandte Dokumente:** GOV-01 enthält Audit-Workflow und Kadenz-Details; ALL-PROMPTS-AUDIT enthält alle Prompt-Texte. Dieses Dokument ergänzt beide — keine Duplikation.

---

## 1. Nicht verhandelbare Architekturregeln

**Observed** — alle aktiv, abgeleitet aus ADR-001–006 und Delivery-Controller-Betrieb.

| # | Regel | Herkunft | Konsequenz bei Verletzung |
|---|-------|----------|--------------------------|
| 1 | Railway = kanonischer Execution-Path für alle Business-Logik | ADR-001 | Kein Algorithm-Code in EF oder Frontend |
| 2 | Ein Writer pro Business-Entity | ADR-002 | Railway schreibt Sessions/Results; Frontend schreibt nur user-scoped Profile mit RLS-Verifikation |
| 3 | Anthropic/Railway + Gemini/Edge Function — permanent | ADR-003 | Keine neuen Anthropic-Calls aus Edge Functions; keine Gemini-Calls aus Railway |
| 4 | `subscription_tier` DB-Enum = Railway Tier-Werte (`free \| privat \| kmu \| profi`) | ADR-006 | Keine neuen Tier-Strings; `personaTypeToTier()` ist kanonisches Mapping |
| 5 | Keine direkten Supabase-Calls aus Frontend-Komponenten | ADR-001 | Immer via Railway API mediiert |
| 6 | Alle LLM-Calls serverseitig via Railway Backend (Anthropic Claude) | ADR-003 | Keine Claude-Calls im Browser oder in Edge Functions |
| 7 | Jede neue DB-Tabelle muss RLS-Policy bei Erstellung haben | ADR-002 | Kein `CREATE TABLE` ohne gleichzeitiger RLS-Policy im selben Migration-File |
| 8 | Schema-Änderungen nur via Migration-Files | ADR-002 | Nie über Supabase Dashboard — immer append-only `.sql` in `supabase/migrations/` |
| 9 | Tier-Prüfungen immer serverseitig — Frontend-Gates sind UI-only | ADR-006 | Serverseitige `requireTier()`-Middleware; Frontend-Checks sind rein visuell |
| 10 | Keine Cross-Repo-Änderungen ohne Impact Assessment | Delivery-Controller | `impact-check`-Skill vor jeder Änderung mit shared state / API / DB |
| 11 | Kein neuer LLM-Call ohne `modelRouter.selectModel()` | ADR-003 + RFB-011 | Direkte Modell-Strings (`'claude-sonnet-4-6'`) sind verboten; immer via modelRouter |
| 12 | Layer-Abhängigkeiten 0 → 1 → 2 → 3 — kein Überspringen | ADR-001 + ENGB01 | Kein Layer-2/3-Code ohne vollständige Layer-0/1-Grundlage; ADR erforderlich bei Abweichung |

---

## 2. Anti-Patterns — Verbotene Muster

**Observed / Proposed** — abgeleitet aus Audit-Findings, ADR-001/002 und Delivery-Controller-Erfahrung.

### AP-01 — Direkte Supabase-Calls aus Frontend-Komponenten
**Verboten.** Ausnahme: user-scoped Profile-Updates mit verifizierten RLS-Policies.
**Begründung:** Business-Logik (Limits, Validierung, Ownership) landet im Browser. Schwer zu testen, kein Server-Side-Enforcement. CRIT-02/HIGH-01 in Wave 1 identifiziert.
**Herkunft:** AGENTS.md (Observed violation), ADR-001 Decision 4
**Korrekte Alternative:** Railway API-Endpunkt verwenden; nie Supabase JS direkt aus Komponenten.

### AP-02 — Algorithm-Logik in Edge Functions oder Frontend
**Verboten.** ZOPA, Nash, Monte Carlo, strategyScore, deadlineEffect, BATNA gehören ausschließlich in `negotiationcoach-backend/src/layer1/`.
**Begründung:** Dual-Maintenance führt zu Schema-Drift (CRIT-01: `user_goal` vs. `own_target`). Zwei unabhängige Implementierungen sind unverifizierbar konsistent.
**Herkunft:** ADR-001 Decision 2; CRIT-01; RFB-006 (DEFERRED → ADR-007)
**Korrekte Alternative:** Edge Functions delegieren via HTTP-Call an Railway.

### AP-03 — Business Rules in Frontend-Hooks
**Verboten.** Session-Title-Truncation (40 Zeichen), Message-Load-Limit (50), Retry-Logik — alles gehört ins Backend.
**Begründung:** Business Rules im Browser sind nicht durchsetzbar und nicht testbar als Contract.
**Herkunft:** ADR-001 Decision 4; `useSessionManager.ts` (Observed)
**Korrekte Alternative:** Railway-Endpunkt implementiert und erzwingt die Regel.

### AP-04 — Silent Fallback Returns statt null/Error
**Verboten.** Funktionen, die bei Fehler still `{}` oder `undefined` zurückgeben, ohne Caller zu informieren.
**Begründung:** SESSION INSERT-Fehler werden aktuell geschluckt (R-08) — sessionId: null ohne Caller-Feedback möglich.
**Herkunft:** WIKI Risikoübersicht R-08; Observed in routes.ts
**Korrekte Alternative:** AppError werfen; Caller muss Fehler explizit behandeln.

### AP-05 — Hardcoded Tier-Werte im Frontend
**Verboten.** Keine `if (tier === 'kmu')` Checks im Frontend die Zugang zu Features steuern.
**Begründung:** Frontend-Tier-Checks sind UI-only und kein Sicherheitsmechanismus. Echter Tier-Schutz liegt im Railway-Backend.
**Herkunft:** ADR-006; Tier-Gate-Lücken (WIKI R-05)
**Korrekte Alternative:** Railway gibt 403 zurück; Frontend zeigt nur UI-Feedback.

### AP-06 — Cross-Repo-Änderungen ohne Impact Assessment
**Verboten.** Keine Änderungen die API-Contracts, Supabase-Schema oder Auth-Flow betreffen ohne vorherigen `impact-check`.
**Begründung:** Ungesehene Auswirkungen führen zu Contract-Drift und broken deployments.
**Herkunft:** Delivery-Controller-Betrieb; `impact-check`-Skill
**Korrekte Alternative:** `impact-check`-Skill vor jeder Änderung mit shared state ausführen.

### AP-07 — Neue LLM-Calls ohne modelRouter
**Verboten.** Direkter Anthropic SDK-Aufruf ohne `modelRouter.selectModel(task, tier)`.
**Begründung:** Cost-Optimierung und Tier-Routing sind nur über modelRouter steuerbar. Bypass verhindert Haiku-für-free-Tier-Routing.
**Herkunft:** RFB-011 (Observed; behoben commit `60848db`); Repo-Governance-Regeln
**Korrekte Alternative:** `const model = modelRouter.selectModel(task, tier); anthropic.messages.create({ model, ... })`

### AP-08 — Neue Express-Endpunkte ohne Zod-Validierung
**Verboten.** Kein `as NegotiationInputs` Cast ohne vorherige Zod-Schema-Validierung des Request-Body.
**Begründung:** Zod ist installiert aber nicht genutzt (R-05). Fehlende Validierung erlaubt malformed Inputs in die Engine.
**Herkunft:** WIKI Risikoübersicht R-05; Repo-Governance-Regeln (Proposed)
**Korrekte Alternative:** Jeder neue Endpunkt hat ein `const result = schema.safeParse(req.body)` vor jedem Zugriff.

---

## 3. Bewährte Entscheidungsprinzipien

**Observed / Proposed** — abgeleitet aus Delivery-Controller-Betrieb und Wave-1-Erfahrung.

### Prinzip 1 — Plan before Implement (Template 1 → Review → GO/HOLD/SPLIT/BACK TO DOCS → Template 2)

```
Template 1 (PLAN ONLY)
      ↓
Delivery Controller Review
      ↓
GO → Template 2 (IMPLEMENT ONLY)
HOLD → Blocker adressieren, nochmal Template 1
SPLIT → Item aufteilen, einzeln behandeln
BACK TO DOCS → Fehlende Dokumentation/ADR zuerst erstellen
```

Niemals Template 2 ohne dokumentiertes GO ausgeben.
Wenn Ownership, Contract, Auth, Permission oder Write Path unklar sind → BACK TO DOCS.

### Prinzip 2 — close-task vor jedem DONE-Stempel

Jeder Backlog-Item-Abschluss läuft durch `/close-task` (Steps A–J):
- TypeCheck (`npx tsc --noEmit`)
- Tests
- Contract-Check
- Backlog-Stempel (Entry Body + Summary Index)
- Wiki-Update (index.md + session-log.md)
- Zwei-Commit-Pattern (Impl-Repo + shared-context)

Kein DONE ohne `/close-task`. Kein `/close-task` ohne TypeCheck-Verifikation.

### Prinzip 3 — ADR vor Implementierung

Architektur-Änderungen erfordern eine ADR-Entscheidung bevor Code entsteht.
Ausnahme: Bug-Fixes innerhalb bestehender Boundaries (kein ADR erforderlich).

Kriterium: "Verändert diese Änderung Ownership, Layer-Grenze, Daten-Schreibpfad, oder AI-Provider-Routing?" → Ja → ADR zuerst.

Aktuelle ADR-Lücke: ADR-007 (Dual Layer-1-Entscheidung) ist DRAFT — blockiert RFB-006 und RFB-026.

### Prinzip 4 — Layer-Abhängigkeiten: 0 → 1 → 2 → 3

Kein Layer-N-Code ohne vollständige und korrekte Layer-(N-1)-Grundlage.

| Layer | Voraussetzung | Status |
|-------|--------------|--------|
| 0 — Data Foundation | — | ✅ |
| 1 — Analysis Engine | Layer 0 ✅ | ✅ |
| 2 — Context Engine | Layer 1 ✅ | ⚠️ fehlerhaft |
| 3 — Simulation Engine | Layer 2 korrekt ✅ | ❌ Wartet auf Layer-2-Fix |

Layer-3-Implementierung beginnt erst nach Layer-2-Fix (Wave-2-Abhängigkeitsgraph).

---

## 4. Aktive Strukturelle Restrisiken

**Observed** — Stand 2026-04-16. Vollständige Risikodokumentation: `docs/wiki/WIKI---Repo-Profile-negotiationcoach-backend.md` Abschnitt 6.

| ID | Risiko | Schwere | Status | Nächste Aktion |
|----|--------|---------|--------|----------------|
| CRIT-01 | Dual Layer-1-Implementierung — EF `_shared/engine/` vs. Railway `src/layer1/` inkompatibles Schema | 🔴 KRITISCH | Deferred → ADR-007 | VG-06 entscheiden, ADR-007 abschließen |
| CRIT-DRIFT | EF-Schema (`user_goal`) ≠ Railway-Schema (`own_target`) — CRITICAL TYPE DRIFT | 🔴 KRITISCH | Deferred → ADR-007 | Geschlossen wenn CRIT-01 resolved |
| RFB-006 | Layer-1-Unification — beide Implementierungen oder EF retire | 🔴 P1 | DEFERRED 2026-04-16 — wartet auf ADR-007 | Erste Implementierungsarbeit nach ADR-007 |
| RFB-026 | batnaDetector EF Reparatur — broken import, Schema-Drift | 🟡 P2 | DEFERRED 2026-04-16 — wartet auf RFB-006 | Nach RFB-006 |
| RFB-032 | Stripe Webhook Handler nicht implementiert | 🔴 HOCH (Business) | Deferred — Stripe nicht live | Aktivieren wenn Stripe live geschaltet |
| R-04 | CORS Wildcard-Header überschreibt cors()-Allowlist | 🟡 MITTEL | Unbehandelt | Nach Layer-2-Fix adressieren |
| R-05 | Zod installiert aber nirgendwo importiert — kein Input-Validation-Pattern | 🟡 MITTEL | Unbehandelt | Neue Endpunkte erzwingen Zod |
| VG-01 | RLS-Enforcement in Production unbestätigt (teams, negotiation_sessions) | 🔴 KRITISCH | Offen — Wave-2-A-Audit-Target | Audit: RLS in Prod verifizieren |
| VG-02 | Cross-User-Read-Prevention unbestätigt | 🔴 HOCH | Offen — Wave-2-A-Audit-Target | Audit: anon_key Cross-User-Test |

---

## 5. Tier-Modell (Kanonisch)

**Observed** — Stand 2026-04-16 nach RFB-036 (`a28d28c`). Vollständig dokumentiert in ADR-006.

| Tier | Preis | Zugang | DB-Enum-Wert |
|------|-------|--------|--------------|
| `free` | 0€ | Demo-Modus, read-only | `free` |
| `privat` | 12€ | Nur Layer-1-Analyse | `privat` |
| `kmu` | 49€ | Layer 1 + Layer 2 Basis, Scenario Marketplace lesen | `kmu` |
| `profi` | 99€ | Alle Features, Layer 3, Scenario Marketplace erstellen, PDF Export | `profi` |

**DB-Enum:** `subscription_tier` in Supabase ist seit ADR-006 / RFB-036 auf Railway Tier-Werte ausgerichtet.
**Mapping-Funktion:** `personaTypeToTier()` in negotiation-buddy — konvertiert UI-Persona-Begriffe zu Railway Tier-Strings.
**Stripe-Status:** Kein Webhook-Handler implementiert — Tier-Upgrade nach Zahlung nicht aktiv (**RFB-032 deferred**).

---

## 6. Audit-Kadenz (Übersicht)

**Observed** — Details und Auslöser-Listen in GOV-01-audit-runbook.md.

| Rhythmus | Umfang | Pflichtartefakte | Auslöser |
|----------|--------|-----------------|---------|
| **Mini-Update** (pro Änderung) | Betroffene Docs, Contracts, ADRs | api-catalog, db-map, frontend-backend.md | Neue Endpunkte, Schema-Änderungen, Auth/Tier-Änderungen, neue EF |
| **Wöchentlich** | Hygiene-Review | redundancy-register, dead-code-candidates, offene VGs | Recurring — jede Woche |
| **Monatlich** | Light Audit | repo-map, feature/service-catalog, data-access-map, db-map | Alle 4–6 Wochen |
| **Vollaudit** | Cross-Repo-Synthese | alle Matrix- und Contract-Docs, Current-State-Report | Vor Major Release, neue Feature-Grenzen, Architektur-Ereignisse |

**Praktische Faustregel:**
- Mini-Update: im selben Task oder PR ausführen
- Vollaudit sofort bei: neuer Feature-Grenze, Integrationswechsel, Schema-Migration, Auth-Umbau

---

## 7. Governance-Rückführung — Was wohin gehört

**Observed / Proposed**

| Ereignis | Pflicht-Artefakt | Ziel |
|----------|-----------------|------|
| Architekturentscheidung | ADR | `shared-context/docs/decision-log/` |
| Abgeschlossenes Backlog-Item | close-task Stempel (Entry Body + Index) + Commit | `refactor-backlog.md` + `wiki/session-log.md` |
| Wave-Abschluss | Review source-of-truth-matrix + bounded-contexts | `shared-context/docs/` |
| Neue API-Erkenntnis (Boundary-Änderung) | frontend-backend.md Update | `shared-context/docs/contracts/` |
| Neue DB-Tabelle | RLS-Policy im selben Migration-File + db-map.md Update | `negotiationcoach-backend/supabase/migrations/` + `shared-context/docs/db-map.md` |

---

## 8. Verification Gaps — Aktueller Stand (2026-04-18)

| VG-ID | Frage | Status |
|---|---|---|
| VG-01 | RLS auf teams/team_members — admin_user_id = auth.uid()? | ✅ Resolved — 10 snake_case Policies via Migration `20260403120000` |
| VG-02 | RLS auf negotiation_sessions — cross-user reads mit anon key? | ✅ Resolved — `user_sees_own_sessions` policy pre-existing |
| VG-03 | Stripe Webhook — wo wird user_metadata.tier aktualisiert? | ✅ Closed — Handler absent; RFB-032 registriert (deferred) |
| VG-04 | Was erstellt die initiale user_profiles Zeile bei Signup? | ⚠️ Offen — vor User-Profile-Features verifizieren |
| VG-05 | Liest EF /chat echten User-Tier aus JWT? | ✅ Resolved — tier aus Request Body gelesen, aber nicht enforced; kein JWT Auth (→ VG-05-A) |
| VG-05-A | EF /chat ohne JWT Auth — kein RFB registriert | ⚠️ Offen — High Severity; kein RFB-Eintrag vorhanden |
| VG-06 | Ist generate-plan EF aktiv oder Railway /api/plan? | ✅ Resolved — generate-plan EF ist ACTIVE; Railway generatePlan() ist Dead Code (→ ADR-005) |
| VG-07 | ADR-004 Option? | ✅ Resolved — Option A akzeptiert |

---

## 9. Backlog-Status Wave 2 (Stand 2026-04-18)

### Completed (Wave 1 — Auszug relevanter Abschlüsse)

| ID | Titel | Commit |
|---|---|---|
| RFB-004 | Session/Message writes → Railway API (alle Phasen A/B/C) | `2c51cb4`, `2415f72`, `6021665`, `243c02d` |
| RFB-031 | session_history Tabellenname-Fix in sessionRoutes.ts | `2c51cb4` |
| RFB-036 | subscription_tier DB-Enum auf Railway Tier-Werte (ADR-006) | `a28d28c` |

### Offen / Blockiert Wave 2

| ID | Status | Blocker |
|---|---|---|
| RFB-006 | ⏸ Deferred | ADR-007 erforderlich |
| RFB-009 | ⏸ Blocked | RFB-007 + VG-05 resolved; scope expanded (EF enforcement nötig) |
| RFB-020 | Open P3 | kein Blocker |
| RFB-026 | ⏸ Deferred | RFB-006 erforderlich |
| RFB-032 | ⏸ Deferred | Stripe nicht live |

### Permanent geparkt (nie in START NEXT REFACTOR nominieren)

- RFB-010 — in RFB-032 überführt
- RFB-016 — deferred, nicht surfacen
- Team-Features (RFB-003 Phase C etc.) — bis explizit angefordert

---

## 10. Offene Governance-Dokumente — Identified 2026-04-18

Die folgenden Governance-Dokumente sind identifiziert aber noch nicht erstellt.
Reihenfolge nach Priorität. Details und Begründungen in `WIKI---Wiki-Gap-Analysis.md`.

| Priorität | Dokument | Zweck |
|---|---|---|
| P1 | `docs/governance/architecture-guardrails.md` | Single-page Reference aller Architekturregeln, Non-negotiables, Anti-Patterns |
| P2 | `docs/governance/supabase-governance.md` | Konsolidierte Supabase-Regeln (Instanzen, Migrations, RLS, Auth) |
| P2 | `docs/governance/change-doc-standard.md` | Pflichtfelder und Definition of Done für Änderungen |
| P2 | `docs/delivery/playbook.md` | Standalone Delivery Playbook (aus initial-setup-baseline konsolidieren) |

**Klassifizierung:** Proposed — noch nicht entschieden, wann erstellt.

---

*Dieses Dokument wird nicht automatisch aktualisiert. Nach jeder Wave und nach jeder wesentlichen Governance-Entscheidung reviewen.*
