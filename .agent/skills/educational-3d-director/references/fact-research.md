# Fact Discovery & Verification — editorial gate

Use when the user asks for unusual facts, mysteries, unknown mechanisms, surprising history, viral educational topics, or broad niche discovery.

## Workflow
1. Define audience, geography, language, and exclusions. Generate candidate **questions**, not sensational claims.
2. Research each candidate with reputable primary evidence when browsing/research tools are available: official scientific bodies, peer-reviewed literature, manufacturer documentation for its own products, museums, original records. Secondary journalism may help identify leads, not serve as sole authority for contested facts.
3. Preserve source URL, publisher, title, publication/access date if available, and exact claim supported. Do not invent citations or assert that browsing was performed unless it was.
4. Separate `verified`, `qualified`, `disputed`, `unverified`. Reject fabricated quotes, made-up numbers, deceptive generalizations. Mark historical reconstructions and model-specific details accurately.
5. Score topics with the bundled `scripts/rank_topics.py` and record editorial judgments. A high score does not override failing fact-check.
6. For chosen topic, create a claim-to-shot evidence map. Every factual reveal should have at least one supporting source; contested or high-stakes assertions need stronger corroboration.
7. Translate the fact into a visual narrative: familiar experience → mystery → hidden mechanism → reveal → nuance/limit → satisfying no-CTA ending when requested.
8. Explicitly label illustrative visualization vs exact reconstruction. Do not animate an unsupported speculative mechanism as fact.

## Credibility traps
- "Nobody knows this", "100% proven", "scientists were shocked" and unsupported superlatives.
- Trending social-video claims passed off as science, surprising correlations presented as causality.
- Model-specific internals asserted from an illustrative cross-section.
- Historical myths that need dated primary records.
- Human health claims without medical-quality documentation.

## Source availability
The skill DOES NOT itself browse the internet. Use the code agent's actual authorized web/research integration when available. If unavailable, produce `research_required` status and a source collection plan; do not mark claims verified.

## Suggested artifacts
- `research/topic_candidates.json` (scored leads)
- `research/claims.json` (supported assertions and caveats)
- `research/sources.json` (bibliographic URL list)
- `research/research_notes.md` (uncertainties, decisions, rejected myths)

Use `scripts/validate_research.py` before moving to final storyboard. Source URLs are metadata, not proof that their content was checked.
