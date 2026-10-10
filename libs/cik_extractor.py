import json
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from libs.sec_client import SecClient


@dataclass(frozen=True)
class Company:
    title: str
    ticker: str
    cik: int


class CIKExtractor:
    company_tickers_url = "https://www.sec.gov/files/company_tickers.json"

    def __init__(self) -> None:
        self.client = SecClient(expiration=timedelta(hours=1))

    def get(self, company_names: list[str]) -> list[Company | None]:
        company_tickers = json.loads(self.client.get(self.company_tickers_url))
        return [self._get(company_tickers, name) for name in company_names]

    def _get(
        self, company_tickers: dict[str, Any], company_name: str
    ) -> Company | None:
        needle = company_name.strip().lower()
        for entry in company_tickers.values():
            if needle in entry["title"].lower() or needle == entry["ticker"].lower():
                return Company(
                    title=entry["title"],
                    ticker=entry["ticker"],
                    cik=entry["cik_str"],
                )
        return None
