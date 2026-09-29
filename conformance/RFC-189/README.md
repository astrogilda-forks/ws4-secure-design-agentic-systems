# RFC-189 conformance: what a verifier may conclude when evidence is absent

These are executable cases for the [RFC-189 draft](https://github.com/astrogilda/ws4-secure-design-agentic-systems/blob/rfc/189-evidence-sufficiency/RFCs/RFC-189.md) and [issue #189](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189). Every case is `candidate_against_proposed` and carries `expected_if_adopted` until WS4 adopts a rule.

Proposed conformance leads: @aeoess and @astrogilda ([proposal](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5827010158), [Imran's reply](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5827685232)).

## The rule, clause by clause

C1-C6 come from [#189](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189). C7 and C8 remain open proposals. The case files cite these IDs.

| ID | Clause | Source |
| --- | --- | --- |
| C1 | `not_established` is a property verdict. A verifier returns it only after the applicable verification ran, when the admissible evidence justifies neither `pass` nor `fail`. It names the unmet obligation and stays bound to the property and the evaluation context. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5629517996), [darklordVirtual](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5630431104) |
| C2 | Malformed input, unsupported verification, parser failure and internal verifier error are processing failures, not `not_established`. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5629517996), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5671639059) |
| C3 | An admissible observation of the prohibited event inside the scope can settle `fail` without complete coverage. No observed event without established coverage is `not_established`. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5672256489) |
| C4 | A negative over a scope passes only when visibility and observation completeness are both established for that same scope. An empty field needs the same checks as a missing one. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5702083982), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5739339967) |
| C5 | Coverage is bound to the claim it covers. Coverage of one claim, or of a narrower scope, does not establish completeness for another. | [chernistry](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5710166163), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5745298467) |
| C6 | Checker input and harness expectation stay structurally separate. | [darklordVirtual](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5630431104), [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5638613689) |
| C7 (open) | An observation that declares incomplete coverage without locating its gap is malformed; explicit unknown coverage can remain `not_established`. | [astrogilda](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5827010158) |
| C8 (open) | A claim of independent observation made from the observed party's own vantage is refused. It supports neither `pass` nor `fail`. | proposed here, case 08 |

The containment paper's section 7 states the same boundary for evidence records: missing visibility or incomplete observation is `not_established` with its missing premise, and malformed records stay visible as processing failures. These cases exercise both texts.

## Two case sets, one rule

| Directory | Evidence | Obligations it exercises |
| --- | --- | --- |
| [aps-conformance-suite cosai-ws4-189-evidence-sufficiency](https://github.com/Agent-Authority-Conformance/aps-conformance-suite/tree/main/interop/cosai-ws4-189-evidence-sufficiency) | producer audit records (SINK-01 to SINK-03) | `producer_capability_coverage`, `observation_coverage` |
| [observed-effect/](https://github.com/astrogilda/ws4-secure-design-agentic-systems/tree/conformance/rfc-189-observed-effect/conformance/RFC-189/observed-effect) | signed Observed Effect records from [agent-evidence-vectors](https://github.com/probityai/agent-evidence-vectors/tree/main/vectors-observed-effect) | `observation_coverage`, `observation_vantage` |

An Observed Effect record states what an observer saw change during one interval, from a vantage the observed party cannot address. It carries:

- the path scope it watched
- the gaps it did not watch
- each write it saw

The reference verifier in the [agent-evidence-vectors](https://pypi.org/project/agent-evidence-vectors/) package decides whether a record is admissible, checking its signatures, the observer's prior commitment and the consistency of its coverage declaration before the checker sees it. The checker here decides only what the RFC decides: what the admitted record lets a verifier conclude.

`observation_vantage` is the [agent-evidence-vocabulary](https://github.com/probityai/agent-evidence-vocabulary/blob/main/vocabulary.yaml) term for who observed: whether every input a claim depends on came from a vantage the observed party could neither forge nor suppress, such as a network boundary, syscall supervision or a hypervisor's read of guest state. A record the observed party could have written or suppressed is not independent evidence of what it asserts. Case 08 is that record.

## Cases

| Case | Record | Expected if adopted | Clauses |
| --- | --- | --- | --- |
| 01 | read-only interval, complete coverage | `pass` | C4 |
| 02 | two writes observed in scope | `fail` | C3 |
| 03 | no write seen, a named gap inside the scope | `not_established` / `observation_coverage` | C1, C4 |
| 04 | record 03, claim narrowed to a path the gap does not touch | `pass` | C4, C5 |
| 05 | a named gap, and a write observed in scope anyway | `fail` | C3 |
| 06 | incomplete coverage, no gap named | processing failure, `coverage-incomplete-without-gaps` | C2, C7 |
| 07 | complete coverage claimed, gap named in scope | processing failure, `coverage-self-contradictory` | C2 |
| 08 | the observed party's own record claiming independence | `not_established` / `observation_vantage` | C1, C8 |
| 09 | record 03 claiming independence over its own gap | `not_established` / `observation_coverage` | C1, C4 |
| 10 | a valid self-reported record that reports writes | `not_established` / `observation_vantage` | C1, O1 |
| 11 | record 01 offered for a different interval | `not_established` / `observation_coverage` | C5 |
| 12 | record 01 asked about a wider scope than it watched | `not_established` / `observation_coverage` | C5 |
| 13 | a property the checker does not implement | processing failure, `UnsupportedVerification` | C2 |

Cases 03, 04 and 05 are the reason naming a gap matters: in all three the checker reads valid records that name /srv/app/vendor/ as unobserved, and it reaches three different verdicts. The same record cannot support "nothing changed under /srv/app/", yet it fully supports "nothing changed under /srv/app/src/", and a write it did see still settles `fail`.

## Open questions for the rule text

- O1: Does a record at the observed party's own vantage that reports an effect in scope settle `fail`, as an admission, or stay `not_established`? Case 10 takes the second reading.

- O2: A record the reference verifier refuses as `invalid` (coherent, but its own rules reject its claim) is graded `not_established` with the obligation its refusal names (cases 08, 09). Should a refused claim of independence also be reported as its own finding?

## Running

```sh
cd conformance/RFC-189/observed-effect
python -m pip install --require-hashes -r requirements.txt
agent-evidence-vectors --corpus vectors-observed-effect   # the pinned corpus behaves as its manifest declares
python run.py                      # grades every case, read-only, non-zero on any mismatch
python -m unittest test_checker    # harness and checker regressions
```

`run.py` resolves each record by its identifier from the installed corpus, checks it against the SHA-256 digest the case pins, and passes the checker only the `checker_input`. It never writes. Every record comes from the published release that `requirements.txt` pins by hash; nothing is copied into this directory.
