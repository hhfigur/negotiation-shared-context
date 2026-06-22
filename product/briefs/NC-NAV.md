# Delivery Brief: NC-NAV
## Navigation & Tier-Struktur Redesign

**Release:** TBD (R-2026-10 kandidiert)
**Status:** In Delivery
**Affected repos:** negotiation-buddy (primary), shared-context (docs)
**Tier impact:** alle
**Created:** 2026-06-19
**Priority:** P1 — Gastmodus erzeugt Token-Kosten ohne Umsatz; Tier-Gating inkohärent

---

## Goal / Outcome

- Kein Gastmodus mehr — App-Zugang erfordert Login + aktives Abo
- `subscription_tier` ist das einzige Gate für Feature-Sichtbarkeit (nicht mehr `persona_type`)
- Alle Tiers bekommen dieselbe Sidebar-Struktur (inkl. Profi)
- Mobile: Bottom Tab Bar (Chat | Tools | Profil)
- Landing Page: statische Demo-Sektion (kein API-Call)
- OnboardingDialog entfernt — Profil-Einstellungen nur unter /profile
- `/profile` zeigt Abo-Status + Dev-Tier-Mock (nur wenn `VITE_DEV_TIER_MOCK=true`)

---

## Entscheidungen (aus Planning-Session 2026-06-19)

- **Kein Free Tier in der App**: `subscription_tier = 'free'` → Redirect auf Landing Page
- **Tier = Persona (automatisch)**: Privat → privat-Modus, KMU → kmu-Modus, Profi → alles
- **Nur sichtbar was nutzbar ist**: keine Badges für gesperrte Features, keine Upgrade-Dialoge in der Navigation
- **Upgrade-CTA nur in /profile**: Abo-Status + Link zum Upgrade
- **OnboardingDialog entfernt**: kein Popup beim ersten Start
- **ADR-006**: `free` bleibt als DB-Enum-Wert — wird als "kein Zugang" behandelt (Redirect), nicht gelöscht
- **ADR-008**: Navigation-Events in Telemetrie aufnehmen (nicht blockend)

---

## Feature-Sichtbarkeit nach Tier

| Feature | Privat | KMU | Profi |
|---|:---:|:---:|:---:|
| Chat + Guided Flow | ✅ | ✅ | ✅ |
| ZOPA-Rechner | ✅ | ✅ | ✅ |
| Canvas (Direkteingabe) | ✅ | ✅ | ✅ |
| Sessions speichern + Liste | ✅ | ✅ | ✅ |
| Strategie-Score | ✅ | ✅ | ✅ |
| Debrief-Dashboard | ✅ | ✅ | ✅ |
| Marktdaten (L2) | ❌ | ✅ | ✅ |
| What-If Simulator | ❌ | ❌ | ✅ |
| ModeSelector (4 Modi) | ❌ | ❌ | ✅ |
| Team-Dashboard | ❌ | ❌ | ✅ |

---

## Phasen

### Phase A — Auth-Gate + Tier-Gating (P1, diese Lieferung)

**A-1: Gastmodus entfernen**
- `isGuest`-Logik in Index.tsx (~15 Stellen) entfernen
- `ProtectedRoute` in App.tsx: `subscription_tier = 'free'` → Redirect auf `/` (Landing)
- CoachHeader + DrawerMenu: Gast-Badge, Login-Button, "Account erstellen"-Link entfernen
- `guestPromptShown`-State + Gast-Migration-Effect in Index.tsx entfernen

**A-2: subscription_tier als primäres Gate**
- `showSessionFeatures`-Logik auf `subscription_tier !== 'free'` umstellen (alle tiers haben Sessions)
- SessionSidebar: Profi-Unterstützung aktivieren (bisher nur kmu/private)
- ModeSelector: nur bei `subscription_tier === 'profi'` anzeigen
- SessionSidebar Tools: nur tier-erlaubte Tools anzeigen (keine Badges für gesperrte)

**A-3: OnboardingDialog entfernen**
- `OnboardingDialog.tsx` aus Index.tsx entfernen
- `showOnboarding`-State entfernen
- Erste-Login-User landen direkt im Chat (kein Popup)
- Persona aus `user_profiles.subscription_tier` ableiten (nicht aus localStorage `negotiation_coach_persona`)

### Phase B — Profi Sidebar (P1)

- SessionSidebar für Profi-Tier aktivieren
- Team-Dashboard-Link in Sidebar (nur Profi)
- Sidebar-Tools: tier-abhängig ohne Badges (gesperrte = unsichtbar)

### Phase C — Mobile Bottom Tab Bar (P2)

- Neue `BottomTabBar.tsx`-Komponente: Chat | Tools | Profil
- Nur auf Mobile (< md) sichtbar
- Tab "Tools": tier-abhängige Tool-Liste
- Tab "Profil": Link zu /profile

### Phase D — /profile Überarbeitung (P2)

- Abo-Status anzeigen (aktueller Tier + Upgrade-CTA)
- `VITE_DEV_TIER_MOCK=true`: Dropdown "Tier simulieren" (setzt localStorage + DB)
- Persona-Auswahl entfernen (wird von Tier abgeleitet)
- Account-Sektion (E-Mail, Passwort)

### Phase E — Landing Page Demo-Sektion (P2)

- Statische Demo-Sektion auf Landing (`/`)
- Beispiel-Analyse (kein echter API-Call)
- CTA: "Jetzt Abo abschließen → starten"

---

## Acceptance Criteria

- AC-1: User mit `subscription_tier = 'free'` wird auf `/` redirected (kein App-Zugang)
- AC-2: User mit `subscription_tier = 'privat'` sieht keine Market-Data- oder What-If-Links
- AC-3: User mit `subscription_tier = 'kmu'` sieht Marktdaten-Tool, aber kein What-If
- AC-4: User mit `subscription_tier = 'profi'` sieht alle Tools + ModeSelector + Team
- AC-5: Kein OnboardingDialog erscheint mehr (für keinen User)
- AC-6: Profi hat Sidebar auf Desktop
- AC-7: TypeCheck negotiation-buddy: 0 Fehler
- AC-8: Render-Log: keine Regression in /api/analyze oder /api/chat

---

## Nicht in Scope

- Stripe-Integration (AR-032, extern blockiert)
- Server-seitige Tier-Enforcement-Hardening (eigenes Security-Item)
- Komplette Neuarchitektur von Index.tsx

---

## Phase B — Implement

**Status:** Done
**Date:** 2026-06-22
**Commit:** 237aee7 (negotiation-buddy)

**Delivered:** Team-Dashboard-Link `{ marker: "06", label: "Team", route: "/team", badge: "Profi" }` in TOOLS-Array von SessionSidebar.tsx eingefügt. Bestehende visibleTools-Filterlogik aus Phase A handled Sichtbarkeit automatisch (nur profi). tsc clean.

---

## Phase C — Implement

**Status:** Done
**Date:** 2026-06-22
**Commit:** ff03384 (negotiation-buddy)

**Delivered:**
- `BottomTabBar.tsx` neu erstellt — 3 Tabs (Chat/Tools/Profil), md:hidden, fixed bottom-0 z-50
- Tools-Tab öffnet Sheet mit tier-gefilterter Tool-Liste (gleiche Logik wie SessionSidebar)
- In App.tsx eingehängt (neben ConsentBanner, innerhalb BrowserRouter)
- BottomBar in Index.tsx in `hidden md:block` gewrappt — auf Mobile durch BottomTabBar ersetzt
- tsc clean, kein Subagent nötig (Scope war direkt implementierbar)

**Bekannte Limitation:** TOOLS-Array in BottomTabBar.tsx ist eine Kopie von SessionSidebar.tsx (non-blocking, für Phase D oder separates Refactor-Item adressieren).

---

## Phase D — Implement

**Status:** Done
**Date:** 2026-06-22
**Commit:** faf5975 (negotiation-buddy)

**Delivered:**
- Persona-Auswahl (PERSONAS-Buttons) entfernt — Tier bestimmt Persona automatisch via `tierToPersonaType()`
- Abo-Status-Card (§I): zeigt aktuellen Tier + Beschreibung + Upgrade-CTA (Link auf /)
- Dev-Tier-Mock (§DEV): nur wenn `VITE_DEV_TIER_MOCK=true` — 3 Buttons (privat/kmu/profi), schreibt localStorage + DB
- Account-Sektion (§IV): zeigt E-Mail (read-only) + Passwort-Ändern-Link → /forgot-password
- **Kritischer Bug gefixt**: `handleSave` schrieb `subscription_tier: "free"` hardcoded → würde nach Phase A jeden User auslockieren. Fix: liest echten Tier aus DB, persistiert ihn korrekt.
- DB-Query erweitert: `subscription_tier` wird jetzt aus `user_profiles` geladen
- tsc clean

---

## Phase E — Implement

**Status:** Done
**Date:** 2026-06-22
**Commit:** 42c6fc7 (negotiation-buddy)

**Delivered:**
- `DemoSection` in Landing.tsx: statische Beispielanalyse (Chat + Ergebnis-Split)
  Gehaltsverhandlung-Szenario mit ZOPA/Nash/BATNA, Eröffnungssatz, Marktdaten-Badge (KMU/Profi),
  Strategie-Score, CTA "Jetzt Abo abschließen → Starten" → /auth
- TierTable: FREI-Tier entfernt — 3 Tiers: Privat 12€ / KMU 49€ / Profi 99€
  Feature-Matrix aktualisiert (Marktdaten ab KMU, What-If/Team ab Profi)
  CTA-Buttons: ?plan=privat / ?plan=kmu / ?plan=profi
- tsc: 0 Fehler

**Open Decision:** statisch oder mock API-Call? → aufgelöst: statisch (kein API-Call, wie im Brief)

---

## Phase A — Implement

**Status:** Done  
**Date:** 2026-06-22  
**Commits:** 74903b3, 847aa79 (repo: negotiation-buddy, branch: main)

**Delivered:**
- A-1: Guest mode removed from Index.tsx, CoachHeader, DrawerMenu, ChatWindow. ProtectedRoute gates `subscription_tier === 'free'` → redirect `/`. Cold-start fix: localStorage absent → let through (not redirect).
- A-2: `showSessionFeatures` uses `subscription_tier !== 'free'`. SessionSidebar filters tools by tier (privat hides Marktdaten + What-If; kmu hides What-If; profi sees all). Badge display removed. ModeSelector gated to profi only.
- A-3: OnboardingDialog removed from Index.tsx JSX. `showOnboarding` state and `handleOnboardingComplete` handler removed. File kept as type source.

**TypeScript:** 0 errors  
**Spec review:** ✅ compliant  
**Code quality:** Approved (1 critical + 1 important fixed in second commit)
