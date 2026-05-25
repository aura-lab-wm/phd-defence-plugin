# phd-defence — Claude Code plugin

> **This file is human documentation, not skill instructions.** Claude never
> loads this README into its prompt — the only text Claude reads when the skill
> runs is `phd-defence/skills/phd-defence/SKILL.md`. Edit that file to change
> behavior; edit this one to change what teammates read.

This repository is a Claude Code **plugin marketplace** (`mastropaolo-skills`)
containing a single plugin, `phd-defence`.

## What the skill does

Stress-tests a research idea, thesis, or NSF proposal against hostile reviewers
before the real ones see it. It bundles:

- a **15-point pre-submission checklist** mapped to NSF review criteria;
- **section-by-section hostile attack templates** — the questions reviewers actually ask;
- an optional **gamified simulator** for low-stakes mock-defense practice.

## Install (for coworkers)

In Claude Code:

```
/plugin marketplace add antonio-mastropaolo/phd-defence-plugin
/plugin install phd-defence@mastropaolo-skills
```

Replace the marketplace source with a local path if you received the folder
directly:

```
/plugin marketplace add /path/to/phd-defence-plugin
/plugin install phd-defence@mastropaolo-skills
```

## Use

Once installed, the skill auto-triggers on phrases like "mock defense",
"stress-test my proposal", or "kill my idea", or invoke it explicitly:

```
/phd-defence:phd-defence
```

(Skills inside plugins are namespaced `plugin-name:skill-name`.)

## Layout

```
.claude-plugin/marketplace.json          # marketplace catalog
phd-defence/
  .claude-plugin/plugin.json             # plugin manifest
  skills/phd-defence/
    SKILL.md                             # skill instructions (+ lens selection)
    references/
      lenses.json                        # lens registry + per-lens simulator config
      lenses/
        research-idea.md                 # default lens
        methodology-strategy.md          # engineering / evaluation strategy
        thesis-defense.md                # dissertation defense
        nsf-grant.md                     # competitive grant proposal
    scripts/simulator.py                 # optional, lens-driven game engine
```

## Lenses

The skill picks an evaluation **lens** that fits the subject — a general
research idea (default), a methodology/evaluation strategy, a thesis defense, or
a grant proposal. Each lens has its own checklist, attack templates, and
simulator attack vectors. Add a domain by dropping a `references/lenses/<id>.md`
and registering it in `references/lenses.json`. List them at runtime with
`python3 ${CLAUDE_SKILL_DIR}/scripts/simulator.py --list-lenses`.
