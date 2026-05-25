# phd-defence (Claude Code plugin)

Stress-test a research idea, thesis, or NSF proposal against hostile reviewers
before the real ones see it. Bundles a 15-point pre-submission checklist mapped
to NSF criteria, section-by-section attack templates, and an optional gamified
simulator.

This repo is a Claude Code **plugin marketplace** (`mastropaolo-skills`)
containing one plugin (`phd-defence`).

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
.claude-plugin/marketplace.json      # marketplace catalog
phd-defence/
  .claude-plugin/plugin.json         # plugin manifest
  skills/phd-defence/
    SKILL.md                         # skill instructions
    references/nsf_hardening.md       # 15-point checklist + attack templates
    scripts/simulator.py             # optional game engine
```
