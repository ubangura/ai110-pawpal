from dataclasses import dataclass


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
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


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
    def schedule(self, owner: Owner) -> Schedule:
        """Build a prioritized daily care schedule within the owner's constraints."""
        constraints = owner.constraints
        preferences = owner.preferences
        tasks = sorted(owner.tasks, key=lambda task: task.priority)
        tasks = tasks[: constraints.max_tasks]

        scheduled_tasks = []
        total_duration_hours = 0.0
        dropped_tasks = []
        for task in tasks:
            if total_duration_hours + task.duration_hours <= constraints.time_available_hours:
                scheduled_tasks.append(task)
                total_duration_hours += task.duration_hours
            else:
                dropped_tasks.append(task)

        if preferences.group_tasks_by_pet:
            scheduled_tasks = sorted(scheduled_tasks, key=lambda task: id(task.pet))

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

        return Schedule(scheduled_tasks, total_duration_hours, "\n".join(lines))
