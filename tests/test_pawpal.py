from datetime import date, timedelta

from pawpal_system import (
    Constraints,
    Frequency,
    Pet,
    Preferences,
    Task,
    Owner,
    Scheduler,
)


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


def test_weekly_task_uses_today_when_no_due_date():
    task = make_task()
    task.frequency = Frequency.WEEKLY
    next_task = task.mark_complete()
    assert next_task.due_date == date.today() + timedelta(weeks=1)


def test_next_occurrence_independent_when_original_mutated():
    task = make_task()
    task.frequency = Frequency.DAILY
    task.due_date = date(2026, 3, 27)
    next_task = task.mark_complete()
    assert next_task is not None
    next_task.name = "Changed"
    assert task.name == "Morning walk"


# --- Scheduling ---


def test_schedule_priority_order_when_tasks_have_different_priorities():
    scheduler = Scheduler()
    owner = make_owner(time_available_hours=10.0, max_tasks=10)
    pet = make_pet()
    owner.add_task(make_task("Low priority", pet=pet, duration_hours=0.5, priority=3))
    owner.add_task(make_task("High priority", pet=pet, duration_hours=0.5, priority=1))
    owner.add_task(make_task("Mid priority", pet=pet, duration_hours=0.5, priority=2))
    schedule = scheduler.schedule(owner)
    names = [t.name for t in schedule.scheduled_tasks]
    assert (
        names.index("High priority")
        < names.index("Mid priority")
        < names.index("Low priority")
    )


def test_schedule_drops_tasks_when_exceeding_time_budget():
    scheduler = Scheduler()
    owner = make_owner(time_available_hours=1.0, max_tasks=10)
    pet = make_pet()
    owner.add_task(make_task("Task A", pet=pet, duration_hours=0.6, priority=1))
    owner.add_task(make_task("Task B", pet=pet, duration_hours=0.6, priority=2))
    schedule = scheduler.schedule(owner)
    assert len(schedule.scheduled_tasks) == 1
    assert schedule.total_duration_hours <= 1.0


def test_schedule_drops_all_when_zero_time_available():
    scheduler = Scheduler()
    owner = make_owner(time_available_hours=0.0, max_tasks=10)
    owner.add_task(make_task(pet=make_pet()))
    schedule = scheduler.schedule(owner)
    assert schedule.scheduled_tasks == []
    assert schedule.total_duration_hours == 0.0


def test_schedule_excludes_lowest_priority_when_exceeding_max_tasks():
    scheduler = Scheduler()
    owner = make_owner(time_available_hours=10.0, max_tasks=2)
    pet = make_pet()
    owner.add_task(make_task("Keep A", pet=pet, duration_hours=0.5, priority=1))
    owner.add_task(make_task("Keep B", pet=pet, duration_hours=0.5, priority=2))
    owner.add_task(make_task("Drop C", pet=pet, duration_hours=0.5, priority=3))
    schedule = scheduler.schedule(owner)
    scheduled_names = [t.name for t in schedule.scheduled_tasks]
    assert "Drop C" not in scheduled_names
    assert len(schedule.scheduled_tasks) == 2


# --- Conflict Detection ---


def test_detect_conflicts_warns_when_same_preferred_time():
    scheduler = Scheduler()
    pet = make_pet()
    t1 = make_task("Walk", pet=pet)
    t1.preferred_time = "08:00"
    t2 = make_task("Feed", pet=pet)
    t2.preferred_time = "08:00"
    warnings = scheduler.detect_conflicts([t1, t2])
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_detect_conflicts_ignores_when_empty_preferred_time():
    scheduler = Scheduler()
    pet = make_pet()
    t1 = make_task("Walk", pet=pet)
    t2 = make_task("Feed", pet=pet)
    warnings = scheduler.detect_conflicts([t1, t2])
    assert warnings == []


def test_detect_conflicts_single_warning_when_three_tasks_same_time():
    scheduler = Scheduler()
    pet = make_pet()
    tasks = []
    for name in ("Walk", "Feed", "Groom"):
        t = make_task(name, pet=pet)
        t.preferred_time = "09:00"
        tasks.append(t)
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1


# --- Filtering ---


def test_filter_completed_tasks_excluded_when_done():
    scheduler = Scheduler()
    pet = make_pet()
    done = make_task("Done task", pet=pet)
    done.completed = True
    pending = make_task("Pending task", pet=pet)
    result = scheduler.filter_completed_tasks([done, pending])
    assert result == [pending]


def test_filter_completed_tasks_empty_when_all_done():
    scheduler = Scheduler()
    pet = make_pet()
    tasks = [make_task(f"Task {i}", pet=pet) for i in range(3)]
    for t in tasks:
        t.completed = True
    assert scheduler.filter_completed_tasks(tasks) == []


def test_filter_tasks_returns_match_when_filtered_by_pet():
    scheduler = Scheduler()
    mochi = make_pet("Mochi")
    luna = make_pet("Luna")
    t1 = make_task("Walk", pet=mochi)
    t2 = make_task("Feed", pet=luna)
    t3 = make_task("Groom", pet=mochi)
    result = scheduler.filter_tasks_by_pet([t1, t2, t3], "Mochi")
    assert all(t.pet.name == "Mochi" for t in result)
    assert len(result) == 2


# --- Boundary ---


def test_schedule_empty_when_no_tasks():
    scheduler = Scheduler()
    owner = make_owner()
    schedule = scheduler.schedule(owner)
    assert schedule.scheduled_tasks == []
    assert schedule.total_duration_hours == 0.0
