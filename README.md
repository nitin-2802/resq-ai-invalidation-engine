# RESQ-AI — Selective Invalidation Engine (Prototype)

A minimal, dependency-free proof of the core mechanism behind RESQ-AI:
**an event should invalidate only the decisions whose assumptions it
breaks — not the whole plan.**

This reproduces the exact worked example from our deck (slide 5,
"Technical Architecture & Implementation"): a bridge closure on road R1
flips 2 of 9 dispatch decisions to `INVALID`, while the other 7 are left
untouched.

## Run it

```
python invalidation_engine.py
```

No dependencies beyond the Python standard library.

## What this proves

- Decisions are stored **with their justifications** (assumptions), not
  just as final answers — following Doyle's (1979) Truth Maintenance
  System.
- When a fact about the world changes, only decisions that actually
  depended on that fact are re-examined — "repair, not restart," per
  Fox, Gerevini, Long & Serina (2006).
- This is the mechanism, isolated from the LLM, the UI, and the backend.
  Those layers (Fusion, Risk, Allocation, Feasibility, Arbiter — see the
  deck) sit on top of this core loop but are not required to demonstrate
  that the invalidation logic itself is real.

## What this does *not* yet include

Scoped out deliberately, per the deck's Feasibility & Viability slide:

- The other four agents (Fusion, Risk, Allocation, Feasibility, Arbiter)
- The LLM-based arbitration and reconciliation layer
- The React dashboard / live zone map
- Real road-graph routing (A*/Dijkstra) — assumptions here are toggled
  directly rather than derived from a routing failure

These are the next build milestones (M1–M4 in the deck).
