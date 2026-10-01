"""How the sales team records each Lead's true path in its sales system.

This sits between the true path (process.py) and the export (hubspot.py): which CRM stage changes
the team enters and when. It never changes the true path; what the export shows is decided here,
and hubspot.py shows only what was recorded before the export date.
"""

from dataclasses import dataclass
from datetime import datetime

from emva_sim.leads import Lead
from emva_sim.process import TruePath


@dataclass(frozen=True)
class Change:
    """One CRM stage change: when it truly happened and when the team recorded it.

    true_at is None for a change with no true event behind it; recorded_at is None for a true
    event the team never recorded.
    """

    stage: str
    true_at: datetime | None
    recorded_at: datetime | None


@dataclass(frozen=True)
class Recorded:
    changes: list[Change]


class Recording:
    def __init__(self, p: dict):
        self.stages = p["pipeline"]["stages"]
        self.order = {s["name"]: i for i, s in enumerate(self.stages)}

    def true_events(self, path: TruePath) -> list[tuple[str, datetime]]:
        """Each CRM stage the deal truly entered and when, in the order it entered them."""
        events = []
        for stage in self.stages:
            if stage.get("milestone"):
                moment = path.provisional_hold_at
            elif stage.get("after_won") == "travelled":
                moment = path.travelled_at
            elif stage.get("after_won") == "cancelled":
                moment = path.cancelled_at
            else:
                moment = path.stage_times.get(stage["ladder"])
            if moment is not None:
                events.append((stage["name"], moment))
        return sorted(events, key=lambda event: (event[1], self.order[event[0]]))

    def lead(self, lead: Lead, path: TruePath) -> Recorded:
        return Recorded([Change(stage, at, at) for stage, at in self.true_events(path)])
