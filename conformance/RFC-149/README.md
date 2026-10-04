# RFC-149 crosswalk: declaration-to-action cases

These cases exercise the Manifest/Credentials/ODIS crosswalk named in step 2 of Proposed work in [RFC-149 at `cfeecc2`](https://github.com/imran-siddique/ws4-secure-design-agentic-systems/blob/cfeecc2cae96e7b220ebffec106d44a1830ef1dc/RFCs/RFC-149.md) ([#210](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/210), issue [#149](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/149)). Each case starts from a declaration and ends at an action or the evidence for one, and states the result a consumer receives, including the result when evidence is missing.

Expected results are read from section 7 of the containment draft at [`8460412`](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/84604125869469926968acdf433501f87d1d1665/whitepapers/agent-containment.md), the head of `feat/containment` after [#219](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/219) merged §7.4. That draft is a working draft and is not yet approved. Nothing here changes RFC-149 or the containment text.

## Two lists, kept apart

**Required by merged text** means the expected result follows from a clause merged into the containment draft at `8460412` (§7, §7.1, §7.2 or §7.4). A manifest revision is one kind of declaration, so these clauses already decide the result.

**Candidate** means the result depends on a boundary RFC-149 leaves to the crosswalk review: subject and instance correlation, issuer acceptance, freshness and revocation, unambiguous content references, and which ODIS component verifies runtime binding. The expected result shown is a proposal for that review.

## Results used

`pass` and `fail` for an absence claim; `not_established` with the missing premise or unmet obligation (§7, §7.4 C1); `pending` for an action whose outcome is unknown, which stays `pending` when the reporting window ends (§7); a processing failure for malformed input, an unsupported verification path, a parser failure or an internal verifier error, which is never `not_established` (§7.4 C2); a discrepancy for executed capability outside the declared set (§7.2).

## Gate items per join

RFC-149 step 2 asks each boundary to name the revision and subject join, the runtime verifier, and the consumer result when independent observation or coverage is missing.

| Join | Revision and subject join | Runtime verifier | Result when observation or coverage is missing |
| --- | --- | --- | --- |
| M-R: Manifest to runtime and action evidence | the manifest revision in force at the invocation, anchored before it, bound to that invocation | the checker that compares execution with the authority in force (§7.2) and grades absence claims (§7.4) | `not_established` with the missing premise: declaration, version binding, execution evidence, coverage, vantage or invocation binding |
| C-M: Credential to Manifest | the credential's reference to a manifest revision by digest, and the instance the credential names | to be named in the crosswalk review (#99 boundary) | `not_established` for the instance when only the digest matches (candidate) |
| O-M: ODIS to Manifest | the registration record or Passport reference to a manifest revision | to be named in the crosswalk review (ODIS boundary) | the access decision is recorded as a decision; runtime binding stays `not_established` without evidence (candidate) |

## Cases required by merged text

`RFC189-OE-nn` cases run today. The harness at [`31fa3d2`](https://github.com/astrogilda/ws4-secure-design-agentic-systems/tree/31fa3d2b706a2824a7eb184e42b306893f35aeb2/conformance/RFC-189/observed-effect) grades them read-only against signed records from `agent-evidence-vectors==0.13.0`, pinned by hash; 17 of 17 match. Those cases stipulate the anchored prior commitment and write visibility for the invocation; they test how a verifier uses those premises, not their provenance. "Fixture to write" marks a case with no executable fixture yet.

| ID | Join | Declaration | Action or evidence | Expected result | Source | Runnable |
| --- | --- | --- | --- | --- | --- | --- |
| DA-01 | M-R | capability declaration D in force at the invocation, anchored before it | invocation of a tool inside D's declared set | membership established; authorization and benign intent not established by membership | §7.2 | fixture to write |
| DA-02 | M-R | D as in DA-01 | executed capability outside D's declared set | discrepancy requiring investigation, never a match | §7.2 | fixture to write |
| DA-03 | M-R | a declaration first produced after the action | any invocation | `not_established`, missing premise: a declaration in force before the invocation | §7.2 | fixture to write |
| DA-04 | M-R | D available | runtime record names no revision of D, or another revision | `not_established`, missing premise: version binding | §7.2 | fixture to write |
| DA-05 | M-R | D and its version binding available | no execution evidence for the invocation | `not_established`, missing premise: execution evidence; not a match and not a benign example for tuning | §7.2 | fixture to write |
| DA-06 | M-R | D | request blocked by enforcement | the request and the enforcement decision are established; successful execution and the absence of partial effects are not | §7.2 | fixture to write |
| DA-07 | M-R | D | provider action with an unknown outcome when the window closes | `pending`, reported as not verified by the end of the window with its duration; never `not_established` | §7, §7.4 C1 | fixture to write |
| DA-08 | M-R | D's prior commitment anchored for the invocation; claim: no write under the declared path scope | independent observation covering the interval, write visibility for this invocation, no write seen | `pass` | §7.4 C4 | RFC189-OE-01 (`v162352770f2f6c1c`) |
| DA-09 | M-R | as DA-08 | a write observed in scope, coverage incomplete | `fail` | §7.4 C3 | RFC189-OE-02 (`v1c6fdd82db5229e4`), RFC189-OE-05 (`vd5e05b0f5d3cde4e`) |
| DA-10 | M-R | as DA-08 | no write seen; a named gap inside the claimed scope | `not_established` / `observation_coverage` | §7.4 C1, C4 | RFC189-OE-03 (`v5b9ea5001ad5ce1a`) |
| DA-11 | M-R | as DA-08 | the agent's own signed record reports writes; no independent observation | `not_established` / `observation_vantage` | §7.4 C3 | RFC189-OE-10 (`v68921dec001a6df3`) |
| DA-12 | M-R | prior commitment anchored for invocation A | record with a matching interval ID whose signed prior commitment belongs to another invocation | `not_established` / `invocation_binding` | §7.4 C5 | RFC189-OE-14 (`v162352770f2f6c1c`) |
| DA-13 | M-R | no prior commitment anchored for the invocation | complete record with a matching interval ID | `not_established` / `invocation_binding` | §7.4 C5 | RFC189-OE-15 (`v162352770f2f6c1c`) |
| DA-14 | M-R | as DA-08 | complete record, but write visibility established for another invocation, or not at all | `not_established` / `producer_capability_coverage` | §7.4 C4, C5 | RFC189-OE-16, RFC189-OE-17 (`v162352770f2f6c1c`) |
| DA-15 | M-R | any | malformed record, unsupported property or unsupported mapping | processing failure, never `not_established` | §7.4 C2, §7.2 | RFC189-OE-06 (`v1cccb4774a282210`), RFC189-OE-07 (`v6e71bd22b5d75d1c`), RFC189-OE-13 |
| DA-16 | M-R | D names a runtime identity or attestation reference | attestation unavailable in this deployment shape | field present as `not-available` with its reason; `not_established` when availability cannot be established | §7.1 | fixture to write |

## Candidate cases

| ID | Join | Declaration | Action or evidence | Proposed result | Boundary it depends on | Runnable |
| --- | --- | --- | --- | --- | --- | --- |
| DA-17 | C-M | credential for instance X references manifest revision D by digest; both issuers accepted | runtime evidence from instance Y running D | `not_established` for X: a matching digest does not bind the instance | subject and instance correlation (#99 row); follows §7.4 C5 if the instance is the bound subject | fixture to write |
| DA-18 | C-M | credential references D by name or a mutable tag, not by digest | any action | processing failure for an ambiguous reference, never a match | unambiguous content references (RFC-149 Scope) | fixture to write |
| DA-19 | C-M | D carries a valid signature by a key outside the relying party's trust policy | any action | integrity and signer attribution established; signer authorization fails | independent acceptance of credential and manifest issuers | same check on an artifact-binding/v1 manifest: `vee1d041fe793404e` |
| DA-20 | C-M | D revoked or superseded before the action; credential still references D | action after the revocation | `fail` when revocation before the action is established; `not_established` / freshness when revocation status at action time is unavailable | freshness and revocation responsibility (#99 row) | fixture to write |
| DA-21 | C-M, O-M | D names a required content item, such as a tool definition | the presented content lacks that item | `not_established`, missing premise: the required item; never a pass | which content needs binding (reuse analysis) | same check on an artifact-binding/v1 manifest: `v63555b6f69adb453` |
| DA-22 | C-M, O-M | D's digest for a covered content item | presented bytes differ from the digest | `fail` | content reference and signature coverage profile | same check on an artifact-binding/v1 manifest: `vb8a8df5360bc6f37` |
| DA-23 | O-M | registration record or Passport carrying a reference to D; an ODIS component grants access | no evidence binding the running instance to D | access decision recorded as a decision; runtime binding to D `not_established` | which component verifies runtime binding and which makes the access decision | fixture to write |
| DA-24 | O-M | registration record and D disagree on the tool set | action uses a tool in the registration record but not in D | discrepancy against D under §7.2; which declaration governs is open | overlap of the registration record and Passport with the manifest | fixture to write |
| DA-25 | O-M, M-R | delegation created at runtime, outside D | delegated action | judged against the runtime delegation record, not D; `not_established` when that record is missing | declared content versus later runtime artifacts (RFC-149 Scope) | fixture to write |

The artifact-binding members ship in `agent-evidence-vectors==0.16.0` ([corpus](https://github.com/probityai/agent-evidence-vectors/tree/v0.16.0/vectors-artifact-binding)) and are graded by `aee-verify` from that repository. They run the same checks over a signed evaluation-artifact manifest; they are evidence for the check, not a manifest profile.

## Next

Fixtures for the "fixture to write" rows follow the RFC189-OE shape: checker input held apart from the expected result (§7.4 C6), records resolved by identifier from a hash-pinned package, graded read-only. A candidate case moves to the required list when the crosswalk review settles the boundary it depends on.
