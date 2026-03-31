from dataclasses import dataclass, field


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
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
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
        pass


class Scheduler:
    def schedule(self, owner: Owner) -> Schedule:
        raise NotImplementedError
