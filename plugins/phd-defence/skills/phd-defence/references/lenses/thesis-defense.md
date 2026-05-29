# Thesis Defense Hardening

How to use the PhD Defence skill to prepare for a real dissertation defense (viva) of a completed body of work — not a grant, not a single idea, but the whole thesis discussed live in front of a committee. The 12 vectors below map onto what a committee actually probes. Treat the defense as a coherent discussion of a body of work, not a damage-based combat game: the goal is to converse fluently about everything you did and why, and the simulator only approximates that.

## The four-question frame

A committee is really asking four questions about your thesis. The 12 vectors group under them.

**Is it one coherent contribution?**
* contribution_boundaries
* coherence
* novelty
* positioning

**Is it rigorous?**
* methodology
* results_validity
* depth

**Do you own it and see past it?**
* limitations
* significance
* future_work

**Can you defend it live?**
* reproducibility
* question_handling

A thesis can have brilliant individual chapters and still wobble if the candidate cannot say what binds them into one contribution (coherence) or where the line falls between their work and a collaborator's (contribution_boundaries). Equally, a tidy narrative cannot survive a committee that finds one thin chapter (depth) or a claim the results do not actually support (results_validity). A defense passes when both halves hold AND the candidate can talk about it under pressure without deflecting.

## Pre-defense checklist

Before you walk in, every one of these 12 vectors should be something you can speak to from memory, pointing at specific chapters, results, or decisions. Check each only when you could answer a hostile committee member without flipping through the document.

* [ ] **contribution_boundaries** — You can say in one sentence what is yours and, crucially, what is NOT: which chapter was joint work, which idea came from your advisor, which dataset or tool you inherited. Claiming too much is the fastest way to lose the room.
* [ ] **coherence** — You can name the single thread that runs through all chapters in one sentence, and explain why they belong in one thesis rather than three unrelated papers. "They're all about X" is weak; "each chapter removes one obstacle to X" is defensible.
* [ ] **novelty** — One sentence per chapter naming what the field did not know before it. Not "we studied X" but "before this, no one had shown Y, and Y matters because Z."
* [ ] **methodology** — You can defend each method as sound on its own AND explain why the methods across chapters are consistent (or justify why they differ). A committee notices when chapter 2's standard of evidence does not match chapter 4's.
* [ ] **results_validity** — For every headline claim, you can point to the specific result that supports it and explain why it supports that claim and not a weaker one. You have anticipated where a result is over-read.
* [ ] **limitations** — You volunteer the boundaries of your work before the committee does. Knowing your own limitations is read as maturity; being shown them is read as a blind spot.
* [ ] **positioning** — You can place the thesis on the field's map: which canonical lines of work it extends, which it departs from, and who the nearest neighbors are. You can name the three works closest to yours and distinguish them.
* [ ] **depth** — Every chapter holds up to the same scrutiny. You know which chapter is thinnest and have a defense ready for why it is included and what it contributes despite its scope.
* [ ] **significance** — You can answer "so what?" beyond "it earned me the degree." Who, inside or outside the field, is different because this work exists?
* [ ] **future_work** — You can describe the next two or three concrete steps and, just as important, articulate why you stopped where you did — a principled boundary, not exhaustion.
* [ ] **reproducibility** — You can say where the code, data, and artifacts live and whether another group could build on them. A defense increasingly weights whether the field can stand on your work.
* [ ] **question_handling** — You can hold a claim under follow-up pressure: restate the question, answer the actual question asked, concede what is genuinely uncertain, and not deflect into rehearsed talking points.

If any box is unchecked the morning of the defense, that is the thread the committee will pull.

## Question-by-question attack templates

These are the questions committees actually ask, grouped by moment in the defense. Have someone fire them at you cold.

### The opening — summarize the contribution

* "Summarize your contribution in two minutes, without jargon, to someone outside your subfield."
* "If you had to cut this thesis to one sentence, what is the claim?"
* "What is the one thing you most want the committee to remember?"
* "Tell us what is in this thesis that was not in any of your published papers."

### Boundary probes — what is yours

* "Chapter 3 is joint work. Which specific part is yours?"
* "Was this idea yours or your advisor's? Walk us through how it actually originated."
* "You used dataset/tool X that someone else built. What would change if you'd had to build it yourself?"
* "If your main collaborator defended tomorrow, what would be in their thesis that is also in yours?"

### Coherence probes — is it one thesis

* "These read like three separate papers. What makes this one body of work?"
* "If I removed chapter 4 entirely, what would the thesis lose?"
* "Your chapters use different methods and different standards of evidence. Why?"
* "Which chapter is the core, and why are the others not just appendices to it?"

### Rigor probes — methods and results

* "This result supports a weaker claim than the one you make in the abstract. Defend the strong version."
* "What confound could produce this result without your hypothesis being true?"
* "Your sample / corpus / benchmark is small. Why should we believe this generalizes?"
* "Show me the result that would most embarrass your thesis if a reviewer found it first."

### Limitations and counterfactual — what you'd do differently

* "What would you do differently if you started this PhD again today?"
* "What is the weakest chapter, and why is it still here?"
* "Where are you most likely wrong, and how would you find out?"
* "What did you try that failed, and what did the failure teach you?"

### The canonical paper you missed

* "Are you familiar with [foundational/recent work]? It seems to anticipate your chapter 2."
* "How does this differ from [nearest competitor]? On the surface they look identical."
* "Why isn't [classic result] cited? It's the standard reference for this problem."

### Live-defense traps

* "I'm not sure I agree with your answer — let me ask again." (Holding under repeated pressure without caving or stonewalling.)
* A two-part question where answering the first half well tempts you to forget the second.
* A question premised on a misreading of your work — can you correct the premise politely instead of answering the wrong question.
* "Take a moment." (Silence is a trap only if you fill it with deflection; a measured pause is fine.)

## Drop-in review prompt

Use this with Claude (or another LLM, or — better — a faculty member adjacent to your committee) to run a hostile read of the dissertation before the real one:

```
You are a hostile but fair dissertation committee reading a completed PhD thesis
for an oral defense. This is a discussion of a whole body of work, not a single
idea. Attack it on these 12 vectors:

contribution_boundaries, coherence, novelty, methodology, results_validity,
limitations, positioning, depth, significance, future_work, reproducibility,
question_handling.

For each vector, produce:
1. A one-sentence specific attack grounded in the actual thesis text (no generic
   "the methodology is unclear" — quote a chapter/result and explain why a
   committee member would push back).
2. A severity rating: BLOCKING (would force major revisions or fail the defense),
   MODERATE (would dominate the discussion and require a strong live answer),
   MINOR (would generate a question but not threaten the outcome).
3. A suggested fix in 1-2 sentences — a revision, or a line of defense to rehearse.

If a vector is already well-handled, say so and quote the text that defends it.

End with the three questions most likely to rattle the candidate live, phrased
exactly as a committee member would ask them.
```

## Using the simulator

Run the practice simulator with the thesis-defense lens, seeding it with the vectors you genuinely defend:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/simulator.py --lens thesis-defense --initial-defended <vectors>
```

A note on fit: the simulator's combat metaphor fits this lens LEAST well of the four. A real defense is a discussion, not a sequence of hit-point exchanges — you are not trying to "survive" your committee, you are trying to converse with them about work you know better than anyone in the room. So use the simulator narrowly:

1. List the vectors you can genuinely speak to (you have a specific, rehearsed answer, not just intent).
2. Run several seeds and note which vectors keep getting added — those are the CATEGORIES of question you are least ready for.
3. For each recurring gap, write the actual question your real committee would ask, using the templates above, and rehearse the answer out loud.
4. Re-list defended vectors and iterate until the simulator graduates quickly from your honest starting position.

The simulator finds CATEGORIES of weakness, not the specific question. It will tell you "you're soft on coherence"; it cannot ask the exact question your external examiner will ask about chapter 4.

## What this won't catch

The simulator does not know your specific thesis. It identifies which categories of question deserve preparation, not the flawed argument on page 80. It also cannot model the live dynamics that decide most defenses: the rhythm of a follow-up, the committee member who is hostile because they are interested, the moment your voice betrays that you do not believe your own answer. Those only surface against real people.

## Companion advice

* A mock defense with two or three faculty adjacent to your committee beats the simulator by a wide margin. Ask them to be hostile and to interrupt.
* Rehearse the two-minute contribution summary until it is automatic — it sets the tone for the whole defense.
* Re-read the three works your committee is most likely to cite against you, and prepare the one-sentence distinction for each.
* Practice the honest answer "I don't know, but here is how I'd find out" out loud. Committees reward it; deflection they punish.
* Sleep before the defense more than you prepare the night before. You already did the work — the defense is about discussing it, and a tired candidate handles follow-ups worst.
