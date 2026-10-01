"""The text in the exports, on simulated data: the enquiry message, Sales notes, Closed Lost
Reasons and bots' spam, written from the phrase bank and the echoed test cache (echo_model).

One fixed seed, six months of leads, exported long after the last one so their notes are in.
"""

import shutil
from datetime import date

import pytest
from conftest import PROFILE, REAL_PROFILE, assert_rate, kinds, number, rows

from emva_sim import dataset, datasets, phrases
from emva_sim.intake import RowKind
from emva_sim.phrases import MissingVariations

HISTORY = dataset.History(start=date(2024, 1, 1), end=date(2024, 6, 30), export=date(2025, 12, 31))
EXPORT = "export/with-calls-and-notes"
CONTACTS = f"{EXPORT}/hubspot-crm-exports-all-contacts-2025-12-31.csv"
MESSAGE = "Message"


@pytest.fixture(scope="module")
def generated(generate):
    return lambda setting: generate(setting, HISTORY)


@pytest.fixture(scope="module")
def middle(generated):
    return generated("middle")


def message_of_deal(folder):
    """Each deal's contact's Message, by deal Record ID."""
    return {
        deal: contact[MESSAGE]
        for contact in rows(folder / CONTACTS)
        for deal in contact["Associated Deal IDs"].split(";")
    }


def test_each_leads_contact_shows_a_message_of_its_hidden_number_of_words(middle):
    messages = message_of_deal(middle)
    leads = kinds(middle, RowKind.LEAD)
    for row in leads:
        assert phrases.words(messages[row["deal_record_id"]]) == int(row["message_words"]), row
    written = [row for row in leads if messages[row["deal_record_id"]]]
    blank = number("middle", "form.message.blank_or_token")
    assert len(written) > (1 - blank) * len(leads)


def missing_cache_profile(tmp_path):
    for name in ("planned-hospitality.toml", "planned-hospitality.phrases.toml"):
        shutil.copy(REAL_PROFILE.parent / name, tmp_path / name)
    return tmp_path / "planned-hospitality.toml"


def test_a_phrase_with_no_cached_variations_stops_generation_naming_the_command(tmp_path):
    copy = missing_cache_profile(tmp_path)
    with pytest.raises(MissingVariations, match="make vary-phrases"):
        dataset.generate(copy, "middle", seed=1, out=tmp_path / "out", history=HISTORY)
    assert not (tmp_path / "out").exists()
    with pytest.raises(MissingVariations):
        datasets.write_all(copy, tmp_path / "sweep", history=HISTORY)
    assert not (tmp_path / "sweep").exists()


def test_one_missing_variation_is_enough_to_stop_generation(tmp_path):
    folder = tmp_path / "p"
    shutil.copytree(PROFILE.parent, folder)
    cache_path = folder / "planned-hospitality.variations.json"
    cache = phrases.read_cache(cache_path, "echo")
    cache["phrases"].pop(sorted(cache["phrases"])[0])
    phrases.write_cache(cache_path, cache)
    with pytest.raises(MissingVariations, match="1 phrases"):
        dataset.generate(folder / PROFILE.name, "middle", seed=1, out=tmp_path, history=HISTORY)


@pytest.mark.parametrize("setting", ["middle", "mess.bot_or_spam@high"])
def test_the_profiles_share_of_bots_write_spam(generated, setting):
    folder = generated(setting)
    messages = message_of_deal(folder)
    bots = kinds(folder, RowKind.BOT)
    links = number(setting, "text.spam_links")
    spam = [row for row in bots if any(link in messages[row["deal_record_id"]] for link in links)]
    # Gibberish has no link: a third of the spam, by kind.
    share = number(setting, "mess.bot_spam_message") * 2 / 3
    assert_rate(len(spam), len(bots), share)
