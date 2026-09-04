---
artifact: policy
policy_id: POL-AIQ-001
title: AI Behavior and Evaluation Policy
status: draft
owner: "<AI_PRODUCT_OWNER>"
version: 0.1.0
approved_by: null
approved_date: null
review_date: null
source_authorities: []
scope: "Prompts, models, retrieval, agents, tools, and AI-generated product behavior"
---

# AI Behavior and Evaluation Policy

> This draft is not normative until approved. Model-provider, legal, security, and product requirements must be verified.

## Objectives

Define intended AI behavior, known failure modes, evidence thresholds, human control, data boundaries, and production monitoring before shipping AI behavior changes.

## Candidate mandatory controls

1. State the task, user population, allowed actions, prohibited actions, and failure consequences.
2. Version prompts, schemas, tools, model configuration, retrieval logic, and evaluation sets that materially affect behavior.
3. Maintain representative positive, negative, adversarial, and boundary cases for material AI features.
4. Use deterministic checks for schema, permissions, tool boundaries, and other deterministic requirements.
5. Measure task-relevant quality and safety rather than relying on subjective spot checks alone.
6. Separate model-generated claims from verified facts in user-facing behavior when material.
7. Define human review, user correction, fallback, escalation, and safe failure for high-impact actions.
8. Prevent secrets and unauthorized personal or confidential data from entering prompts, retrieval, logs, or providers.
9. Record model or provider changes, expected impact, comparison evidence, and rollback.
10. Monitor production signals and feed systematic failures into incidents or new intents.

## AI assessment prompts

- What outcome is the AI expected to produce, and how can it fail?
- What exact prompt, model, retrieval, agent, or tool behavior changes?
- Which evaluation cases discriminate the old and new behavior?
- Can generated output trigger an action, and where is authorization enforced?
- What happens when the model is unavailable, uncertain, maliciously prompted, or wrong?
- Which production signal indicates degradation?

## Evidence expected

- Versioned behavior specification.
- Evaluation set provenance and coverage.
- Baseline and candidate results with limitations.
- Tool and permission boundary tests.
- Human-control and fallback evidence.
- Production monitoring and rollback decision.
