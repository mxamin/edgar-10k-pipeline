import json

import pytest

from libs.form_10k_downloader import Form10KDownloader
from libs.sec_client import SecClient

HTML = b"<html>10-K</html>"


def submissions(*filings):
    forms, accessions, documents = (
        zip(*filings, strict=True) if filings else ((), (), ())
    )
    return {
        "filings": {
            "recent": {
                "form": list(forms),
                "accessionNumber": list(accessions),
                "primaryDocument": list(documents),
            }
        }
    }


@pytest.fixture
def fake_client(monkeypatch):
    calls = []
    state = {"submissions": None}

    def fake_get(self, url):
        calls.append(url)
        if url.endswith(".json"):
            return json.dumps(state["submissions"]).encode()
        return HTML

    monkeypatch.setattr(SecClient, "get", fake_get)
    return calls, state


def test_submissions_url_is_zero_padded(fake_client):
    calls, state = fake_client
    state["submissions"] = submissions()
    Form10KDownloader().get(320193)
    assert calls[0] == "https://data.sec.gov/submissions/CIK0000320193.json"


def test_returns_most_recent_10k_html(fake_client):
    calls, state = fake_client
    state["submissions"] = submissions(
        ("10-Q", "0000320193-25-000010", "q.htm"),
        ("10-K/A", "0000320193-25-000005", "ka.htm"),
        ("10-K", "0000320193-24-000123", "aapl-20240928.htm"),
        ("10-K", "0000320193-23-000106", "aapl-20230930.htm"),
    )
    assert Form10KDownloader().get(320193) == HTML
    assert calls[1] == (
        "https://www.sec.gov/Archives/edgar/data/320193/"
        "000032019324000123/aapl-20240928.htm"
    )


def test_returns_none_without_10k(fake_client):
    calls, state = fake_client
    state["submissions"] = submissions(("10-Q", "0000320193-25-000010", "q.htm"))
    assert Form10KDownloader().get(320193) is None
    assert len(calls) == 1
