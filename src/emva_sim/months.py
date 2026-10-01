"""Calendar months: their last day, and the part of each that a date range covers."""

import calendar
from datetime import date


def last_day(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])


def span(year: int, month: int, start: date, end: date) -> tuple[date, date]:
    """The first and last day of the month that fall between start and end."""
    return max(date(year, month, 1), start), min(last_day(year, month), end)


def covered(start: date, end: date) -> list[tuple[int, int, float]]:
    """Each calendar month from start to end, with the share of its days the range covers."""
    months, year, month = [], start.year, start.month
    while (year, month) <= (end.year, end.month):
        first, last = span(year, month, start, end)
        months.append((year, month, ((last - first).days + 1) / last_day(year, month).day))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months
