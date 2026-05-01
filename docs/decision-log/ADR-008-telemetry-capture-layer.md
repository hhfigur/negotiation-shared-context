# ADR-008 — Telemetrie Capture-Layer: PostHog Cloud EU

**Status:** DECIDED
**Datum:** 2026-05-01
**Entscheider:** Maik
**Klassifizierung:** Architecture Decision — Analytics & Observability

## Kontext

NC-TELEMETRY A+B haben console.log-basierte Events eingeführt
(analyze_completed Backend, tool_opened Frontend). console.log ist
ephemer — nicht aggregiert, nicht abfragbar, keine Baselines möglich.

Um metrics.md befüllen und NC-ONBOARDING unblockieren zu können,
wird ein persistenter Capture-Layer benötigt.

## Entscheidung

**PostHog Cloud EU** ist der kanonische Analytics-Layer für NegotiationCoach AI.

## Optionen bewertet

| Option | Entscheidung | Begründung |
|--------|-------------|------------|
| PostHog Cloud EU | ✅ GEWÄHLT | Free bis 1M Events/Monat, React+Node SDK, EU-Region, DSGVO-konform |
| Self-Hosted PostHog | ❌ | Zu hoher Ops-Aufwand für aktuelles Volumen |
| Custom /api/telemetry | ❌ | Kein Dashboard, hoher Eigenaufwand |
| Render Log-Drain | ❌ | Nur Backend, kein Frontend, ephemer |
| Sentry | ❌ als alleinige Option | Error-Tracking, kein Event-Analytics |

## Implementierung

**Backend (negotiationcoach-backend):**
- src/services/telemetry.ts — PostHog Node Client, trackEvent(), shutdownTelemetry()
- Env-Variablen: POSTHOG_API_KEY, POSTHOG_HOST (Render.com)
- Event: analyze_completed (tier, negotiation_type, zopa_exists, strategy_score)

**Frontend (negotiation-buddy):**
- src/lib/telemetry.ts — posthog-js, initTelemetry(), trackEvent(), setConsent()
- src/components/ConsentBanner.tsx — Consent-Banner, persistiert in localStorage
- Env-Variablen: VITE_POSTHOG_API_KEY, VITE_POSTHOG_HOST (Lovable Build Secrets)
- Events: tool_opened (5× Tool-Pages, useRef-Guard gegen Doppel-Trigger)

## DSGVO-Rationale

- Kein PII in Events: nur Enum-Werte (tier, negotiation_type) und boolean/number
- Kein Freitext aus Verhandlungen
- EU-Region: Daten verlassen EU nicht
- Consent-Banner: aktiv — User muss explizit akzeptieren
- persistence: 'memory' — kein persistenter Cookie ohne Consent
- autocapture: false — nur explizite trackEvent()-Calls

## Konsequenzen

- PostHog Cloud EU ist neue externe Service-Abhängigkeit
- VITE_POSTHOG_API_KEY muss als Lovable Build Secret gesetzt werden
- Ohne Key: kein Crash, keine Events (Early-Return in initTelemetry)
- session_started / chat_flow_completed: noch nicht verkabelt —
  Insertion-Punkte im Repo vorhanden, separates GO erforderlich
- Nach 14 Tagen mit gesetztem Key: metrics.md Baselines befüllbar
- NC-ONBOARDING unblockiert sobald Baselines vorliegen

## Referenzen

- NC-TELEMETRY-A: cec6af7 (Backend console.log → PostHog)
- NC-TELEMETRY-B: 5b66bfc (Frontend Events, Lovable)
- NC-TELEMETRY-C Backend: cec6af7
- NC-TELEMETRY-C Frontend: Lovable-intern (kein Hash verfügbar)
