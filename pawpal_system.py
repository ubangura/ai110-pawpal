from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Constraints:
    time_available_hours: float
    max_tasks: int = 10


@dataclass
class Preferences:
    group_tasks_by_pet: bool = False


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_conditions: bool = False


@dataclass
class Task:
    name: str
    pet: Pet
    duration_hours: float
    priority: int
    description: str = ""
    preferred_time: str = ""
    frequency: Frequency = Frequency.ONCE
    due_date: date | None = None
    completed: bool = False

    def mark_complete(self) -> Task | None:
        """Mark complete. Returns next occurrence if recurring, else None."""
        self.completed = True
        if self.frequency == Frequency.DAILY:
            next_date = (self.due_date or date.today()) + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            next_date = (self.due_date or date.today()) + timedelta(weeks=1)
        else:
            return None
        return Task(
            name=self.name,
            pet=self.pet,
            duration_hours=self.duration_hours,
            priority=self.priority,
            description=self.description,
            preferred_time=self.preferred_time,
            frequency=self.frequency,
            due_date=next_date,
        )


class Owner:
    def __init__(
        self,
        name: str,
        constraints: Constraints,
        preferences: Preferences | None = None,
    ):
        self.name = name
        self.constraints = constraints
        self.preferences = preferences or Preferences()
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add a care task to this owner's task list."""
        self.tasks.append(task)


class Schedule:
    def __init__(
        self,
        scheduled_tasks: list[Task],
        total_duration_hours: float,
        reasoning: str = "",
    ):
        self.scheduled_tasks = scheduled_tasks
        self.total_duration_hours = total_duration_hours
        self.reasoning = reasoning

    def display(self) -> None:
        """Print the schedule and reasoning to stdout."""
        print("=== Today's Pet Care Schedule ===")
        for i, task in enumerate(self.scheduled_tasks, start=1):
            print(f"  {i}. {task.name} — {task.pet.name} ({task.duration_hours:.1f}h)")
        print(f"\nTotal: {self.total_duration_hours:.1f}h")
        if self.reasoning:
            print(f"\n{self.reasoning}")


class Scheduler:
    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by preferred_time (HH:MM). Tasks without a time go last."""
        return sorted(tasks, key=lambda task: task.preferred_time or "99:99")

    def filter_completed_tasks(self, tasks: list[Task]) -> list[Task]:
        """Remove tasks that are already completed."""
        return [task for task in tasks if not task.completed]

    def filter_tasks_by_pet(self, tasks: list[Task], pet_name: str) -> list[Task]:
        """Return only tasks for the specified pet."""
        return [task for task in tasks if task.pet.name == pet_name]

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warning messages for tasks with the same preferred_time."""
        time_map: dict[str, list[Task]] = {}
        for task in tasks:
            if task.preferred_time:
                time_map.setdefault(task.preferred_time, []).append(task)

        warnings = []
        for time, group in time_map.items():
            if len(group) > 1:
                names = ", ".join(f"{task.name} ({task.pet.name})" for task in group)
                warnings.append(f"Conflict at {time}: {names}")
        return warnings

    def fit_to_budget(
        self, tasks: list[Task], time_available_hours: float
    ) -> tuple[list[Task], list[Task]]:
        """Select tasks that fit within the time budget. Returns (scheduled, dropped)."""
        scheduled = []
        dropped = []
        total = 0.0
        for task in tasks:
            if total + task.duration_hours <= time_available_hours:
                scheduled.append(task)
                total += task.duration_hours
            else:
                dropped.append(task)
        return scheduled, dropped

    def apply_ordering(
        self, tasks: list[Task], preferences: Preferences
    ) -> list[Task]:
        """Apply preference-based ordering, then sort by preferred time."""
        ordered = tasks
        if preferences.group_tasks_by_pet:
            ordered = sorted(ordered, key=lambda task: id(task.pet))
        return self.sort_by_time(ordered)

    def build_reasoning(
        self,
        owner: Owner,
        scheduled_tasks: list[Task],
        dropped_tasks: list[Task],
        total_duration_hours: float,
    ) -> str:
        """Build a human-readable explanation of the scheduling decisions."""
        constraints = owner.constraints
        preferences = owner.preferences

        lines = [
            f"Scheduled {len(scheduled_tasks)} of {len(owner.tasks)} tasks "
            f"totalling {total_duration_hours:.1f}h "
            f"(budget: {constraints.time_available_hours:.1f}h).",
        ]

        if len(owner.tasks) > constraints.max_tasks:
            lines.append(
                f"Task cap of {constraints.max_tasks} applied — "
                f"{len(owner.tasks) - constraints.max_tasks} lowest-priority task(s) excluded before scheduling."
            )

        if dropped_tasks:
            names = ", ".join(task.name for task in dropped_tasks)
            lines.append(f"Dropped due to time constraints: {names}.")

        if preferences.group_tasks_by_pet:
            lines.append("Tasks grouped by pet.")

        lines.extend(self.detect_conflicts(scheduled_tasks))

        return "\n".join(lines)

    def schedule(self, owner: Owner) -> Schedule:
        """Build a prioritized daily care schedule within the owner's constraints."""
        tasks = sorted(owner.tasks, key=lambda task: task.priority)
        tasks = tasks[: owner.constraints.max_tasks]

        scheduled, dropped = self.fit_to_budget(tasks, owner.constraints.time_available_hours)
        scheduled = self.apply_ordering(scheduled, owner.preferences)
        total = sum(task.duration_hours for task in scheduled)
        reasoning = self.build_reasoning(owner, scheduled, dropped, total)

        return Schedule(scheduled, total, reasoning)
