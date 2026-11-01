# Bounded evidence acquisition

1. Translate the audience decision into a list of *testable claims*. List at least one rival explanation per causal claim.
2. Map every claim to evidence types, source families and falsifiers before searching.
3. Rank data gaps by `decision_impact / max(1, retrieval_cost)` but retain critical priority whenever an unsupported assertion would flip the conclusion.
4. First run calculations with already available observations. An unknown cannot be fixed by a more attractive visual.
5. Preferred retrieval: issuer filings and explanatory materials; earnings Q&A; accounting scope/segment notes; peers with the *same period*; independent government/industry statistics. Search narrowly and avoid sources published after the as-of date.
6. Preserve retrieved metadata: issuer/source title, publication date, URL, reporting period, metric definition, unit, whether it is actual vs forecast, significant consolidation changes, and what it does NOT establish.
7. Find counterevidence. Cross-company comparisons are context, not identical experiments. Never attribute differences to one cause where FX exposure, accounting, business mix, geographies, and one-offs differ.
8. Stop when high-impact decision claims can be defended, or no credible obtainable source is available. Mark residual gaps clearly and downgrade the conclusion.
9. Re-run numerical and semantic QA when new facts change headlines. Every slide claim cites source IDs, not just a bibliography.
10. Present findings in Japanese by default while keeping this skill metadata and docs in English.

`research_gate.py` is intentionally offline/deterministic; retrieval is delegated to tools available to the host agent. If there is no browsing tool, stop on unfulfilled research rather than pretend to search.
