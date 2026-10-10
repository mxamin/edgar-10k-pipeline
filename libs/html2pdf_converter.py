import hashlib
import io

from weasyprint import HTML

from config import CACHE_PDF_DIR


class Html2PdfConverter:
    def __init__(self) -> None:
        CACHE_PDF_DIR.mkdir(parents=True, exist_ok=True)

    def convert(self, html: bytes) -> bytes:
        key = hashlib.sha256(html).hexdigest()
        cache_path = CACHE_PDF_DIR / f"{key}.pdf"
        if cache_path.exists():
            return cache_path.read_bytes()

        pdf = HTML(file_obj=io.BytesIO(html)).write_pdf()
        cache_path.write_bytes(pdf)
        return pdf
