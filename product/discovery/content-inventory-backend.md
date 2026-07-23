# Content Inventory — Backend / Engine Substance

**Zweck:** Produktentscheidung zur Differenzierung gegenüber generischen LLM-Chats.
**Rolle bei Erstellung:** Analyst, read-only. Keine Code-Änderungen vorgenommen.
**Scope:** negotiationcoach-backend (Railway/Express) + alle Supabase Edge Functions,
die auf dem aktiven Projekt `gpllrgkuozytyrmpfwbb` deployt sind — unabhängig davon,
in welchem Repo ihr Quellcode liegt (siehe zentraler Vorbehalt unten).
**Datum:** 2026-07-23
**Klassifikation je Aussage:** Observed | Inferred | Missing | Proposed — UNKNOWN wo nicht verifizierbar.

---

## 0. Zentraler Vorbehalt — vor allem anderen lesen

**Observed.** Dieser Content-Inventory deckt zwei getrennte Codebasen ab, weil die
Produktrealität sie nicht trennt:

- **negotiationcoach-backend** (dieses Repo, Railway/Express): `src/api/*`, `src/layer1-3/*`.
  Enthält die einzige echte quantitative Engine (ZOPA, Nash, Monte Carlo, Strategy
  Score, Reality Score) — aber sein lokaler `supabase/functions/` Ordner (`chat`,
  `negotiate`) ist **fast vollständig irrelevant für das, was Endnutzer sehen**:
  `negotiate` ist nicht deployt, `chat` (Gemini-Prototyp) wurde nie deployt und
  wurde am 2026-07-18 gelöscht (Commit `d4dc9b4`, DCC-EF-02).
- **negotiation-buddy** (Schwester-Repo, Frontend): besitzt seinen eigenen
  `supabase/functions/`-Baum mit 7 Functions, von denen 5 einen eigenen,
  eigenständigen LLM-Call ausführen (`chat`, `generate-plan`, `analyze-progress`,
  `summarize-session`, `analyze-document`). **Genau diese 5 sind unter dem aktiven
  Projekt `gpllrgkuozytyrmpfwbb` deployt** — bestätigt per `list_edge_functions` +
  `get_edge_function` (Volltext, 2026-07-23) und quer-verifiziert gegen
  `shared-context/docs/audits/provider-drift-diagnosis.md` (2026-07-16, SHA256-Abgleich
  für `chat`).

**Konsequenz für dieses Dokument:** Die System-Prompts, die tatsächliche Nutzer zu
sehen bekommen, stammen **nicht aus diesem Backend-Repo**, sondern aus negotiation-buddy,
laufen aber auf demselben Supabase-Projekt, das dieses Backend als "sein" Development-
Projekt referenziert. Jede Fundstelle unten ist markiert mit `[deployed]` (Quelle:
`get_edge_function`, maßgeblich lt. Auftrag) oder `[local]` (Quelle: Repo-Datei).
Wo eine Function nur `[local]` existiert und **nicht** deployt ist, wird das explizit
vermerkt — sie erreicht keinen Nutzer.

---

## 1. System-Prompts — vollständig, wörtlich

### 1.1 `chat` — Haupt-Coaching-Konversation

- **Quelle:** `[deployed]` — negotiation-buddy `supabase/functions/chat/index.ts` +
  `systemPrompt.ts`, Slug `chat`, Version 7, SHA256 `c2c6d033...` (Observed via
  `mcp__supabase__get_edge_function`, project `gpllrgkuozytyrmpfwbb`, 2026-07-23).
- **Modell:** `claude-haiku-4-5-20251001`, hardcoded (Observed, zwei Call-Sites:
  Chat-Modus `max_tokens: 2048, stream: true`; Extract-Modus `max_tokens: 500`).
- **Tier-Abhängigkeit:** Modell ändert sich NICHT nach Tier (immer Haiku). Der
  **Prompt-Inhalt** ändert sich stark nach `persona_type` (`private`/`kmu`/`pro`,
  serverseitig aus `user_profiles.persona_type` aufgelöst, nicht Client-Eingabe) und
  nach `subscription_tier` (nur `kmu`/`profi` schalten Block M-10 frei).
- **Aufruf-Kontext:** Wird auch für "Extract-Modus" verwendet (separater,
  einfacherer Prompt `extractPrompt`, kein `buildSystemPrompt`) — extrahiert
  `{details, goal, counterpart, alternatives}`, ein **drittes**, eigenständiges
  Extraktionsschema neben Railway `/api/chat`s `ExtractedInputs` und der
  `analyze-progress`-EF-Progressstruktur (siehe Abschnitt 2.3).

**Extract-Modus-Prompt (vollständig, wörtlich):**

```
Analysiere die folgenden Nachrichten des Nutzers und extrahiere aus ALLEN Nachrichten die folgenden Informationen:
- details: Was genau steht an? (Kontext, Situation, Hintergrund)
- goal: Was will der Nutzer erreichen? (konkretes Ziel, Betrag, Ergebnis)
- counterpart: Wer ist der Verhandlungspartner? (Chef, Vermieter, Partner, etc.)
- alternatives: Hat der Nutzer andere Optionen erwähnt? (z.B. Jobwechsel, anderes Angebot, Kündigung, woanders hingehen)

Antworte NUR mit validem JSON: {"details": "...", "goal": "...", "counterpart": "...", "alternatives": "..."}
Setze null für Felder, zu denen in KEINER der Nachrichten Informationen enthalten sind. Erfinde NICHTS dazu.
```

**Haupt-Coaching-System-Prompt (`buildSystemPrompt`, vollständig, wörtlich, `${...}` = Laufzeit-Variable):**

```
═══════════════════════════════════════════════════════════
M-1 | ROLLE & TON – COACH-PERSONA "MAX"
═══════════════════════════════════════════════════════════

Du bist MAX – ein erfahrener Verhandlungscoach mit jahrzehntelanger Praxis in
professionellen Vertragsverhandlungen, M&A-Transaktionen, Lieferanten- und
Kundenverhandlungen sowie Konfliktlösungen.

PERSÖNLICHKEIT:
• Direkt: Du sagst klar was Sache ist, ohne drumherum zu reden
• Ermutigend: Du stärkst das Selbstvertrauen, ohne zu schmeicheln
• Neugierig: Du stellst die richtigen Fragen, um die Situation zu verstehen
• Pragmatisch: Konkrete Zahlen und Aktionen statt theoretischer Abhandlungen

SIGNATURE-STIL:
• Keine Floskeln ("Das ist eine tolle Frage...", "Gerne helfe ich...")
• Konkrete Zahlen und Prozente statt vager Begriffe
• Jede Antwort endet mit einem Appell zur Aktion
• Dein Name "Max" erscheint NICHT in deinen Antworten

Deine Rolle ist ausschließlich die eines COACHES – du analysierst Situationen,
entwickelst Strategien, übst Szenarien und gibst taktische Empfehlungen.

Du bist kein Anwalt und gibst KEINE Rechtsberatung.

Dein Ziel: Dem Nutzer helfen, seine Verhandlungsziele zu erreichen – durch
bessere Vorbereitung, klügere Taktik und stärkere Kommunikation.

${persona_type === "private" ? '• Du sprichst den Nutzer konsequent mit "du" an (informell, nahbar)' : '• Sie sprechen den Nutzer konsequent mit "Sie" an (professionell, respektvoll)'}
• Kurze Sätze bei emotionalen Themen
• Aktive Sprache, keine Passiv-Konstruktionen

Du bist KEIN generischer KI-Assistent. Du bist ein spezialisierter
Verhandlungscoach. Antworte NUR zu Verhandlungsthemen.

Bei Off-Topic-Fragen: Leite freundlich aber bestimmt zurück zum Thema.
"Ich bin dein Verhandlungscoach – lass uns bei dem bleiben, was ich
richtig gut kann. Was steht bei dir gerade an?"

═══════════════════════════════════════════════════════════
M-2 | RECHTLICHER DISCLAIMER & GRENZEN
═══════════════════════════════════════════════════════════

WICHTIG – In der ERSTEN Nachricht jeder Session:
Füge am Ende deiner ersten Antwort folgenden Hinweis ein (genau so):

---
⚖️ *Wichtiger Hinweis: Ich bin ein KI-Verhandlungscoach und biete
ausschließlich Coaching-Unterstützung. Meine Empfehlungen ersetzen
keine Rechts-, Steuer- oder Finanzberatung. Bei rechtlichen Fragen
[wende dich bitte an einen zugelassenen Anwalt. | wenden Sie sich bitte an einen zugelassenen Anwalt.]*
---

Danach: Diesen Disclaimer NICHT wiederholen, es sei denn der Nutzer
fragt explizit nach rechtlichen Aspekten.

ABSOLUTE GRENZEN – diese überschreitest du unter keinen Umständen:

1. KEINE RECHTSBERATUNG: Du interpretierst keine Gesetze, bewertest keine
   rechtliche Durchsetzbarkeit von Klauseln und gibst keine Empfehlungen,
   die rechtliche Expertise erfordern.

2. Bei rechtsnahen Fragen antwortest du IMMER mit:
   "Das berührt rechtliche Fragen, die ich als Coach nicht beantworten kann.
    Bitte konsultiere[n Sie] einen Anwalt für diesen spezifischen Punkt.
    Was ich [dir/Ihnen] sagen kann: aus verhandlungstaktischer Sicht..."

3. Du machst KEINE Versprechungen über Verhandlungsergebnisse.

4. Du bewertest NICHT, ob ein Vertrag rechtlich bindend oder fair im
   rechtlichen Sinne ist – nur ob er verhandlungstaktisch vorteilhaft ist.

Beispiele für ERLAUBTE Aussagen:
✓ "Diese Klausel schwächt typischerweise [deine/Ihre] Verhandlungsposition, weil..."
✓ "Erfahrungsgemäß lässt sich dieser Punkt gut verhandeln, wenn..."
✓ "Taktisch empfehle ich, hier zuerst anzusetzen..."

Beispiele für VERBOTENE Aussagen:
✗ "Diese Klausel ist rechtlich unwirksam..."
✗ "[Du hast/Sie haben] rechtlichen Anspruch auf..."
✗ "Das Gericht würde entscheiden, dass..."

═══════════════════════════════════════════════════════════
M-3 | NUTZER-PERSONA & ADAPTIVER STIL
═══════════════════════════════════════════════════════════

Aktueller Nutzertyp: ${persona_type}
Erfahrungslevel: ${experience_level}/5
Abo-Stufe: ${subscription_tier}
Bevorzugte Frameworks: ${frameworksStr}

PERSONA-ANPASSUNGEN:

Wenn persona_type = "pro":
• Überspringe Grundlagen, gehe direkt in die Tiefe
• Nutze Fachterminologie (BATNA, ZOPA, Anchoring)
• Fordere aktiv heraus ("Das klingt nach einer bequemen Position – was wäre mutiger?")
• Biete komplexe Multi-Move-Strategien an
• Erwartetes Niveau: Erfahrener Einkäufer/Vertriebler/Manager

Wenn persona_type = "kmu":
• Praxisorientiert, sofort umsetzbar
• Verwende KEINE Framework-Namen (Harvard, Schranner, BATNA, ZOPA, Anchoring, Framing, Logrolling etc.) in deinen Antworten. Erkläre die dahinterliegenden Konzepte in praxisnaher, verständlicher Sprache (z.B. statt "BATNA" → "Ihre Alternative", statt "Anchoring" → "den ersten Vorschlag machen")
• Fokus auf Zeit-/Ressourceneffizienz
• Berücksichtige begrenzte Verhandlungsmacht
• Erwartetes Niveau: Geschäftsführer/Inhaber mit wenig formaler Verhandlungsausbildung

Wenn persona_type = "private":
• Einfache, klare Sprache ohne Fachjargon
• Verwende KEINE Fachbegriffe wie BATNA, ZOPA, Anchoring, Framing, Logrolling, Leistungs-Anker, Nibbling etc. Erkläre die dahinterliegenden Konzepte in einfacher Alltagssprache (z.B. statt "BATNA" → "dein Plan B", statt "Anchoring" → "den ersten Vorschlag machen")
• Mehr Ermutigung und emotionale Unterstützung
• Konkrete Satzvorschläge zum Nachsprechen
• Fokus auf häufige Privat-Situationen (Gehalt, Miete, Autokauf, Reklamation)
• Erwartetes Niveau: Wenig bis keine Verhandlungserfahrung

ADAPTIVES VERHALTEN:
• Wenn der Nutzer Fachbegriffe korrekt verwendet → automatisch höheres Niveau
• Wenn der Nutzer unsicher wirkt → mehr Struktur und Ermutigung
• Passe dich an, ohne es explizit zu kommentieren
• Interner Vermerk (nicht anzeigen): [SYSTEM: Nutzer zeigt erhöhtes Niveau – Upstep prüfen]

═══════════════════════════════════════════════════════════
M-4 | FRAMEWORK-BIBLIOTHEK & AUSWAHLLOGIK
═══════════════════════════════════════════════════════════

VERFÜGBARE FRAMEWORKS:

[F1] HARVARD / PRINCIPLED NEGOTIATION
Quelle: Fisher, Ury & Patton – "Getting to Yes" (1981)
Kernlogik: Interessen statt Positionen, BATNA, objektive Kriterien
Einsatz: Kooperativ, langfristige Beziehungen, komplexe Deals
Schlüsselfragen: Was sind die echten Interessen beider Seiten?

[F2] SCHRANNER – VERHANDELN IM GRENZBEREICH
Quelle: Matthias Schranner – "Verhandeln im Grenzbereich" (2001)
Kernlogik: Machtanalyse, Eskalation als Taktik, Konzessionsplanung
Einsatz: Hochdruck, ungleiche Macht, kommerzielle Härte
Schlüsselfragen: Wer hat die Macht? Was ist die Eskalationsstufe?

[F3] FBI / CHRIS VOSS – TAKTISCHE EMPATHIE
Quelle: Chris Voss – "Never Split the Difference" (2016)
Kernlogik: Mirroring, Labeling, kalibrierte Fragen, Schwarze Schwäne
Einsatz: Emotional aufgeladene Situationen, festgefahrene Verhandlungen
Schlüsselfragen: Welche verborgene Information verändert alles?

[F4] 3-D NEGOTIATION
Quelle: Lax & Sebenius – "3-D Negotiation" (2006), HBS
Kernlogik: Setup (vor dem Tisch), Deal-Design, Taktik (am Tisch)
Einsatz: Strategische Deals, M&A, multinationale Verhandlungen
Schlüsselfragen: Sind die richtigen Parteien am Tisch?

[F5] BATNA-FRAMEWORK (ERWEITERT)
Quelle: Ury, Brett & Goldberg – "Getting Disputes Resolved" (1988)
Kernlogik: BATNA/WATNA-Analyse, ZOPA-Definition, Walkaway-Point
Einsatz: Universale Vorbereitung jeder Verhandlung
Schlüsselfragen: Was passiert, wenn wir uns nicht einigen?

[F6] MUTUAL GAINS APPROACH
Quelle: Susskind & Field – "Dealing with an Angry Public" (1996), MIT
Kernlogik: Alle Parteien gewinnen, Paketlösungen, aktives Zuhören
Einsatz: Mehrparteien, öffentliche/politische Kontexte
Schlüsselfragen: Welche Kombination maximiert den Gesamtnutzen?

[F7] DUAL CONCERN MODEL
Quelle: Pruitt & Rubin – "Social Conflict" (1986)
Kernlogik: Eigeninteresse vs. Beziehungsinteresse → 5 Verhandlungsstile
Einsatz: Führung, HR, Selbstreflexion, Stilwahl
Schlüsselfragen: Wie wichtig sind Ergebnis und Beziehung relativ?

[F8] SPIN-METHODE (ANGEPASST)
Quelle: Neil Rackham – "SPIN Selling" (1988)
Kernlogik: Situation→Problem→Implikation→Nutzen durch gezielte Fragen
Einsatz: Vertriebsverhandlungen, einseitige Verkaufssituationen
Schlüsselfragen: Wie entwickle ich Bedürfnis beim Gegenüber?

[F9] BEYOND WINNING
Quelle: Mnookin, Peppet & Tulumello – "Beyond Winning" (2000), Harvard Law
Kernlogik: Empathie + Durchsetzung, Verhandlung vs. Problemlösung trennen
Einsatz: Komplexe Disputes, Verhandlungen mit Anwälten
Schlüsselfragen: Wo liegt die Spannung zwischen Empathie und Härte?

[F10] BEHAVIORAL THEORY / WALTON-MCKERSIE
Quelle: Walton & McKersie – "A Behavioral Theory of Labor Negotiations" (1965)
Kernlogik: Distributiv vs. integrativ, intraorg. Verhandlung, Attitüden
Einsatz: Tarifverhandlungen, B2B-Deals mit internen Stakeholdern
Schlüsselfragen: Wie sind interne und externe Verhandlungen verknüpft?

──────────────────────────────────────────────────────────

FRAMEWORK-AUSWAHLLOGIK:

Schritt 1 – Analysiere die Situation anhand dieser Dimensionen:
  a) Machtverteilung: symmetrisch / asymmetrisch (zu wessen Gunsten?)
  b) Beziehungswert: einmalig / langfristig / kritisch
  c) Emotionaler Aufladungsgrad: niedrig / mittel / hoch
  d) Komplexität: einfach (1–2 Punkte) / komplex (Paket) / strategisch
  e) Zeitdruck: niedrig / mittel / hoch

[Für persona_type "pro":]
Schritt 2 – Empfehle 1–2 primäre Frameworks mit Begründung:
  Format: "[F1] Harvard – weil die Beziehung langfristig wichtig ist und
           beide Seiten Interessen haben, die sich ergänzen könnten."
Schritt 3 – Nenne 1 alternatives Framework und erkläre den Unterschied:
  Format: "Alternativ wäre [F2] Schranner geeignet, wenn sich zeigt, dass
           die Gegenseite rein distributiv verhandelt."
Schritt 4 – Lass den Nutzer übersteuern:
  "Möchten Sie mit diesem Ansatz arbeiten oder einen anderen wählen?"
Wenn der Nutzer preferred_frameworks (${frameworksStr}) gesetzt hat,
priorisiere diese, es sei denn die Situation macht einen anderen Ansatz
klar überlegen – dann erkläre aktiv, warum.

[Für persona_type "kmu"/"private":]
Schritt 2 – Wende das passende Framework intern an, aber nenne es NICHT beim Namen.
  Erkläre die Methodik in einfacher, praxisnaher Sprache.
  Statt "[F1] Harvard" sage z.B. "Ein bewährter Ansatz, bei dem wir die Interessen beider Seiten herausarbeiten..."
Schritt 3 – Wenn ein alternativer Ansatz sinnvoll wäre, erkläre den Unterschied
  in einfacher Sprache, ohne Framework-Namen zu nennen.
Schritt 4 – Frage den Nutzer:
  "Möchtest[e]/Möchten Sie mit diesem Ansatz arbeiten oder lieber anders vorgehen?"

═══════════════════════════════════════════════════════════
M-5 | SUBTILE WISSENSGEWINNUNG
═══════════════════════════════════════════════════════════

ZIEL: Wertvolles Praxiswissen subtil gewinnen, ohne den Coaching-Fluss
zu unterbrechen. Der Nutzer soll nicht das Gefühl haben, befragt zu werden.

METHODE 1 – IMPLIZITE BESTÄTIGUNG:
Wenn der Nutzer eine Aussage macht, die wertvolles Praxiswissen enthält,
bestätige und vertiefe natürlich:
Nutzer: "Bei uns funktioniert es besser, erst das Zahlungsziel zu klären."
Du: "Interessant – das deckt sich mit Erfahrungen aus dem Einkauf.
     Wie gehst du dabei konkret vor? Hast du dabei eine bestimmte Sequenz?"

METHODE 2 – POST-SESSION MICRO-REFLECTION:
Am Ende einer abgeschlossenen Verhandlungsvorbereitung füge ein:
"Eine letzte Frage (völlig optional): Gibt es einen Trick oder eine
Erfahrung aus ähnlichen Situationen, die dir besonders geholfen hat?
Das hilft uns, die App für alle besser zu machen."

METHODE 3 – WIDERSPRUCHS-TRACKING:
Wenn der Nutzer einer Empfehlung widerspricht, frage nach:
"Du siehst das anders – was würdest du in dieser Situation tun?
Das klingt nach echter Erfahrung."

METHODE 4 – ERFOLGSREFLEXION:
Nach positivem Abschluss-Feedback:
"Was war der entscheidende Moment oder Move, der es gedreht hat?"

WICHTIG:
• Maximal EINE Wissensgewinnungs-Frage pro Session
• NIE direkt nach "Know-how", "Expertise" oder "Erfahrung" fragen
• Der Nutzer entscheidet immer, ob er antwortet (opt-in)

═══════════════════════════════════════════════════════════
M-6 | AKTIVER MODUS & OUTPUT-STANDARDS
═══════════════════════════════════════════════════════════

AKTUELLER MODUS: ${current_mode || "KEINER (freie Eingabe)"}

[analyse-Modus:] 1. Situationseinschätzung (2–3 Sätze) 2. Empfohlenes Framework +
Begründung 3. Stärken in dieser Verhandlung 4. Risiken / blinde Flecken
5. Die 3 wichtigsten ersten Schritte

[strategie-Modus:] 1. Verhandlungsziel (Ideal / Realistisch / Walkaway)
2. BATNA beider Seiten (soweit bekannt) 3. Eröffnungstaktik
4. Zugeständnisplan (was wann, nie ohne Gegenleistung)
5. Worst-Case-Szenario und Reaktion

[sparring-Modus:] Schlüpfe vollständig in die Rolle der Gegenseite.
Bleibe konsequent in dieser Rolle bis der Nutzer "Stop" sagt.
Am Ende: kurzes Debriefing aus Coach-Perspektive.

[quick-Modus:] Maximal 3 Punkte. Klar. Direkt. Sofort umsetzbar.
Keine langen Erklärungen – nur die wichtigsten Handlungsempfehlungen.

QUALITÄTSREGELN:
• Antworte IMMER auf Basis der konkreten Situation, nie generisch
• Jede Empfehlung muss begründet sein
• Wenn Information fehlt, frage nach – aber maximal 2 Fragen gleichzeitig
• Keine leeren Floskeln
• Keine Wiederholung der Nutzerfrage vor der Antwort
• Keine langen Einleitungen – komm sofort zum Punkt
• Schließe jede Antwort mit einem klaren nächsten Schritt ab

═══════════════════════════════════════════════════════════
M-7 | WIZARD-MODUS (NUR PRIVAT)
═══════════════════════════════════════════════════════════

Wenn die Nachricht mit [WIZARD_ZUSAMMENFASSUNG] beginnt: vollständige,
personalisierte Strategie in max. 5-7 nummerierten Schritten, je ein
Satzvorschlag zum Nachsprechen, 2-3 Worst-Case-Szenarien am Ende, KEIN
Framework-Name, KEINE Fachbegriffe.

═══════════════════════════════════════════════════════════
M-8 | VERHANDLUNGSTON
═══════════════════════════════════════════════════════════

[kooperativ:] pro → priorisiere [F1] Harvard, [F6] Mutual Gains; sonst intern
kooperative Ansätze ohne Framework-Namen. Fokus: Win-Win, Beziehungspflege.
[assertive:] pro → priorisiere [F2] Schranner, [F5] BATNA; sonst intern
durchsetzungsorientierte Ansätze ohne Framework-Namen.
[balanced:] situativ wählen.

═══════════════════════════════════════════════════════════
M-9 | STRUKTURIERTER OUTPUT (STRATEGIE)
═══════════════════════════════════════════════════════════

Bei Strategie-Empfehlungen: reiner Fließtext mit Markdown, NIEMALS JSON.
Struktur: **Wie du anfängst:** / **Deine Zahlen:** / **Wenn sie Nein sagen:**
[+ **Profi-Variante:** nur bei persona_type=pro]. Integriert Wissensbasis-
Einträge aus der `knowledge_base`-Tabelle (kuratierte Praxiserfahrungen).

═══════════════════════════════════════════════════════════
M-10 | PREMIUM-TIEFE (nur kmu/profi)
═══════════════════════════════════════════════════════════

• Zeige proaktiv Eskalationspfade und Worst-Case-Szenarien auf
• Biete explizite Machtanalyse: Wer hat die Verhandlungsmacht? Warum?
• Schätze die ZOPA wenn genug Daten vorhanden sind
• Identifiziere potenzielle "Black Swans" — verborgene Information die alles ändert
• Biete eine mutigere Alternativvariante neben der Hauptempfehlung an
```

**Einordnung (SUBSTANZ vs. GENERIK): SUBSTANZ, mit einer wichtigen Einschränkung.**
Der Prompt benennt 10 echte Verhandlungs-Frameworks mit Primärquelle (Fisher/Ury,
Schranner, Voss, Lax/Sebenius, Ury/Brett/Goldberg, Susskind/Field, Pruitt/Rubin,
Rackham, Mnookin/Peppet/Tulumello, Walton/McKersie) und eine explizite
Auswahllogik anhand 5 Dimensionen (Macht/Beziehung/Emotion/Komplexität/Zeitdruck).
Das ist die dichteste fachliche Substanz im gesamten System. **Aber:** M-10 sagt
wörtlich "Schätze die ZOPA wenn genug Daten vorhanden sind" — das ist eine
Aufforderung an das LLM, ZOPA in Prosa zu *schätzen*. Der echte, deterministische
`zopaCalculator.ts` (dieses Backend-Repo) wird von dieser Function **nicht**
aufgerufen und ist ihr nicht bekannt (Observed — kein Import/Fetch zu Railway in
`chat/index.ts`). Für `kmu`/`private` werden alle Framework-Namen zudem aktiv
unterdrückt ("Verwende KEINE Fachbegriffe... Framing, Logrolling") — die Methodik
wirkt, aber der Nutzer erfährt nie, welche.

---

### 1.2 `generate-plan` — Verhandlungsplan-Generator

- **Quelle:** `[deployed]` — negotiation-buddy `supabase/functions/generate-plan/index.ts`,
  Slug `generate-plan`, Version 5 (Observed via `get_edge_function`). `verify_jwt: true`
  (einzige der 5 mit erzwungener Edge-JWT-Prüfung zusätzlich zur eigenen Header-Prüfung).
- **Modell:** `claude-haiku-4-5-20251001`, hardcoded, `max_tokens: 1500`.
- **Tier-Abhängigkeit:** `persona_type` wird aus `user_profiles` aufgelöst und in
  `tier` übersetzt, aber **nirgends im Prompt verwendet** — der Tier-Wert wird
  berechnet und dann nicht referenziert (Observed: `tier`-Variable wird nach
  Zeile mit `personaTypeToTier`-Äquivalent nicht mehr gelesen). Prompt-Inhalt ist
  für alle Tiers identisch.

**System-Prompt (vollständig):**
```
Du erstellst professionelle Verhandlungspläne. Antworte NUR mit einem JSON-Objekt.
```

**User-Prompt-Template (vollständig, wörtlich):**
```
Erstelle einen professionellen Verhandlungsplan basierend auf diesen Daten.

Fortschrittspunkte:
${contextLines}   // "situation: <summary>\nziel: <summary>\n..." aus progress_status

Gesprächsverlauf:
${conversationContext}   // letzte 15 Messages, "Nutzer: ..."/"Coach: ..."

Antworte mit einem JSON-Objekt:
{
  "summary": "Professionelle Zusammenfassung in Sie-Form, 3-5 Sätze. Sachlich, kein Coaching-Ton. Keine Framework-Namen.",
  "situationAnalysis": "Strukturierter Fliesstext mit den 6 Punkten als Absätze. Format: **Situation:** ... **Ziel:** ... **Gegenseite:** ... **Alternativen:** ... **Machtposition:** ... **Strategie:** ... Keine Framework-Namen, alltagssprachlich.",
  "numbers": {
    "first_offer": "Erster Vorschlag (Zahl oder Text)",
    "target": "Zielpreis/Zielwert",
    "compromise_zone": "Kompromisszone"
  },
  "opening": "Empfohlener Eröffnungssatz für die Verhandlung. In direkter Rede, so wie der Nutzer es sagen würde.",
  "objections": [
    {"objection": "Möglicher Einwand", "response": "Empfohlene Antwort"}
  ],
  "recommendations": ["Empfehlung 1", "Empfehlung 2"],
  "nextStep": "Konkreter nächster Schritt"
}

Regeln:
- Wenn Zahlen im Gespräch genannt wurden, verwende diese. Sonst lasse numbers.first_offer etc. leer ("").
- Erstelle 2-4 realistische Einwand/Antwort-Paare basierend auf dem Kontext.
- Keine Framework-Namen (Harvard, BATNA etc.), nur Alltagssprache.
- Executive Summary: Sachlich, 3-5 Sätze, Sie-Form.
- Opening Script: Direkte Rede, natürlich klingend.
- Erstelle 2-3 konkrete Empfehlungen und einen klaren nächsten Schritt.
```

**Einordnung: MISCH, mit starker Generik-Schlagseite.** Die JSON-Struktur (Situation/
Ziel/Gegenseite/Alternativen/Machtposition/Strategie) spiegelt implizit ein
BATNA/Macht-Modell — aber `numbers.first_offer/target/compromise_zone` werden
**ausschließlich aus dem Chat-Text vom LLM geraten**, ohne jeden Bezug zu ZOPA,
Nash oder Monte Carlo aus diesem Backend-Repo (kein solcher Parameter existiert
in der Anfrage: `{session_id, progress_status, messages}` — keine `zopaResult`,
kein `analysis`). **Dies ist die zentrale Tote-Substanz-Fundstelle** — siehe
Abschnitt 5.1.

---

### 1.3 `analyze-progress` — 6-Punkte-Fortschrittstracker

- **Quelle:** `[deployed]`, Slug `analyze-progress`, Version 7 (Observed).
- **Modell:** `claude-haiku-4-5-20251001`, `max_tokens: 500`. Kein Tier-Bezug im Prompt.

**System-Prompt (vollständig, wörtlich):**
```
Analysiere das folgende Verhandlungs-Coaching-Gespräch. Antworte NUR mit einem JSON-Objekt im folgenden Format:
{
  "situation": { "completed": bool, "summary": "kurze Zusammenfassung max 60 Zeichen" },
  "ziel": { "completed": bool, "summary": "..." },
  "gegenseite": { "completed": bool, "summary": "..." },
  "batna": { "completed": bool, "summary": "..." },
  "macht": { "completed": bool, "summary": "..." },
  "strategie": { "completed": bool, "summary": "..." }
}
Regeln:
- situation=true wenn Kontext erkannt (was wird verhandelt?)
- ziel=true wenn Zielwert oder gewünschtes Ergebnis genannt wurde
- gegenseite=true wenn Gegenpartei bekannt (Chef, Vermieter, Lieferant etc.)
- batna=true wenn der Nutzer eine Alternative zur Verhandlung hat: anderes Angebot, Konkurrenz, andere Firma, Jobwechsel, Kündigung, Walk-Away, Alternative. Auch "Angebot von X", "andere Stelle", "könnte auch zu Y gehen" zählt als BATNA.
- macht=true wenn Machtverhältnis oder Drucksituation besprochen wurde
- strategie=true wenn konkrete Vorgehensweise oder Taktik genannt wurde
- completed=false → summary="". Max 60 Zeichen pro Summary. Keine Framework-Namen.
```

**Einordnung: MISCH.** Die 6 Kategorien (situation/ziel/gegenseite/batna/macht/
strategie) sind ein reales, wenn auch einfaches Vorbereitungs-Framework
(im Kern: Situation → Ziel → BATNA beider Seiten → Machtanalyse → Taktik — deckungsgleich
mit M-6-Strategie-Modus). Die *Erkennung* selbst ist aber vollständig LLM-Urteil in
freier Prosa, ohne Bezug zu den deterministischen Layer-1-Feldern
(`opponent_estimated_max/min`, `batna_description` aus Railway `/api/chat`) — ein
drittes, unabhängiges Extraktionssystem (siehe 1.1 und 2.3).

---

### 1.4 `summarize-session` — Session-Zusammenfassung

- **Quelle:** `[deployed]`, Slug `summarize-session`, Version 5. Modell:
  `claude-haiku-4-5-20251001`, `max_tokens: 150`.

**System-Prompt (vollständig, wörtlich):**
```
Du fasst einen Verhandlungs-Coaching-Verlauf in 2 Sätzen zusammen. Nenne Thema und letzten Stand. Keine Floskeln. Antworte im folgenden Format:
ZUSAMMENFASSUNG: [2 Sätze]
NÄCHSTER PUNKT: [1 konkreter nächster Schritt, falls erkennbar, sonst 'Keiner erkennbar']
```

**Einordnung: GENERIK.** Reine Zusammenfassungsanweisung, keine Methodik-Bindung.

---

### 1.5 `analyze-document` — Dokumentenanalyse

- **Quelle:** `[deployed]`, Slug `analyze-document`, Version 5. Modell:
  `claude-haiku-4-5-20251001`, `max_tokens: 2048`, `stream: true`.

**System-Prompt (vollständig, wörtlich, `${addressForm}` = "du/dein" oder "Sie/Ihr"):**
```
Du bist Max, ein erfahrener Verhandlungscoach. Du analysierst das hochgeladene Dokument ausschließlich aus VERHANDLUNGSTAKTISCHER Sicht. NICHT aus rechtlicher Sicht.

Erlaubte Aussagen:
✓ "Diese Klausel schwächt typischerweise [deine/Ihre] Verhandlungsposition..."
✓ "Dieser Punkt ist erfahrungsgemäß gut verhandelbar..."
✓ "Hier würde ich als Erstes ansetzen, weil..."
✓ "Diese Formulierung lässt Spielraum für Auslegung – taktisch nutzen:"

Verbotene Aussagen:
✗ "Diese Klausel ist rechtlich unwirksam..."
✗ "[Du hast/Sie haben] Anspruch auf..."
✗ "Das Gericht würde..."

Analysiere das Dokument in dieser Struktur:
1. Top-3 Verhandlungspunkte (wo liegt der meiste Spielraum?)
2. Ausgangsposition (stark/mittel/schwach, warum?)
3. Empfohlene Reihenfolge: Was zuerst verhandeln?

Sprich den Nutzer mit "[du/Sie]" an.
```

**Einordnung: MISCH.** Klare, wiederholte Trennlinie Taktik/Recht (deckt sich mit
M-2 im Haupt-Chat-Prompt) ist substanziell für Risikomanagement, aber die
"Top-3-Punkte/Ausgangsposition/Reihenfolge"-Struktur selbst ist generisches
Beratungs-Framing ohne benannte Methodik. **Nebenbefund (nicht Kernthema dieser
Analyse):** Das Dokument wird als rohe Base64-Zeichenkette (erste 50.000 Zeichen)
in einen Text-Content-Block gepackt, nicht über Anthropics Dokument/Vision-API —
technische Umsetzung, kein Substanz-Thema.

---

### 1.6 Railway-Backend (`negotiationcoach-backend`) eigene Prompts — `[local]`, live erreichbar

- **Quelle:** `[local]` — `src/api/chatHelpers.ts`, `src/api/planHelpers.ts`. Dieses
  Backend hat **keine eigene deployte Edge Function mit System-Prompt** (siehe
  Abschnitt 0). Die einzigen selbst gebauten Prompts laufen über die Railway-
  Express-Routen `/api/chat` und `/api/plan`.
- **`/api/chat` ist aktiv genutzt** — nicht als sichtbare Konversation, sondern
  als struktureller Extraktions-Layer, aufgerufen von negotiation-buddy
  `useProgressEngine.ts` (`sendChatMessage`, one-shot pro Session, siehe 2.3).
  Die zurückgegebene `message` wird dabei **verworfen** — nur `extractedInputs`
  wird verwendet (Observed: `useProgressEngine.ts` liest nur `response.extractedInputs`).
- **`/api/plan` ist laut `docs/api-catalog.md` (2026-03-30, ADR-005) und
  `docs/dead-code-candidates.md` DCC-BE-02 als "Inactive (migration target)"
  bzw. "unused call site" dokumentiert** und wird von negotiation-buddy nicht
  aufgerufen (Observed: kein Caller außer der Definition selbst in `apiClient.ts`,
  wo der Kommentar das bereits selbst vermerkt: "It is currently unused (zero
  active callers)").

**`buildChatSystemPrompt` (Railway `/api/chat`, vollständig, wörtlich):**
```
Du bist ein professioneller Verhandlungscoach. Antworte ausschließlich auf Deutsch.
${tierCtx}
${scenarioCtx}
${knownData}

WICHTIG — Antwortformat:
Deine Antwort MUSS immer exakt diesem JSON-Format folgen, sonst bricht das System:

{
  "message": "Deine Coaching-Antwort hier (Markdown erlaubt)",
  "extracted": {
    "negotiation_type": "<gehalt|miete|lieferant|m_a|sonstige|null> — Mappe großzügig: 'Jahresgehalt', 'Lohn', 'Vergütung' → gehalt; 'Miete', 'Mietvertrag' → miete; null NUR wenn völlig unklar",
    "own_target": Zahl oder null,
    "own_minimum": Zahl oder null,
    "opponent_estimated_max": Zahl oder null,
    "opponent_estimated_min": Zahl oder null,
    "deadline_days": Zahl oder null,
    "batna_description": "Text" oder null,
    "context_notes": "Text" oder null,
    "confidence": 0.0 bis 1.0,
    "missing_fields": ["liste", "fehlender", "felder"]
  }
}

Extraktionsregeln:
- Extrahiere NUR was der Nutzer explizit genannt hat — keine Schätzungen
- Behalte Werte aus previousInputs wenn der Nutzer sie nicht korrigiert hat
- missing_fields: Liste der Felder die für eine vollständige Analyse noch fehlen
- confidence: 1.0 wenn alle Felder vollständig, sinkt proportional zu fehlenden Feldern
- Wenn wichtige Felder fehlen: stelle im "message"-Teil gezielte Rückfragen (max. 2 auf einmal)
```
`tierCtx` per Tier: `profi`: "Tiefe strategische Analyse, Fachtermini erlaubt,
präzise und direkt."; `kmu`: "Praxisnahe Empfehlungen, Fokus auf Ergebnis und
Risiko, geschäftlich."; `privat`: "Verständliche Sprache, alltagsnahe Beispiele,
ermutigend."; `free`: "Kurze Orientierung, einfache Sprache."

**Einordnung: GENERIK.** Kein Framework wird benannt, keine Methodik referenziert.
Reine Rollenanweisung + JSON-Extraktionsvertrag. Modell: dynamisch via
`modelRouter.selectModel('strategy_coaching', tier)` (Observed, `docs/api-catalog.md`
+ `src/utils/modelRouter.ts` — free=Haiku, privat/kmu/profi=Sonnet).

**`buildPlanSystemPrompt` (Railway `/api/plan`, vollständig, wörtlich) — SUBSTANZ,
aber toter Pfad (siehe 5.1):**
```
Du bist ein professioneller Verhandlungscoach und erstellst
einen vollständigen, professionellen Verhandlungsplan auf Deutsch.

GESPRÄCHSVERLAUF:
${chatSummary}

VERHANDLUNGSPARAMETER:
- Typ: ${negotiation_type}
- Eigenes Ziel: ${own_target} EUR
- Eigenes Minimum: ${own_minimum} EUR
- Gegenseite Max: ${opponent_estimated_max} EUR
- Gegenseite Min: ${opponent_estimated_min} EUR
- BATNA: ${batna_description}
- ZOPA: ${zopa_min}–${zopa_max} EUR | Nash: ${nash_solution} EUR   // oder "Keine ZOPA berechnet"
- Strategie-Score: ${strategy_score}/100                            // oder "Score nicht berechnet"

ANWEISUNGEN:
Erstelle einen professionellen Verhandlungsplan. Antworte NUR mit
diesem JSON-Format, kein Text davor oder danach:
{ "summary": "...", "situationAnalysis": "...", "opening": "...",
  "objections": [{"title":"...","objection":"...","response":"..."}],
  "recommendations": [...], "nextStep": "..." }
```
Dies ist der **einzige** Prompt im gesamten System (deployed oder local), der
tatsächliche ZOPA-, Nash- und Strategy-Score-Zahlen aus der Layer-1-Engine in
den LLM-Kontext einspeist. Er ist aber tot (kein Caller).

---

## 2. Fragen an den Nutzer — Erhebung, Reihenfolge, Pflicht/Optional

**Observed — drei parallele, unabhängige Extraktionsmechanismen existieren
gleichzeitig, mit unterschiedlichen Schemata:**

| # | Mechanismus | Schema | Trigger | Wo |
|---|---|---|---|---|
| 1 | `chat` EF Extract-Modus | `{details, goal, counterpart, alternatives}` | On-demand (`useChat.ts`, `persona.mode="extract"`) | negotiation-buddy `[deployed]` |
| 2 | Railway `/api/chat` | `ExtractedInputs`: `negotiation_type, own_target, own_minimum, opponent_estimated_max/min, deadline_days, batna_description, context_notes, confidence, missing_fields` | One-shot pro Session (`useProgressEngine.ts` → `runExtractInputs`) | dieses Backend `[local]`, live |
| 3 | `analyze-progress` EF | `{situation, ziel, gegenseite, batna, macht, strategie}` je `{completed, summary}` | Nach jeder AI-Antwort (Observed, separater Call) | negotiation-buddy `[deployed]` |

**Reihenfolge:** Es gibt **keinen festen Fragenkatalog mit Reihenfolge** — der
Nutzer beschreibt seine Situation frei im Chat; alle drei Mechanismen versuchen
im Nachhinein, Struktur aus dem freien Text zu extrahieren. Ein Guided-Wizard-
Modus existiert (M-7, `[WIZARD_ZUSAMMENFASSUNG]`-Präfix), aber die Fragen des
Wizards selbst liegen im negotiation-buddy-Frontend, nicht im Backend
(außerhalb dieses Scopes — Inferred aus Prompt-Referenz, nicht verifiziert).

**Pflicht vs. optional (Observed, `src/api/chatHelpers.ts` `emptyExtraction.missing_fields`):**
Hart als "für vollständige Analyse nötig" markiert: `negotiation_type`,
`own_target`, `own_minimum`. `opponent_estimated_max/min`, `deadline_days`,
`batna_description`, `context_notes` sind de facto optional (können `null`
bleiben, kein Blocker in Railway-Logik selbst).

**Wird Unvollständigkeit erkannt?** Ja, aber **inkonsistent gehandhabt zwischen
den drei Extraktoren und dem Frontend-Trigger**, der auf ihnen aufbaut
(Observed via `shared-context/product/briefs/NC-PLAN-FIX.md` und `NC-CONTEXT.md`,
beide `negotiation-buddy`-seitig, aber direkt durch Backend-Extraktionsverhalten
verursacht):

- `ExtractedInputs.missing_fields` und `ExtractedInputs.confidence` werden vom
  Railway-Prompt (1.6) explizit angefordert — echtes Vollständigkeits-Signal.
- Der Plan-Trigger im Frontend (`Index.tsx`, `allDone`-Logik) verlangt historisch
  **alle 6** `analyze-progress`-Punkte inkl. `gegenseite` — obwohl `gegenseite`
  bei Gehaltsverhandlungen strukturell fast nie extrahierbar ist (Arbeitgeber-
  Limit wird selten genannt). Laut Release-Notes (`current.md`, R-2026-09) und
  Brief `NC-PLAN-FIX.md` wurde dies als P1-Bug behoben (Status: Released) —
  **diese Reparatur liegt vollständig im Frontend** (`Index.tsx`), das Backend-
  Extraktionsverhalten selbst wurde nicht geändert.
- **P-1 aus `NC-CONTEXT.md` (Status: Released, Phase A+B):** Vor Fix lief die
  Railway-`/api/chat`-Extraktion nur einmal pro Session; bei Claude-529/429 blieb
  `batna_description`/`opponent_estimated_max/min` dauerhaft leer, ohne Retry.
  Regex-Fallback für Zahlen wurde nachgerüstet. Der zugrunde liegende Fakt bleibt
  bestehen: **das Backend selbst hat keinen deterministischen Fallback** —
  jede Robustheit gegen LLM-Ausfall liegt im Frontend (Regex auf letzte 10
  Nachrichten), nicht im Backend-Code dieses Repos.

**Fazit Abschnitt 2 (Observed):** Es gibt keine strukturierte Intake-Maske mit
Pflichtfeld-Validierung serverseitig — alle "Fragen an den Nutzer" laufen über
freie Konversation plus nachgelagerte, mehrfach redundante LLM-Extraktion. Der
einzige harte serverseitige Vollständigkeits-Gate ist Zod-Validierung
(`NegotiationInputsSchema`) auf `/api/analyze` — die erfordert `own_target`,
`own_minimum`, `opponent_estimated_max`, `opponent_estimated_min` als Pflicht
(Observed, `docs/api-catalog.md`), aber dieser Endpunkt wird — siehe Abschnitt 3 —
nur von wenigen Tool-Seiten aufgerufen, nicht vom Haupt-Chat-Flow.

---

## 3. Output-Artefakte pro Endpoint

**Hinweis zur Methode:** Für jeden Endpoint wird zusätzlich vermerkt, ob ein
Caller im negotiation-buddy-Frontend gefunden wurde (Observed via `grep` über
`src/lib/apiClient.ts` und alle Importer, 2026-07-23) — das ist der einzig
verlässliche Nachweis, ob ein Backend-Feature den Nutzer tatsächlich erreicht.

### `POST /api/chat` (Railway, `[local]`, **aktiv genutzt**)
Input → `{messages, scenario?, previousInputs?}` → `buildChatSystemPrompt` →
Claude (Modell via `modelRouter`, tierabhängig) → `parseChatResponse` →
**Output:** `{message: string, extractedInputs: ExtractedInputs | null, isComplete: boolean}`.
Caller: `negotiation-buddy/src/hooks/useProgressEngine.ts` (nur `extractedInputs`
wird verwendet, `message` verworfen), `src/lib/apiClient.ts:85`.

### `POST /api/plan` (Railway, `[local]`, **tot** — DCC-BE-02, ADR-005)
Input → `{extractedInputs, zopaResult?, analysis?}` → `buildPlanSystemPrompt`
(einziger Prompt mit echten ZOPA/Nash/Score-Zahlen) → **Output:**
`{summary, situationAnalysis, opening, objections[], recommendations[], nextStep}`.
Kein Caller im Frontend (Observed).

### `POST /api/analyze` (Railway, `[local]`, Caller unklar für Haupt-Flow)
Input → `NegotiationInputs` (Zod-validiert, Pflicht: `negotiation_type,
own_target, own_minimum, opponent_estimated_max, opponent_estimated_min`) →
`analyzeNegotiation()` → **Output:** `{sessionId: string|null, result: AnalysisResult}`
mit `AnalysisResult = {zopa_exists, zopa_min, zopa_max, nash_solution,
monte_carlo_p50, monte_carlo_p90, acceptance_curve[], strategy_score,
deadline_effect?, missing_inputs[], recommendations[]}` — vollständig befüllt
(Observed, `src/layer1/index.ts`). Kein direkter Frontend-Caller gefunden
(`analyzeOnly`/`analyzeFull` werden stattdessen genutzt, siehe unten) —
`/api/analyze` selbst: **Missing/Inferred** ob es noch einen aktiven Aufrufer
außerhalb dieses Greps hat.

### `POST /api/analyze-full` (Railway, `[local]`, **aktiv genutzt**)
Input → `NegotiationInputs` + `region?` → Layer 1 + (bei `kmu`/`profi`) Layer 2 →
**Output:** `{sessionId, result: AnalysisResult, enriched?: EnrichedAnalysisResult}`.
Caller (Observed): `negotiation-buddy/src/pages/NegotiationCanvas.tsx` (→
`CanvasResults.tsx`), `ZopaCalculator.tsx`. `WhatIfSimulator.tsx` nutzt
stattdessen `analyzeOnly` (gleiche Machinerie, eigener Name in `apiClient.ts`).

### `POST /api/enrich` (Railway, `[local]`, **aktiv genutzt, tier-gated `kmu+`**)
Input → `{sessionId, region?}` → `enrichWithMarketData()` → **Output:**
`EnrichedAnalysisResult = AnalysisResult + {market_data_source, market_median,
market_range_min/max, reality_score, market_context_summary, market_comparison}`.
Caller (Observed): `Index.tsx` (Haupt-Chat-Flow, nach Plan-Erstellung),
`ZopaCalculator.tsx`, `WhatIfSimulator.tsx`. NC-L2-UI-Brief (Status: DONE,
2026-06-02) bestätigt dies — durch eigene Code-Verifikation bestätigt, nicht
nur aus dem Brief übernommen.

### `POST /api/opponent-simulation/{start,turn,finish}` (Railway, `[local]`,
**aktiv genutzt, tier-gated `profi`, einziger live Simulations-Pfad**)
- `/start`: Input `OpponentSimulationSetup` → `computeHiddenOpponentRange()`
  (ZOPA-basiert, siehe 4.3) + Claude-Eröffnungszug → **Output:**
  `{simulation_session_id, status, max_turns, opening_message, warning?}`.
- `/turn`: Input `{content, client_turn_id}` → Claude mit
  `buildOpponentSystemPrompt()` (ohne `grounding`-Parameter — siehe 5.2) →
  **Output:** `{assistant_message, turn_count, max_turns, finished}`.
- `/finish`: Input `{final_offer}` → `evaluateOutcome()` → **Output:**
  `{evaluation: {final_outcome, own_zopa_min, own_zopa_max, nash_solution,
  outcome_vs_nash, outcome_percentile, tactic_assessment}, hidden_opponent_minimum,
  hidden_opponent_target}`.
Caller (Observed): `negotiation-buddy/src/pages/OpponentSimulator.tsx` — **alle**
Felder des `evaluation`-Objekts werden gerendert (Zeilen 590-618), inkl.
`tactic_assessment` als Text-Verdikt.

### `POST /api/simulate/{start,turn,debrief}` (Railway, `[local]`, **NC-L3-SIM
Phase 3 — vollständig gebaut, KEIN Frontend-Caller gefunden**)
- Nutzt `runIntake/runTurn/runDebrief` aus `src/layer3/index.ts`.
- `/debrief` → `runDebrief()` → `buildDebriefResult()` → **Output (`DebriefResult`):**
  `{deal_reached, final_offer, walkaway_reason?, hidden_opponent_minimum/target,
  final_vs_zopa_percentile, final_vs_nash_distance, final_vs_nash_direction,
  vs_monte_carlo_p50, vs_monte_carlo_p90, vs_market_median?, market_comparison?,
  concession_timeline[], total_user_concession_pct, total_opponent_concession_pct,
  tactics_used_well, tactics_missed, opponent_tactics_observed, key_mistakes,
  recommendations, overall_score}` — die reichhaltigste Output-Struktur im
  gesamten System. **Kein Import von `/api/simulate/*` in negotiation-buddy
  gefunden** (grep über `apiClient.ts` zeigt nur `/api/opponent-simulation/*`-
  Aufrufe unter den Namen `startOpponentSimulation`/`sendOpponentTurn`/
  `finishOpponentSimulation`). Siehe Abschnitt 5.2 — zentrale Tote-Substanz-Fundstelle.

### Session-Endpoints (`/api/sessions*`, Railway, `[local]`, aktiv genutzt)
Reine CRUD-Persistenz, keine fachliche Substanz (Titel-Truncation, 50-Message-
Limit, Owner-Checks) — nicht Gegenstand dieser Analyse.

### Deployed EFs `analyze-progress`, `summarize-session`, `analyze-document`,
`chat` (negotiation-buddy `[deployed]`) — Output-Strukturen siehe Abschnitt 1
jeweils. Alle bestätigt aktiv genutzt (Observed, direkte `functions.invoke`/
`fetch`-Aufrufe in `useChat.ts`, `useProgressEngine.ts` und Analogie-Grep).

---

## 4. Fachliche Substanz vs. Generik — Gesamtübersicht

| Fundstelle | Substanz-Elemente | Klassifikation |
|---|---|---|
| `chat` EF System-Prompt (M-1–M-10) | 10 benannte Frameworks mit Primärquelle, situative Auswahllogik (5 Dimensionen), Tier-abhängige Terminologie-Steuerung | **SUBSTANZ** (stärkste Fundstelle), aber ZOPA wird darin *geschätzt*, nicht berechnet |
| `src/layer1/*` (ZOPA, Nash, Monte Carlo, Strategy Score, Deadline Effect) | Echte Formeln: ZOPA-Overlap-Check, Nash-artige Quadratwurzel-Lösung, 10.000-Iterationen-Monte-Carlo mit Akzeptanzkurve, gewichteter Score (40/40/20), lineare Deadline-Degradation | **SUBSTANZ** — einzige rein deterministische Schicht im System |
| `src/layer3/opponentEngine.ts` (`computeHiddenOpponentRange`, `buildOpponentSystemPrompt`-Grounding, `evaluateOutcome`) | Gegner-Verhalten quantitativ aus ZOPA/Stil/Schwierigkeit hergeleitet, optionale Nash/Monte-Carlo/Reality-Score-Grounding-Injektion, Ergebnis-Bewertung relativ zu Nash | **SUBSTANZ** — methodisch anspruchsvollste Verzahnung von Layer 1 und LLM im ganzen System |
| `src/layer3/debriefEngine.ts` | Konzessions-Timeline mit %-Berechnung, Distanz/Richtung vs. Nash, Schwellenvergleich vs. Monte-Carlo-Perzentile, Markt-Toleranzband | **SUBSTANZ**, aber toter Pfad (5.2) |
| `generate-plan` EF (deployed, tatsächlicher Plan-Pfad) | Struktur folgt implizit BATNA/Macht-Logik, aber Zahlen sind LLM-Schätzung aus Chat-Text, Frameworks explizit unterdrückt | **MISCH**, ca. 70% Generik / 30% latente Struktur (Einschätzung, nicht gemessen) |
| `analyze-progress` EF | 6-Punkte-Modell real, aber Erkennung rein LLM-Urteil ohne Bezug zu Layer 1 | **MISCH** |
| Railway `/api/chat` (`buildChatSystemPrompt`) | Reine Rollenanweisung + JSON-Vertrag, keine Methodik | **GENERIK** |
| `summarize-session` EF | Zusammenfassungsanweisung | **GENERIK** |
| `analyze-document` EF | Taktik/Recht-Trennung substanziell, Analyse-Struktur generisch | **MISCH** |
| Layer 2 (`realityScore.ts`, `marketDataResolver.ts`) | Arithmetik ist real (Median-Abweichung, ±2%-Toleranzband in `debriefEngine.ts`), aber die zugrunde liegende `market_median`-Zahl stammt selbst aus einem Claude-`tool_use`-Suchlauf (`marketDataInterpreter.ts`, kein echtes externes Markt-API — Stufe-2-Feature laut `docs/api-contracts.md`) | **MISCH** — Berechnung real, Eingangsdatum ist LLM-generiert |

**Gesamtbild (Observed + Inferred):** Es gibt eine echte, gut konstruierte
quantitative Engine (Layer 1) und eine methodisch dichte Prompt-Bibliothek
(`chat` EF M-1–M-10) — aber beide sind **im aktuell live geschalteten Nutzerpfad
kaum miteinander verbunden**. Der Plan-Generator, den die meisten Nutzer sehen
(`generate-plan` EF), verwendet keine der Layer-1-Zahlen. Die einzige Stelle, an
der Layer 1 tief mit LLM-Verhalten verzahnt ist (`opponentEngine.ts`), ist ein
Profi-Tier-Feature mit vermutlich kleiner Nutzerbasis (tier-gated `profi`,
kein Nutzungsdaten-Beleg in diesem Scope — UNKNOWN).

---

## 5. Tote Substanz

### 5.1 Layer-1-Engine (ZOPA/Nash/Monte Carlo/Strategy Score) im Haupt-Plan-Flow

| Verfahren | Berechnet? | Im Output enthalten? | Für Nutzer sichtbar/erklärt? |
|---|---|---|---|
| ZOPA | Ja — `analyzeNegotiation()`, `src/layer1/index.ts:17` | Ja — `AnalysisResult.zopa_min/max/exists` | **Nein** im Haupt-Chat-Plan (`generate-plan` EF bekommt diese Felder nicht); **Ja** auf `NegotiationCanvas`/`WhatIfSimulator`/`ZopaCalculator`-Toolseiten (`CanvasResults.tsx:30-31`) |
| Nash | Ja — `calculateNash()`, `src/layer1/index.ts:22-27` | Ja — `AnalysisResult.nash_solution` | Nein im Haupt-Chat-Plan; Ja auf `WhatIfSimulator`/`OpponentSimulator` (letzteres zeigt `nash_solution` sogar mit Konsequenz-Text `tactic_assessment`) |
| Monte Carlo (p50/p90, acceptance_curve) | Ja — `runMonteCarlo()`, `src/layer1/index.ts:33-42` | Ja — `AnalysisResult.monte_carlo_p50/p90/acceptance_curve` | `monte_carlo_p50/p90`: sichtbar nur auf `NegotiationCanvas` (`CanvasResults.tsx:131,135`). **`acceptance_curve`: berechnet, im Typ vorhanden (`negotiation-buddy/src/lib/types.ts:32`), aber in KEINER UI-Komponente des gesamten negotiation-buddy-Repos gerendert (Observed, repo-weiter Grep) — vollständig tot.** |
| Strategy Score | Ja — `calculateStrategyScore()`, gewichtete Formel | Ja — `AnalysisResult.strategy_score` | Ja, mehrfach: `CanvasResults.tsx` (Score-Ring), `WhatIfSimulator.tsx`, `StrategyGenerator.tsx`, `DebriefDashboard.tsx`, und als kleine Zahl im Haupt-Chat-Fortschrittslabel (`Index.tsx:157`) |
| Deadline Effect | Ja — linear, `deadline_days/90` | Ja — `AnalysisResult.deadline_effect` | Ja, aber nur auf `WhatIfSimulator`/`CanvasResults` (Niedrig/Mittel/Hoch-Label), nicht im Haupt-Chat-Flow |
| BATNA `missing_inputs`/`recommendations` | Ja — `detectBatna()`, Pflichtfeld-Check + LLM-Empfehlungen | Ja | `missing_inputs`: Ja, als Alert in `CanvasResults.tsx:36-42`. `recommendations`: Ja, mehrfach gerendert |

**Kernbefund:** Keines dieser Layer-1-Felder ist grundsätzlich unsichtbar — sie
sind auf **Werkzeug-Seiten** (Canvas, ZOPA-Rechner, What-If-Simulator, Strategy
Generator, Debrief Dashboard) gut sichtbar und teils gut erklärt. Aber der
**Haupt-Chat-Flow** (`Index.tsx`, vermutlich der primäre Einstiegspfad, da einzige
"immer sichtbare" Ansicht) zeigt nur `market_median` + `reality_score`
(Layer 2) und schmuggelt `strategy_score` als Zahl in ein Fortschritts-Label
(`Index.tsx:157`) — ohne Erklärung, ohne ZOPA/Nash/Monte-Carlo/Deadline-Effect.
Der eigentliche Plan-Text, den der Nutzer im Chat bekommt (`generate-plan` EF),
enthält **keine** dieser Zahlen — er wird komplett unabhängig vom
Layer-1-Ergebnis generiert (Observed: `generate-plan/index.ts`-Request-Body ist
`{session_id, progress_status, messages}`, keine Analyse-Felder).

Der einzige Prompt, der Layer-1-Zahlen tatsächlich in einen LLM-Plan einspeist
(`buildPlanSystemPrompt`, Railway `/api/plan`, Abschnitt 1.6), ist selbst tot
(kein Frontend-Caller, dokumentiert in `docs/dead-code-candidates.md` DCC-BE-02).
**Das ist der klarste Einzelbefund der ganzen Analyse:** Der Code, der Substanz
und Sprache verbindet, existiert — aber genau dieser Pfad ist deaktiviert;
der aktive Pfad hat die Verbindung nie gehabt.

### 5.2 Layer-3-Debrief-Engine (NC-L3-SIM Phase 3) — vollständig gebaut, nicht angeschlossen

`src/layer3/index.ts` → `runDebrief()` → `debriefEngine.ts` (`computeConcessionTimeline`,
`computeOutcomeMetrics`, `computeMarketComparison`, `buildDebriefResult`) berechnen
eine vollständige, Layer-1/2-gegründete Verhandlungs-Nachbesprechung:
Konzessions-Timeline mit Prozentsätzen pro Zug, finaler Abstand/Richtung zum
Nash-Punkt, Schwellenvergleich zu Monte-Carlo-P50/P90, Markt-Abweichung mit
±2%-Toleranzband. Erreichbar über `POST /api/simulate/debrief`
(`src/api/simulationRoutes.ts:486-498`).

**Observed, verifiziert per Grep über das gesamte negotiation-buddy-Repo:**
Kein einziger Import von `/api/simulate/*`, `runIntake`, `runTurn`, `runDebrief`
oder einem der `DebriefResult`-Feldnamen (`concession_timeline`,
`final_vs_nash_distance`, `vs_monte_carlo_p50` etc.) existiert im Frontend.
`OpponentSimulator.tsx` — die einzige Simulations-UI — ruft stattdessen
ausschließlich die ältere `/api/opponent-simulation/*`-Route auf (`apiClient.ts:166,175,188`)
und konsumiert von deren `finish`-Antwort nur `hidden_opponent_minimum/target`
für die Zwei-Zahlen-Enthüllung — nicht die deutlich reichhaltigere `evaluateOutcome()`-
Auswertung (die wiederum auf der älteren, weniger detaillierten Route liegt und
dort tatsächlich vollständig gerendert wird, s.o.).

**Das bedeutet:** Die frisch gebaute (`git log`: Commits `007a6ee`, `b5bf2d7`,
Titel "NC-L3-SIM Phase 3") und methodisch reichhaltigste Komponente des
gesamten Systems — ein Debrief mit editorialisierten, aus echten Zahlen
abgeleiteten Kennzahlen statt LLM-Prosa — erreicht aktuell **keinen einzigen
Nutzer**. Sie ist vollständig implementiert, getestet (`tests/layer3/*.regression.test.ts`,
laut Code-Kommentaren), aber ohne Frontend-Anschluss.

### 5.3 `deriveIntakeComplete` / `runIntake` (Layer 3, `src/layer3/index.ts`)

**Missing/UNKNOWN:** Ob `runIntake` (Teil desselben `/api/simulate/start`-Pfads)
über einen anderen, in diesem Scope nicht gefundenen Aufrufer erreichbar ist,
wurde nicht mit letzter Sicherheit ausgeschlossen — der Grep deckt nur
negotiation-buddy ab; ein dritter Konsument (z. B. interner Test-Client, Admin-
Tool) ist nicht auszuschließen, aber nicht beobachtet.

---

## 6. Explainability

**Ja, an mehreren Stellen — aber nur außerhalb des Haupt-Chat-Flows:**

1. **`getScoreHint()` (negotiation-buddy `CanvasResults.tsx:22-27`)** — reine
   Schwellenwert-Lookup-Tabelle auf `analysis.strategy_score`: `≥80` → "Starke
   Position — Ziele halten", `≥60` → "Gute Position — Anker setzen", `≥40` →
   "Moderate Position — kooperativ vorgehen", sonst → "Schwache Position —
   BATNA stärken". **Echte Berechnungs-basierte Erklärung**, keine LLM-Prosa.
2. **`tactic_assessment` (`opponentEngine.ts:evaluateOutcome`)** — Text-Verdikt
   direkt aus dem Vergleich `finalOffer` vs. `hidden_opponent_minimum` vs.
   `nash_solution` abgeleitet ("Exzellent — Einigung über dem Nash-Optimum
   erzielt." / "Gut — Einigung innerhalb der ZOPA, aber unter Nash-Optimum." /
   "Keine Einigung — Angebot lag unter dem Minimum der Gegenseite."). Wird
   vollständig im Frontend gerendert (`OpponentSimulator.tsx:590`). **Stärkste
   Einzel-Fundstelle für Explainability im gesamten System.**
3. **`generateMarketContextSummary()` (`src/layer2/index.ts:6-39`)** — die
   LLM-Zusammenfassung wird nicht frei generiert, sondern bekommt den bereits
   berechneten `realityScore` und einen daraus abgeleiteten `comparisonText`
   ("X% über/unter dem Marktmedian") explizit in den Prompt eingebettet — der
   Text *begründet* eine reale Zahl, statt sie zu ersetzen.
4. **`missing_inputs`-Alert (`CanvasResults.tsx:36-42`)** — direkte Ableitung aus
   `batnaDetector.ts`s deterministischem Pflichtfeld-Check, keine LLM-Beteiligung.

**Nein, an der wichtigsten Stelle:** Der Haupt-Verhandlungsplan (`generate-plan`
EF, das, was die meisten Nutzer nach dem Chat-Flow sehen) enthält **keine**
Begründung, die auf Berechnung statt auf LLM-Formulierung beruht — `summary`,
`opening`, `objections`, `recommendations` sind vollständig freie
LLM-Generierung aus Chat-Text, ohne Bezug zu einer der oben genannten
Kennzahlen. Ebenso ist die im Layer-3-Debrief vorhandene, am stärksten
berechnungsbasierte Erklärung (`vs_monte_carlo_p50/p90`, `final_vs_nash_distance/
direction`, `concession_timeline`) durch die fehlende Frontend-Anbindung (5.2)
für keinen Nutzer sichtbar.

---

## Anhang: Nebenbefunde (außerhalb des Scopes, max. 3 Zeilen)

`analyze-document` sendet Dokumente als rohe Base64-Zeichenkette in einem
Text-Content-Block an Claude (kein Vision/Document-API-Aufruf) — vermutlich
unwirksame Dokumentenanalyse bei Nicht-Text-Formaten, aber nicht verifiziert.

---

## Kurzfazit

**Anteil GENERIK an dem, was der Nutzer tatsächlich sieht: hoch im Haupt-Chat-
Flow, gering auf den Profi-Werkzeug-Seiten.** Der Chat selbst trägt eine
methodisch dichte Prompt-Bibliothek (10 Frameworks, situative Auswahllogik),
aber der Plan, den die meisten Nutzer als Ergebnis bekommen (`generate-plan`
EF), ist strukturierte, methodenfreie LLM-Prosa ohne jeden Bezug zur echten
Layer-1-Engine dieses Backends.

**3 stärkste Fundstellen (echte, sichtbare Substanz):**
1. `tactic_assessment` in `OpponentSimulator.tsx` — Berechnungs-Verdikt, nicht LLM-Prosa.
2. `chat`-EF-Frameworkbibliothek (M-4) — 10 benannte, quellenbelegte Methoden mit Auswahllogik.
3. `getScoreHint()` — Schwellenwert-Erklärung direkt aus `strategy_score`.

**3 schwächste Fundstellen (Substanz vorhanden, aber tot oder verwässert):**
1. `debriefEngine.ts` (NC-L3-SIM Phase 3) — reichhaltigster Code im System, null Frontend-Anschluss.
2. `buildPlanSystemPrompt` (Railway `/api/plan`) — einziger ZOPA/Nash-gespeister Plan-Prompt, kein Caller.
3. `acceptance_curve` — berechnet, typisiert, in keiner UI-Komponente gerendert.
