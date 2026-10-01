"""vary-phrases: each bank phrase is sent once to the model, its reply checked and cached.

Every test uses the fake model; no test touches the network.
"""

import json
import shutil

import anthropic
import httpx2
import pytest
from conftest import REAL_PROFILE
from fake_model import FakeModel

from emva_sim import cli, phrases, vary
from emva_sim.vary import Request


def write_profile(folder, bank_text, model="fake-model"):
    (folder / "p.toml").write_text(
        '[text]\nphrase_bank = "p.phrases.toml"\nvariations = "p.variations.json"\n'
        f'variations_per_phrase = 3\nmodel = "{model}"\n'
    )
    (folder / "p.phrases.toml").write_text(bank_text)
    return folder / "p.toml"


BANK = """
[about]
message = "an enquiry"
notes = "a sales note"
[meaning]
"notes.real" = "the lead is a real buyer"
[message.en]
token = ["Call me", { text = "We arrive on {date}.", requires = ["dated"] }]
[message.fr]
token = ["Appelez-moi"]
[notes]
call = ["No answer"]
real = ["Partner keen to go"]
"""


def cached(profile):
    return json.loads(profile.with_name("p.variations.json").read_text())["phrases"]


SUFFIXES = ["(one)", "(two)", "(three)"]


def numbered(request):
    return [f"{request.phrase} {suffix}" for suffix in SUFFIXES[: request.n]]


def test_every_phrase_is_sent_once_and_its_variations_cached_with_the_model(tmp_path):
    profile = write_profile(tmp_path, BANK)
    result = vary.run(profile, FakeModel(numbered))
    assert result.sent == 5 and not result.failed
    assert cached(profile)[phrases.key("Call me")] == {
        "phrase": "Call me",
        "variations": ["Call me (one)", "Call me (two)", "Call me (three)"],
        "model": "fake-model",
    }
    again = FakeModel(numbered)
    assert vary.run(profile, again).sent == 0
    assert again.asked == [] and again.checked == []


def test_only_phrases_missing_from_the_cache_are_sent(tmp_path):
    profile = write_profile(tmp_path, BANK)
    vary.run(profile, FakeModel(numbered))
    profile.with_name("p.phrases.toml").write_text(BANK.replace('"No answer"', '"Left a message"'))
    fake = FakeModel(numbered)
    vary.run(profile, fake)
    assert [r.phrase for r in fake.asked] == ["Left a message"]
    assert phrases.key("No answer") not in cached(profile)


def test_an_entry_another_model_wrote_is_sent_again(tmp_path):
    profile = write_profile(tmp_path, BANK)
    vary.run(profile, FakeModel(numbered))

    class Other(FakeModel):
        model = "other-model"

    other = Other(numbered)
    assert vary.run(profile, other).sent == 5
    assert {e["model"] for e in cached(profile).values()} == {"other-model"}


def test_each_request_says_what_the_text_is_its_language_and_how_many_variations(tmp_path):
    fake = FakeModel(numbered)
    vary.run(write_profile(tmp_path, BANK), fake)
    by_phrase = {r.phrase: r for r in fake.asked}
    assert by_phrase["Appelez-moi"].language == "French"
    assert by_phrase["Call me"].language == "English"
    assert by_phrase["No answer"].about == "a sales note"
    assert {r.n for r in fake.asked} == {3}


def test_each_variation_of_a_signal_phrase_is_checked_to_say_what_the_phrase_says(tmp_path):
    profile = write_profile(tmp_path, BANK)
    fake = FakeModel(numbered)
    vary.run(profile, fake)
    statement = "the lead is a real buyer"
    assert fake.checked == [(f"Partner keen to go {s}", statement) for s in SUFFIXES]
    assert cached(profile)[phrases.key("Partner keen to go")]["meaning_check"] == {
        "statement": "the lead is a real buyer",
        "answers": ["yes", "yes", "yes"],
    }
    assert "meaning_check" not in cached(profile)[phrases.key("Call me")]


def test_a_variation_that_drifts_from_the_phrases_meaning_is_not_cached(tmp_path):
    profile = write_profile(tmp_path, BANK)
    drifting = FakeModel(numbered, says=lambda sentence, statement: not sentence.endswith("(two)"))
    result = vary.run(profile, drifting)
    assert [pid for pid, _ in result.failed] == ["notes.real#1"]
    assert "does not say" in result.failed[0][1]
    assert phrases.key("Partner keen to go") not in cached(profile)


@pytest.mark.parametrize(
    ("answer", "reason"),
    [
        (lambda r: ["Call me now", "Ring me"], "3 variations"),
        (lambda r: ["Ring me", "Ring me", "Phone me"], "twice"),
        (lambda r: ["Call me", "Ring me", "Phone me"], "the phrase itself"),
        (lambda r: ["Ring me", "Phone me", ""], "empty"),
        (lambda r: ["Ring me", "Phone me", "Call me\nplease"], "one line"),
        (lambda r: ["Ring me", "Phone me", "Please could you give me a call some time"], "words"),
        (lambda r: ["Ring me", "Phone me", "Call me at 9"], "number"),
        (lambda r: ["Ring me", "Phone me", "Call me, Tom"], "capitalised"),
    ],
)
def test_a_reply_that_breaks_a_rule_is_not_cached(tmp_path, answer, reason):
    profile = write_profile(tmp_path, '[about]\nmessage = "x"\n[message.en]\ntoken = ["Call me"]\n')
    result = vary.run(profile, FakeModel(answer))
    assert result.sent == 0
    assert [pid for pid, _ in result.failed] == ["message.en.token#1"]
    assert reason in result.failed[0][1]
    assert cached(profile) == {}


def test_a_reply_that_is_not_the_asked_json_is_not_cached(tmp_path):
    profile = write_profile(tmp_path, '[about]\nmessage = "x"\n[message.en]\ntoken = ["Call me"]\n')
    prose = FakeModel(reply=lambda r: "Sure! Here are some variations: Ring me, Phone me")
    assert "JSON" in vary.run(profile, prose).failed[0][1]


def test_a_model_failure_counts_one_phrase_as_failed_and_the_run_goes_on(tmp_path):
    profile = write_profile(tmp_path, BANK)

    def flaky(request):
        if request.phrase == "Call me":
            raise vary.ModelFailed("the API failed: APIConnectionError")
        return numbered(request)

    result = vary.run(profile, FakeModel(flaky))
    assert result.failed == [("message.en.token#1", "the API failed: APIConnectionError")]
    assert result.sent == 4


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
        shutil.copy(REAL_PROFILE.parent / name, tmp_path / name)
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
    monkeypatch.setattr(vary, "HaikuClient", lambda key, model: FakeModel(numbered))
    cli.main(["vary-phrases", "--profile", str(profile)])
    printed = capsys.readouterr()
    assert "sk-secret-value" not in printed.out + printed.err
    assert "5 phrases sent" in printed.out


class Messages:
    """Stands in for the Anthropic SDK's client.messages: records each request and answers
    with the text and stop reason given, or raises the error given."""

    def __init__(self, text="", stop_reason="end_turn", error=None):
        self.requests = []
        self.text, self.stop_reason, self.error = text, stop_reason, error

    def create(self, **request):
        self.requests.append(request)
        if self.error:
            raise self.error
        block = type("Block", (), {"type": "text", "text": self.text})()
        return type("Response", (), {"content": [block], "stop_reason": self.stop_reason})()


def haiku(messages):
    client = vary.HaikuClient("key", "claude-haiku-4-5-20251001")
    client.client.messages = messages
    return client


def test_the_haiku_client_asks_the_named_model_for_json_and_returns_its_text():
    messages = Messages('{"variations": ["Ring me", "Phone me"]}')
    reply = haiku(messages).variations(Request("Call me", "an {odd} enquiry", "English", 2))
    assert json.loads(reply) == {"variations": ["Ring me", "Phone me"]}
    request = messages.requests[0]
    assert request["model"] == "claude-haiku-4-5-20251001"
    assert request["output_config"]["format"]["type"] == "json_schema"
    assert request["messages"][0]["content"] == "Call me"
    # Braces in what the bank says about the text are written as they are.
    assert "an {odd} enquiry" in request["system"] and "Write 2 variations" in request["system"]


def test_the_haiku_client_asks_whether_a_sentence_says_the_statement():
    messages = Messages('{"answer": "no"}')
    reply = haiku(messages).answer("Just pricing for now", "the lead is a real buyer")
    assert json.loads(reply) == {"answer": "no"}
    assert "the lead is a real buyer" in messages.requests[0]["system"]
    assert messages.requests[0]["messages"][0]["content"] == "Just pricing for now"


@pytest.mark.parametrize("stop_reason", ["max_tokens", "refusal"])
def test_a_reply_cut_short_or_refused_is_a_model_failure(stop_reason):
    messages = Messages('{"variations": ["Ring', stop_reason=stop_reason)
    with pytest.raises(vary.ModelFailed, match=stop_reason):
        haiku(messages).variations(Request("Call me", "an enquiry", "English", 2))


def test_an_api_error_is_a_model_failure():
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    messages = Messages(error=anthropic.APIConnectionError(request=request))
    with pytest.raises(vary.ModelFailed, match="APIConnectionError"):
        haiku(messages).variations(Request("Call me", "an enquiry", "English", 2))
