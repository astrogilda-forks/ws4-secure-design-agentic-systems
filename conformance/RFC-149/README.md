# RFC-149 candidate cases: declaration to action

These cases serve the crosswalk gate in step 2 of [RFC-149's proposed work](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/1a1a2effdbddf1013680fea52e56ee190c171e69/RFCs/RFC-149.md#proposed-work-and-review) ([#210](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/210), [#149](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/149)). For each boundary, the gate names the exact revision and subject join, the runtime verifier, and the result a consumer receives when independent observation or coverage is missing. Each case starts from a declaration, ends at an action or the evidence for one, and states that result. Nothing here changes RFC-149 or the containment text.

## Merged text and proposed text stay separate

| Text | Status | What a case may cite |
| --- | --- | --- |
| Section 7 of the containment draft at [`84604125`](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/84604125869469926968acdf433501f87d1d1665/whitepapers/agent-containment.md), the head of `feat/containment` after #219 | merged into the working draft; the paper is not yet approved | `7.1`, `7.2`, `7.4 C1` to `7.4 C6`, under `requirements.merged` |
| The step 2 gate of RFC-149 at `1a1a2eff` | proposed scope, under review on #210 | `revision-and-subject-join`, `runtime-verifier`, `missing-evidence-result`, under `requirements.proposed` |

Every case is `candidate`. Its `consumer_result.decided_by` says whether merged clauses already decide the result (`merged`) or whether it waits on a boundary the crosswalk review has to settle (`proposed`). `run.py` checks the facts: each member's bytes match the pinned digest, each pinned reader reaches the stated verdict, and a result decided by merged text cites a merged clause.

## Gate items per join

| Join | Revision and subject join | Runtime verifier | Result when observation or coverage is missing |
| --- | --- | --- | --- |
| D-C: manifest to deployed content | each artifact named by role, path and digest in a signed manifest from an accepted signer | a reader that rehashes the deployed files against the manifest (`aee-verify` here) | `not_established` with the missing artifact or dependency |
| M-R: manifest to runtime and action evidence | the declaration in force at the invocation, anchored before it and bound to it | the checker that compares execution with the authority in force (7.2) and grades absence claims (7.4) | `not_established` with the missing premise: declaration, version binding, execution evidence, coverage, vantage or invocation binding |
| C-M: credential to manifest | the credential's digest reference to a manifest revision, and the instance it names | to be named in the crosswalk review (the #99 boundary) | `not_established` for the instance when only the digest matches |
| O-M: ODIS to manifest | the registration record or Passport reference to a manifest revision | to be named in the crosswalk review (the ODIS boundary) | the access decision stays a decision; runtime binding stays `not_established` without evidence |

## Cases that run

| Case | Join | Evidence | Reader | Consumer result | Decided by | Merged clauses |
| --- | --- | --- | --- | --- | --- | --- |
| D2A-01 | D-C | every role present, digests match, pinned signer | `verified` | `pass` | proposed | |
| D2A-02 | D-C | one covered byte changed after signing | `failed` | `fail` | proposed | |
| D2A-03 | D-C, C-M | valid signature by a key the consumer did not pin | `failed` | `fail` | proposed | |
| D2A-04 | D-C | valid signature over a non-canonical encoding | `failed` | processing failure | proposed | 7.4 C2 |
| D2A-05 | D-C | trajectory pointer names a document the record did not hash | `failed` | `fail` | proposed | |
| D2A-06 | D-C, C-M | a required artifact never captured | `not-established` | `not_established` / `content_coverage` | merged | 7.2, 7.4 C1 |
| D2A-07 | D-C | an external subagent document the manifest does not cover | `not-established` | `not_established` / `dependency_coverage` | merged | 7.4 C1, C4 |
| D2A-08 | M-R | digest-bound request, permit, write observed independently | `valid`, authoritative | `pass` | merged | 7.2, 7.4 C4, C5 |
| D2A-09 | M-R | action changed after the decision, request digest left | `malformed` | processing failure | merged | 7.4 C2 |
| D2A-10 | M-R | arguments declared not bindable | `valid`, voluntary | `not_established` / `invocation_binding` | merged | 7.2, 7.4 C1, C5 |
| D2A-11 | M-R | deny, before and after roots equal | `valid`, authoritative | `pass` | merged | 7.2, 7.4 C4 |
| D2A-12 | M-R | deny, and a write observed anyway | `valid`, authoritative | `fail` | merged | 7.2, 7.4 C3 |
| D2A-13 | M-R | deny, the one write attributed to another request | `valid`, authoritative | `pass` | merged | 7.4 C5 |
| D2A-14 | M-R | deny, and a write no request claims | `valid`, authoritative | `not_established` / `effect_attribution` | merged | 7.4 C1, C5 |
| D2A-15 | M-R | the agent's own vantage, no prior commitment | `valid`, voluntary | `not_established` / `observation_vantage` | merged | 7.4 C1, C3 |
| D2A-16 | M-R | effect edited to none and re-signed with the real key | `malformed` | processing failure | merged | 7.4 C2 |

Cases D2A-01 to D2A-07 read the [artifact-binding corpus](https://github.com/probityai/agent-evidence-vectors/tree/v0.16.0/vectors-artifact-binding): a signed manifest names each artifact of a run by role, path and digest. It runs the content checks a manifest revision needs, on an evaluation-run manifest rather than an Agent Manifest profile. Cases D2A-08 to D2A-16 read the [agent audit record corpus](https://github.com/probityai/agent-evidence-vectors/tree/v0.16.0/vectors-agent-audit-record), the conformance set of [draft-gilda-wimse-agent-audit-record-01](https://datatracker.ietf.org/doc/draft-gilda-wimse-agent-audit-record/01/), whose record keeps the decision beside the effect an observer derived from the declared scope.

The M-R absence claims also run as the [section 7.4 cases](https://github.com/astrogilda-forks/ws4-secure-design-agentic-systems/tree/conformance/rfc-189-observed-effect/conformance/RFC-189): binding (11, 14, 15), coverage (03, 19), write visibility (16 to 18), a self-reported write (10, 23), processing failures (06, 07, 13), and an action outcome still `pending` after the window ends (20, 22).

## Cases from merged text without a fixture yet

| Case | Join | Declaration | Action or evidence | Consumer result | Merged clause |
| --- | --- | --- | --- | --- | --- |
| D2A-17 | M-R | declaration D in force at the invocation, anchored before it | invocation of a tool inside D's declared set | membership established; authorization and benign intent not established by membership | 7.2 |
| D2A-18 | M-R | D as in D2A-17 | executed capability outside D's declared set | a discrepancy requiring investigation, never a match | 7.2 |
| D2A-19 | M-R | a declaration first produced after the action | any invocation | `not_established` / declaration in force before the invocation | 7.2 |
| D2A-20 | M-R | D available | the runtime record names no revision of D, or another one | `not_established` / version binding | 7.2 |
| D2A-21 | M-R | D and its version binding available | no execution evidence for the invocation | `not_established` / execution evidence; never a match or a benign tuning example | 7.2 |
| D2A-22 | M-R | D | request blocked by enforcement | attempt and enforcement decision established; execution and the absence of partial effects not established | 7.2 |
| D2A-23 | M-R | D names a runtime identity or attestation reference | attestation unavailable in this deployment shape | field present as `not-available` with its reason; `not_established` when availability cannot be established | 7.1 |

## Candidate cases for the crosswalk review

| Case | Join | Declaration | Action or evidence | Proposed result | Boundary it waits on |
| --- | --- | --- | --- | --- | --- |
| D2A-24 | C-M | credential for instance X references manifest revision D by digest; both issuers accepted | runtime evidence from instance Y running D | `not_established` for X: a matching digest does not bind the instance | subject and instance correlation (#99); follows 7.4 C5 if the instance is the bound subject |
| D2A-25 | C-M | credential references D by name or a mutable tag | any action | processing failure for an ambiguous reference, never a match | unambiguous content references (RFC-149 scope) |
| D2A-26 | C-M | D revoked or superseded before the action; the credential still references D | action after the revocation | `fail` when revocation before the action is established; `not_established` / freshness when revocation status at action time is unavailable | freshness and revocation (#99) |
| D2A-27 | O-M | registration record or Passport referencing D; an ODIS component grants access | no evidence binding the running instance to D | the access decision recorded as a decision; runtime binding to D `not_established` | which component verifies runtime binding and which decides access |
| D2A-28 | O-M | registration record and D disagree on the tool set | action uses a tool in the registration record but not in D | a discrepancy against D under 7.2; which declaration governs is open | overlap of the registration record and Passport with the manifest |
| D2A-29 | O-M, M-R | delegation created at runtime, outside D | delegated action | judged against the runtime delegation record, not D; `not_established` when that record is missing | declared content versus later runtime artifacts (RFC-149 scope) |

D2A-03, D2A-06 and D2A-02 already run the signer-acceptance, required-content and digest-mismatch versions of the C-M join on a signed manifest.

## Questions these cases put to the crosswalk

- D2A-04: the reader refuses a valid signature over a non-canonical encoding as `failed`, while 7.4 C2 makes malformed input a processing failure. The crosswalk has to say which result a consumer receives.
- D2A-03: a correctly signed manifest from a signer the relying party does not accept. Whether that is `fail` or `not_established` turns on the credential issuer and manifest signer boundary under [#99](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/99).

Fixtures for D2A-17 to D2A-29 follow the same shape as the cases that run: checker input held apart from the expected result (7.4 C6), records resolved by identifier from the hash-pinned package, graded read-only. A candidate moves to the merged-text tables when the crosswalk review settles its boundary.

## Running

```sh
cd conformance/RFC-149/declaration-to-action
python -m pip install --require-hashes -r requirements.txt
go install github.com/probityai/agent-evidence-vectors/cmd/aee-verify@v0.16.0
python run.py    # read-only; non-zero on any mismatch
```
