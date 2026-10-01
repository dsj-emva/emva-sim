"""How the sales team records each Lead's true path, on simulated data.

One fixed seed, six months of leads, exported long after the last one so nearly every stage change
is recorded before the export. Each rate's tolerance is about three standard errors at that size,
written before the numbers were looked at.
"""

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

import pytest

from emva_sim import dataset

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2025, 12, 31))
DEALS = "export/deals-and-contacts-only/hubspot-crm-exports-safari-enquiries-2025-12-31.csv"
TRUTH = "hidden-truth/hidden-truth.csv"
STAGES = "hidden-truth/stage-history.csv"
EXPORT = "2025-12-31 00:00"


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def entered(stage):
    return f'Date entered "{stage} (Safari Enquiries)"'


@pytest.fixture(scope="module")
def middle(tmp_path_factory):
    out = tmp_path_factory.mktemp("out")
    return dataset.generate(PROFILE, "middle", seed=1, out=out, history=HISTORY)


def history_by_deal(folder):
    by_deal = defaultdict(list)
    for change in rows(folder / STAGES):
        by_deal[change["deal_record_id"]].append(change)
    return by_deal


def test_the_export_shows_the_latest_recorded_entry_of_each_stage_before_the_export(middle):
    deals = {d["Record ID"]: d for d in rows(middle / DEALS)}
    by_deal = history_by_deal(middle)
    assert set(by_deal) == set(deals)
    for deal_id, changes in by_deal.items():
        latest = {}
        for change in changes:
            if change["recorded_entered_at"] and change["recorded_entered_at"] < EXPORT:
                latest[change["crm_stage"]] = max(
                    latest.get(change["crm_stage"], ""), change["recorded_entered_at"]
                )
        shown = {
            column: at
            for column, at in deals[deal_id].items()
            if column.startswith("Date entered") and at
        }
        assert shown == {entered(stage): at for stage, at in latest.items()}, deal_id
