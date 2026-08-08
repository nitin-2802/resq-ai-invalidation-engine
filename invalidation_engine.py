"""
RESQ-AI — Assumption Graph & Selective Invalidation Engine
=============================================================

Proof-of-concept for the core claim in the RESQ-AI deck (slide 5):

    "An event invalidates only the decisions whose assumptions it
    breaks. The rest of the plan stands, and crews already moving
    are never re-tasked."

This script reproduces the exact worked example from the deck:
  - 9 dispatch decisions form "Plan v1"
  - Event: road R1 floods and becomes impassable
  - Only decisions that assumed "R1 is passable" flip to INVALID
  - The remaining decisions are left untouched

Design basis (from the deck's Research & Reference slide):
  - Doyle, J. (1979). A Truth Maintenance System.
        -> decisions are stored WITH their justifications (assumptions),
           and only re-examined when a justification fails.
  - Fox, Gerevini, Long & Serina (2006). Plan Stability: Replanning vs
    Plan Repair.
        -> repairing only the broken parts of a plan is faster and more
           stable than replanning from scratch.

No LLM, no UI, no backend required to prove this mechanism —
this is pure graph logic, deliberately kept dependency-free
(standard library only) so it's trivial to run and inspect.

Usage:
    python invalidation_engine.py
"""

from dataclasses import dataclass, field
from enum import Enum


class Status(Enum):
    VALID = "VALID"
    INVALID = "INVALID"


@dataclass
class Assumption:
    """A single fact about the world that one or more decisions rely on."""
    id: str
    description: str
    holds: bool = True  # True = fact is currently true


@dataclass
class Decision:
    """A dispatch decision, carrying the assumptions it depends on."""
    id: str
    description: str
    assumption_ids: list = field(default_factory=list)
    status: Status = Status.VALID


class WorldState:
    """
    The shared world-state: one place holding every assumption and
    every decision, plus the assumption graph linking them.
    """

    def __init__(self):
        self.assumptions: dict[str, Assumption] = {}
        self.decisions: dict[str, Decision] = {}

    def add_assumption(self, a: Assumption):
        self.assumptions[a.id] = a

    def add_decision(self, d: Decision):
        self.decisions[d.id] = d

    def break_assumption(self, assumption_id: str):
        """An event fires and a fact about the world becomes false."""
        self.assumptions[assumption_id].holds = False

    def propagate_invalidation(self) -> list[str]:
        """
        Walk the assumption graph: any decision that depends on a
        now-false assumption flips to INVALID. Everything else is
        left exactly as it was — this is the 'repair, not restart'
        behaviour from the deck.

        Returns the list of decision IDs that flipped this round.
        """
        newly_invalid = []
        for decision in self.decisions.values():
            if decision.status == Status.INVALID:
                continue  # already invalid, nothing to do
            for a_id in decision.assumption_ids:
                if not self.assumptions[a_id].holds:
                    decision.status = Status.INVALID
                    newly_invalid.append(decision.id)
                    break
        return newly_invalid

    def print_ledger(self, title: str):
        print(f"\nDECISION LEDGER · {title}")
        print(f"{'ID':<6}{'DESCRIPTION':<40}{'STATUS':<10}")
        print("-" * 56)
        for d in self.decisions.values():
            print(f"{d.id:<6}{d.description:<40}{d.status.value:<10}")


def build_bridge_closure_scenario() -> WorldState:
    """
    Recreates the exact scenario from the deck's slide 5:
    9 decisions, most routed independently, two of them (D-07, D-11)
    sharing a dependency on road R1 being passable.
    """
    ws = WorldState()

    # --- Assumptions: facts about the world each decision depends on ---
    ws.add_assumption(Assumption("A1_R1_passable", "Road R1 is passable"))
    ws.add_assumption(Assumption("A2_T2_unassigned", "Team T2 is unassigned"))
    ws.add_assumption(Assumption("A3_Z4_priority_high", "Zone Z4 priority >= HIGH"))
    ws.add_assumption(Assumption("A4_R4_passable", "Road R4 is passable"))
    ws.add_assumption(Assumption("A5_R2_passable", "Road R2 is passable"))
    ws.add_assumption(Assumption("A6_R3_passable", "Road R3 is passable"))

    # --- Decisions: dispatches, each carrying the assumptions it rests on ---
    ws.add_decision(Decision("D-05", "Team T1 -> Zone Z2 via R4", ["A4_R4_passable"]))
    ws.add_decision(Decision("D-07", "Team T2 -> Zone Z4 via R1",
                              ["A1_R1_passable", "A2_T2_unassigned", "A3_Z4_priority_high"]))
    ws.add_decision(Decision("D-11", "Amb A2 -> Hospital H1 via R1", ["A1_R1_passable"]))
    ws.add_decision(Decision("D-02", "Team T3 -> Zone Z1 via R2", ["A5_R2_passable"]))
    ws.add_decision(Decision("D-03", "Team T4 -> Zone Z5 via R3", ["A6_R3_passable"]))
    ws.add_decision(Decision("D-04", "Amb A1 -> Hospital H2 via R4", ["A4_R4_passable"]))
    ws.add_decision(Decision("D-06", "Team T5 -> Zone Z3 via R2", ["A5_R2_passable"]))
    ws.add_decision(Decision("D-08", "Amb A3 -> Shelter S1 via R3", ["A6_R3_passable"]))
    ws.add_decision(Decision("D-09", "Team T6 -> Zone Z6 via R4", ["A4_R4_passable"]))

    return ws


def main():
    ws = build_bridge_closure_scenario()

    print("=" * 56)
    print(" RESQ-AI — Selective Invalidation Demo")
    print("=" * 56)

    ws.print_ledger("PLAN v1 (9 decisions, awaiting approval)")

    print("\nEVENT  t+08:00   R1 flooded, impassable")
    ws.break_assumption("A1_R1_passable")

    flipped = ws.propagate_invalidation()

    print(f"\nAssumption A1 fails -> {len(flipped)} decision(s) flip to INVALID: {flipped}")

    ws.print_ledger("PLAN v2 (after selective repair)")

    total = len(ws.decisions)
    untouched = total - len(flipped)
    print(f"\n{untouched} of {total} decisions untouched — the rest of the response keeps moving.")
    print(f"(A full re-plan would have re-tasked all {total} of {total}, including crews already en route.)")


if __name__ == "__main__":
    main()
