import dataclasses
import json

import pytest

from libs.cik_extractor import CIKExtractor, Company
from libs.sec_client import SecClient

COMPANY_TICKERS = {
    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
    "1": {"cik_str": 1326801, "ticker": "META", "title": "Meta Platforms, Inc."},
    "2": {"cik_str": 1871149, "ticker": "MTAL", "title": "Metallus Inc."},
    "3": {"cik_str": 789019, "ticker": "MSFT", "title": "MICROSOFT CORP"},
}

APPLE = Company(title="Apple Inc.", ticker="AAPL", cik=320193)
META = Company(title="Meta Platforms, Inc.", ticker="META", cik=1326801)
MICROSOFT = Company(title="MICROSOFT CORP", ticker="MSFT", cik=789019)


@pytest.fixture
def extractor():
    return CIKExtractor()


def test_matches_by_title(extractor):
    assert extractor._get(COMPANY_TICKERS, "apple") == APPLE


def test_matches_by_ticker(extractor):
    assert extractor._get(COMPANY_TICKERS, "msft") == MICROSOFT


def test_match_is_case_insensitive(extractor):
    assert extractor._get(COMPANY_TICKERS, "  MicroSoft ") == MICROSOFT


def test_first_match_wins(extractor):
    assert extractor._get(COMPANY_TICKERS, "meta") == META


def test_cik_is_int(extractor):
    cik = extractor._get(COMPANY_TICKERS, "metallus").cik
    assert isinstance(cik, int)
    assert cik == 1871149


def test_result_is_immutable(extractor):
    result = extractor._get(COMPANY_TICKERS, "apple")
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.cik = 0


def test_no_match_returns_none(extractor):
    assert extractor._get(COMPANY_TICKERS, "nonexistent") is None


def test_get_preserves_order_of_names(extractor, monkeypatch):
    monkeypatch.setattr(
        SecClient, "get", lambda self, url: json.dumps(COMPANY_TICKERS).encode()
    )
    assert extractor.get(["meta", "nope", "apple"]) == [META, None, APPLE]
