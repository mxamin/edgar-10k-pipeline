import logging
import os
import signal
import sys
import time

from config import PDF_DIR
from libs.cik_extractor import CIKExtractor
from libs.form_10k_downloader import Form10KDownloader
from libs.html2pdf_converter import Html2PdfConverter

logger = logging.getLogger("edgar-10k-pipeline")

DEFAULT_COMPANIES = [
    "Apple",
    "Meta",
    "Alphabet",
    "Amazon",
    "Netflix",
    "Goldman Sachs",
]


class Shutdown(BaseException):
    pass


def handle_signal(signum: int, _frame) -> None:
    logger.info("Received %s, shutting down", signal.Signals(signum).name)
    raise Shutdown


def read_company_names() -> list[str]:
    raw = os.environ.get("COMPANIES", "")
    return [name.strip() for name in raw.split(",") if name.strip()]


def run_cycle(
    company_names: list[str],
    extractor: CIKExtractor,
    downloader: Form10KDownloader,
    converter: Html2PdfConverter,
) -> None:
    logger.info("Resolving CIKs for %d companies", len(company_names))
    companies = extractor.get(company_names)

    for name, company in zip(company_names, companies, strict=True):
        if company is None:
            logger.warning("[%s] Company not found in SEC ticker list", name)
            continue

        label = f"{company.title} ({company.ticker}, CIK {company.cik})"
        logger.info("[%s] Resolved to %s", name, label)
        try:
            logger.info("[%s] Fetching most recent 10-K", name)
            html = downloader.get(company.cik)
            if html is None:
                logger.warning("[%s] No 10-K found for %s", name, label)
                continue
            logger.info("[%s] Downloaded 10-K HTML (%d bytes)", name, len(html))

            logger.info("[%s] Converting 10-K to PDF", name)
            pdf = converter.convert(html)
            pdf_path = PDF_DIR / f"{company.title}_{company.ticker}_{company.cik}.pdf"
            pdf_path.write_bytes(pdf)
            logger.info("[%s] PDF generated: %s (%d bytes)", name, pdf_path, len(pdf))
        except Exception:
            logger.exception("[%s] Failed to process %s", name, label)


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger("weasyprint").setLevel(logging.WARNING)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    company_names = read_company_names()
    if not company_names:
        logger.info("COMPANIES env variable is not set, using the default list")
        company_names = DEFAULT_COMPANIES
    interval = float(os.environ.get("INTERVAL_SECONDS", "3600"))

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    extractor = CIKExtractor()
    downloader = Form10KDownloader()
    converter = Html2PdfConverter()

    logger.info(
        "Starting pipeline for %s, interval %.0fs", ", ".join(company_names), interval
    )
    cycle = 0
    try:
        while True:
            cycle += 1
            logger.info("Cycle %d started", cycle)
            try:
                run_cycle(company_names, extractor, downloader, converter)
            except Exception:
                logger.exception("Cycle %d failed", cycle)
            logger.info("Cycle %d finished, sleeping %.0fs", cycle, interval)
            time.sleep(interval)
    except Shutdown:
        logger.info("Stopped")
        logging.shutdown()
        os._exit(0)


if __name__ == "__main__":
    main()
