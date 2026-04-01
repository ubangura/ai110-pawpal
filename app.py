import streamlit as st
from pawpal_system import Constraints, Owner, Pet, Preferences, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown("""
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
""")

with st.expander("Scenario", expanded=True):
    st.markdown("""
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
""")

with st.expander("What you need to build", expanded=True):
    st.markdown("""
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
""")

st.divider()

# --- Session state initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None
    st.session_state.schedule = None

# --- Owner Setup ---
st.subheader("Owner Setup")
with st.form("owner_form"):
    name = st.text_input("Owner name", value="Jordan")
    time_available_hours = st.number_input(
        "Time available today (hours)",
        min_value=0.5,
        max_value=24.0,
        value=4.0,
        step=0.5,
    )
    max_tasks = st.number_input("Max tasks", min_value=1, max_value=20, value=10)
    group_tasks_by_pet = st.checkbox("Group tasks by pet")
    submitted = st.form_submit_button("Save owner")

if submitted:
    constraints = Constraints(
        time_available_hours=time_available_hours, max_tasks=int(max_tasks)
    )
    preferences = Preferences(group_tasks_by_pet=group_tasks_by_pet)
    st.session_state.owner = Owner(
        name=name, constraints=constraints, preferences=preferences
    )
    st.session_state.schedule = None
    st.success(f"Owner '{name}' saved.")

# --- Add Pet ---
if st.session_state.owner is not None:
    st.divider()
    st.subheader("Pets")

    with st.form("pet_form"):
        pet_name = st.text_input("Pet name", value="Mochi")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
        health_conditions = st.checkbox("Has health conditions")
        pet_submitted = st.form_submit_button("Add pet")

    if pet_submitted:
        pet = Pet(
            name=pet_name,
            species=species,
            age=int(age),
            health_conditions=health_conditions,
        )
        st.session_state.owner.add_pet(pet)
        st.success(f"Pet '{pet_name}' added.")

    if st.session_state.owner.pets:
        st.write("Current pets:")
        st.table(
            [
                {
                    "Name": p.name,
                    "Species": p.species,
                    "Age": p.age,
                    "Health conditions": p.health_conditions,
                }
                for p in st.session_state.owner.pets
            ]
        )

# --- Add Task ---
if st.session_state.owner is not None and len(st.session_state.owner.pets) > 0:
    st.divider()
    st.subheader("Tasks")

    pet_names = [p.name for p in st.session_state.owner.pets]

    with st.form("task_form"):
        task_name = st.text_input("Task name", value="Morning walk")
        selected_pet_name = st.selectbox("Pet", pet_names)
        duration_hours = st.number_input(
            "Duration (hours)", min_value=0.1, max_value=8.0, value=0.5, step=0.1
        )
        priority = st.number_input(
            "Priority (1 = highest)", min_value=1, max_value=10, value=1
        )
        description = st.text_input("Description (optional)", value="")
        task_submitted = st.form_submit_button("Add task")

    if task_submitted:
        selected_pet = next(
            p for p in st.session_state.owner.pets if p.name == selected_pet_name
        )
        task = Task(
            name=task_name,
            pet=selected_pet,
            duration_hours=duration_hours,
            priority=int(priority),
            description=description,
        )
        st.session_state.owner.add_task(task)
        st.success(f"Task '{task_name}' added.")

    if st.session_state.owner.tasks:
        st.write("Current tasks:")
        st.table(
            [
                {
                    "Task": t.name,
                    "Pet": t.pet.name,
                    "Duration (h)": t.duration_hours,
                    "Priority": t.priority,
                }
                for t in st.session_state.owner.tasks
            ]
        )

# --- Generate Schedule ---
if st.session_state.owner is not None and len(st.session_state.owner.tasks) > 0:
    st.divider()
    st.subheader("Build Schedule")

    if st.button("Generate schedule"):
        scheduler = Scheduler()
        st.session_state.schedule = scheduler.schedule(st.session_state.owner)

    if st.session_state.schedule is not None:
        schedule = st.session_state.schedule
        st.write("### Today's Schedule")
        if schedule.scheduled_tasks:
            st.table(
                [
                    {
                        "#": i,
                        "Task": t.name,
                        "Pet": t.pet.name,
                        "Duration (h)": t.duration_hours,
                        "Priority": t.priority,
                    }
                    for i, t in enumerate(schedule.scheduled_tasks, start=1)
                ]
            )
            st.write(f"**Total: {schedule.total_duration_hours:.1f}h**")
        else:
            st.warning("No tasks could be scheduled within the given constraints.")

        if schedule.reasoning:
            st.info(schedule.reasoning)
