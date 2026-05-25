---
name: phd-defence
description: Stress-test a research idea, thesis, or NSF proposal against hostile reviewers before the real ones see it. The skill bundles a 15-point pre-submission checklist mapped to NSF criteria, section-by-section attack templates with the questions reviewers actually ask, and an optional gamified simulator for low-stakes practice. Use whenever the user says /phd-defence, wants a mock defense, wants to identify weaknesses in a draft proposal, wants Claude to play hostile reviewer, or wants a hardening checklist for NSF or similar grants. Trigger even if the user only says "kill my idea", "stress-test my proposal", "defence simulation", or "mock defense."
---

# PhD Defence

A skill for hardening a research idea, thesis, or grant proposal against hostile review. The skill bundles three things, in descending order of practical value:

1. **A 15-point pre-submission checklist** mapped to NSF criteria and common reviewer concerns.
2. **Section-by-section hostile attack templates** with the specific questions reviewers actually ask.
3. **An optional gamified simulator** that models the iterative defense-and-revise dynamic, useful for getting a feel for the mechanic or for low-stakes practice.

The simulator is the LEAST important artifact. It is a stylized model and cannot read the actual proposal. The checklist and attack templates are where the value sits.

## When to use this skill

Use it in any of these cases:
1. User has a research idea, thesis chapter, or proposal draft and wants it stress-tested.
2. User wants a checklist for what to address before NSF submission.
3. User wants Claude to play hostile reviewer on their actual proposal.
4. User invokes `/phd-defence` or asks for a "mock defense."

## The actually useful workflow

For a real proposal, do this in order. Do NOT skip to the simulator.

**Step 1: Run the 15-point checklist against the proposal.** See `references/nsf_hardening.md` for the full list. Mark each vector as defended, partial, or absent. This step requires reading the proposal carefully, not running code.

**Step 2: For each absent or partial vector, write specific hostile questions grounded in the user's actual text.** A real reviewer attacks "your evaluation plan uses accuracy on a 200-sample test set drawn from the same distribution as your training data," not "evaluation is weak." The attack must quote the proposal.

**Step 3: Have the user defend each attack in writing or out loud.** Where the defense is shaky, that's where revision is needed. Where the defense is solid, mark the vector defended.

**Step 4 (optional): Run the simulator** with `--initial-defended <vectors>` set to what the user genuinely has defended. The simulator output is more useful as a confidence calibration than as a gap finder, because the simulator does not know the proposal content.

## What the simulator does and does not do

The simulator runs a panel of 5 fictional reviewers who ask 8 questions per attempt, drawn from 15 attack vectors. Undefended vectors take damage, candidate dies, the highest-damage vector that landed is added to the defended set, repeat until the candidate survives a full attempt.

Useful for:
* Getting a feel for the attack-and-revise loop before doing it for real.
* Demonstrating that proposals usually need multiple revision rounds.
* Practice in low-stakes mode for users who freeze in real defenses.

NOT useful for:
* Identifying specific weaknesses in a specific proposal. The simulator does not read the proposal. The vectors it flags are whatever its RNG happened to land on. This is echo, not insight.
* Predicting how an actual panel will respond. Real panels have champion-and-detractor dynamics, program officer priorities, and content expertise that no toy model captures.
* Statistical claims about which vectors are "consistent gaps" across seeds. The game is stochastic and small-N; cross-seed patterns are not informative.

## Running the simulator

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/simulator.py --seed 42
```

Useful options:
* `--initial-defended novelty prior_work` — start with some vectors already defended
* `--quiet` — show only summary
* `--json` — structured output
* `--hp 100 --questions-per-attempt 8` — tune difficulty

## Modes of play

**Mode 1 (recommended for real proposals): Hostile review with Claude as reviewer.** Claude reads the user's proposal, runs the 15-point checklist, identifies gaps, and writes specific hostile questions grounded in the proposal text. The simulator is not used or is used only afterward as a confidence check.

**Mode 2: Watch a simulated run.** Run the simulator and walk through the output. Useful for first-time users to understand the mechanic. Do not pretend the output is diagnosing the user's real proposal.

**Mode 3: Interactive role-play.** Claude plays the committee in real time. User defends out loud or in writing. Claude judges each defense (full / partial / no) and tracks HP. On death, Claude tells the user which question landed hardest. Good for oral defense practice; requires the user to have a real proposal to defend.

Default to Mode 1 if the user has a proposal. Use Mode 2 only if the user explicitly wants to see the game.

## Honest limitations

Expert review of this skill noted that the simulator's vector flags duplicate the user's own `--initial-defended` input rather than producing independent insight. That is correct. The simulator is a pedagogical scaffold, not a diagnostic tool.

Expert review also noted that real PhD defenses are not damage-based combat — they are coherent discussions of a body of work. This skill leans more usefully toward grant proposal hardening (where the hostile-reviewer mental model fits) than toward actual dissertation defense (where it doesn't quite). Use accordingly.

A 10-minute conversation with a colleague who knows the field will produce better feedback than running the simulator. Use the simulator when no such colleague is available, or as warmup before that conversation.

## Reference files

* `references/nsf_hardening.md` — the 15-point checklist, section-by-section attack templates, and pre-submission workflow. Read this first.
* `scripts/simulator.py` — the optional game engine.

## Related

There is a sister skill, `friction-run`, which uses a similar adversarial-simulation structure for budget defense. They share design philosophy (encode pressure into a simulation, extract the playbook) but solve different problems.
