# Diagnosis Report — BUG-20260521-session-reload-after-auth

**Datum:** 2026-05-21
**Status:** PLAN ONLY — kein Code geändert
**Repo:** negotiation-buddy (primary) · negotiationcoach-backend (secondary)

---

## Root Cause (Zusammenfassung)

`useSessionManager` lädt Sessions über einen direkten Supabase-Client-Call (kein Backend-API-Aufruf).
Der zuständige `useEffect` hat die Dependency-Array `[personaType, loadSessions]`.
Nach Logout + Re-Login mit denselben Credentials bleibt `personaType` unverändert → Effect feuert nicht → `loadSessions()` wird nie aufgerufen → Session-Liste bleibt leer.

**Primäre Ursache:** Fehlende Auth-Dependency im useEffect  
**Sekundäre Ursache:** Silent failure — kein Error-Logging bei Lade-Fehler  
**Tertiäre Ursache:** Race condition bei JWT-Token-Bereitschaft  
**Architektur-Abweichung:** Direct Supabase-Call statt Backend-API (ADR-002-Verletzung)

---

## Execution-Pfad (Observed)

### Normaler Login (erstmalig):
```
useAuth.onAuthStateChange → user gesetzt
→ Index.tsx Effect [user] (Z. 183–205) → loadProfile() → persona gesetzt
→ useSessionManager Effect [personaType] (Z. 46–50) → loadSessions() aufgerufen
→ supabase.auth.getSession() → userId → supabase.from("negotiation_sessions")
  .select("*").eq("user_id", userId) → setSessions(data)
```

### Nach Logout + Re-Login (Bug-Pfad):
```
Logout → user = null
→ Index.tsx Effect [user] (Z. 183) → if (!user) return  ← KEIN Reset von persona
→ persona bleibt auf altem Wert ("pro")

Re-Login → user = gesetzt
→ Index.tsx Effect [user] → loadProfile() → persona = "pro" (gleicher Wert)
→ useSessionManager Effect [personaType] → personaType = "pro" (keine Änderung!)
→ Dependency-Array erkennt keine Änderung → Effect FEUERT NICHT
→ loadSessions() wird NICHT aufgerufen
→ setSessions() wird NICHT aufgerufen
→ Session-Liste bleibt leer
```

---

## Findings

### F-01 — Fehlende Auth-Dependency im useEffect
**Label:** Observed  
**Datei:Zeile:** `src/hooks/useSessionManager.ts:46–50`
```typescript
useEffect(() => {
  if (personaType && personaType !== "private") {
    loadSessions();
  }
}, [personaType, loadSessions]);  // ← authSession/user fehlt als Dependency
```
`authSession` oder `user` sind nicht im Dependency-Array. Nach Re-Login mit identischer `personaType` feuert der Effect nicht erneut.

---

### F-02 — Logout leert Session-State nicht
**Label:** Observed  
**Datei:Zeile:** `src/pages/Index.tsx:183–205`
```typescript
useEffect(() => {
  if (!user) return;  // ← Kein setSessions([]) vor return
  // ...
}, [user]);
```
Wenn `user` auf `null` wechselt (Logout), wird `persona` nicht zurückgesetzt und `setSessions([])` nicht aufgerufen. Der alte Zustand bleibt.

---

### F-03 — Kein GET /api/sessions-Endpunkt im Backend
**Label:** Observed  
**Datei:Zeile:** `negotiationcoach-backend/src/api/sessionRoutes.ts` (gesamte Datei)  
Vorhandene Endpunkte: `POST /sessions`, `PATCH /sessions/:id`, `POST /sessions/:id/messages`  
Vorhanden in routes.ts: `GET /sessions/:id` (einzelne Session)  
**Missing:** Kein `GET /sessions` (Liste) existiert. Sessions werden **ausschließlich** via direktem Supabase-Client geladen — Verletzung von ADR-002 (Backend kanonisch).

---

### F-04 — Silent Failure: kein Error-Logging in loadSessions()
**Label:** Observed  
**Datei:Zeile:** `src/hooks/useSessionManager.ts:40–43`
```typescript
if (!error && data) {
  setSessions(data as Session[]);
}
setIsLoadingSessions(false);
// ← Kein else, kein console.error(), kein toast.error()
```
Fehler bei der Supabase-Abfrage werden still geschluckt. Nutzer erhält keinen Hinweis auf das Scheitern.

---

### F-05 — Silent Failure: früher Return ohne userId
**Label:** Observed  
**Datei:Zeile:** `src/hooks/useSessionManager.ts:28–31`
```typescript
const { data: { session: authSessionLocal } } = await supabase.auth.getSession();
const userId = authSessionLocal?.user?.id;
if (!userId) return;  // ← kein Log, kein Toast, kein Hinweis
```
Falls JWT beim ersten Load-Versuch noch nicht bereit ist, wird lautlos abgebrochen.

---

### F-06 — Race Condition: getSession() ohne JWT-Garantie
**Label:** Inferred  
**Datei:Zeile:** `src/hooks/useSessionManager.ts:28`  
`loadSessions()` ruft intern `supabase.auth.getSession()` auf — nicht das aus dem Auth-Context kommende, garantiert gültige Token. Nach Token-Refresh könnte der erste Call noch das abgelaufene Token erwischen.

---

### F-07 — apiClient.ts: keine getSessionsList()-Funktion
**Label:** Missing  
**Datei:Zeile:** `src/lib/apiClient.ts`  
`getSession(sessionId, token)` existiert (einzelne Session). Eine `getSessionsList(token)`-Funktion fehlt vollständig. Konsistenz mit ADR-002 wäre nur über Backend-Endpunkt erreichbar.

---

## Fehler-Hierarchie

| # | Befund | Typ | Schwere |
|---|---|---|---|
| F-01 | Missing Auth-Dependency im useEffect | Observed | Root Cause |
| F-02 | Logout leert persona/sessions nicht | Observed | Root Cause |
| F-03 | Kein GET /api/sessions Backend-Endpunkt | Observed | Arch-Debt (ADR-002) |
| F-04 | Silent failure: kein Error-Logging | Observed | Verschlimmert Diagnose |
| F-05 | Silent return bei !userId | Observed | Race-Condition-Trigger |
| F-06 | Race condition JWT-Bereitschaft | Inferred | Sekundär |
| F-07 | Fehlende apiClient.ts-Funktion | Missing | Folge-Architektur-Debt |

---

## Minimaler Fix-Scope (Planung, kein Code)

**Minimal (behebt den Bug ohne Arch-Refactor):**
1. `Index.tsx` — Bei Logout (`if (!user) return`) zuerst `persona` und `sessions` zurücksetzen
2. `useSessionManager.ts` — `loadSessions()` explizit bei personalType-Wechsel UND Auth-State-Wechsel aufrufen (User als zusätzliche Dependency oder expliziter Call nach Login)
3. `useSessionManager.ts` — Silent failures durch `toast.error()` ersetzen

**Nicht in diesem Fix (separate Issues):**
- ADR-002-Compliance: Backend GET /api/sessions — wäre Breaking Change, separates Ticket
- Race Condition JWT: separates Hardening-Ticket

---

## Betroffene Dateien (Änderungen nötig)

| Datei | Änderung |
|---|---|
| `src/hooks/useSessionManager.ts` | Dependency-Array + Error-Logging |
| `src/pages/Index.tsx` | Persona/Sessions-Reset bei Logout |

**Nicht ändern:**
- `negotiationcoach-backend/` — kein Backend-Fix in diesem Scope
- `src/lib/apiClient.ts` — ADR-002-Compliance ist separates Issue
