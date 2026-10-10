import hashlib

import pytest

from libs import html2pdf_converter
from libs.html2pdf_converter import Html2PdfConverter

HTML = b"<html><body>hi</body></html>"


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(html2pdf_converter, "CACHE_PDF_DIR", tmp_path)
    return tmp_path


def cache_path(cache_dir, html):
    return cache_dir / f"{hashlib.sha256(html).hexdigest()}.pdf"


def test_cache_miss_renders_and_caches(cache_dir):
    pdf = Html2PdfConverter().convert(HTML)

    assert pdf.startswith(b"%PDF")
    assert cache_path(cache_dir, HTML).read_bytes() == pdf


def test_cache_hit_returns_cached_without_rendering(cache_dir, monkeypatch):
    cache_path(cache_dir, HTML).write_bytes(b"cached")

    def fail(*args, **kwargs):
        raise AssertionError("should not render")

    monkeypatch.setattr(html2pdf_converter, "HTML", fail)

    assert Html2PdfConverter().convert(HTML) == b"cached"


def test_different_html_uses_different_cache_file(cache_dir):
    converter = Html2PdfConverter()
    other = b"<html><body>bye</body></html>"

    converter.convert(HTML)
    converter.convert(other)

    assert cache_path(cache_dir, HTML).exists()
    assert cache_path(cache_dir, other).exists()
    assert len(list(cache_dir.iterdir())) == 2
