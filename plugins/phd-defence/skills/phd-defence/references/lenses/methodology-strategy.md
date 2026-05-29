# Methodology / Strategy Hardening

How to use the PhD Defence game to stress-test an engineering, evaluation, or study-design strategy before you spend the effort running it. The lens's 12 attack vectors map onto the questions a sharp engineer or statistician asks when deciding whether a test plan, pipeline, or experimental protocol is sound and actually runnable.

## The four-theme frame

A strategy can be conceptually elegant and still be unrunnable, or runnable and measure the wrong thing. The 12 vectors fall into four themes; a strategy that survives review has an answer in all four.

**Does it measure the right thing?**
* construct_validity
* confounds
* ground_truth

**What does it miss?**
* coverage
* false_negatives
* aggregation_blind_spots

**Can you actually run it?**
* cost_orchestration
* baseline_simplicity
* reproducibility

**How do you trust the output?**
* false_positives
* failure_modes
* self_validation

Take the recurring example: "Use two independent LLMs (GPT-5.5 Pro and Gemini 3.1), each via shell/CLI, to author ~1,000 test cases for a bot; keep a case only when BOTH models agree it's useful and targets a subtle bug; log all reasoning." It can ace measurement and still die on theme three (orchestrating 2K shell invocations plus an agreement-exchange step) or theme four (the consensus filter silently discards real bugs one model found alone). All four themes must harden.

## Pre-flight checklist

Before you run anything, every vector below should have a defended answer you can point at — a documented decision, a control, a budget, a baseline number. Check each only when you can name the specific mechanism, not the intent.

* [ ] **construct_validity** — A sentence stating what the procedure measures and why that is the thing you care about. "Targets a subtle bug" must be operationalized: a subtle bug like "40 profiles imported but the UI didn't update" is a backend/frontend state desync — does your procedure actually exercise state-after-mutation, or just input/output pairs?
* [ ] **coverage** — A named taxonomy of case classes and which classes the procedure systematically exercises vs. skips. If both models only write request/response cases, the whole class of silent state-desync bugs is uncovered by construction.
* [ ] **cost_orchestration** — A concrete accounting: N invocations, wall-clock, token/API cost, and who or what drives the agreement-exchange step. "Two models via shell at 1K cases each plus a cross-check" is a real labor and rate-limit cost, not a footnote.
* [ ] **false_positives** — A stated filter for spurious findings and its cost. How many flagged "bugs" are noise, who triages them, and does triage eat the time the automation saved?
* [ ] **false_negatives** — An explicit account of what real defects slip through silently and why that's acceptable. The consensus filter is a false-negative generator by design.
* [ ] **ground_truth** — A named oracle. When a case flags a bug, how do you KNOW it's real and not a model hallucination? A model asserting "this is a bug" is not ground truth.
* [ ] **reproducibility** — Pinned model versions, seeds/temperature, prompts, and logs sufficient for someone else to re-run and get the same kept set. "GPT-5.5 Pro via CLI" with no version pin or temperature is not reproducible.
* [ ] **baseline_simplicity** — A one-sentence justification for why this beats a cheaper baseline (one model, a fuzzer, a hand-written suite, existing coverage tooling) that may do nearly as well.
* [ ] **aggregation_blind_spots** — A statement of what the consensus/voting/aggregation step throws away. "Keep only where BOTH agree" discards every case where exactly one model found a real bug.
* [ ] **confounds** — A list of uncontrolled variables (shared training data making "independent" models correlated, prompt order, the bot's nondeterminism) that could explain agreement without it meaning quality.
* [ ] **failure_modes** — How the strategy fails and whether failure is loud or silent. A rate-limit mid-run that quietly drops half the cases is a silent failure that corrupts the result.
* [ ] **self_validation** — How you validate the STRATEGY itself, not its outputs: on a seeded set of known bugs, does the kept set actually catch them? Without this you have no evidence the method works at all.

If any box is unchecked before you run, that's where the strategy will waste your effort or mislead you.

## Dimension-by-dimension attack templates

For each theme, the questions a hostile engineer or statistician actually asks. Run these against your design and see what survives.

### Does it measure the right thing? (construct_validity, confounds, ground_truth)

* "You say cases must 'target a subtle bug.' Define subtle. Right now it means 'whatever the model calls subtle.'"
* "Your motivating bug is a UI-not-updating-after-import state desync. Do any of your generated cases assert on post-mutation UI state, or are they all stateless I/O?"
* "Both models share most of their training corpus. Their 'independent agreement' is confounded — they fail the same way. What makes them actually independent?"
* "When a case flags a bug, what's your oracle? If the only confirmation is a second model agreeing, you've validated a hallucination with a hallucination."
* "The bot is nondeterministic. A 'bug' that reproduces 1 in 5 runs — is that a defect or a confound you didn't control?"

### What does it miss? (coverage, false_negatives, aggregation_blind_spots)

* "List the classes of bugs your two-model author can NOT produce. State desync, race conditions, and time-dependent bugs are usually not in that distribution."
* "Your consensus filter keeps a case only when both models agree. So every real bug that GPT-5.5 found and Gemini missed is discarded. How many real defects did you throw away to buy precision?"
* "The aggregation step optimizes for agreement, not for catching the hard bug. The hardest bugs are exactly the ones one model sees and the other doesn't."
* "What does 'log all reasoning' get you if the kept set is filtered before the interesting disagreements are ever inspected?"
* "The import bug — 40 profiles in, UI stale — would either model even propose it? If not, no amount of voting recovers it."

### Can you actually run it? (cost_orchestration, baseline_simplicity, reproducibility)

* "Walk me through one full run. Two models, ~1,000 cases each, via shell, plus an agreement-exchange pass. That's thousands of CLI calls. Who babysits rate limits and retries?"
* "What's the wall-clock and dollar cost of one run, and the cost of re-running after you tweak a prompt? If it's a day and $X, you'll run it twice and never again."
* "Why two frontier models via shell instead of one model plus a coverage tool, or a hand-written suite seeded from known incidents? Show me the simpler baseline doesn't get 80% of the value for 10% of the effort."
* "You didn't pin model versions or temperature. When the vendor silently ships a new checkpoint, your kept set changes and you can't tell whether the bot regressed or the model did."
* "Could I re-run this from your logs and get the same kept set? If not, it's a demo, not a method."

### How do you trust the output? (false_positives, failure_modes, self_validation)

* "Of the cases you keep, how many are actually useful on inspection? If triage is manual and the false-positive rate is high, the automation created work."
* "If a rate limit drops half your cases mid-run, does the pipeline halt loudly or quietly emit a partial result you'll mistake for complete?"
* "How is the strategy itself validated? Seed a known set of subtle bugs — including the import/UI desync — and show the kept set catches them. Without that you have zero evidence the consensus method works."
* "If both models converge on a wrong notion of 'useful,' the whole pipeline is confidently wrong and nothing in it will tell you."

## Drop-in review prompt

Use this prompt with Claude (or another LLM, or — better — a skeptical colleague) to run hostile review of a strategy:

```
You are a hostile senior engineer and a statistician reviewing a proposed
methodology / test plan / evaluation strategy. Attack it on these 12 vectors:

construct_validity, coverage, cost_orchestration, false_positives,
false_negatives, ground_truth, reproducibility, baseline_simplicity,
aggregation_blind_spots, confounds, failure_modes, self_validation.

For each vector, produce:
1. A one-sentence specific attack grounded in the actual strategy (no generic
   "validity is unclear" — name the concrete step and why it breaks).
2. A severity rating: BLOCKING (the strategy produces misleading or unusable
   results, or can't be run), MODERATE (a real gap that degrades trust in the
   output), MINOR (worth noting but doesn't change the conclusion).
3. A suggested fix in 1-2 sentences (a control, a baseline, an oracle, a budget).

If a vector is already well defended, say so and name the mechanism that defends it.

End with the three vectors most likely to sink this strategy in practice.
```

## Using the simulator

Run the lens against your starting position:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/simulator.py --lens methodology-strategy --initial-defended <vectors>
```

Pass the vectors you genuinely defend (a documented control or budget, not intent) as `--initial-defended`, e.g. `construct_validity ground_truth reproducibility`. Run several seeds; across runs, note which vectors keep getting added on death — those are your consistent gaps. For the running example, expect `aggregation_blind_spots`, `false_negatives`, and `cost_orchestration` to surface fast. For each gap, write the specific attack a real reviewer would make against YOUR design using the templates above, then fix it and re-run until the simulator graduates quickly from your honest starting position.

The goal is not to "win" the simulation — it's to catch the gap before you burn a day running a method that measures the wrong thing.

## What this won't catch

The simulator does not know your specific strategy. It identifies CATEGORIES of weakness, not the specific flaw on a specific line — it can tell you `aggregation_blind_spots` is a gap, but not that *your* consensus filter discards the one bug that mattered. Use it to find which categories deserve attention, then bring in domain judgment to patch the actual hole.

It also can't run your strategy for you. The only true test of `self_validation` is seeding a set of known defects and measuring whether the method recovers them. The simulator surfaces that you need that test; it can't be that test.

## Companion advice

* Before running at full scale, run the strategy on a tiny seeded set with a few known-answer cases (including one silent-state bug). If it can't catch a bug you planted, it won't catch the ones you didn't.
* Cost the orchestration honestly in invocations, wall-clock, and dollars. A method you'll only ever run once is a demo, not a pipeline.
* Always state the simpler baseline you're beating and by how much. If you can't quantify the gain over one model or a hand-written suite, the complexity isn't earned.
