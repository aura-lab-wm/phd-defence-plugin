# NSF Proposal Hardening

How to use the PhD Defence game to harden an NSF proposal (or any competitive grant) before submission. The game's 15 attack vectors map onto the questions a real panel actually asks.

## The two-criterion frame

Every NSF proposal is judged on two criteria. Most of the 15 game vectors fall under one or the other.

**Intellectual Merit (IM):**
* novelty
* prior_work
* methodology
* evaluation
* baselines
* theoretical_basis
* intellectual_merit
* limitations
* reproducibility

**Broader Impacts (BI):**
* broader_impact
* ethics
* data_availability

**Both / programmatic:**
* feasibility
* scalability
* team_expertise

A proposal can have brilliant IM and still get triaged because BI is an afterthought. Equally, a strong BI section cannot rescue a thin IM core. The game forces both halves to harden.

## Pre-submission checklist

Before submission, every one of these 15 vectors should have a defended section, paragraph, or sentence in the proposal. Use the checklist below; check each only when you can point to specific text that answers a hostile reviewer's question.

* [ ] **novelty** — One sentence that names what no one else has done. Not "we propose to study X" but "no prior work has done Y, despite Z attempts."
* [ ] **prior_work** — A related-work section that includes the 3-5 closest competitors, not just supportive citations. Cite work that could be confused with yours and distinguish it.
* [ ] **methodology** — Concrete methods, not "we will use machine learning." Specify the family, the inputs, the outputs, the training regime, the validation protocol.
* [ ] **evaluation** — A success metric written as a sentence the reviewer can check off: "We will measure X using Y, and the project succeeds if Z."
* [ ] **baselines** — Named comparisons. "vs. random" is a red flag; "vs. state-of-the-art method A and the dominant industry tool B" is defensible.
* [ ] **theoretical_basis** — A paragraph that explains WHY the approach should work, grounded in established theory or empirical regularity.
* [ ] **limitations** — Explicit statement of what the work will NOT do. Reviewers trust proposals that bound their claims.
* [ ] **reproducibility** — A sentence about code, data, and artifacts being released. NSF increasingly weights this.
* [ ] **intellectual_merit** — A dedicated subsection or paragraph headed exactly "Intellectual Merit" (it is required and reviewers look for the heading).
* [ ] **broader_impact** — A dedicated subsection headed exactly "Broader Impacts". Vague claims about "society" or "students" fail. Name specific activities, populations, and metrics.
* [ ] **ethics** — IRB plan if human subjects, RCR training plan, dual-use considerations for sensitive AI/security work.
* [ ] **data_availability** — Where the data comes from, who owns it, what licenses apply, what happens if access is lost mid-project.
* [ ] **feasibility** — A timeline (Gantt or year-by-year) that shows the work fits the budget and duration. Include risk mitigation for the riskiest step.
* [ ] **scalability** — A sentence explaining how this generalizes past the immediate scope, or honest acknowledgment that this is foundational and scaling is later work.
* [ ] **team_expertise** — A paragraph that explains why YOUR team is the one to do this. Prior publications, prior infrastructure, prior collaborations.

If any box is unchecked at submission time, that's where the proposal will be attacked.

## Section-by-section attack templates

For each typical NSF section, here are the attacks reviewers actually run. Run these against your draft and see what survives.

### Project Summary

* "This is one paragraph and it's vague. I can't tell what you're actually doing."
* "The Intellectual Merit and Broader Impacts statements are required and you've buried them in prose."
* "I can't tell who the audience is."

### Introduction / Motivation

* "Why now? What changed that makes this tractable today?"
* "Your motivation is a generic societal problem. The leap from there to your specific approach is not justified."
* "You're conflating the importance of the problem with the importance of YOUR approach."

### Related Work

* "You missed the most relevant paper, which is from a competing group."
* "You cite work as supportive that actually contradicts your premise."
* "Where's the work from before 2020? This problem isn't new."
* "Every cited paper is from your own group or your collaborators."

### Proposed Approach

* "I don't see a method here, I see a research direction."
* "You handwave the hardest step. How exactly will you do X?"
* "The aims are independent — failure of aim 1 doesn't stop aim 2 from running, which is suspicious."
* "Aim 3 depends on aim 2's success. What's plan B if aim 2 fails?"

### Evaluation Plan

* "How will you know it worked?"
* "Your metric is qualitative. Why?"
* "What's the null result and how would you publish it?"
* "Your baselines are weak."

### Broader Impacts

* "These activities (outreach, mentoring) are things you should already be doing. What's specific to this proposal?"
* "You list activities but no measurement plan."
* "The target population is generic. Which underrepresented group, where, how recruited?"

### Budget & Timeline

* "The first year does almost nothing while the last year does everything."
* "The travel budget is unrealistic."
* "You request 2 grad students but only describe work for 1."
* "No funding for the artifacts/release you promise."

### Team / Facilities

* "You list collaborators but no letters from them."
* "The PI has no prior publications in this area."
* "What happens if the postdoc leaves in year 2?"

## Drop-in review prompt

Use this prompt with Claude (or another LLM, or — better — a human collaborator) to run hostile review:

```
You are a hostile NSF panel reviewer. Read the attached proposal and attack it
on these 15 vectors:

novelty, prior_work, methodology, evaluation, feasibility, scalability,
reproducibility, ethics, broader_impact, theoretical_basis, baselines,
limitations, team_expertise, data_availability, intellectual_merit.

For each vector, produce:
1. A one-sentence specific attack grounded in the actual proposal text (no generic
   "the methodology is unclear" — quote a specific sentence and explain why a
   reviewer would push back).
2. A severity rating: BLOCKING (would cause triage), MODERATE (would cause
   reduced score), MINOR (would generate a critique but not affect funding).
3. A suggested revision in 1-2 sentences.

If a vector is already strongly addressed in the proposal, say so and quote the
text that defends it.

End with the three vectors most likely to kill the proposal in panel.
```

## How to use the simulator in service of an actual proposal

Workflow:

1. Read your proposal honestly. List the vectors you genuinely defend (sections that have specific text, not just intent).
2. Run `python simulator.py --initial-defended <those vectors> --seed N` with several different seeds.
3. Across runs, note which vectors keep getting added on death. Those are the consistent gaps.
4. For each gap, write the hostile attack a real reviewer would make AGAINST YOUR SPECIFIC PROPOSAL. Use the section templates above as a starting point but make it specific.
5. Revise the proposal to defend the gap.
6. Re-list defended vectors. Re-run the simulator. Iterate until the simulator graduates quickly (1-2 deaths) from your actual starting position.

The goal is not to "win" the simulation — it's to use the simulation as a forcing function that catches gaps before a real panel does.

## What this won't catch

The simulator does not know your specific research content. It can identify CATEGORIES of weakness, not the specific flawed argument on page 4. Use the simulator to find which categories deserve attention, then bring in domain expertise (advisor, collaborators, program officer) to actually patch the specific holes.

The simulator also doesn't model the social dynamics of a real panel (champion-and-detractor structure, the program officer's priorities, the deadline pressure that affects how carefully a panelist reads). For those, your local NSF-experienced colleagues are the real ground truth.

## Companion advice

* Talk to your program officer before submission. Most weaknesses they would flag, you can fix in writing.
* Run a mock panel with 3-4 colleagues from adjacent fields. They will catch what specialty colleagues miss.
* Read three recently-funded proposals in the same program. The pattern of what got through is the most useful prior you can build.
