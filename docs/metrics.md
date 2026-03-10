# Metric Definitions

All metrics are computed over a single calendar week identified by its Monday `week_start` date.
A "session belongs to week W" means `session_date >= W AND session_date < W + 7 days`.

---

## 1. Attendance Rate (per student, per week)

```
attendance_rate(student, week) = attended_count / scheduled_count
```

Where:
- `attended_count` = sessions with status `present` or `late`
- `scheduled_count` = sessions with status `present`, `late`, or `no_show`
  (`cancelled` sessions are excluded from both counts — the slot never ran)

**Average attendance rate (week):**

```
avg_attendance_rate(week) = mean of attendance_rate(s, week) for every student s
                            who has at least one session that week
```

**Edge cases:**
- Student has zero sessions in the week, or only `cancelled` sessions → `scheduled_count = 0`; exclude from the average (do not divide by zero).
- Student has only `no_show` sessions → attended_count = 0, rate = 0.0 (included).

**Target:** avg_attendance_rate ≈ 0.85 (tolerance ±0.01 in tests).

---

## 2. No-Show Rate (per subject, per week)

```
no_show_rate(subject, week) = no_show_count / scheduled_count
```

Where:
- `no_show_count` = sessions for that subject that week with status `no_show`
- `scheduled_count` = all sessions for that subject that week

**Edge cases:**
- Subject has zero sessions in the week → rate is undefined; return `None`.
- `cancelled` sessions are included in the denominator (they were scheduled).

**Target:** no_show_rate("Computer Science", week) = 0.10 exactly (1 out of 10).

---

## 3. Tutor Utilization (per tutor, per week)

```
utilization(tutor, week) = booked_hours / available_hours
```

Where:
- `booked_hours` = sum of `scheduled_hours` for all sessions assigned to that tutor that week,
  regardless of status (cancelled sessions count toward booked hours — the assumption is that the
  tutor's slot was reserved and could not be reassigned; if the business frees cancelled slots,
  exclude `cancelled` from this sum instead)
- `available_hours` = `tutors.available_hours_per_week`

**Understaffed threshold:** utilization > 0.85.

**Edge cases:**
- Tutor has zero sessions that week → utilization = 0.0.
- `available_hours` is guaranteed > 0 by a CHECK constraint; no division-by-zero risk.

**Target:** at least one tutor has utilization > 0.85 in the target week.

---

## 4. At-Risk Students (per week)

```
at_risk(student, week) = student_progress.progress_percent < 60
```

A student is at risk if their `progress_percent` for `week_start = W` is strictly below 60.

**Edge cases:**
- Student has no progress record for that week → not considered at risk (excluded).
- progress_percent = 60.0 → NOT at risk (threshold is strict less-than).

**Target:** exactly 2 students at risk in the target week.

---

## Summary table

| # | Metric | Scope | Formula | Target |
|---|---|---|---|---|
| 1 | `avg_attendance_rate` | all students, one week | mean of (attended / scheduled) per student | ≈ 0.85 (±0.01) |
| 2 | `no_show_rate` | one subject, one week | no_show / scheduled | 0.10 for Computer Science |
| 3 | `utilization` | one tutor, one week | booked_hours / available_hours | > 0.85 for ≥ 1 tutor |
| 4 | `at_risk_count` | all students, one week | count where progress_percent < 60 | exactly 2 |
