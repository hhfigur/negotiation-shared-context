# Skill: pm-release-review

## Purpose
Create a post-release review after a release is verified.
Usage: `/pm-release-review <RELEASE-ID>`

## Steps
1. Read `product/releases/current.md`
2. Read all briefs for in-scope items
3. Collect: shipped scope, metric movement, verified vs. released-but-unverified
4. Identify risks, issues, and follow-up actions
5. Create `product/release-reviews/<RELEASE-ID>.md`
6. Propose next release ID and initial scope (carry-forward items)
7. Output: review file path

---
**OUTPUT-SIGNAL:**
> RELEASE REVIEW COMPLETE — [RELEASE-ID] — [DATUM]
> Review: product/release-reviews/[RELEASE-ID].md
> Warte auf Bestätigung vom User bevor Archivierung.
