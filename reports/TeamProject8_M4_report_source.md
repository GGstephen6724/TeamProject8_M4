

# Evaluated + User-Tested Agent

TeamProject8_M4

Team 8: George Stephen and Manuel Rosales
CEN 4930 AI Agent Studio | Fall 2026
Prepared November 18, 2026

DRAFT - the engineering evaluation is real; five rehearsal scenarios are fictional. Required real external-user sessions are not complete.

Repository and provenance

Canonical team repository: https://github.com/GGstephen6724/TeamProject8_M4. Work starts from George Stephen's November 18 commit d55baf6a, whose parent is the actual M3 commit 8a6d910. The inherited local checkout is named TeamProject8_M2; its history is preserved. New M4 changes use their actual current dates.

This document distinguishes teammate-reported results, newly executed tests, measured engineering regressions, synthetic rehearsal material, and missing human evidence. It is not a claim that the whole milestone is complete.



# 1. The committed evaluation protocol

M3 committed ten cases, three runs per case, a majority-of-three case rule, a critic threshold, tracing, and manual review of safety cases TC03, TC07 and TC08. This evaluation retains the same ten scenarios and expected listing sets. Each run isolates the job fixture and preferences in a temporary directory. TC05 actually restarts MCP before reusing the same preference file; TC09 includes both missing and malformed database variants.

A run passes only when its deterministic checks pass and every applicable critic dimension is at least 4/5. A case passes with at least two successful runs. The original overall gate was at least 80% case pass rate, zero fabricated released listings, and mean critic score at least 4.0 before external testing. Human safety review remains pending and is not replaced by automated scores.

Complete input, expected output, actual outputs for all repetitions, pass/fail, critic mean and failed checks appear in evaluation_results.csv. Per-run JSON stores raw MCP calls, filters, records, handoff, guardrail outcomes, usage and critic rationales. The fixed expectations are defined before execution in evaluate.py.



# 2. Results, failures and protocol repair

The executed suite has a 90% case pass rate (9/10); individual-run success is 26/30. The critic mean is 4.71/5. Case-level success does not erase a failed repetition: every failed run is listed below and retained in the machine-readable evidence.

Critic evidence correction

The initial critic payload supplied the request, record list, analyst fields and rendered answer but omitted the literal tool status message. An empty record list was treated as insufficient support in no-match runs. The protocol was repaired once for every critic-eligible output by adding the full raw MCP events. Agent responses were not regenerated for this repair. Original critic records remain in evaluation/initial_critic. The initial case count was 9/10; the corrected count is 9/10. This is an evaluation-method correction, not an agent-quality gain.

TC03 / repetition 1

Critic quality threshold: The answer faithfully reports the tool’s output (no matching remote part‑time jobs at $40+/hr) and does not fabricate listings. It clearly notes the prototype nature and limited sample, addressing limitations. However, it offers little actionable guidance beyond the negative result, limiting practical usefulness.

TC03 / repetition 2

Critic quality threshold: The answer faithfully reflects the tool output that no jobs matched, and clearly states its prototype and unverified nature, satisfying evidence and honesty. It is only partially useful because it provides no alternatives or guidance beyond stating the lack of matches.

TC03 / repetition 3

Critic quality threshold: The response accurately reflects the tool output (no matching jobs) and honestly notes the prototype nature, but offers little practical guidance for the user's request.

TC04 / repetition 2

Filter selection / retrieval: actual IDs [], filters {'keywords': 'software developer, software engineer, programmer', 'remote': True, 'employment_type': 'part time', 'minimum_salary': 18, 'skill_match': 'any'}. The model-translated filter failed the fixed expected set.

Targeted refinements after the full suite

TC04: Keyword punctuation normalization. Separate post-fix runs passed 3/3. These follow-ups do not overwrite the main 30-run matrix above; they measure specific later changes.

TC03: No-match next-step guidance. Separate post-fix runs passed 3/3. These follow-ups do not overwrite the main 30-run matrix above; they measure specific later changes.

Failure boundary

Prompt/filter selection, retrieval behavior, output validation, and critic evaluation are distinct causes. A filter miss can produce a truthful tool-based no-match response that is still wrong for the user's intended request. Canonical rendering reduces fabrication risk but cannot make an incorrectly selected query complete. A critic score is a noisy model judgment, not a human usability rating.



# 3. Improvements since M3

The README CHANGES section records reasons and measured effects. These direct-tool and mutation checks compare the actual M3 code at 8a6d910 with the refined implementation on controlled fixtures. They are not live user studies and are not directly comparable with George's teammate-reported 10/10 result.

Why the architecture changed

Raw MCP records now cross the handoff beside the original request, model draft and applied filters. The analyst therefore evaluates the tool evidence even if the first model omits a record from its prose. Both agent outputs use structured contracts. Listing IDs must match the tool records, and analyst skill strings must occur in the relevant record. Invalid assessments are withheld. Displayed titles, companies, location and salary are copied from tool records rather than model-generated prose.

Search-time normalization accepts common employment-type spacing and hyphen variants. Annual salary comparisons require an explicit period and display the 2,080-hour assumption. An all-skill mode is distinct from the legacy any-skill mode. Non-finite salaries and malformed records are rejected. Preferences use atomic file replacement and a current-request mutation check; these controls remain a local prototype, not multi-user authentication.

An early live smoke test returned a structured “search” statement without executing a search. The orchestrator was corrected to select the required tool at the entry step and to rely on recorded calls. It never treats a model's promise to search as a successful operation.



# 4. Trace-backed operation and cost scenario

Observed workload

Across 24 search turns with an analyst handoff, the measured mean is 2,170 input tokens and 773 output tokens for the operational agents, excluding the evaluation critic. Token counts come from SDK usage records; local OpenInference JSON spans and Phoenix ingestion provide trace evidence. They are a small-fixture workload estimate, not a production traffic benchmark.

Phoenix runs locally. The suite exports spans to its OTLP endpoint and retains spans.jsonl independently. The report does not claim that a screenshot of a dashboard proves correctness; the raw calls and deterministic comparisons provide the relevant evidence. Human review of the designated safety cases is still required.

Inherited pricing assumptions, not current market quotes

M3 used $1 per million input tokens and $5 per million output tokens, plus a 25% buffer. Applying those same hypothetical rates to this measured workload gives approximately $0.00754 per operational search. At ten searches per active student per month, the corresponding model component is $0.0754 per student/month. The educational NRP run is not a commercial invoice.

M3's institutional proposal was $0.75 per active student/month and $290 fixed monthly cost at its 1,000-user tier. Replacing only the inference term would change that scenario, but job-data licensing, support, sales and maintenance uncertainty remain. No career center has accepted the price and no live data feed is priced here. A lower model cost alone does not validate the business.

Remaining technical limits

Eight fictional records; model-selected filters; finite keyword aliases; no verified vacancy freshness; no account isolation or concurrent multi-user memory; no employer contact or application submission. A fit score is an assessment, never a hiring probability. The local CLI and printed filters need real comprehension testing.



# 5. Real user-testing status and execution plan

Completed external sessions available for this package: zero. The following are empty status records, not session summaries. No roles, dates, ratings, quotes or outcomes are invented for actual participants.

Preserve the M3 recruitment and success criteria

Recruit six external FGCU students to cover the guide's minimum of five, including at least two non-CS majors and at least two who work while studying. No teammate or instructor is a substitute. The original thresholds were five of six completing the first task without help; median relevance and trust at least 3.5; four of six reuse ratings at least 4; at least three naming a concrete analyst insight; and zero fabricated listings. Do not silently replace those six-person criteria with a five-person denominator.

20-minute facilitated session

0-2 minutes: consent, context and think-aloud instructions. 2-7: search using real personal constraints. 7-11: explicitly save a preference and reuse it. 11-14: use the analyst to choose a listing and explain why. 14-20: collect ratings and open-ended responses. One teammate facilitates; another records actual behavior without coaching.

Capture relevance, trust and reuse on 1-5 scales; unassisted completion; time to first useful result; exact hesitation and rephrasing; a specific analyst insight; and what would make the person return. Ask what the participant does today and whether the agent is better or worse for that task. The session recorder writes actual transcripts and unfilled observations locally.

Command: python user_test_session.py --tester T01
Private capture folder: .local_sessions/ (git-ignored). Anonymize before sharing.



# 6. Fictional rehearsals - scenarios 1 and 2

SIMULATION ONLY - fictional roles and hypothetical actions. No real people, interviews, observations, ratings, validation or measured usability results.

SIM01 | Fictional working non-CS student

Date/format: Fictional tabletop rehearsal; not a user session

Task given: Find remote part-time work at $18/hour; compare skill overlap.

Hypothetical steps: Hypothetical: enters constraints, inspects the three sample matches, then compares customer-service overlap with technical skills.

Possible stuck point: Hypothesis: could read a fit score as a hiring probability or assume every named skill is required.

Surprise status: No real surprise was observed. Rehearsal highlights that any-skill matching needs explanation.

Possible reuse condition: Hypothesis: might return if listings were live and the distinction between evidence and fit judgment were clear.

SIM02 | Fictional CS student seeking an internship

Date/format: Fictional tabletop rehearsal; not a user session

Task given: Find Python work at a minimum $24/hour.

Hypothetical steps: Hypothetical: asks for Python plus pay, sees Junior Software Developer, then asks whether it is an internship.

Possible stuck point: Hypothesis: could assume a returned full-time developer role satisfies an unstated internship requirement.

Surprise status: No observed surprise. Rehearsal exposes the gap between a matching skill and an appropriate career stage.

Possible reuse condition: Hypothesis: might return with explicit role-level and internship filters plus verified employer requirements.



# 7. Fictional rehearsals - scenarios 3 and 4

SIMULATION ONLY - fictional roles and hypothetical actions. No real people, interviews, observations, ratings, validation or measured usability results.

SIM03 | Fictional local student with customer-service experience

Date/format: Fictional tabletop rehearsal; not a user session

Task given: Find full-time IT support in Fort Myers, at least $20/hour.

Hypothetical steps: Hypothetical: searches locally, inspects the Gulf Systems sample, then checks commute and schedule information.

Possible stuck point: Hypothesis: location alone may be mistaken for a feasible commute or compatible timetable.

Surprise status: No observed surprise. Missing schedule evidence is a useful debrief topic.

Possible reuse condition: Hypothesis: would need shift and commute information before considering the tool a replacement for a job board.

SIM04 | Fictional working student with a high pay threshold

Date/format: Fictional tabletop rehearsal; not a user session

Task given: Search remote part-time work paying at least $40/hour.

Hypothetical steps: Hypothetical: receives no matches, lowers the threshold deliberately, and compares the changed result set.

Possible stuck point: Hypothesis: could interpret a sample no-match result as evidence that no such job exists anywhere.

Surprise status: No observed surprise. The scenario tests whether the small-sample limitation is noticed.

Possible reuse condition: Hypothesis: may return if database coverage is transparent and the tool offers optional, explicit alternatives.



# 8. Fictional rehearsal - scenario 5

SIMULATION ONLY - fictional roles and hypothetical actions. No real people, interviews, observations, ratings, validation or measured usability results.

SIM05 | Fictional returning student with a stale remote preference

Date/format: Fictional tabletop rehearsal; not a user session

Task given: Save remote=true, restart, reuse it, then search locally with an override.

Hypothetical steps: Hypothetical: saves a preference, restarts, checks applied filters, and requests an explicit local override.

Possible stuck point: Hypothesis: could forget the saved preference or confuse remote=false with onsite-only.

Surprise status: No observed surprise. Rehearsal identifies preference transparency as a topic to verify with real participants.

Possible reuse condition: Hypothesis: may return if applied preferences are visible and easy to clear.

How to use the rehearsal material

Use these scenarios to check whether instructions are clear, whether the data fixture supports a task, and whether the note-taker has fields for meaningful observations. Replace no part of a real record with simulated content. A fictional “would use again” condition is a prompt for a question, not a retention estimate.

Three real participants expressing the same confusion would support a pattern. Three fictional scenarios designed around the same risk do not. Counts and medians in the final synthesis must come from collected real sessions only.



# 9. Provisional synthesis

593 words | technical evidence and simulation-informed hypotheses; empirical user synthesis pending.

This is a provisional synthesis of technical evaluation and fictional rehearsal scenarios, not a report of completed user research. Zero external-user sessions are available. No statement below claims that three actual testers behaved similarly, that a participant endorsed the product, or that a measured usability threshold was met. The simulations help choose questions for the real study; they do not supply answers to those questions.

The first planning pattern is the difference between matching a listing and helping a person decide. SIM01 considers skill overlap, SIM02 adds career stage, and SIM03 asks about timetable and commute. These scenarios suggest a common hypothesis: technically valid filters can still leave the decisive constraint unknown. The current output identifies missing information and labels fit scores as judgments. Real sessions must establish whether users notice those distinctions and whether they can explain a specific insight from the analyst without facilitator coaching.

A second hypothesis concerns the meaning of an empty result. SIM04 deliberately uses a high hourly-pay threshold; SIM05 considers a preference that silently narrows the search. Neither scenario represents an observed person. Together they motivate testing whether a participant interprets no sample matches as no jobs anywhere, understands the applied preferences, and can intentionally revise a constraint. The facilitator should capture the exact point where that interpretation becomes visible rather than infer confusion from a long pause.

The strongest available evidence is technical rather than market validation. The system records actual MCP calls, passes raw records into the analyst, and renders job facts from those records. Repeated integration runs test the committed prompts, and controlled regressions demonstrate specific improvements over M3. This establishes bounded behavior on a small fictional dataset. It does not establish time saved in a genuine search, employer relevance, repeat usage, willingness to pay, or superiority over an ordinary job board. There is no real participant statement to cite as the strongest validation moment.

The most important evaluation lesson is that the critic also needs complete evidence. An initial no-match assessment treated an empty record list as insufficient support for the response. The literal MCP status was not present in that critic payload. The repaired protocol provides the full tool events to every critic, preserves the original scores, and rescored all eligible outputs once. Agent outputs were not regenerated to improve the numbers. Any remaining mismatch is reported with its actual filters and critic rationale. Separately, an early smoke test showed why a model saying it was searching is not evidence that a search happened.

Three changes take priority before the final presentation. First, run the promised external sessions with truthful records, including non-CS and working students, because this is the missing evidence about usefulness and comprehension. Second, test clearer no-match and saved-preference explanations with those participants; the existing fixed prompts cannot establish whether users understand the sample boundary or an override. Third, validate a route to current, permitted job data with a career-center contact before treating the institutional business model as more than a hypothesis. These outrank cosmetic expansion because they address evidence gaps that can change the product decision.

For each session, retain the task wording, actual interaction steps, assistance, hesitation points, unexpected remarks, and whether the person would return. Record relevance, trust, and reuse ratings alongside time to first useful result. Do not replace a missing answer with an assumed rating. After the study, identify patterns supported by at least three real sessions, select an actual validation moment, and revise this synthesis. Until then, the responsible conclusion is that the engineering prototype has been evaluated but user value remains unvalidated.


# 10. Proposed pivot-or-proceed decision

358 words | proposed scope-down recommendation; team approval and real-user evidence pending.

Proposed decision: scope down to a supervised educational pilot while withholding any claim of validated user value. This is an interim recommendation for the team to approve, not a statement that both members have already agreed. The agent will continue to demonstrate filtering, explicit handoff, memory and evidence checks on fictional local listings. It will not be represented as a live job marketplace, a verified vacancy service, or an automated application system.

The technical evidence supports continued development within that boundary. The refined system has raw MCP handoffs, programmatic checks on record IDs and skill fields, canonical rendering of listing facts, and direct regression measurements against the actual M3 commit. The accompanying evaluation table records the ten committed cases, three runs each, with failures retained. The separate critic-protocol repair is disclosed rather than silently replacing inconvenient scores. Those are reasons to keep working on the prototype, not proof that real students find it valuable.

The user evidence does not yet support proceeding to a broader product. There are zero real external-session summaries, so no actual relevance or trust median, no observed unassisted completion rate, and no real reuse response. Five fictional scenarios cannot fill those gaps. This absence is a limitation in the evidence, not evidence that users rejected the idea. It would be equally unsupported to claim strong validation or to abandon the domain because a fictional persona might hesitate.

The narrowed target is a student demonstrating and reviewing a transparent job-search workflow with a facilitator, using explicit sample data. Before expanding, the team should complete the M3 study, manually review the designated safety cases, and verify whether a career center would value the workflow enough to support access to current listings. A clearly better-supported use case could justify a later pivot. Consistent real-user success plus acceptable technical results could justify proceeding.

The BMC therefore treats institutional licensing and partnerships as unvalidated hypotheses, separates users from prospective buyers, and makes data freshness and consent essential activities. Pricing remains an inherited scenario rather than a validated quote. This decision can be revised when evidence changes; it does not turn missing observations into a positive or negative market conclusion.
Before this can be submitted as a complete M4

Collect the five required real external-session summaries; complete the M3 safety review; replace the provisional synthesis with patterns and a concrete real validation moment; obtain the team's actual decision; compare the BMC against the original M2 artifact; and merge or publish the reviewed code in the team repository. The provided files make these gaps visible rather than certifying them as complete.



# 11. Provisional Business Model Canvas

All nine blocks are shown. The original M2 BMC artifact was not found in the supplied local materials. Labels below identify updates relative to the available M3 narrative, not a verified line-by-line comparison with M2. Claims that depend on real-user or buyer evidence remain unvalidated.

Sources, ownership and AI disclosure

Sources: Team Project Guide, M4 sections; TeamProject8_M3.pdf (Oct 28, 2026); inherited repo at 8a6d910; George's M4 result document at d55baf6a; current per-run JSON, CSV, OpenInference/Phoenix traces and regression measurements. The Canvas screenshot lists 16 points while the supplied guide lists 14; this draft follows the substantive requirements.

George's inherited code, tests and teammate-reported evaluation remain attributed to him. This continuation was requested by Manuel. OpenAI Codex drafted and refined the code, ran tests, generated the five explicitly fictional rehearsals and prepared this report. NRP gpt-oss generated live agent outputs and critic ratings. No shared approval, new contribution by George, real participant data, or independent student review is fabricated.
