# Project Brief

## Goal
Build a command-line assistant for a student club officer who needs to reserve
shared campus facilities (seminar rooms, the auditorium, the club room, the studio).
The officer types questions in natural language; the assistant uses **tools** to
check facility info, check existing bookings, find a free time slot, and reserve one.

## Users
One club officer (총무/동아리 대표). Not technical. Wants a fast, correct answer —
especially "is this time free?" and "when IS it free?".

## What the assistant can do
- Show facility info: capacity, operating hours, equipment, hourly rate
- Check existing reservations for a facility on a given date
- Find the next available time slot of a given length, avoiding conflicts
- Calculate the rental cost for a booking
- Reserve a facility for a time range (updates the reservation list)

## Out of scope
- Web UI, real databases, real payments, external calendar APIs, multiple simultaneous bookers

## Why not the café agent
A café never has to worry about two orders happening "at the same time in the same
place." Our core problem — finding a conflict-free time slot across existing bookings —
has no café equivalent. `find_available_slot` is not `get_menu` or `check_stock` with
a new name: it is an interval-scheduling computation over the day's reservations.

## Success criteria
- Never guesses a free time: all availability comes from tools, not from the LLM.
- Can answer questions that need 2–3 tools in a row (e.g. check schedule → find slot → reserve).
- Recovers from tool errors (e.g. unknown facility name, double-booked time) instead of crashing.
- Asks for confirmation before changing data (reserve_facility).
