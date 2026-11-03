"""Grade every committed case against checker.evaluate. Read-only.

First check that section 7.4 in this checkout still hashes to the digest in
AGAINST, so a change to the rule cannot leave the cases green. Then, for each
case file: check that it is a candidate case pinned to that digest, resolve the
named Observed Effect record to its bytes, check the bytes against the pinned
SHA-256, build the checker input from `checker_input` alone, evaluate, and
compare the outcome with `expected`. The expectation never reaches the checker.
Nothing in the tree is written; any mismatch, missing record, hash mismatch or
case pinned to other text exits non-zero. `--summary FILE` appends a plain
account of the run to FILE, which CI shows on the run's summary page.

Records come only from the installed `agent-evidence-vectors` package: the
published corpus at the release requirements.txt pins by hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from importlib import metadata, resources
from typing import Any

import checker

HERE = os.path.dirname(os.path.abspath(__file__))

# The text every case is graded against: the SHA-256 of section 7.4, from its
# heading up to the next heading. A digest rather than a commit, because it can
# be checked against the paper in this checkout and it can change in the same
# commit as the text. Repinning to an amended 7.4 changes this constant and
# every case file together: `python run.py --text-digest` prints the new value.
AGAINST = {
    "document": "whitepapers/agent-containment.md",
    "section": "7.4",
    "text_sha256": "eecd5cc0181c305542da3ac754b9a3504990d4c1978aa40b947c18b764a43257",
}
STATUS = "candidate"
FAILURES = (
    checker.MalformedEvidence,
    checker.UnsupportedVerification,
    checker.CandidateInputError,
)


def section_digest(text: str) -> str | None:
    """The digest of section 7.4 in `text`, or None if it has no such section."""
    found = re.search(r"^### 7\.4 .*?(?=^#{1,3} )", text, re.MULTILINE | re.DOTALL)
    if found is None:
        return None
    return hashlib.sha256(found.group(0).rstrip(" \n-").encode("utf-8")).hexdigest()


def paper_digest() -> str | None:
    path = os.path.join(HERE, "..", "..", "..", AGAINST["document"])
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return section_digest(fh.read())


def text_problem(digest: str | None) -> str | None:
    """Why the cases cannot be read against this checkout's text, if they cannot."""
    if digest is None or digest == AGAINST["text_sha256"]:
        return None
    return (
        f"section {AGAINST['section']} hashes to {digest}, the cases pin "
        f"{AGAINST['text_sha256']}"
    )


def record_bytes(vector: str) -> bytes:
    published = resources.files("agent_evidence_vectors").joinpath(
        "corpora", "vectors-observed-effect", "statements", f"{vector}.json"
    )
    if not published.is_file():
        raise FileNotFoundError(f"record {vector} is not in the installed corpus")
    return published.read_bytes()


def build_input(case: dict[str, Any]) -> dict[str, Any]:
    spec = case["checker_input"]
    ref = spec["evidence"]["observed_effect"]
    raw = record_bytes(ref["vector"])
    digest = hashlib.sha256(raw).hexdigest()
    if digest != ref["sha256"]:
        raise ValueError(
            f"record {ref['vector']} hashes to {digest}, case pins {ref['sha256']}"
        )
    return {
        "property": spec["property"],
        "evidence": {"envelope": raw},
        "context": {
            "claim_ref": spec["context"]["claim_ref"],
            "observer_public_key": spec["context"]["observer_public_key"],
            "anchored_commitment_digest": spec["context"].get(
                "anchored_commitment_digest"
            ),
            "producer_capability": spec["context"].get("producer_capability"),
            "producer": spec["context"].get("producer"),
            "independence_evidence": spec["context"].get("independence_evidence"),
        },
    }


def outcome(checker_input: dict[str, Any]) -> dict[str, Any]:
    try:
        result = checker.evaluate(checker_input)
    except FAILURES as exc:
        out: dict[str, Any] = {
            "verdict": None,
            "processing_failure": type(exc).__name__,
        }
        if isinstance(exc, checker.MalformedEvidence):
            out["codes"] = exc.codes
        return out
    prop = checker_input["property"]
    ctx = checker_input["context"]
    expected_evaluation = {
        "property": {"name": prop["name"], "scope": prop["scope"]},
        "context": {
            "claim_ref": ctx["claim_ref"],
            "observer_public_key": ctx["observer_public_key"],
            "anchored_commitment_digest": ctx.get("anchored_commitment_digest"),
            "producer_capability": ctx.get("producer_capability"),
            "producer": ctx.get("producer"),
            "independence_evidence": ctx.get("independence_evidence"),
        },
    }
    if result.get("evaluation") != expected_evaluation:
        raise ValueError("checker result is not bound to the evaluated property and context")
    axis = "outcome" if "outcome" in result else "verdict"
    return {axis: result[axis], "unmet_obligation": result["unmet_obligation"]}


# Both case sets now read merged text, so both carry the same pin.
PINS = {"RFC189-OE-": AGAINST, "RFC189-IND-": AGAINST}


def check_pin(case: dict[str, Any]) -> None:
    case_id = case.get("id", "")
    against = next((pin for pre, pin in PINS.items() if case_id.startswith(pre)), None)
    if against is None:
        raise ValueError(f"case id {case_id!r} belongs to no pinned case set")
    if case.get("status") != STATUS or case.get("against") != against:
        raise ValueError(
            f"case is not a {STATUS} case pinned to section {against['section']} "
            f"at text {against['text_sha256'][:12]}"
        )


MEANING = {
    "ok": "The checker reached the answer the case expects.",
    "FAIL": (
        "The checker reached a different answer from the case. Either the checker "
        "changed or the expectation did; the clauses say which part of 7.4 decides."
    ),
    "ERROR": (
        "The case could not be graded: its record is missing, or the record's bytes "
        "miss the digest the case pins, or the case is pinned to other text. No "
        "verdict was reached."
    ),
}


def answer(got: dict[str, Any]) -> str:
    return str(got.get("verdict") or got.get("outcome") or got.get("processing_failure"))


def summary(rows: list[dict[str, Any]], digest: str | None, problem: str | None) -> str:
    good = sum(row["status"] == "ok" for row in rows)
    counts: dict[str, int] = {}
    for row in rows:
        if row["status"] == "ok":
            counts[row["answer"]] = counts.get(row["answer"], 0) + 1
    lines = [
        f"## Section 7.4 cases: {good} of {len(rows)} match their expectation",
        "",
        "Each case gives a checker one signed record and one question, and states the "
        "answer section 7.4 requires. The cases test what a checker may conclude from "
        "the evidence. They do not test a sandbox or a deployment, the fixtures are "
        "synthetic, and a pass here says nothing about whether any real system holds.",
        "",
        f"- Rule: `{AGAINST['document']}` section {AGAINST['section']}, text digest "
        f"`{AGAINST['text_sha256'][:12]}`",
        "- Text check: "
        + (
            "this checkout has no section 7.4 to compare, so this run did not check it"
            if digest is None
            else f"MISMATCH, {problem}"
            if problem
            else "section 7.4 in this checkout matches that digest"
        ),
        f"- Records: agent-evidence-vectors {metadata.version('agent-evidence-vectors')}, "
        "installed by hash; each case pins its record by SHA-256",
        "",
        "| Answer the checker reached | Cases |",
        "| --- | --- |",
    ]
    lines += [f"| `{name}` | {counts[name]} |" for name in sorted(counts)]
    lines += [
        "",
        "`pass` and `fail` settle the claim. `not_established` means the evidence cannot "
        "settle it, and names what is missing. `present`, `absent` and `pending` are "
        "observation states for an action's outcome. A processing failure means the "
        "input could not be evaluated, which is never a verdict.",
    ]
    bad = [row for row in rows if row["status"] != "ok"]
    if problem:
        lines += [
            "",
            f"**The rule changed.** {problem}. Read what changed in 7.4, decide whether "
            "any expectation moves, then repin with `python run.py --text-digest`.",
        ]
    if bad:
        lines += ["", "### Cases to look at", ""]
    for row in bad:
        lines.append(f"- **{row['id']}** ({row['status']}): {MEANING[row['status']]}")
        lines.append(f"  - Reached: `{row['got']}`")
        if row.get("want"):
            lines.append(f"  - Expected: `{row['want']}`")
        if row.get("clauses"):
            lines.append(f"  - Clauses: {', '.join(row['clauses'])}")
        if row.get("note"):
            lines.append(f"  - What the case tests: {row['note']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grade the section 7.4 cases.")
    parser.add_argument("--summary", metavar="FILE", help="append a plain account of the run")
    parser.add_argument(
        "--text-digest", action="store_true", help="print the digest of 7.4 in this checkout"
    )
    args = parser.parse_args(argv)
    digest = paper_digest()
    if args.text_digest:
        print(digest)
        return 0 if digest else 2
    problem = text_problem(digest)
    case_dir = os.path.join(HERE, "cases")
    names = sorted(n for n in os.listdir(case_dir) if n.endswith(".json"))
    if not names:
        print("no cases found", file=sys.stderr)
        return 2
    mismatches = 0
    rows: list[dict[str, Any]] = []
    for name in names:
        with open(os.path.join(case_dir, name), encoding="utf-8") as fh:
            case = json.load(fh)
        row = {
            "id": case.get("id", name),
            "clauses": case.get("clauses"),
            "note": case.get("note"),
        }
        rows.append(row)
        try:
            check_pin(case)
            got = outcome(build_input(case))
        except (OSError, ValueError, KeyError) as exc:
            print(f"ERROR {row['id']}: {exc}")
            row.update(status="ERROR", got=str(exc))
            mismatches += 1
            continue
        want = case["expected"]
        ok = got == want
        mismatches += not ok
        status = "ok  " if ok else "FAIL"
        print(f"{status} {case['id']}: {json.dumps(got, sort_keys=True)}")
        row.update(status=status.strip(), got=json.dumps(got, sort_keys=True), answer=answer(got))
        if not ok:
            print(f"     expected {json.dumps(want, sort_keys=True)}")
            row["want"] = json.dumps(want, sort_keys=True)
    print(f"{len(names) - mismatches} of {len(names)} cases match their expectation")
    if problem:
        print(f"TEXT {problem}")
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as fh:
            fh.write(summary(rows, digest, problem))
    return 1 if mismatches or problem else 0


if __name__ == "__main__":
    sys.exit(main())
