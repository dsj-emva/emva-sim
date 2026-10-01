import csv
from datetime import date
from pathlib import Path

import pytest

from emva_sim import dataset, profile

PROFILE = Path(__file__).parent.parent / "profiles" / "planned-hospitality.toml"
HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2024, 7, 5))
DEALS = "export/with-calls-and-notes/hubspot-crm-exports-safari-enquiries-2024-07-05.csv"
CONTACTS = "export/with-calls-and-notes/hubspot-crm-exports-all-contacts-2024-07-05.csv"
CALLS = "export/with-calls-and-notes/hubspot-crm-exports-all-calls-2024-07-05.csv"
TRUTH = "hidden-truth/hidden-truth.csv"


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def raw():
    return profile.load(PROFILE)


@pytest.fixture(scope="module")
def middle(tmp_path_factory):
    out = tmp_path_factory.mktemp("out")
    return dataset.generate(PROFILE, "middle", seed=1, out=out, history=HISTORY)


def test_the_deals_export_has_one_deal_per_lead_at_the_profiles_volume(middle):
    deals = rows(middle / DEALS)
    assert len(deals) == 400 * 6
    assert list(deals[0])[0] == "Record ID"
