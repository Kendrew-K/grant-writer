import datetime
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import grants  # noqa: E402

TODAY = datetime.date(2026, 9, 25)


def test_relevance_counts_whole_words_only():
    assert grants.relevance("Youth Orchestra concert series") == 2
    assert grants.relevance("Rural broadband expansion") == 0


def test_rolling_and_future_deadlines_are_open_past_ones_are_not():
    assert grants.is_open({"deadline": ""}, TODAY)
    assert grants.is_open({"deadline": "09/25/2026"}, TODAY)
    assert not grants.is_open({"deadline": "09/24/2026"}, TODAY)


def fake_fetch(endpoint, payload):
    if endpoint == "search2":
        return {"oppHits": [
            {"id": "1", "title": "Grants for Arts Projects: Music", "agency": "NEA", "closeDate": "02/12/2027"},
            {"id": "2", "title": "Museum Grants", "agency": "IMLS", "closeDate": "11/13/2026"},
            {"id": "3", "title": "Orchestra touring", "agency": "NEA", "closeDate": "01/01/2020"},
            {"id": "4", "title": "Music exchange", "agencyCode": "DOS-EGY", "agency": "U.S. Mission to Egypt", "closeDate": ""},
            {"id": "5", "title": "Symphony forecast", "agency": "NEA", "closeDate": ""},
        ]}
    if payload["opportunityId"] in (3, 4):
        raise AssertionError("expired and embassy grants must be skipped before the detail fetch")
    if payload["opportunityId"] == 5:
        return {"forecast": {"forecastDesc": "orchestra", "estApplicationResponseDateStr": "2019-12-05-00-00-00"}}
    texts = {1: "<p>Supports orchestras &amp; chamber music.</p>", 2: "<p>Museum collections.</p>"}
    return {"synopsis": {"synopsisDesc": texts[payload["opportunityId"]], "awardCeiling": "100000",
                         "applicantTypes": [{"description": "Nonprofits"}]}}


def test_scrape_keeps_open_music_grants_and_drops_the_rest():
    found = grants.scrape_grants_gov(fetch=fake_fetch, today=TODAY)
    assert [g["id"] for g in found] == ["gg-1"]
    assert found[0]["amount"] == "100000"
    assert found[0]["eligibility"].startswith("Nonprofits")


def test_rescrape_refreshes_facts_but_keeps_the_users_status(tmp_path):
    path = tmp_path / "grants.csv"
    rows = {}
    grants.merge(rows, grants.scrape_grants_gov(fetch=fake_fetch, today=TODAY)[0])
    rows["gg-1"]["status"] = "ready-for-review"
    grants.write_tracker(rows, path)

    rows = grants.read_tracker(path)
    grants.merge(rows, {**rows["gg-1"], "deadline": "03/01/2027"})
    assert rows["gg-1"]["status"] == "ready-for-review"
    assert rows["gg-1"]["deadline"] == "03/01/2027"


def test_top_hides_finished_and_expired_grants_and_ranks_by_relevance():
    base = {"funder": "", "title": "", "url": "", "amount": "", "eligibility": "", "note": "", "updated": ""}
    rows = {
        "a": {**base, "id": "a", "relevance": "1", "deadline": "10/01/2026", "status": "new"},
        "b": {**base, "id": "b", "relevance": "4", "deadline": "", "status": "drafting"},
        "c": {**base, "id": "c", "relevance": "9", "deadline": "", "status": "submitted"},
        "d": {**base, "id": "d", "relevance": "9", "deadline": "01/01/2026", "status": "new"},
    }
    assert [r["id"] for r in grants.top(rows, 10, TODAY)] == ["b", "a"]


def test_mark_rejects_unknown_ids(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    try:
        grants.main(["mark", "nope", "skipped"])
    except SystemExit as e:
        assert "No grant with id nope" in str(e)
    else:
        raise AssertionError("expected SystemExit")
