from pawpal_system import Constraints, Pet, Task, Owner


# --- Fixtures ---
def make_owner(name="John Doe", time_available_hours=8.0, max_tasks=5):
    constraints = Constraints(time_available_hours=time_available_hours, max_tasks=max_tasks)
    return Owner(name=name, constraints=constraints)

def make_pet(name="Mochi"):
    return Pet(name=name, species="dog", age=3)


def make_task(name="Morning walk", pet=None, duration_hours=0.5, priority=1):
    return Task(name=name, pet=pet or make_pet(), duration_hours=duration_hours, priority=priority)

# --- Tests ---

def test_task_incomplete_when_created():
    task = make_task()
    assert task.completed is False


def test_task_complete_when_marked():
    task = make_task()
    task.mark_complete()
    assert task.completed is True

def test_task_count_increase_when_add_task():
    owner = make_owner()
    initial_task_count = len(owner.tasks)
    task = make_task()
    owner.add_task(task)
    assert len(owner.tasks) == initial_task_count + 1
