"""Check every declaration-to-action case against the pinned reference readers.

Each case names one member of a published corpus, the reader that judges it,
the verdict that reader must reach, and the result a consumer receives under
the candidate crosswalk rule. This harness checks the parts that are facts:
the member's bytes match the digest the case pins, and the pinned reader
reaches the verdict the case states. The consumer result is the candidate
expectation the crosswalk review is asked to adopt or change; the harness
checks only that it is well formed and that each case keeps its adopted and
proposed requirements apart. Nothing is written; any mismatch exits non-zero.

Readers: `auditrecord` from the `agent-evidence-vectors` package, and
`aee-verify` (the Go reader at the same tag) for the artifact-binding corpus,
found on PATH or through $AEE_VERIFY.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from functools import cache
from importlib import resources
from typing import Any

from agent_evidence_vectors import auditrecord

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = "agent-evidence-vectors==0.16.0"
STATUS = "candidate"

# Adopted text: section 7.4 of the containment paper as merged through #219.
ADOPTED_COMMIT = "84604125869469926968acdf433501f87d1d1665"
ADOPTED_CLAUSES = frozenset({"C1", "C2", "C3", "C4", "C5", "C6"})
# Proposed text, not adopted: the crosswalk gate in step 2 of RFC-149's
# proposed work, at the head of #210 when these cases were written.
PROPOSED_COMMIT = "1a1a2effdbddf1013680fea52e56ee190c171e69"
PROPOSED_ITEMS = frozenset(
    {"revision-and-subject-join", "runtime-verifier", "missing-evidence-result"}
)
RESULTS = frozenset({"pass", "fail", "not_established", "pending", "processing_failure"})


def corpus(name: str) -> Any:
    return resources.files("agent_evidence_vectors").joinpath("corpora", name)


def manifest(name: str) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(corpus(name).joinpath("MANIFEST.json").read_text())
    return loaded


def entry(name: str, member: str) -> dict[str, Any]:
    for item in manifest(name)["vectors"]:
        if item["id"] == member:
            found: dict[str, Any] = item
            return found
    raise KeyError(f"{member} is not a member of {name} in {SOURCE}")


def member_bytes(name: str, member: str) -> bytes:
    item = entry(name, member)
    path = item.get("file") or item.get("manifest") or f"statements/{member}.json"
    data: bytes = corpus(name).joinpath(path).read_bytes()
    return data


@cache
def aee_verify_verdicts(name: str) -> dict[str, str]:
    binary = os.environ.get("AEE_VERIFY") or shutil.which("aee-verify")
    if not binary:
        raise FileNotFoundError("aee-verify is not on PATH and $AEE_VERIFY is unset")
    done = subprocess.run(
        [binary, "-json", str(corpus(name))], capture_output=True, text=True, check=True
    )
    report = json.loads(done.stdout)
    return {m["id"]: m["kind"] for m in report["members"]}


def read(case: dict[str, Any]) -> dict[str, Any]:
    ev = case["evidence"]
    name, member = ev["corpus"], ev["member"]
    if ev["reader"] == "aee-verify":
        return {"verdict": aee_verify_verdicts(name)[member]}
    raw = member_bytes(name, member)
    if ev["reader"] == "auditrecord":
        meta = manifest(name)
        report = auditrecord.verify(
            raw,
            auditrecord.Policy(
                predicate_type=meta["predicateType"],
                observer_public_key=meta["keys"]["observer"]["publicKey"],
            ),
        )
        out = {"verdict": report.verdict, "codes": report.codes}
        if report.verdict == "valid":
            out["tier"] = report.derived_tier
        return out
    raise ValueError(f"unknown reader {ev['reader']!r}")


def check(case: dict[str, Any]) -> list[str]:
    problems = []
    if case.get("status") != STATUS:
        problems.append(f"status is {case.get('status')!r}, not {STATUS!r}")
    ev = case["evidence"]
    if ev.get("source") != SOURCE:
        problems.append(f"source is {ev.get('source')!r}, not {SOURCE!r}")
    digest = hashlib.sha256(member_bytes(ev["corpus"], ev["member"])).hexdigest()
    if digest != ev["sha256"]:
        problems.append(f"member hashes to {digest}, case pins {ev['sha256']}")
    got = read(case)
    if got != case["reader_expected"]:
        problems.append(f"reader returned {got}, case expects {case['reader_expected']}")
    result = case["consumer_result"]
    if result.get("result") not in RESULTS:
        problems.append(f"consumer result {result.get('result')!r} is not one of {sorted(RESULTS)}")
    is_open = result.get("result") in {"not_established", "pending"}
    if is_open and not result.get("unmet_obligation"):
        problems.append("an open consumer result must name its unmet obligation")
    reqs = case["requirements"]
    adopted = reqs["adopted"]
    if adopted["commit"] != ADOPTED_COMMIT or not set(adopted["clauses"]) <= ADOPTED_CLAUSES:
        problems.append("adopted requirements must cite section 7.4 clauses at 84604125")
    proposed = reqs["proposed"]
    if proposed["commit"] != PROPOSED_COMMIT or not set(proposed["items"]) <= PROPOSED_ITEMS:
        problems.append("proposed requirements must cite RFC-149 gate items at 1a1a2eff")
    return problems


def main() -> int:
    case_dir = os.path.join(HERE, "cases")
    names = sorted(n for n in os.listdir(case_dir) if n.endswith(".json"))
    if not names:
        print("no cases found", file=sys.stderr)
        return 2
    bad = 0
    for name in names:
        with open(os.path.join(case_dir, name), encoding="utf-8") as fh:
            case = json.load(fh)
        try:
            problems = check(case)
        except (OSError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
            problems = [f"{type(exc).__name__}: {exc}"]
        bad += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} {case.get('id', name)}")
        for problem in problems:
            print(f"     {problem}")
    print(f"{len(names) - bad} of {len(names)} cases check against {SOURCE}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
