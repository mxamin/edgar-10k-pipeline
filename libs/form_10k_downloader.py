import json
from datetime import timedelta

from libs.sec_client import SecClient


class Form10KDownloader:
    submissions_url = "https://data.sec.gov/submissions/CIK{cik}.json"
    document_url = (
        "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}"
    )

    def __init__(self) -> None:
        self.client = SecClient(expiration=timedelta(hours=1))

    def get(self, cik: int) -> bytes | None:
        submissions = json.loads(
            self.client.get(self.submissions_url.format(cik=f"{cik:010d}"))
        )
        recent = submissions["filings"]["recent"]
        for form, accession, document in zip(
            recent["form"],
            recent["accessionNumber"],
            recent["primaryDocument"],
            strict=True,
        ):
            if form == "10-K":
                return self.client.get(
                    self.document_url.format(
                        cik=cik,
                        accession=accession.replace("-", ""),
                        document=document,
                    )
                )
        return None
