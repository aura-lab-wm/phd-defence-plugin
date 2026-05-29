# Research Idea Hardening

How to use the PhD Defence game to stress-test a research idea or direction before you commit months to it. This is the pre-paper, pre-commitment lens: you have a hypothesis or a plan, not yet a result. The 12 attack vectors map onto the questions a sharp colleague asks over coffee, where the only thing on the line is whether the idea is worth pursuing at all.

## The three-theme frame

The 12 vectors group into three questions. An idea can pass one and still be dead on the others.

**Is it new and worth it?**
* novelty
* prior_work
* problem_significance
* contribution_clarity

**Is the plan sound?**
* approach_soundness
* evaluation_validity
* threats_to_validity
* falsifiability

**Is it doable and bounded?**
* feasibility
* scope_boundaries
* assumptions
* alternatives

A genuinely new idea (theme 1) with no credible path to a result (theme 2) is a daydream. A sound, doable plan (themes 2 and 3) for something already known (theme 1) is busywork. The game forces all three to harden.

## Pre-flight checklist

Before you commit to the idea, every one of these 12 vectors should have a defended answer — a sentence you could say out loud and a colleague couldn't immediately knock down. Check each only when you can point to a specific answer, not an intention.

* [ ] **novelty** — One sentence naming the specific thing no one has done: "no prior work has measured X under condition Y," not "we will study X." If the new part is "applying A to B," say why nobody bothered and what makes it non-obvious.
* [ ] **prior_work** — Name the 3-5 closest efforts, including the ones that look most like yours, and state the delta for each. "Closest is Smith 2024, which did A; we do B, which they couldn't because C."
* [ ] **problem_significance** — Name who cares and what changes for them if you're right. "Researchers in subfield X currently can't do Y; this unblocks Z." Not "this is an important problem."
* [ ] **approach_soundness** — A concrete chain from idea to result, with the hardest step named, not skipped. Each step should be something you know how to do or know how to learn.
* [ ] **evaluation_validity** — A success criterion written so a skeptic can check it: "We'll measure X with Y; the idea is supported if Z, and not supported if W." A measurement that can only confirm is not a measurement.
* [ ] **threats_to_validity** — The 2-3 confounds, biases, or alternative explanations that could produce your result without the idea being true, plus how you'd rule each out.
* [ ] **feasibility** — A sentence tying the plan to what you actually have: data, compute, access, skills, time. Name the single resource whose absence kills it.
* [ ] **scope_boundaries** — An explicit statement of what's in and what's deferred. If the idea has three clauses joined by "and," it's probably three projects; pick one.
* [ ] **falsifiability** — The specific result that would make you abandon the idea. If no observable outcome would change your mind, it's not a research idea yet.
* [ ] **contribution_clarity** — The contribution in one sentence, of the form "We show that ___." If you can't finish that sentence without a list, the contribution is not yet clear.
* [ ] **assumptions** — The load-bearing assumptions you're not testing (that the data is clean, that the effect is large enough to see, that the proxy measures the real thing). Name them so you know what you're betting on.
* [ ] **alternatives** — Why this approach over the obvious simpler one. Name the simpler thing a reviewer will suggest and say why it's insufficient, not why it's beneath you.

If any box is unchecked, that's where the idea gets attacked — usually by someone who likes you and is trying to save you six months.

## Dimension-by-dimension attack templates

These are the questions a sharp colleague actually asks. Run them against your idea and see what survives. The good ones quote your claim back at you.

### Is it new and worth it?

* "You say this is the first time anyone's done X — but Group Y did Z in 2023. What's the actual delta, in one sentence?"
* "Strip away the framing: isn't the new part just applying an existing method to a new dataset? Why is that a contribution and not an exercise?"
* "Who is harmed by this problem staying unsolved? Name a person or a project that's currently blocked."
* "Finish the sentence 'We show that ___' right now. If it takes you three clauses, you don't know what you're claiming."
* "Say the same idea exists. Would the field actually change, or would three people cite it and move on?"

### Is the plan sound?

* "Walk me from your hypothesis to a figure in a paper. Which step are you waving your hands at?"
* "How would you know it worked? And separately — what result would convince a person who thinks you're wrong?"
* "What's the boring explanation for the result you expect? Selection bias, a confound, the effect being an artifact of your measurement?"
* "Tell me the result that would make you drop this idea. If there isn't one, you're not testing anything."
* "Your metric can only go up if you're right. What does it look like if you're wrong — and can your design even produce that?"

### Is it doable and bounded?

* "What do you need that you don't have? Be specific: which dataset, whose access, how much compute, which skill you'd have to learn first."
* "This sounds like three projects glued together. Which one is the dissertation chapter and which two are you deferring?"
* "What are you assuming is true that you're not going to check? Name the assumption that, if false, sinks everything."
* "The obvious thing is to just do [simpler approach]. Why isn't that enough? Don't tell me it's less interesting — tell me what it can't do."
* "If your single hardest step turns out to be impossible in month two, is there a salvageable result, or is it all-or-nothing?"

## Drop-in review prompt

Use this prompt with Claude (or another LLM, or — better — a human colleague) to run hostile review of the idea:

```
You are a sharp, friendly-but-merciless colleague reviewing a research idea
BEFORE any work is done. Read the idea below and attack it on these 12 vectors:

novelty, prior_work, problem_significance, approach_soundness,
evaluation_validity, threats_to_validity, feasibility, scope_boundaries,
falsifiability, contribution_clarity, assumptions, alternatives.

For each vector, produce:
1. A one-sentence specific attack grounded in the actual idea (no generic "the
   novelty is unclear" — quote the claim and explain why a colleague pushes back,
   e.g. "you say X is new, but Group Y did Z; what's the delta?").
2. A severity rating: KILLS (the idea isn't worth pursuing as stated), WEAKENS
   (worth pursuing but this must be fixed first), MINOR (a caveat, not a blocker).
3. A suggested fix in 1-2 sentences.

If a vector is already well defended, say so and quote the part of the idea that
defends it.

End with the three vectors most likely to kill the idea, and for each, the single
question you'd want answered before you'd spend a week on this.
```

## Using the simulator

You can run the simulator against this lens directly:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/simulator.py --lens research-idea --initial-defended <vectors>
```

List the vectors you genuinely defend as `--initial-defended` (space-separated ids you can already answer with specific text, not intent). Run it across several seeds. The vectors that keep getting added on death are your consistent gaps — that's where to spend your thinking.

The simulator finds CATEGORIES of weakness, not the specific flaw. It knows that your idea is shaky on, say, `threats_to_validity`; it does not know that your particular confound is a sampling bias on page-zero of your head. Use it to learn which categories deserve attention, then do the actual patching yourself.

## What this won't catch

The simulator does not know your research content. It cannot tell you that the closest prior work is a 2022 paper you haven't read, that your proxy doesn't measure what you think, or that the dataset you're counting on is paywalled. It surfaces the shape of the weakness, not the weakness.

It also can't judge taste — whether the idea is interesting, timely, or worth a smart person's year. That judgment lives with people who know the subfield.

## Companion advice

* A 20-minute conversation with one domain expert beats any number of simulator runs. Bring them the one-sentence contribution and the falsifying result; if those two survive, the idea has a spine.
* Write the abstract of the paper you don't have yet. If you can't write a crisp four-sentence abstract for the result you hope to get, the contribution isn't clear enough to start.
* Find the closest prior paper and read it adversarially, looking for the reason your idea is already done. Better to find it now than in your related-work section.
* Steelman the simpler alternative before you dismiss it. The fastest way to lose a year is to skip the obvious approach because it felt unexciting.
