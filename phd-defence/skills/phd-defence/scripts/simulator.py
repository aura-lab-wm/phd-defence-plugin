#!/usr/bin/env python3
"""
PhD Defence game simulator.

A panel of expert reviewers attacks a thesis/proposal. Each undefended weakness
takes HP damage. When HP hits zero, the candidate "dies", the killing attacks
are added to the defended set (the idea is revised), and a new attempt begins.

Win condition: complete a defense run with full HP remaining (no damage landed),
meaning every attack vector has been hardened. This typically takes 5-10 deaths,
which models the "your idea gets killed enough times that it becomes rock solid"
intuition from real PhD work and NSF proposal preparation.
"""

import argparse
import json
import random
import sys
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Tuple


# The full pool of attack vectors. A real PhD or NSF proposal must eventually
# defend against most of these. The set is intentionally broad — a freshly
# written idea typically has only 2-4 of these defended on the first pass.
ATTACK_VECTORS = [
    "novelty",            # Is this actually new vs prior work?
    "prior_work",         # Have you covered the relevant literature?
    "methodology",        # Is your method sound?
    "evaluation",         # How will you measure success?
    "feasibility",        # Can this actually be done in the budget/time?
    "scalability",        # Does it work beyond toy scale?
    "reproducibility",    # Can others replicate it?
    "ethics",             # Have you addressed ethical concerns?
    "broader_impact",     # Why does this matter to society?
    "theoretical_basis",  # What's the underlying theory?
    "baselines",          # Have you compared to the right baselines?
    "limitations",        # What can't this do?
    "team_expertise",     # Why is YOUR team the one to do this?
    "data_availability",  # Where does the data come from?
    "intellectual_merit", # Is the intellectual contribution clear?
]


# Each committee member has 1-2 specialties (attack vectors they hit harder)
# and a base damage range.
COMMITTEE = [
    {
        "name": "Prof. Hawthorne",
        "title": "the theory hawk",
        "specialties": ["theoretical_basis", "novelty"],
        "base_damage": (14, 22),
        "specialty_damage": (22, 34),
    },
    {
        "name": "Prof. Okafor",
        "title": "the methodologist",
        "specialties": ["methodology", "evaluation", "baselines"],
        "base_damage": (12, 20),
        "specialty_damage": (20, 32),
    },
    {
        "name": "Prof. Lindqvist",
        "title": "the program officer",
        "specialties": ["feasibility", "broader_impact", "team_expertise"],
        "base_damage": (14, 22),
        "specialty_damage": (22, 34),
    },
    {
        "name": "Prof. Reyes",
        "title": "the skeptic",
        "specialties": ["prior_work", "limitations", "reproducibility"],
        "base_damage": (12, 18),
        "specialty_damage": (18, 30),
    },
    {
        "name": "Prof. Tanaka",
        "title": "the impact reviewer",
        "specialties": ["intellectual_merit", "ethics", "data_availability"],
        "base_damage": (14, 20),
        "specialty_damage": (20, 32),
    },
]


# Damage multiplier when the candidate has the attack vector in their
# defended set. 0 = fully bulletproof, 1 = no defense at all.
DEFENSE_LEVELS = {
    "undefended":    1.0,   # full damage
    "partial":       0.7,   # only modestly reduced by tangential prep
    "defended":      0.0,   # bulletproof
}


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


def assign_partial_defenses(defended: Set[str]) -> Set[str]:
    """When you defend one vector well, related ones get partial defense.

    e.g., defending 'methodology' gives partial defense on 'evaluation' and
    'baselines'. This models real research where preparing for one tough
    question incidentally prepares you for adjacent ones.
    """
    related = {
        "methodology": {"evaluation", "baselines"},
        "evaluation": {"methodology", "baselines"},
        "baselines": {"methodology", "prior_work"},
        "novelty": {"prior_work"},
        "prior_work": {"novelty", "baselines"},
        "feasibility": {"data_availability", "team_expertise"},
        "scalability": {"feasibility"},
        "reproducibility": {"methodology"},
        "broader_impact": {"intellectual_merit", "ethics"},
        "intellectual_merit": {"broader_impact", "novelty"},
        "theoretical_basis": {"novelty", "methodology"},
        "limitations": {"reproducibility"},
        "team_expertise": {"feasibility"},
        "data_availability": {"feasibility", "ethics"},
        "ethics": {"broader_impact", "data_availability"},
    }
    partial: Set[str] = set()
    for d in defended:
        partial.update(related.get(d, set()))
    return partial - defended


def run_attempt(
    attempt_num: int,
    defended: Set[str],
    starting_hp: int,
    questions_per_attempt: int,
    rng: random.Random,
) -> AttemptResult:
    """One pass through the defense. Returns the attempt record and updates
    the defended set with whatever attacks killed the candidate (if any)."""
    hp = starting_hp
    partial = assign_partial_defenses(defended)
    questions: List[QuestionResult] = []
    killing_vectors: List[str] = []

    for q in range(questions_per_attempt):
        reviewer = rng.choice(COMMITTEE)
        is_specialty = rng.random() < 0.45  # 45% specialty
        if is_specialty:
            vector = rng.choice(reviewer["specialties"])
            dmg_range = reviewer["specialty_damage"]
        else:
            vector = rng.choice(ATTACK_VECTORS)
            dmg_range = reviewer["base_damage"]

        raw_damage = rng.randint(dmg_range[0], dmg_range[1])
        defense = get_defense_level(vector, defended, partial)
        final_damage = int(round(raw_damage * DEFENSE_LEVELS[defense]))
        hp -= final_damage

        questions.append(QuestionResult(
            reviewer=reviewer["name"],
            vector=vector,
            is_specialty=is_specialty,
            raw_damage=raw_damage,
            defense=defense,
            final_damage=final_damage,
        ))

        if final_damage > 0:
            killing_vectors.append(vector)

        if hp <= 0:
            break

    died = hp <= 0
    defended_at_end = set(defended)
    if died:
        # The candidate "dies". The most-damaging undefended vectors from this
        # attempt are added to the defended set (the idea is revised based on
        # what killed them). We add up to 2 per death — researchers typically
        # patch the biggest leaks first.
        damage_by_vector: Dict[str, int] = {}
        for q in questions:
            if q.defense == "undefended":
                damage_by_vector[q.vector] = damage_by_vector.get(q.vector, 0) + q.final_damage
        # Sort by total damage dealt, add top 1 to the defended set
        sorted_vectors = sorted(damage_by_vector.items(), key=lambda x: -x[1])
        for vec, _ in sorted_vectors[:1]:
            defended_at_end.add(vec)
        # If only partial-defended vectors hit, promote one of them
        if not damage_by_vector:
            partial_hits = [q.vector for q in questions if q.defense == "partial"]
            if partial_hits:
                defended_at_end.add(rng.choice(partial_hits))

    return AttemptResult(
        attempt_number=attempt_num,
        starting_hp=starting_hp,
        ending_hp=max(0, hp),
        died=died,
        questions=questions,
        defended_vectors_at_start=sorted(defended),
        defended_vectors_at_end=sorted(defended_at_end),
    )


def run_defense(
    initial_defended: List[str] = None,
    starting_hp: int = 100,
    questions_per_attempt: int = 8,
    max_attempts: int = 15,
    seed: int = 42,
) -> GameResult:
    """Run the full game: keep attempting until candidate survives a full
    pass with HP > 0 at the end, OR max_attempts is reached."""
    rng = random.Random(seed)
    initial = set(initial_defended or [])
    defended = set(initial)
    attempts: List[AttemptResult] = []
    total_q = 0
    total_dmg = 0

    for n in range(1, max_attempts + 1):
        attempt = run_attempt(n, defended, starting_hp, questions_per_attempt, rng)
        attempts.append(attempt)
        total_q += len(attempt.questions)
        total_dmg += sum(q.final_damage for q in attempt.questions)
        defended = set(attempt.defended_vectors_at_end)

        if not attempt.died:
            # Survived a full attempt — the idea is rock solid
            return GameResult(
                total_attempts=n,
                survived=True,
                final_defended_set=sorted(defended),
                attempts=attempts,
                total_questions_faced=total_q,
                total_damage_taken=total_dmg,
            )

    return GameResult(
        total_attempts=max_attempts,
        survived=False,
        final_defended_set=sorted(defended),
        attempts=attempts,
        total_questions_faced=total_q,
        total_damage_taken=total_dmg,
    )


def format_attempt(attempt: AttemptResult) -> str:
    lines = []
    lines.append(f"\n--- Attempt {attempt.attempt_number} (HP {attempt.starting_hp}) ---")
    lines.append(f"Defended going in: {', '.join(attempt.defended_vectors_at_start) or '(nothing yet)'}")
    lines.append("")
    hp = attempt.starting_hp
    for i, q in enumerate(attempt.questions, 1):
        sp = " [specialty]" if q.is_specialty else ""
        hp -= q.final_damage
        marker = "X" if q.defense == "undefended" else ("~" if q.defense == "partial" else "+")
        lines.append(
            f"  Q{i}: {q.reviewer} attacks {q.vector}{sp} "
            f"raw={q.raw_damage} def={q.defense} {marker}{q.final_damage}  HP={max(0, hp)}"
        )
    if attempt.died:
        lines.append(f"  >> DIED. Idea revised. New defenses added.")
    else:
        lines.append(f"  >> SURVIVED with {attempt.ending_hp} HP.")
    return "\n".join(lines)


def format_summary(result: GameResult) -> str:
    verdict = "GRADUATED" if result.survived else "PROPOSAL STILL VULNERABLE"
    lines = [
        "",
        "=" * 60,
        f"FINAL VERDICT: {verdict}",
        "=" * 60,
        f"Total attempts: {result.total_attempts}",
        f"Deaths before graduation: {result.total_attempts - (1 if result.survived else 0)}",
        f"Questions faced: {result.total_questions_faced}",
        f"Total damage absorbed: {result.total_damage_taken}",
        f"Final defended vectors ({len(result.final_defended_set)}/{len(ATTACK_VECTORS)}):",
    ]
    for v in result.final_defended_set:
        lines.append(f"  + {v}")
    undefended = [v for v in ATTACK_VECTORS if v not in result.final_defended_set]
    if undefended:
        lines.append(f"\nStill undefended (potential gaps):")
        for v in undefended:
            lines.append(f"  ? {v}")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--hp", type=int, default=100)
    p.add_argument("--questions-per-attempt", type=int, default=8)
    p.add_argument("--max-attempts", type=int, default=15)
    p.add_argument(
        "--initial-defended",
        nargs="*",
        default=[],
        help=f"Attack vectors already defended at start. Choose from: {', '.join(ATTACK_VECTORS)}",
    )
    p.add_argument("--quiet", action="store_true", help="Only show summary, not per-attempt detail")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable")
    args = p.parse_args()

    # Validate initial defenses
    invalid = [v for v in args.initial_defended if v not in ATTACK_VECTORS]
    if invalid:
        print(f"Invalid vectors: {invalid}", file=sys.stderr)
        print(f"Valid options: {ATTACK_VECTORS}", file=sys.stderr)
        sys.exit(1)

    result = run_defense(
        initial_defended=args.initial_defended,
        starting_hp=args.hp,
        questions_per_attempt=args.questions_per_attempt,
        max_attempts=args.max_attempts,
        seed=args.seed,
    )

    if args.json:
        out = {
            "total_attempts": result.total_attempts,
            "survived": result.survived,
            "final_defended_set": result.final_defended_set,
            "total_questions_faced": result.total_questions_faced,
            "total_damage_taken": result.total_damage_taken,
            "attempts": [
                {
                    "attempt_number": a.attempt_number,
                    "starting_hp": a.starting_hp,
                    "ending_hp": a.ending_hp,
                    "died": a.died,
                    "defended_at_start": a.defended_vectors_at_start,
                    "defended_at_end": a.defended_vectors_at_end,
                    "questions": [asdict(q) for q in a.questions],
                }
                for a in result.attempts
            ],
        }
        print(json.dumps(out, indent=2))
        return

    if not args.quiet:
        for attempt in result.attempts:
            print(format_attempt(attempt))
    print(format_summary(result))


if __name__ == "__main__":
    main()
