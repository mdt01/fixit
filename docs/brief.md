# FixIt — product brief

## Problem
Hostel and campus maintenance requests are made by phone calls, paper registers and
WhatsApp messages. Requests get lost, nobody knows who is working on what, and students
cannot see whether anything is happening. Wardens have no numbers to show the
administration.

## Users
- **Students** report problems (fan, tap, Wi-Fi, furniture, cleaning) and follow them.
- **Technicians** see the jobs assigned to them and record what they fixed.
- **Wardens** assign jobs, watch deadlines and report on workload.

## What success looks like (first release)
1. A student can report a problem in under a minute and always see its status.
2. Every ticket has a deadline (SLA) based on its category and priority.
3. A warden can see all overdue tickets and each technician's workload at a glance.
4. Nobody can see or change tickets that are not theirs to see or change.

## Out of scope for the first release
Mobile app, e-mail or SMS notifications, photo uploads, spare-parts inventory, single
sign-on with the university directory.

## Constraints
Python 3.12, runs on one small server or a laptop, SQLite is enough for one campus,
no paid services. Every change goes through tests and review.
