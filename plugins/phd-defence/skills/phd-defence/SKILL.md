---
name: phd-defence
description: Stress-test any idea, thesis, research direction, methodology/evaluation strategy, or grant proposal against hostile reviewers before the real ones see it. The skill picks an evaluation LENS that fits the subject — research-idea (default), methodology-strategy, thesis-defense, or nsf-grant — and applies that lens's checklist, section-by-section attack templates, and an optional gamified simulator. Use whenever the user wants a mock defense, wants weaknesses found in a draft/idea/plan, wants Claude to play hostile reviewer, or says /phd-defence, "kill my idea", "stress-test my proposal", "poke holes in this strategy", "mock defense", or "harden my NSF proposal."
---

# PhD Defence

A skill for hardening *any* intellectual artifact against hostile review by
stress-testing it before real reviewers do. The subject can be a general
research idea, a methodology or evaluation strategy, a completed thesis, or a
grant proposal — so the skill is built around **pluggable lenses**, one per kind
of subject. Each lens supplies its own checklist, its own attack templates, and
its own set of simulator attack vectors.

The skill bundles three things, in descending order of practical value:

1. **A per-lens checklist** of the vectors a reviewer will probe.
2. **Section/dimension-by-dimension hostile attack templates** — the specific questions reviewers actually ask.
3. **An optional gamified simulator** that models the iterative defend-and-revise dynamic. It is the LEAST important artifact (a stylized model that cannot read the actual subject); the checklist and attack templates are where the value sits.

## When to use this skill

- The user has an idea, thesis chapter, strategy, plan, or proposal draft and wants it stress-tested.
- The user wants a checklist of what to address before submitting/committing.
- The user wants Claude to play hostile reviewer on their actual artifact.
- The user invokes `/phd-defence` or asks for a "mock defense" / "kill my idea" / "poke holes in this."

## Step 0 — pick the lens (do this first)

The *subject* of evaluation and the *lens* you judge it through are separate.
Classify the subject, then choose the matching lens:

| Lens | Use when the subject is… |
|---|---|
| `research-idea` (default) | a general research idea, hypothesis, or direction — pre-paper, pre-commitment |
| `methodology-strategy` | an engineering / experimental / test / evaluation strategy, pipeline, or protocol |
| `thesis-defense` | a completed PhD/dissertation body of work facing a committee |
| `nsf-grant` | a competitive grant/funding proposal (NSF or similar) |

The registry in `references/lenses.json` maps each lens to its checklist file,
its trigger keywords, and its simulator config. Match on the subject and on the
user's wording (e.g. "grant"/"broader impacts" → `nsf-grant`; "test plan"/
"evaluation strategy"/"pipeline" → `methodology-strategy`; "dissertation"/
"committee" → `thesis-defense`). **If the subject doesn't clearly fit a grant,
thesis, or strategy, default to `research-idea`.** When genuinely ambiguous, ask
the user which lens fits before proceeding. Adding a new domain later = drop a
`references/lenses/<id>.md` + register it in `lenses.json`; nothing else changes.

## The actually useful workflow

For a real artifact, do this in order. Do NOT skip to the simulator.

**Step 1: Read `references/lenses/<lens>.md` and run its checklist against the subject.** Mark each vector as defended, partial, or absent. This requires reading the artifact carefully, not running code.

**Step 2: For each absent or partial vector, write specific hostile questions grounded in the user's actual text.** A real reviewer attacks "your consensus filter discards any case only one model flags, so a real bug the other model missed is silently dropped," not "the methodology is weak." The attack must quote/reference the artifact.

**Step 3: Have the user defend each attack in writing or out loud.** Where the defense is shaky, that's where revision is needed. Where it's solid, mark the vector defended.

**Step 4 (optional): Run the simulator** with `--lens <lens> --initial-defended <vectors>` set to what the user genuinely has defended. The simulator output is more useful as confidence calibration than as a gap finder, because it does not know the subject's content.

## Running the simulator

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/simulator.py --lens research-idea --seed 42
```

Useful options:
* `--list-lenses` — show every lens and its attack vectors
* `--lens <id>` — choose the lens (default: `research-idea`)
* `--initial-defended <vectors>` — start with some vectors already defended (lens-specific; see `--list-lenses`)
* `--quiet` — show only the summary
* `--json` — structured output
* `--hp 100 --questions-per-attempt 8` — tune difficulty

The simulator runs a panel of fictional reviewers drawn from the chosen lens's
committee; undefended vectors take damage; on death the highest-damage vector is
added to the defended set; repeat until the candidate survives a full pass.

## Modes of play

**Mode 1 (recommended for a real artifact): Hostile review with Claude as reviewer.** Pick the lens, read its checklist, identify gaps, and write specific hostile questions grounded in the artifact text. The simulator is unused or used only afterward as a confidence check.

**Mode 2: Watch a simulated run.** Run the simulator and walk through the output. Useful for first-time users to understand the mechanic. Do not pretend the output diagnoses the user's real artifact.

**Mode 3: Interactive role-play.** Claude plays the panel from the chosen lens in real time. User defends out loud or in writing. Claude judges each defense (full / partial / no) and tracks HP. Good for oral-defense practice; requires a real artifact to defend.

Default to Mode 1 if the user has an artifact. Use Mode 2 only if they explicitly want to see the game.

## Honest limitations

- The simulator does not know the specific content. It identifies CATEGORIES of weakness, not the specific flawed argument on page 4. Use it to find which categories deserve attention, then bring domain expertise to patch the specific holes.
- The combat metaphor fits some lenses better than others: it maps well to grant/strategy hardening (hostile-reviewer mental model) and least well to a real dissertation defense, which is a coherent discussion of a body of work, not damage-based combat. The `thesis-defense` lens leans on the checklist and question templates more than the game.
- A 10–20 minute conversation with a colleague who knows the field beats running the simulator. Use the simulator when no such colleague is available, or as warmup before that conversation.

## Reference files

* `references/lenses.json` — the lens registry: subject→lens mapping, trigger keywords, and per-lens simulator config (attack vectors, committee personas, partial-defense map). Read this to choose the lens.
* `references/lenses/<lens>.md` — the checklist, attack templates, and drop-in review prompt for each lens. Read the chosen one first.
* `scripts/simulator.py` — the optional, lens-driven game engine.

## Related

There is a sister skill, `friction-run`, which uses a similar
adversarial-simulation structure for budget defense. They share design
philosophy (encode pressure into a simulation, extract the playbook) but solve
different problems.
