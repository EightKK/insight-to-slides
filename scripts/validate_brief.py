#!/usr/bin/env python3
"""Validate a communication brief: JSON Schema first, then semantic editorial rules.

Usage: python3 scripts/validate_brief.py communication-brief.json
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import EXIT_FAIL, EXIT_PASS, Parser, read_json, run, schema_errors

INTENTS = {"inform", "align", "decide", "explore"}
CLAIMS = {"fact", "interpretation", "hypothesis", "recommendation"}
ROLES = {"finding", "context", "comparison", "decision", "hypothesis", "recommendation", "summary", "reference", "appendix"}
LANGUAGE_TAG = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
JAPANESE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
ASCII_WORDS = re.compile(r"[A-Za-z]{2,}")


def output_language(data):
    """Return the requested language; missing language means Japanese."""
    doc = data.get("document") if isinstance(data, dict) else None
    raw = doc.get("output_language", "ja") if isinstance(doc, dict) else "ja"
    return raw if isinstance(raw, str) and LANGUAGE_TAG.fullmatch(raw) else "ja"


def _language_warning(text, location, language, warnings):
    """Only a heuristic; proper nouns and technical terms can be false positives."""
    if not isinstance(text, str) or not text.strip():
        return
    primary = language.split("-", 1)[0]
    if primary == "ja" and not JAPANESE.search(text):
        # Require a plausible English sentence; abbreviations/axis labels alone
        # should not be treated as definitive violations.
        if len(ASCII_WORDS.findall(text)) >= 3:
            warnings.append(f"{location}: possible English-only prose in Japanese output; review manually")
    elif primary == "en" and JAPANESE.search(text):
        warnings.append(f"{location}: possible untranslated Japanese in English output; review manually")


def catalog_ids():
    catalog = read_json(Path(__file__).resolve().parents[1] / "patterns" / "catalog.json")
    return {item["id"] for item in catalog["patterns"]}


def validate(data):
    """Return (errors, warnings). Schema errors are prefixed with 'schema:'."""
    errors, warnings = [], []
    if not isinstance(data, dict):
        return ["Top-level value must be a JSON object"], warnings
    errors.extend("schema: " + e for e in schema_errors(data, "communication-brief.schema.json"))
    try:
        _semantic_rules(data, errors, warnings)
    except (TypeError, AttributeError, KeyError) as exc:
        errors.append(f"semantic rules could not run on malformed input ({type(exc).__name__}: {exc}); fix schema errors first")
    return errors, warnings


def _semantic_rules(data, errors, warnings):
    known_patterns = catalog_ids()
    doc = data.get("document", {})
    if not isinstance(doc, dict):
        doc = {}
        errors.append("document must be an object")
    for field in ("title", "audience", "primary_question", "medium"):
        if not isinstance(doc.get(field), str) or not doc.get(field, "").strip():
            errors.append(f"document.{field} must be a non-empty string")
    if doc.get("intent") not in INTENTS:
        errors.append("document.intent is not a supported intent")
    if "output_language" in doc:
        lang = doc["output_language"]
        if not isinstance(lang, str) or not LANGUAGE_TAG.fullmatch(lang):
            errors.append("document.output_language must be a valid language tag (e.g. ja, en, ja-JP)")
    lang = output_language(data)
    # A conventional cover is identity metadata, NOT a substantive slide or action title.
    cover = doc.get("cover")
    if cover is not None:
        allowed_cover_fields = {"title", "subtitle", "reporting_period", "scope", "source_or_publication_date", "presenter", "organization"}
        if not isinstance(cover, dict) or not isinstance(cover.get("title"), str) or not cover["title"].strip():
            errors.append("document.cover.title must be a non-empty string when a cover is present")
        else:
            for key, value in cover.items():
                if key not in allowed_cover_fields:
                    errors.append(f"document.cover.{key} is not permitted: no takeaway or claim fields on a cover")
                elif not isinstance(value, str):
                    errors.append(f"document.cover.{key} must be a string")
                else:
                    _language_warning(value, f"document.cover.{key}", lang, warnings)
    for key in ("title", "audience", "primary_question", "decision_owner"):
        _language_warning(doc.get(key), f"document.{key}", lang, warnings)
    for key in ("key_assumptions", "limitations"):
        if isinstance(doc.get(key), list):
            for i, value in enumerate(doc[key]):
                _language_warning(value, f"document.{key}[{i}]", lang, warnings)

    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty array")
        evidence = []
    evidence_map = {}
    for i, ev in enumerate(evidence):
        if not isinstance(ev, dict):
            errors.append(f"evidence[{i}] must be an object")
            continue
        ev_id = ev.get("id")
        if not isinstance(ev_id, str) or not ev_id:
            errors.append(f"evidence[{i}] is missing an id")
            continue
        if ev_id in evidence_map:
            errors.append(f"Duplicate evidence id: {ev_id}")
        evidence_map[ev_id] = ev
        for field in ("statement", "source", "kind", "confidence"):
            if not isinstance(ev.get(field), str) or not ev[field].strip():
                errors.append(f"evidence[{i}].{field} must be non-empty")
        if ev.get("kind") == "calculation" and not ev.get("formula"):
            errors.append(f"Calculated evidence {ev_id} is missing a formula")
        if ev.get("source") in ("unknown", "不明", "未確認") and ev.get("confidence") == "high":
            warnings.append(f"{ev_id}: high confidence but unknown source")
        _language_warning(ev.get("statement"), f"evidence[{i}].statement", lang, warnings)
        if isinstance(ev.get("caveats"), list):
            for j, value in enumerate(ev["caveats"]):
                _language_warning(value, f"evidence[{i}].caveats[{j}]", lang, warnings)
    for ev_id, ev in evidence_map.items():
        for ref in ev.get("input_refs", []):
            if ref not in evidence_map:
                errors.append(f"Evidence {ev_id} references missing input {ref}")
            if ref == ev_id:
                errors.append(f"Evidence {ev_id} self-references its input")

    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        errors.append("slides must be a non-empty array")
        slides = []
    slide_ids = set()
    for i, slide in enumerate(slides):
        if not isinstance(slide, dict):
            errors.append(f"slides[{i}] must be an object")
            continue
        slide_id = slide.get("id", f"#{i}")
        if slide_id in slide_ids:
            errors.append(f"Duplicate slide id: {slide_id}")
        slide_ids.add(slide_id)
        if slide.get("role") not in ROLES:
            errors.append(f"{slide_id}: unsupported role")
        if slide.get("claim_type") not in CLAIMS:
            errors.append(f"{slide_id}: unsupported claim_type")
        for field in ("headline", "takeaway"):
            if not isinstance(slide.get(field), str) or not slide.get(field, "").strip():
                errors.append(f"{slide_id}: {field} is empty")
            _language_warning(slide.get(field), f"{slide_id}.{field}", lang, warnings)
        title = slide.get("headline")
        if not isinstance(title, str):
            title = ""
        else:
            if len(title) > 55:
                warnings.append(f"{slide_id}: long headline ({len(title)} characters); check projected legibility")
            if slide.get("role") not in ("reference", "appendix") and title.endswith(("について", "の概要", "の状況")):
                warnings.append(f"{slide_id}: topic-only Japanese headline; consider an action title")
        if slide.get("role") in ("reference", "appendix") and len(title) > 16:
            warnings.append(f"{slide_id}: reference slide title should be a short functional label")
        content_types = slide.get("reference_content_types")
        if content_types is not None:
            allowed_types = {"sources", "definitions", "scope", "caveats", "forecast", "comparison", "supporting_details"}
            if not isinstance(content_types, list) or not content_types or any(c not in allowed_types for c in content_types) or len(set(content_types)) != len(content_types):
                errors.append(f"{slide_id}: reference_content_types must be a nonempty unique list of allowed types")
            elif slide.get("role") == "reference" and lang.split("-", 1)[0] == "ja":
                expected_title = "出典" if set(content_types) == {"sources"} else "出典・注記"
                if title != expected_title:
                    warnings.append(f"{slide_id}: reference page title should be {expected_title} for the declared content types")
            elif slide.get("role") == "appendix" and lang.split("-", 1)[0] == "ja" and title != "付録":
                warnings.append(f"{slide_id}: appendix title should normally be 付録")
        if not slide.get("audit_tokens"):
            errors.append(f"{slide_id}: audit_tokens are required for render-to-brief verification")
        refs = slide.get("evidence_refs", [])
        if not isinstance(refs, list) or not refs or not all(isinstance(r, str) for r in refs):
            errors.append(f"{slide_id}: no evidence references")
        else:
            for ref in refs:
                if ref not in evidence_map:
                    errors.append(f"{slide_id}: unknown evidence id {ref}")
        visual = slide.get("visual")
        if not isinstance(visual, dict) or not all(visual.get(k) for k in ("pattern", "visual_focus", "design_notes")):
            errors.append(f"{slide_id}: visual requires pattern, visual_focus, and design_notes")
        else:
            if not visual.get("pattern_id"):
                errors.append(f"{slide_id}: visual.pattern_id is required")
            elif visual["pattern_id"] not in known_patterns:
                errors.append(f"{slide_id}: unknown visual.pattern_id {visual['pattern_id']}")
            for key in ("visual_focus", "design_notes"):
                _language_warning(visual.get(key), f"{slide_id}.visual.{key}", lang, warnings)
            for j, value in enumerate(visual.get("avoid", [])):
                _language_warning(value, f"{slide_id}.visual.avoid[{j}]", lang, warnings)
        for key in ("counterpoints", "uncertainties"):
            for j, value in enumerate(slide.get(key, [])):
                _language_warning(value, f"{slide_id}.{key}[{j}]", lang, warnings)
        if slide.get("role") == "decision":
            discussion = slide.get("discussion")
            if not isinstance(discussion, dict) or not discussion.get("question"):
                errors.append(f"{slide_id}: decision slide requires a specific question")
            elif not isinstance(discussion.get("options"), list) or len(discussion["options"]) < 2:
                errors.append(f"{slide_id}: decision slide requires at least two real options")
        discussion = slide.get("discussion")
        if isinstance(discussion, dict):
            for key in ("question", "next_action"):
                _language_warning(discussion.get(key), f"{slide_id}.discussion.{key}", lang, warnings)
            for key in ("options", "missing_information"):
                for j, value in enumerate(discussion.get(key, [])):
                    _language_warning(value, f"{slide_id}.discussion.{key}[{j}]", lang, warnings)
        if slide.get("claim_type") in ("hypothesis", "interpretation", "recommendation") and not (slide.get("uncertainties") or slide.get("counterpoints")):
            warnings.append(f"{slide_id}: interpretation, hypothesis, or recommendation lacks caveats")
    if doc.get("intent") == "decide" and not any(isinstance(s, dict) and s.get("role") == "decision" for s in slides):
        warnings.append("Decision intent but no decision slide")


def main(argv=None):
    ap = Parser(description=__doc__)
    ap.add_argument("brief")
    args = ap.parse_args(argv)
    data = read_json(args.brief)
    errors, warnings = validate(data)
    for msg in errors:
        print("ERROR:", msg)
    for msg in warnings:
        print("WARN:", msg)
    if not errors:
        print(f"PASS: brief valid ({len(warnings)} warning(s)); output_language={output_language(data)}.")
    return EXIT_FAIL if errors else EXIT_PASS


if __name__ == "__main__":
    run(main)
