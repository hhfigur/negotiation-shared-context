# BUG-20260521-session-reload-after-auth — Diagnosis Report

**Datum:** 2026-05-21  
**Bug-ID:** BUG-20260521-session-reload-after-auth  
**Status:** DIAGNOSED — kein Code geändert  
**Autor:** Claude Code Diagnostic Pass  

---

## 1. Bug Summary

Nach Logout und erneutem Login sind alle vorherigen Chat-Sessions aus der Sidebar verschwunden.
Die Sessions existieren in der DB (`negotiation_sessions`), werden aber nicht geladen, weil
`useSessionManager` seinen `loadSessions()`-Effekt nur bei Änderung von `personaType` auslöst —
nicht bei Auth-State-Wechseln. Wenn der User sich mit denselben Credentials erneut einloggt,
bleibt `personaType` unverändert → kein Effekt → keine Daten.

---

## 2. Observed — direkt im Code sichtbar

### O-01 — Kein `GET /api/sessions`-Endpunkt (Liste) im Backend
**Datei:** `negotiationcoach-backend/src/api/sessionRoutes.ts` (gesamte Datei)  
**Datei:** `shared-context/docs/contracts/frontend-backend.md:341–343`  
Der API-Katalog listet `POST /api/sessions`, `PATCH /api/sessions/:id`, `POST /api/sessions/:id/messages`.  
`GET /api/sessions` (Session-**Liste**) ist **nicht dokumentiert und nicht implementiert**.  
Sessions werden ausschließlich direkt via Supabase-Client geladen — Verletzung von ADR-002.

### O-02 — Session-Load via direktem Supabase-Call, nicht via Backend-API
**Datei:** `useSessionManager.ts:29–38`
```typescript
const { data: { session: authSessionLocal } } = await supabase.auth.getSession();
const userId = authSessionLocal?.user?.id;
if (!userId) return;
const { data, error } = await supabase
  .from("negotiation_sessions")
  .select("*")
  .eq("user_id", userId)
  .order("updated_at", { ascending: false });
```
`loadSessions()` ruft intern **noch einmal** `supabase.auth.getSession()` auf, nicht das aus
`useAuth()` übergebene Token. Kein Backend-Hop, kein `apiClient.ts`.

### O-03 — `loadSessions()` wird nur bei `personaType`-Änderung ausgelöst
**Datei:** `useSessionManager.ts:46–50`
```typescript
useEffect(() => {
  if (personaType && personaType !== "private") {
    loadSessions();
  }
}, [personaType, loadSessions]);
```
Der Effekt hat **keine Auth-bezogene Dependency**: kein `user`, kein `authSession`,
kein `session`. Nach Re-Login mit identischem Account bleibt `personaType` unverändert →
React erkennt keine Änderung → Effekt feuert nicht → `loadSessions()` wird nicht aufgerufen.

### O-04 — `persona` wird bei Logout nicht zurückgesetzt
**Datei:** `Index.tsx:183–205`
```typescript
useEffect(() => {
  if (!user) return;          // ← kein setSessions([]) oder setPersona(null) vor return
  // loadProfile() ...
  setPersona(config);
}, [user]);
```
Wenn `user` auf `null` wechselt (Logout), springt der Effekt mit `return` raus.
`persona` (und damit `personaType`) behält seinen alten Wert.

### O-05 — `persona` wird zusätzlich aus localStorage geladen
**Datei:** `Index.tsx:33, 62–63`
```typescript
const PERSONA_KEY = "negotiation_coach_persona";
const [persona, setPersona] = useState<PersonaConfig | null>(loadPersona);
```
`loadPersona` liest bei Init aus `localStorage`. Auch nach Logout ist `persona` daher sofort
gesetzt — bevor `user` verfügbar ist. Nach Login bleibt der localStorage-Wert identisch →
`setPersona(config)` schreibt denselben Wert → kein State-Change → kein Effekt.

### O-06 — Silent failure bei fehlendem `userId` in `loadSessions()`
**Datei:** `useSessionManager.ts:31`
```typescript
if (!userId) return;  // kein console.error(), kein toast, kein Log
```
Falls `getSession()` beim ersten Load kein Token liefert, bricht die Funktion lautlos ab.
Nutzer sieht leere Liste ohne Fehlermeldung.

### O-07 — Supabase-Fehler in `loadSessions()` werden still geschluckt
**Datei:** `useSessionManager.ts:40–43`
```typescript
if (!error && data) {
  setSessions(data as Session[]);
}
setIsLoadingSessions(false);
// ← kein else, kein console.error(), kein toast.error()
```
Kontrast zu `createSession` / `archiveSession`, die beide `toast.error()` aufrufen.
RFB-014 beschreibt dasselbe fire-and-forget-Muster für `saveMessage`.

### O-08 — `authSession` aus `useAuth()` wird in `useSessionManager` nicht für Session-Load genutzt
**Datei:** `useSessionManager.ts:25, 54, 88, 140`  
`const { session: authSession } = useAuth()` wird importiert.  
Es wird für `createSession`, `saveMessage`, `archiveSession` als Token-Quelle verwendet,  
**aber nicht in `loadSessions()`** (Z. 28–44). Dort wird intern `supabase.auth.getSession()` aufgerufen.

---

## 3. Inferred — aus Kontext erschlossen

### I-01 — Auth-State-Chain: Login erreicht `useSessionManager` zu spät oder gar nicht
**Basis:** O-03, O-04, O-05  
Chain nach Login:  
`supabase.signIn()` → `onAuthStateChange(SIGNED_IN)` → `setUser(user)` → `useEffect([user])`
→ `loadProfile()` → `setPersona(config)` → `useSessionManager`-Effekt `[personaType]`  

Falls `personaType` identisch mit dem localStorage-Wert: **kein Re-Render von `useSessionManager`**.

### I-02 — Race Condition: `getSession()` in `loadSessions()` kann vor Token-Settlement feuern
**Basis:** O-02, `useAuth.tsx:25–45`  
`onAuthStateChange` setzt `user`/`session` synchron. Wenn danach `personaType` sich ändert
und `loadSessions()` aufgerufen wird, kann `supabase.auth.getSession()` einen Augenblick vor
dem vollständigen Token-Refresh feuern — besonders bei Token-Refresh-Flows.

### I-03 — `personaType !== "private"` Gate blockiert möglicherweise laden für free-Accounts
**Basis:** `useSessionManager.ts:47`  
Accounts mit `personaType = "private"` laden **nie** Sessions. Falls ein Account nach
Supabase-Migration zeitweise ohne gültiges Profil ist und `private` gesetzt wird, sind
Sessions dauerhaft unsichtbar — ohne Fehler.

---

## 4. Missing — fehlende Information für vollständige Diagnose

### M-01 — Kein Observability: Was passiert im Network Tab bei Login?
Unklar, ob und mit welchem HTTP-Status ein Session-Load-Request nach Re-Login abgesendet wird.
Ein direkter Supabase-Call ist im Network Tab sichtbar als `POST /rest/v1/negotiation_sessions?select=*`.
Ob dieser Call nach Re-Login gesendet wird, ist nicht durch Code-Lesen verifizierbar — muss live getestet werden.

### M-02 — Wert von `personaType` vor und nach Re-Login
Unklar, ob localStorage nach Re-Login denselben Wert wie beim ersten Login hat.
Wenn das Konto `persona_type = "kmu"` hat und dieser Wert auch in localStorage liegt,
ist die Kette O-05 → I-01 der exakte Bug-Pfad. Noch nicht live verifiziert.

### M-03 — Verhalten bei erstem Login (ohne localStorage-Eintrag) vs. Re-Login
Es ist unklar, ob der Bug nur bei Re-Login auftritt oder auch bei allerersten Logins mit
leerem localStorage. Unterschied würde helfen, O-05 als primären Trigger zu bestätigen.

---

## 5. Root Cause Hypothesis (Proposed)

**Primär:** `useSessionManager.ts:46–50` — Dependency-Array `[personaType, loadSessions]` enthält
keine Auth-bezogene Variable. Nach Re-Login mit identischem Account ändert sich `personaType`
nicht (weil localStorage denselben Wert enthält, den `setPersona()` setzen würde) →
React-Effekt feuert nicht → `loadSessions()` wird nie aufgerufen.

**Verstärkt durch:** `Index.tsx:184` — `if (!user) return` leert `persona` nicht bei Logout.
Damit ändert sich `personaType` nie → Effekt feuert auch beim nächsten Login nicht.

**Sekundär:** O-06, O-07 — Silent failures maskieren Lade-Fehler und erschweren Diagnose.

---

## 6. Files Involved (read-only)

| Datei | Relevanz |
|---|---|
| `negotiation-buddy/src/hooks/useSessionManager.ts` | Root Cause (Z. 46–50, 28–44) |
| `negotiation-buddy/src/hooks/useAuth.tsx` | Auth-State-Lieferant (Z. 25–45) |
| `negotiation-buddy/src/pages/Index.tsx` | Persona-Load-Effekt (Z. 183–205); `personaType`-Übergabe (Z. 255) |
| `negotiationcoach-backend/src/api/sessionRoutes.ts` | Kein GET-Sessions-Endpoint (Beleg O-01) |
| `shared-context/docs/contracts/frontend-backend.md:341–343` | API-Katalog ohne Session-Liste |
| `shared-context/docs/audits/refactor-backlog.md:765–803` | RFB-014 (fire-and-forget) |

---

## 7. ADR / Contract Implications

| Ref | Implikation |
|---|---|
| **ADR-002** (Session Ownership) | `loadSessions()` liest direkt aus Supabase — kein Backend-Hop. Verletzt ADR-002 (Backend kanonisch). Session-Listing wäre ein neuer Endpunkt `GET /api/sessions`. |
| **frontend-backend.md:341** | `GET /api/sessions` (Liste) fehlt im Kontrakt und im Backend. Vor Implementierung muss Kontrakt erweitert werden. |
| **RFB-014** | Fire-and-forget gilt laut Backlog für `saveMessage`, ist aber auch in `loadSessions()` vorhanden (O-07). Scope von RFB-014 sollte auf `loadSessions` ausgeweitet werden. |
| **RFB-004-C** | Nicht direkt betroffen, aber derselbe technische Schulden-Cluster. |

---

## 8. Risks if Left Unfixed

| Risiko | Schwere |
|---|---|
| Nutzer sehen nach Re-Login leere Session-Liste — verlieren scheinbar alle Daten | P1 — Vertrauensverlust |
| Silent failure: Nutzer wird nicht informiert, wenn Session-Load fehlschlägt | P2 — Diagnoseproblem |
| Sessions bleiben bei Supabase-Token-Problem dauerhaft unsichtbar, ohne Fehlerhinweis | P2 |
| ADR-002-Verletzung: direkter Supabase-Call umgeht Server-Side-Ownership-Prüfung | Architektur-Schuld |

---

## 9. Recommended Fix Scope (Proposed — nicht implementieren)

**Minimal (2 Dateien, behebt den Bug):**

**`useSessionManager.ts`:**
1. `authSession` (aus `useAuth()`) als Dependency in den `loadSessions()`-Effekt aufnehmen:
   `}, [personaType, authSession, loadSessions]);`
2. `loadSessions()` intern auf `authSession?.user?.id` statt `supabase.auth.getSession()` umstellen.
3. Error-Logging bei leerem `userId` und bei Supabase-Fehler hinzufügen (`console.error` / `toast.error`).

**`Index.tsx`:**
4. Im `[user]`-Effekt bei `!user`: `setPersona(null)` aufrufen, damit `personaType` sich ändert
   und beim nächsten Login der `loadSessions()`-Effekt sicher feuert.

**Nicht in diesem Fix:**
- ADR-002-Compliance (Backend `GET /api/sessions`) — separate Breaking-Change, eigenes Ticket
- RFB-014-Scope-Erweiterung — separate Refactor-Aufgabe

---

## 10. Acceptance Criteria — Bewertung

| Kriterium | Prüfbar? | Bewertung |
|---|---|---|
| `npx tsc --noEmit` clean | ✅ Ja | Standardprüfung, im Frontend-Repo ausführbar |
| curl `GET /api/sessions` → Sessions sichtbar | ❌ Nicht anwendbar | Endpunkt existiert nicht — kein curl-Test möglich vor Implementierung |
| Layer-1-Tests grün | ⚠️ Eingeschränkt | Backend hat keine spezifischen Session-Manager-Tests; kein direkter Testpfad für useSessionManager |
| Session nach Logout + Re-Login sichtbar | ✅ Manuell prüfbar | Smoke-Test: Login → Session starten → Logout → Login → Sessions sichtbar |
| Network Tab: `POST /rest/v1/negotiation_sessions?select=*` nach Re-Login sichtbar | ✅ Ja | Browser DevTools Network Tab nach Login prüfen |

**Empfehlung:** Acceptance Criteria 2 (`curl`) durch manuellen Smoke-Test ersetzen,
da kein Backend-Endpunkt existiert. Layer-1-Tests sind kein valides Gate für diesen Bug.
