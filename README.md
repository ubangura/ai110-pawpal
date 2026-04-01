# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The scheduler goes beyond basic task listing with several features:

- **Priority-based filtering** — tasks are sorted by priority (1 = highest) and fitted into the owner's time budget. Tasks that don't fit are dropped and reported.
- **Preferred times** — each task can have an optional `preferred_time` (HH:MM format). The schedule is sorted chronologically so the daily plan reads like a timeline.
- **Conflict detection** — if two or more tasks share the same preferred time, the scheduler flags them with a warning in the reasoning output.
- **Group by pet** — an optional preference that clusters tasks for the same pet together in the schedule.
- **Recurring tasks** — tasks can be set to `DAILY` or `WEEKLY` frequency. When marked complete, `mark_complete()` returns a new task instance with the next due date calculated via `timedelta`.
- **Explainable output** — every schedule includes a reasoning summary: what was scheduled, what was dropped and why, whether grouping was applied, and any detected conflicts.
