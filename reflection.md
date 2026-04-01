# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The two main design decisions I made were how to represent constraints and preferences, and how to structure the scheduling logic. I created separate classes for `Constraints` and `Preferences` to encapsulate those concepts and make it easier to manage them. For scheduling, I decided to implement a simple priority-based algorithm that considers task duration and owner preferences.

I did consider a Task being related to multiple pets and a pet being able to have multiple owners, but I decided to keep it simple for this project and assume a one-to-one relationship between pets and owners. This allowed me to focus on the scheduling logic without getting bogged down in complex relationships in scheduling.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. Initially, the `Owner` class had a `time_available_hours` attribute directly, but I realized that it would be cleaner to have a separate `Constraints` class that could include not just time availability but also other constraints. This change made the design more flexible and allowed for easier expansion in the future if I wanted to add more types of constraints.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers two  constraints and one preference. The constraints are `time_available_hours` (the total time budget for the day) and `max_tasks` (a cap on how many tasks can be scheduled). The preference is `group_tasks_by_pet`, which reorders the final schedule to cluster tasks for the same pet together.

Task priority (an integer where 1 is highest priority) determines which tasks are scheduled first and which are dropped when the time budget runs out. I decided that time availability was the most important constraint because it reflects real-world limit. The `max_tasks` cap was added to prevent overwhelming schedules. Priority was chosen as the tiebreaker because not all tasks are equally critical (e.g., medication is more important than playtime).

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses a greedy approach: it sorts tasks by priority and schedules them one by one until the time budget is exhausted, skipping any task that doesn't fit. This means it may skip a long high-priority task and still schedule several shorter lower-priority tasks that fit in the remaining time. So, the scheduler doesn't find the globally optimal combination of tasks.

This tradeoff is reasonable for a version 1 app. An owner benefits more from a simple, explainable plan — "these tasks were scheduled in priority order, these were dropped because time ran out" — than from a mathematically optimal but harder-to-understand result.

Additionally, the conflict detection only checks for exact `preferred_time` matches. It flags two tasks at "07:00" but not a 1-hour task at "07:00" overlapping with a task at "07:30." Detecting overlapping durations would require computing end times (`start + duration`) and checking for range intersections, which adds complexity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
