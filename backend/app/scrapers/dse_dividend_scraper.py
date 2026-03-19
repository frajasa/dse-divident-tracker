import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper

logger = logging.getLogger("dse.scraper.dividends")

DSE_CORPORATE_ACTIONS_URL = "https://www.dse.co.tz/content/corporate-actions"


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
    """Scrapes dividend / corporate action data from the DSE website."""

    def scrape_corporate_actions(self) -> list[RawDividendRecord]:
        """Fetch and parse the corporate actions page. Returns list of records."""
        html = self._fetch_page(DSE_CORPORATE_ACTIONS_URL)
        if not html:
            logger.error("Failed to fetch corporate actions page")
            return []
        try:
            return self._parse_corporate_actions_table(html)
        except Exception:
            logger.exception("Error parsing corporate actions page")
            return []

    def _parse_corporate_actions_table(self, html: str) -> list[RawDividendRecord]:
        """Parse the HTML table of corporate actions into RawDividendRecord list.

        The DSE corporate actions page typically contains a table with columns:
        Company | Action | Financial Year | Amount | Announcement | Books Closure | Payment Date
        Column ordering may vary — this method adapts based on header text.
        """
        soup = BeautifulSoup(html, "html.parser")
        records: list[RawDividendRecord] = []

        table = soup.find("table")
        if not table:
            # Try finding data in div-based layouts
            logger.warning("No table found on corporate actions page, trying alternative selectors")
            return self._parse_corporate_actions_divs(soup)

        rows = table.find_all("tr")
        if len(rows) < 2:
            logger.warning("Corporate actions table has fewer than 2 rows")
            return records

        # Parse header to determine column mapping
        header_cells = rows[0].find_all(["th", "td"])
        headers = [cell.get_text(strip=True).lower() for cell in header_cells]

        col_map = self._build_column_map(headers)

        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            record = self._row_to_record(cells, col_map)
            if record:
                records.append(record)

        logger.info("Parsed %d dividend records from corporate actions page", len(records))
        return records

    def _parse_corporate_actions_divs(self, soup: BeautifulSoup) -> list[RawDividendRecord]:
        """Fallback parser for div-based layouts."""
        records: list[RawDividendRecord] = []
        # Look for common DSE page structures
        items = soup.select(".view-content .views-row, .corporate-action-item, .node-content")
        for item in items:
            text = item.get_text(" ", strip=True)
            # Try to extract structured data from text blocks
            record = self._text_block_to_record(text)
            if record:
                records.append(record)
        return records

    @staticmethod
    def _build_column_map(headers: list[str]) -> dict[str, int]:
        """Map semantic column names to indices based on header text."""
        col_map: dict[str, int] = {}
        for i, h in enumerate(headers):
            if "company" in h or "symbol" in h or "security" in h:
                col_map["symbol"] = i
            elif "year" in h or "period" in h:
                col_map["financial_year"] = i
            elif "amount" in h or "dividend" in h or "per share" in h:
                col_map["amount"] = i
            elif "announcement" in h or "declared" in h:
                col_map["announcement_date"] = i
            elif "closure" in h or "book" in h:
                col_map["books_closure_date"] = i
            elif "payment" in h or "pay date" in h:
                col_map["payment_date"] = i
            elif "type" in h or "action" in h:
                col_map["type"] = i
        return col_map

    def _row_to_record(self, cells: list, col_map: dict[str, int]) -> RawDividendRecord | None:
        """Convert a table row into a RawDividendRecord using the column map."""

        def cell_text(key: str) -> str:
            idx = col_map.get(key)
            if idx is not None and idx < len(cells):
                return cells[idx].get_text(strip=True)
            return ""

        symbol = cell_text("symbol").upper().strip()
        if not symbol:
            return None

        amount = self._parse_amount(cell_text("amount"))
        if amount is None:
            return None

        financial_year = cell_text("financial_year") or ""
        dividend_type = self._infer_dividend_type(cell_text("type"))

        return RawDividendRecord(
            symbol=symbol,
            financial_year=financial_year,
            dividend_per_share=amount,
            announcement_date=self._parse_date(cell_text("announcement_date")),
            books_closure_date=self._parse_date(cell_text("books_closure_date")),
            payment_date=self._parse_date(cell_text("payment_date")),
            dividend_type=dividend_type,
            source_url=DSE_CORPORATE_ACTIONS_URL,
        )

    def _text_block_to_record(self, text: str) -> RawDividendRecord | None:
        """Best-effort extraction from a free-text block. Returns None if not enough data."""
        # This is a last-resort parser; real extraction depends on actual page structure
        return None

    @staticmethod
    def _infer_dividend_type(type_text: str) -> str:
        """Normalise dividend type text to one of: interim, final, special."""
        t = type_text.lower()
        if "interim" in t:
            return "interim"
        if "special" in t:
            return "special"
        return "final"
