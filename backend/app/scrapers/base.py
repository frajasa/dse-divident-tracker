import logging
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger("dse.scraper")


class BaseScraper:
    """Base class for DSE web scrapers with retry logic and parsing helpers."""

    def __init__(self):
        self.timeout = settings.scraper_timeout
        self.max_retries = settings.scraper_max_retries
        self.headers = {"User-Agent": settings.scraper_user_agent}

    def _fetch_page(self, url: str) -> str | None:
        """Fetch an HTML page with retry and backoff. Returns HTML string or None."""
        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                    resp = client.get(url)
                    resp.raise_for_status()
                    return resp.text
            except httpx.HTTPError as e:
                logger.warning("Fetch attempt %d/%d failed for %s: %s", attempt, self.max_retries, url, e)
                if attempt < self.max_retries:
                    import time
                    time.sleep(2 ** attempt)
        logger.error("All %d fetch attempts failed for %s", self.max_retries, url)
        return None

    def _fetch_pdf(self, url: str) -> bytes | None:
        """Fetch a PDF file. Returns bytes or None."""
        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                    resp = client.get(url)
                    resp.raise_for_status()
                    return resp.content
            except httpx.HTTPError as e:
                logger.warning("PDF fetch attempt %d/%d failed for %s: %s", attempt, self.max_retries, url, e)
                if attempt < self.max_retries:
                    import time
                    time.sleep(2 ** attempt)
        logger.error("All %d PDF fetch attempts failed for %s", self.max_retries, url)
        return None

    @staticmethod
    def _parse_date(text: str) -> datetime | None:
        """Parse common DSE date formats into a date object."""
        if not text or not text.strip():
            return None
        text = text.strip()
        formats = [
            "%d %B %Y",      # 12 June 2024
            "%d %b %Y",      # 12 Jun 2024
            "%d/%m/%Y",      # 12/06/2024
            "%Y-%m-%d",      # 2024-06-12
            "%d-%m-%Y",      # 12-06-2024
            "%d.%m.%Y",      # 12.06.2024
        ]
        for fmt in formats:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        logger.warning("Could not parse date: %s", text)
        return None

    @staticmethod
    def _parse_amount(text: str) -> Decimal | None:
        """Parse a monetary amount string into Decimal, stripping commas and currency symbols."""
        if not text or not text.strip():
            return None
        cleaned = re.sub(r"[^\d.]", "", text.strip())
        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            logger.warning("Could not parse amount: %s", text)
            return None
