import logging
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper

logger = logging.getLogger("dse.scraper.dividends")

# The DSE corporate actions page uses div-based card layout (not tables)
DSE_CORPORATE_ACTIONS_URL = "https://dse.co.tz/listed/corporate/actions"


@dataclass
class RawDividendRecord:
    symbol: str
    financial_year: str
    dividend_per_share: Decimal
    announcement_date: date | None
    books_closure_date: date | None
    payment_date: date | None
    dividend_type: str  # interim, final, special
    source_url: str


class DSEDividendScraper(BaseScraper):
    """Scrapes dividend / corporate action data from the DSE website.

    The DSE corporate actions page displays data as card/div blocks, each containing:
    - Company ticker (from image alt text or nearby text)
    - "Announced a Dividend of [amount]"
    - Announcement date, Books Closure date, Payment date
    """

    def scrape_corporate_actions(self) -> list[RawDividendRecord]:
        """Fetch and parse the corporate actions page."""
        html = self._fetch_page(DSE_CORPORATE_ACTIONS_URL)
        if not html:
            logger.error("Failed to fetch corporate actions page")
            return []
        try:
            return self._parse_corporate_actions(html)
        except Exception:
            logger.exception("Error parsing corporate actions page")
            return []

    def _parse_corporate_actions(self, html: str) -> list[RawDividendRecord]:
        """Parse the DSE corporate actions page.

        The page uses div-based cards with company logos and text blocks.
        Each card contains dividend info in paragraph text.
        """
        soup = BeautifulSoup(html, "html.parser")
        records: list[RawDividendRecord] = []

        # Strategy 1: Find company symbols from logo images
        # Images have paths like "/storage//securities/VODA/Logo/VODA.jpg"
        img_tags = soup.find_all("img", src=re.compile(r"/securities/\w+/", re.IGNORECASE))

        for img in img_tags:
            # Extract symbol from image path
            src = img.get("src", "")
            symbol_match = re.search(r"/securities/(\w+)/", src)
            if not symbol_match:
                continue
            symbol = symbol_match.group(1).upper()

            # Get the parent container that holds this card's data
            card = img.find_parent("div")
            if not card:
                continue

            # Walk up to find a container with enough text content
            for _ in range(5):
                text = card.get_text(" ", strip=True)
                if "dividend" in text.lower() or "books" in text.lower() or "payment" in text.lower():
                    break
                parent = card.find_parent("div")
                if parent:
                    card = parent
                else:
                    break

            record = self._extract_dividend_from_text(symbol, card.get_text(" ", strip=True))
            if record:
                records.append(record)

        # Strategy 2: If no images found, try regex on full page text
        if not records:
            records = self._parse_from_full_text(soup)

        # Deduplicate: DSE page often has duplicate entries
        records = self._deduplicate(records)

        logger.info("Parsed %d dividend records from corporate actions page", len(records))
        return records

    @staticmethod
    def _deduplicate(records: list[RawDividendRecord]) -> list[RawDividendRecord]:
        """Remove duplicate records based on (symbol, dividend_per_share, announcement_date)."""
        seen: set[tuple] = set()
        unique: list[RawDividendRecord] = []
        for rec in records:
            key = (rec.symbol, rec.dividend_per_share, rec.announcement_date)
            if key not in seen:
                seen.add(key)
                unique.append(rec)
        return unique

    def _extract_dividend_from_text(self, symbol: str, text: str) -> RawDividendRecord | None:
        """Extract dividend data from a text block associated with a company symbol."""

        # Extract dividend amount: "Dividend of TZS 65" or "Dividend of 818" or "TZS 9.95 per share"
        amount = None
        amount_patterns = [
            r"[Dd]ividend\s+of\s+(?:TZS\s+)?([0-9,]+(?:\.\d+)?)",
            r"TZS\s+([0-9,]+(?:\.\d+)?)\s+(?:per\s+share)?",
            r"([0-9,]+(?:\.\d+)?)\s+per\s+share",
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                amount = self._parse_amount(match.group(1))
                if amount:
                    break

        if amount is None:
            return None

        # Extract dates using common patterns
        # "Announced [Month Day, Year]" or "Announced [Day Month Year]"
        announcement_date = self._extract_date_near_keyword(text, r"[Aa]nnounce\w*")
        books_closure_date = self._extract_date_near_keyword(text, r"[Bb]ooks?\s*[Cc]losure")
        payment_date = self._extract_date_near_keyword(text, r"[Pp]ayment")

        # Infer financial year from announcement date
        financial_year = ""
        ref_date = announcement_date or books_closure_date
        if ref_date:
            # Dividends announced in Jan-Jun usually belong to the previous year
            if ref_date.month <= 6:
                financial_year = str(ref_date.year - 1)
            else:
                financial_year = str(ref_date.year)

        return RawDividendRecord(
            symbol=symbol,
            financial_year=financial_year,
            dividend_per_share=amount,
            announcement_date=announcement_date,
            books_closure_date=books_closure_date,
            payment_date=payment_date,
            dividend_type="final",
            source_url=DSE_CORPORATE_ACTIONS_URL,
        )

    def _extract_date_near_keyword(self, text: str, keyword_pattern: str) -> date | None:
        """Find a date that appears near a keyword in the text."""
        # Date patterns to look for after the keyword
        date_patterns = [
            # "July 19, 2023" or "July 19 2023"
            r"([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
            # "19 July 2023"
            r"(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})",
            # "19/07/2023" or "2023-07-19"
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]

        # Find the keyword position
        keyword_match = re.search(keyword_pattern, text)
        if not keyword_match:
            return None

        # Search for dates in text after the keyword (within 100 chars)
        search_region = text[keyword_match.start():keyword_match.start() + 150]

        for pattern in date_patterns:
            match = re.search(pattern, search_region)
            if match:
                date_str = match.group(1)
                parsed = self._parse_date_flexible(date_str)
                if parsed:
                    return parsed

        return None

    @staticmethod
    def _parse_date_flexible(text: str) -> date | None:
        """Parse various date formats found on the DSE website."""
        from datetime import datetime

        text = text.strip().replace(",", "")
        formats = [
            "%B %d %Y",      # July 19 2023
            "%d %B %Y",      # 19 July 2023
            "%b %d %Y",      # Jul 19 2023
            "%d %b %Y",      # 19 Jul 2023
            "%d/%m/%Y",      # 19/07/2023
            "%Y-%m-%d",      # 2023-07-19
        ]
        for fmt in formats:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None

    def _parse_from_full_text(self, soup: BeautifulSoup) -> list[RawDividendRecord]:
        """Fallback: scan the full page text for dividend patterns."""
        records: list[RawDividendRecord] = []
        full_text = soup.get_text(" ", strip=True)

        # Look for patterns like "CRDB ... Dividend of TZS 65 ... Announced ... Books Closure ... Payment"
        # Split by company symbols (uppercase 2-8 letter words that appear before "dividend")
        blocks = re.split(r"(?=\b[A-Z]{2,10}\b\s.*?[Dd]ividend)", full_text)

        for block in blocks:
            if "dividend" not in block.lower():
                continue

            # Extract symbol (first uppercase word)
            sym_match = re.match(r"\b([A-Z]{2,10})\b", block)
            if not sym_match:
                continue

            symbol = sym_match.group(1)
            record = self._extract_dividend_from_text(symbol, block)
            if record:
                records.append(record)

        return records
