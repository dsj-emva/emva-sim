"""vary-phrases: each bank phrase is sent once to the model, its reply checked and cached.

Every test uses a fake client; no test touches the network.
"""

import json
import shutil
from pathlib import Path

import pytest

from emva_sim import cli, phrases, vary
from emva_sim.vary import Request

PROFILES = Path(__file__).parent.parent / "profiles"


class Fake:
    """Answers like the model would, recording what it was asked."""

    model = "fake-model"

    def __init__(self, answer=None):
        self.asked: list[Request] = []
        self.answer = answer or (lambda r: [f"{r.phrase} ({i})" for i in range(r.n)])

    def variations(self, request: Request) -> str:
        self.asked.append(request)
        return json.dumps({"variations": self.answer(request)})


def write_profile(folder, bank_text):
    (folder / "p.toml").write_text(
        '[text]\nphrase_bank = "p.phrases.toml"\nvariations = "p.variations.json"\n'
        'variations_per_phrase = 3\nmodel = "fake-model"\n'
    )
    (folder / "p.phrases.toml").write_text(bank_text)
    return folder / "p.toml"


BANK = """
[about]
message = "an enquiry"
notes = "a sales note"
[message.en]
token = ["Call me", "We arrive on {date}."]
[message.fr]
token = ["Appelez-moi"]
[notes]
call = ["No answer"]
"""


def cached(profile):
    return json.loads(profile.with_name("p.variations.json").read_text())["phrases"]


def test_every_phrase_is_sent_once_and_its_variations_cached_with_the_model(tmp_path):
    profile = write_profile(tmp_path, BANK)
    fake = Fake()
    result = vary.run(profile, fake)
    assert result.sent == 4 and not result.failed
    entry = cached(profile)[phrases.key("Call me")]
    assert entry == {
        "phrase": "Call me",
        "variations": ["Call me (0)", "Call me (1)", "Call me (2)"],
        "model": "fake-model",
    }
    again = Fake()
    assert vary.run(profile, again).sent == 0
    assert again.asked == []


def test_only_phrases_missing_from_the_cache_are_sent(tmp_path):
    profile = write_profile(tmp_path, BANK)
    vary.run(profile, Fake())
    profile.with_name("p.phrases.toml").write_text(BANK.replace('"No answer"', '"Left a message"'))
    fake = Fake()
    vary.run(profile, fake)
    assert [r.phrase for r in fake.asked] == ["Left a message"]
    assert phrases.key("No answer") not in cached(profile)


def test_each_request_says_what_the_text_is_its_language_and_how_many_variations(tmp_path):
    fake = Fake()
    vary.run(write_profile(tmp_path, BANK), fake)
    by_phrase = {r.phrase: r for r in fake.asked}
    assert by_phrase["Appelez-moi"].language == "French"
    assert by_phrase["Call me"].language == "English"
    assert by_phrase["No answer"].about == "a sales note"
    assert {r.n for r in fake.asked} == {3}


@pytest.mark.parametrize(
    ("answer", "reason"),
    [
        (lambda r: ["Call me now", "Ring me"], "3 variations"),
        (lambda r: ["Ring me", "Ring me", "Phone me"], "twice"),
        (lambda r: ["Call me", "Ring me", "Phone me"], "the phrase itself"),
        (lambda r: ["Ring me", "Phone me", ""], "empty"),
        (lambda r: ["Ring me", "Phone me", "Call me\nplease"], "one line"),
        (lambda r: ["Ring me", "Phone me", "Please could you give me a call some time"], "words"),
    ],
)
def test_a_reply_that_breaks_a_rule_is_not_cached(tmp_path, answer, reason):
    profile = write_profile(tmp_path, '[about]\nmessage = "x"\n[message.en]\ntoken = ["Call me"]\n')
    result = vary.run(profile, Fake(answer))
    assert result.sent == 0
    assert [pid for pid, _ in result.failed] == ["message.en.token#1"]
    assert reason in result.failed[0][1]
    assert cached(profile) == {}


def test_a_variation_must_keep_every_slot(tmp_path):
    profile = write_profile(
        tmp_path, '[about]\nmessage = "x"\n[message.en]\nwhen = ["We arrive on {date}."]\n'
    )
    lost = Fake(lambda r: ["We land on {date}.", "We get in on {date}.", "We arrive soon."])
    assert "slots" in vary.run(profile, lost).failed[0][1]
    renamed = Fake(lambda r: ["We land on {date}.", "We get in {day}.", "Arriving {date}."])
    assert "slots" in vary.run(profile, renamed).failed[0][1]


def test_a_reply_that_is_not_the_asked_json_is_not_cached(tmp_path):
    profile = write_profile(tmp_path, '[about]\nmessage = "x"\n[message.en]\ntoken = ["Call me"]\n')

    class Prose(Fake):
        def variations(self, request):
            return "Sure! Here are some variations: Ring me, Phone me"

    assert "JSON" in vary.run(profile, Prose()).failed[0][1]


def test_the_api_key_comes_from_the_environment_before_a_local_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# local\nOTHER=1\nANTHROPIC_API_KEY=from-file\n")
    assert vary.api_key({}, env_file) == "from-file"
    assert vary.api_key({"ANTHROPIC_API_KEY": "from-env"}, env_file) == "from-env"
    with pytest.raises(vary.NoApiKey, match="ANTHROPIC_API_KEY"):
        vary.api_key({}, tmp_path / "missing.env")


def test_the_command_without_a_key_stops_before_any_request_and_says_why(
    tmp_path, monkeypatch, capsys
):
    for name in ("planned-hospitality.toml", "planned-hospitality.phrases.toml"):
        shutil.copy(PROFILES / name, tmp_path / name)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["vary-phrases", "--profile", str(tmp_path / "planned-hospitality.toml")])
    assert exit_info.value.code == 2
    assert "ANTHROPIC_API_KEY" in capsys.readouterr().err
    assert not (tmp_path / "planned-hospitality.variations.json").exists()


def test_the_command_never_prints_the_key(tmp_path, monkeypatch, capsys):
    profile = write_profile(tmp_path, BANK)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-secret-value")
    monkeypatch.setattr(vary, "HaikuClient", lambda key, model: Fake())
    cli.main(["vary-phrases", "--profile", str(profile)])
    printed = capsys.readouterr()
    assert "sk-secret-value" not in printed.out + printed.err
    assert "4 phrases sent" in printed.out


class Messages:
    """Stands in for the Anthropic SDK's client.messages, recording the request."""

    def __init__(self):
        self.request = None

    def create(self, **request):
        self.request = request

        class Block:
            type = "text"
            text = '{"variations": ["Ring me", "Phone me"]}'

        class Response:
            content = [Block()]
            stop_reason = "end_turn"

        return Response()


def test_the_haiku_client_asks_the_named_model_for_json_and_returns_its_text():
    client = vary.HaikuClient("key", "claude-haiku-4-5-20251001")
    client.client.messages = messages = Messages()
    reply = client.variations(Request("Call me", "an enquiry", "English", 2))
    assert json.loads(reply) == {"variations": ["Ring me", "Phone me"]}
    assert messages.request["model"] == "claude-haiku-4-5-20251001"
    assert messages.request["output_config"]["format"]["type"] == "json_schema"
    assert "Call me" in messages.request["messages"][0]["content"]
    assert "2" in messages.request["system"]
