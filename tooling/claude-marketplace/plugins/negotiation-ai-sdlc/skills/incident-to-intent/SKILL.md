---
name: incident-to-intent
description: Convert a Negotiation AI production incident, control-band breach, support pattern, or operational failure into a canonical incident record and a linked follow-up intent without implementing a fix. Use only through explicit invocation.
argument-hint: "[incident-id-or-source] [existing or new change-id]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Convert Incident to Intent

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/ARTIFACT_CONTRACT.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/DEBUG_PROTOCOL.md`
4. `${CLAUDE_PLUGIN_ROOT}/references/EVIDENCE_STANDARD.md`
5. Existing release, outcome, incident, monitoring, support, and diagnostic evidence

## Workflow

1. Identify the source incident and check for an existing canonical incident or change to prevent duplication.
2. Create or update `incident.md` with impact, detection, timeline, containment, recovery, cause status, and follow-up actions. Do not copy secrets or sensitive raw data.
3. Link `debug-evidence.md` when technical diagnosis exists. Do not manufacture a cause from temporal correlation.
4. Create a new `intent.md` when preventive, corrective, detection, recovery, or learning work requires a distinct change. Preserve incident language and evidence while framing an outcome, not a predetermined patch.
5. Link the incident, originating release or outcome, and follow-up change in both traceability records.
6. Keep emergency containment distinct from the durable change. Record any emergency exception and follow-up owner.
7. Do not modify implementation, deploy, or alter production during this Skill.

## Required result

Report canonical incident path, impact and cause status, containment evidence, created or linked follow-up intent, owners and open actions, traceability updates, and exact next action.
