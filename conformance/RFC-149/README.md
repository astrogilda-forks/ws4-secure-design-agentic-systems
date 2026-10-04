# RFC-149 candidate cases: declaration to action

These cases serve the crosswalk gate in step 2 of [RFC-149's proposed work](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/1a1a2effdbddf1013680fea52e56ee190c171e69/RFCs/RFC-149.md#proposed-work-and-review) ([#210](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/210)). For each boundary, the gate names the exact artifact revision and subject join, the runtime verifier, and the result a consumer receives when independent observation or coverage is missing. Each case exercises one join on one published evidence record and states the consumer result for that join. The record's reader is pinned by hash.

## Requirements and cases stay separate

| Kind | Text | What a case may cite |
| --- | --- | --- |
| Adopted | [Section 7.4 of the containment paper](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/84604125869469926968acdf433501f87d1d1665/whitepapers/agent-containment.md#74-evidence-sufficiency-for-absence-claims), merged into `feat/containment` at `84604125` | clauses C1 to C6, under `requirements.adopted` |
| Proposed, not adopted | The step 2 gate of RFC-149 at `1a1a2eff` | `revision-and-subject-join`, `runtime-verifier`, `missing-evidence-result`, under `requirements.proposed` |

Every case is `candidate`. Its `consumer_result` is a candidate expectation for the crosswalk review, not a requirement. `run.py` checks the facts: each member's bytes match the pinned digest, and each pinned reader reaches the verdict the case states. It refuses a case that cites anything else as adopted or proposed.

## Cases

| Case | Boundary | Evidence | Reader | Consumer result | 7.4 | Gate |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | declaration to content | every role present, digests match, pinned signer | `verified` | `pass` | | join, verifier |
| 02 | declaration to content | one covered byte changed after signing | `failed` | `fail` | | join |
| 03 | declaration to content | valid signature by a key the consumer did not pin | `failed` | `fail` | | join, verifier |
| 04 | declaration to content | valid signature over a non-canonical encoding | `failed` | processing failure | C2 | join |
| 05 | declaration to content | trajectory pointer names a document the record did not hash | `failed` | `fail` | | join |
| 06 | declaration to content | a required artifact never captured | `not-established` | `not_established` / `content_coverage` | C1 | join, missing |
| 07 | declaration to content | an external subagent document the declaration does not cover | `not-established` | `not_established` / `dependency_coverage` | C1, C4 | join, missing |
| 08 | request to action | digest-bound request, permit, write observed independently | `valid`, authoritative | `pass` | C4, C5 | join, verifier |
| 09 | request to action | action changed after the decision, request digest left | `malformed` | processing failure | C2 | join |
| 10 | request to action | arguments declared not bindable | `valid`, voluntary | `not_established` / `invocation_binding` | C1, C5 | join, missing |
| 11 | decision to effect | deny, before and after roots equal | `valid`, authoritative | `pass` | C4 | verifier |
| 12 | decision to effect | deny, and a write observed anyway | `valid`, authoritative | `fail` | C3 | verifier |
| 13 | decision to effect | deny, the one write attributed to another request | `valid`, authoritative | `pass` | C5 | verifier |
| 14 | decision to effect | deny, and a write no request claims | `valid`, authoritative | `not_established` / `effect_attribution` | C1, C5 | verifier, missing |
| 15 | decision to effect | the agent's own vantage, no prior commitment | `valid`, voluntary | `not_established` / `observation_vantage` | C1, C3 | verifier, missing |
| 16 | decision to effect | effect edited to none and re-signed with the real key | `malformed` | processing failure | C2 | verifier |

Cases 01 to 07 read the [artifact-binding corpus](https://github.com/probityai/agent-evidence-vectors/tree/v0.16.0/vectors-artifact-binding): a signed manifest names each artifact of a run by role, path and digest. Cases 08 to 16 read the [agent audit record corpus](https://github.com/probityai/agent-evidence-vectors/tree/v0.16.0/vectors-agent-audit-record), the conformance set of [draft-gilda-wimse-agent-audit-record-01](https://datatracker.ietf.org/doc/draft-gilda-wimse-agent-audit-record/01/). That record keeps the decision beside the effect an observer derived from the declared scope.

The effect-to-invocation join and its coverage are covered by the [section 7.4 cases](https://github.com/astrogilda/ws4-secure-design-agentic-systems/tree/conformance/rfc-189-observed-effect/conformance/RFC-189), which are not repeated here. Cases 11, 14 and 15 there test binding, 03 and 19 coverage, 10 and 23 a self-reported write, and 20 an action outcome still `pending` after the window ends.

## Questions these cases put to the crosswalk

- Case 04: the reader refuses a valid signature over a non-canonical encoding as `failed`, while C2 makes malformed input a processing failure. The crosswalk needs to say which result a consumer receives.
- Case 03: a correctly signed manifest from a signer the relying party does not accept. Whether that is `fail` or `not_established` turns on the credential issuer and manifest signer boundary under [#99](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/99).
- No case covers the credential-to-manifest-revision join yet: instance correlation, freshness and revocation. Those cases follow the claim #99 defines.

## Running

```sh
cd conformance/RFC-149/declaration-to-action
python -m pip install --require-hashes -r requirements.txt
go install github.com/probityai/agent-evidence-vectors/cmd/aee-verify@v0.16.0
python run.py    # read-only; non-zero on any mismatch
```
