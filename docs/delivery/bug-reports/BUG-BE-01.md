# BUG-BE-01 — Railway /api/chat gibt 500 bei extractedInputs-Extraktion

**Entdeckt:** 2026-04-21 (Live-Test)
**Status:** OPEN — Neuansatz beschlossen 2026-04-22
**Klassifikation:** P0 — Core Data Flow broken
**Repos:** negotiationcoach-backend, negotiation-buddy

## Symptome
- POST /api/chat gibt 500 zurück
- extractedInputs ist nach jedem Chat-Turn undefined in localStorage
- ZOPA-Rechner, What-If Simulator und Strategie erhalten keine Chat-Daten
- Fehlermeldung: "This model does not support assistant message prefill"
  (trailing assistant message) — Fix 2b6fe03 hat Fehler nicht behoben
- Zweiter Fehler aus Logs: "inputs column not found in negotiation_sessions"

## Neuansatz-Entscheidung (2026-04-22)
Railway /api/chat als Extraktions-Pfad wird aufgegeben.
Stattdessen: extractedInputs direkt aus Edge Function /negotiate streamen.
Die EF ist der primäre Chat-Pfad (SSE) — sie soll extractedInputs
als finales JSON-Objekt am Ende des Streams zurückgeben.
useChat.ts parst diesen Block und schreibt in AnalysisContext.

## Offene Fixes (vor Neuansatz)
- inputs-Spalte in negotiation_sessions: grep und entfernen (separates Item)

## Abhängigkeiten
- RFB-039 (Context-Verlust bei Navigation) — verwandt
- RFB-040 (What-If Slider) — nach Neuansatz angehen
