#!/usr/bin/env python3
"""
PhD Defence game simulator (lens-driven).

A panel of reviewers attacks the subject under evaluation. Each undefended
weakness takes HP damage. When HP hits zero, the candidate "dies", the killing
attack is added to the defended set (the idea is revised), and a new attempt
begins. Win by completing a full pass with HP > 0 — every vector hardened.

The attack vectors, committee personas, and partial-defense map are NOT
hardcoded: they are loaded from ../references/lenses.json for the chosen
`--lens`. That lets the same mechanic run against a grant proposal, a general
research idea, an engineering/evaluation strategy, or a thesis defense. Pick the
lens that fits the subject; `--list-lenses` shows the options.
"""

import argparse
import json
import os
import random
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set

LENSES_PATH = Path(__file__).resolve().parent.parent / "references" / "lenses.json"

# Damage multiplier by defense level. 0 = bulletproof, 1 = no defense.
DEFENSE_LEVELS = {"undefended": 1.0, "partial": 0.7, "defended": 0.0}


@dataclass
class Lens:
    key: str
    label: str
    vectors: List[str]
    vector_desc: Dict[str, str]
    committee: List[dict]
    related: Dict[str, List[str]]


def load_lenses() -> dict:
    if not LENSES_PATH.exists():
        print(f"lenses.json not found at {LENSES_PATH}", file=sys.stderr)
        sys.exit(2)
    return json.loads(LENSES_PATH.read_text())


def build_lens(cfg: dict, key: str) -> Lens:
    lenses = cfg.get("lenses", {})
    if key not in lenses:
        print(f"Unknown lens: {key!r}. Available: {', '.join(sorted(lenses))}", file=sys.stderr)
        sys.exit(1)
    l = lenses[key]
    committee = []
    for m in l["committee"]:
        committee.append({
            "name": m["name"],
            "title": m.get("title", ""),
            "specialties": list(m["specialties"]),
            "base_damage": tuple(m["base_damage"]),
            "specialty_damage": tuple(m["specialty_damage"]),
        })
    return Lens(
        key=key,
        label=l.get("label", key),
        vectors=list(l["vectors"].keys()),
        vector_desc=dict(l["vectors"]),
        committee=committee,
        related={k: list(v) for k, v in l.get("related", {}).items()},
    )


@dataclass
class QuestionResult:
    reviewer: str
    vector: str
    is_specialty: bool
    raw_damage: int
    defense: str
    final_damage: int


@dataclass
class AttemptResult:
    attempt_number: int
    starting_hp: int
    ending_hp: int
    died: bool
    questions: List[QuestionResult]
    defended_vectors_at_start: List[str]
    defended_vectors_at_end: List[str]


@dataclass
class GameResult:
    total_attempts: int
    survived: bool
    final_defended_set: List[str]
    attempts: List[AttemptResult]
    total_questions_faced: int
    total_damage_taken: int


def get_defense_level(vector: str, defended: Set[str], partial: Set[str]) -> str:
    if vector in defended:
        return "defended"
    if vector in partial:
        return "partial"
    return "undefended"


def assign_partial_defenses(defended: Set[str], related: Dict[str, List[str]]) -> Set[str]:
    """Defending one vector well gives partial defense to adjacent ones — prep
    for one tough question incidentally prepares you for neighbors."""
    partial: Set[str] = set()
    for d in defended:
        partial.update(related.get(d, []))
    return partial - defended


def run_attempt(attempt_num, defended, starting_hp, questions_per_attempt, lens, rng) -> AttemptResult:
    hp = starting_hp
    partial = assign_partial_defenses(defended, lens.related)
    questions: List[QuestionResult] = []

    for _ in range(questions_per_attempt):
        reviewer = rng.choice(lens.committee)
        is_specialty = rng.random() < 0.45
        if is_specialty:
            vector = rng.choice(reviewer["specialties"])
            dmg_range = reviewer["specialty_damage"]
        else:
            vector = rng.choice(lens.vectors)
            dmg_range = reviewer["base_damage"]

        raw_damage = rng.randint(dmg_range[0], dmg_range[1])
        defense = get_defense_level(vector, defended, partial)
        final_damage = int(round(raw_damage * DEFENSE_LEVELS[defense]))
        hp -= final_damage

        questions.append(QuestionResult(
            reviewer=reviewer["name"], vector=vector, is_specialty=is_specialty,
            raw_damage=raw_damage, defense=defense, final_damage=final_damage,
        ))
        if hp <= 0:
            break

    died = hp <= 0
    defended_at_end = set(defended)
    if died:
        damage_by_vector: Dict[str, int] = {}
        for q in questions:
            if q.defense == "undefended":
                damage_by_vector[q.vector] = damage_by_vector.get(q.vector, 0) + q.final_damage
        for vec, _ in sorted(damage_by_vector.items(), key=lambda x: -x[1])[:1]:
            defended_at_end.add(vec)
        if not damage_by_vector:
            partial_hits = [q.vector for q in questions if q.defense == "partial"]
            if partial_hits:
                defended_at_end.add(rng.choice(partial_hits))

    return AttemptResult(
        attempt_number=attempt_num, starting_hp=starting_hp, ending_hp=max(0, hp),
        died=died, questions=questions,
        defended_vectors_at_start=sorted(defended),
        defended_vectors_at_end=sorted(defended_at_end),
    )


def run_defense(lens, initial_defended=None, starting_hp=100, questions_per_attempt=8,
                max_attempts=15, seed=42) -> GameResult:
    rng = random.Random(seed)
    defended = set(initial_defended or [])
    attempts: List[AttemptResult] = []
    total_q = total_dmg = 0

    for n in range(1, max_attempts + 1):
        attempt = run_attempt(n, defended, starting_hp, questions_per_attempt, lens, rng)
        attempts.append(attempt)
        total_q += len(attempt.questions)
        total_dmg += sum(q.final_damage for q in attempt.questions)
        defended = set(attempt.defended_vectors_at_end)
        if not attempt.died:
            return GameResult(n, True, sorted(defended), attempts, total_q, total_dmg)

    return GameResult(max_attempts, False, sorted(defended), attempts, total_q, total_dmg)


def format_attempt(attempt: AttemptResult) -> str:
    lines = [f"\n--- Attempt {attempt.attempt_number} (HP {attempt.starting_hp}) ---",
             f"Defended going in: {', '.join(attempt.defended_vectors_at_start) or '(nothing yet)'}", ""]
    hp = attempt.starting_hp
    for i, q in enumerate(attempt.questions, 1):
        sp = " [specialty]" if q.is_specialty else ""
        hp -= q.final_damage
        marker = "X" if q.defense == "undefended" else ("~" if q.defense == "partial" else "+")
        lines.append(f"  Q{i}: {q.reviewer} attacks {q.vector}{sp} "
                     f"raw={q.raw_damage} def={q.defense} {marker}{q.final_damage}  HP={max(0, hp)}")
    lines.append("  >> DIED. Idea revised. New defenses added." if attempt.died
                 else f"  >> SURVIVED with {attempt.ending_hp} HP.")
    return "\n".join(lines)


def format_summary(result: GameResult, lens: Lens) -> str:
    verdict = "GRADUATED" if result.survived else "STILL VULNERABLE"
    lines = ["", "=" * 60, f"LENS: {lens.label} ({lens.key})", f"FINAL VERDICT: {verdict}", "=" * 60,
             f"Total attempts: {result.total_attempts}",
             f"Deaths before graduation: {result.total_attempts - (1 if result.survived else 0)}",
             f"Questions faced: {result.total_questions_faced}",
             f"Total damage absorbed: {result.total_damage_taken}",
             f"Final defended vectors ({len(result.final_defended_set)}/{len(lens.vectors)}):"]
    for v in result.final_defended_set:
        lines.append(f"  + {v}")
    undefended = [v for v in lens.vectors if v not in result.final_defended_set]
    if undefended:
        lines.append("\nStill undefended (potential gaps):")
        for v in undefended:
            lines.append(f"  ? {v} — {lens.vector_desc.get(v, '')}")
    return "\n".join(lines)


def main():
    cfg = load_lenses()
    default_lens = cfg.get("default") or next(iter(cfg.get("lenses", {})), "")

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lens", default=default_lens,
                   help=f"Evaluation lens (default: {default_lens}). See --list-lenses.")
    p.add_argument("--list-lenses", action="store_true", help="List available lenses and exit.")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--hp", type=int, default=100)
    p.add_argument("--questions-per-attempt", type=int, default=8)
    p.add_argument("--max-attempts", type=int, default=15)
    p.add_argument("--initial-defended", nargs="*", default=[],
                   help="Vectors already defended at start (lens-specific; see --list-lenses).")
    p.add_argument("--quiet", action="store_true", help="Only show summary.")
    p.add_argument("--json", action="store_true", help="Emit JSON.")
    args = p.parse_args()

    if args.list_lenses:
        for key, l in cfg.get("lenses", {}).items():
            star = " (default)" if key == default_lens else ""
            print(f"\n{key}{star} — {l.get('label', '')}")
            for v, d in l["vectors"].items():
                print(f"    {v}: {d}")
        return

    lens = build_lens(cfg, args.lens)

    invalid = [v for v in args.initial_defended if v not in lens.vectors]
    if invalid:
        print(f"Invalid vectors for lens {lens.key!r}: {invalid}", file=sys.stderr)
        print(f"Valid options: {', '.join(lens.vectors)}", file=sys.stderr)
        sys.exit(1)

    result = run_defense(lens, initial_defended=args.initial_defended, starting_hp=args.hp,
                         questions_per_attempt=args.questions_per_attempt,
                         max_attempts=args.max_attempts, seed=args.seed)

    if args.json:
        print(json.dumps({
            "lens": lens.key, "lens_label": lens.label,
            "total_attempts": result.total_attempts, "survived": result.survived,
            "final_defended_set": result.final_defended_set,
            "total_questions_faced": result.total_questions_faced,
            "total_damage_taken": result.total_damage_taken,
            "attempts": [{
                "attempt_number": a.attempt_number, "starting_hp": a.starting_hp,
                "ending_hp": a.ending_hp, "died": a.died,
                "defended_at_start": a.defended_vectors_at_start,
                "defended_at_end": a.defended_vectors_at_end,
                "questions": [asdict(q) for q in a.questions],
            } for a in result.attempts],
        }, indent=2))
        return

    if not args.quiet:
        for attempt in result.attempts:
            print(format_attempt(attempt))
    print(format_summary(result, lens))


if __name__ == "__main__":
    main()
