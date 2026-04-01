from datetime import date, timedelta

from pawpal_system import Constraints, Frequency, Pet, Task, Owner


# --- Fixtures ---
def make_owner(name="John Doe", time_available_hours=8.0, max_tasks=5):
    constraints = Constraints(
        time_available_hours=time_available_hours, max_tasks=max_tasks
    )
    return Owner(name=name, constraints=constraints)


def make_pet(name="Mochi"):
    return Pet(name=name, species="dog", age=3)


def make_task(name="Morning walk", pet=None, duration_hours=0.5, priority=1):
    return Task(
        name=name,
        pet=pet or make_pet(),
        duration_hours=duration_hours,
        priority=priority,
    )


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


# --- Recurring tasks ---


def test_once_task_returns_none_when_completed():
    task = make_task()
    next_task = task.mark_complete()
    assert next_task is None


def test_daily_task_returns_next_day_when_completed():
    task = make_task()
    task.frequency = Frequency.DAILY
    task.due_date = date(2026, 3, 27)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == date(2026, 3, 28)
    assert next_task.completed is False
    assert next_task.frequency == Frequency.DAILY


def test_weekly_task_returns_next_week_when_completed():
    task = make_task()
    task.frequency = Frequency.WEEKLY
    task.due_date = date(2026, 3, 27)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == date(2026, 4, 3)
    assert next_task.completed is False


def test_daily_task_uses_today_when_no_due_date():
    task = make_task()
    task.frequency = Frequency.DAILY
    next_task = task.mark_complete()
    assert next_task.due_date == date.today() + timedelta(days=1)
