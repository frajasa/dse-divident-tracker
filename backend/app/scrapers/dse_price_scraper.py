import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper
from app.config import settings

logger = logging.getLogger("dse.scraper.prices")

DSE_MARKET_SUMMARY_URL = "https://www.dse.co.tz/content/market-summary"


@dataclass
class RawPriceRecord:
    symbol: str
    price: Decimal
    volume: int | None
    date: date | None


class DSEPriceScraper(BaseScraper):
    """Scrapes current market prices from the DSE website."""

    def scrape_market_prices(self) -> list[RawPriceRecord]:
        """Fetch and parse market prices. Tries HTML first, falls back to PDF."""
        records = self._scrape_html_prices()
        if records:
            return records

        logger.info("HTML scrape returned no results, trying data API")
        return self._scrape_data_api()

    def _scrape_html_prices(self) -> list[RawPriceRecord]:
        """Parse prices from the DSE market summary HTML page."""
        html = self._fetch_page(DSE_MARKET_SUMMARY_URL)
        if not html:
            return []
        try:
            return self._parse_market_table(html)
        except Exception:
            logger.exception("Error parsing market summary page")
            return []

    def _scrape_data_api(self) -> list[RawPriceRecord]:
        """Try fetching prices from the data API endpoint."""
        url = f"{settings.dse_api_base_url}/api/market-data"
        html = self._fetch_page(url)
        if not html:
            return []
        try:
            return self._parse_market_table(html)
        except Exception:
            logger.exception("Error parsing data API response")
            return []

    def _parse_market_table(self, html: str) -> list[RawPriceRecord]:
        """Parse market prices from an HTML table.

        Expected columns: Security | Close Price | Volume | ...
        Adapts to header text.
        """
        soup = BeautifulSoup(html, "html.parser")
        records: list[RawPriceRecord] = []

        table = soup.find("table")
        if not table:
            logger.warning("No table found in market data page")
            return records

        rows = table.find_all("tr")
        if len(rows) < 2:
            return records

        header_cells = rows[0].find_all(["th", "td"])
        headers = [cell.get_text(strip=True).lower() for cell in header_cells]
        col_map = self._build_price_column_map(headers)

        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            record = self._row_to_price_record(cells, col_map)
            if record:
                records.append(record)

        logger.info("Parsed %d price records", len(records))
        return records

    @staticmethod
    def _build_price_column_map(headers: list[str]) -> dict[str, int]:
        col_map: dict[str, int] = {}
        for i, h in enumerate(headers):
            if "security" in h or "symbol" in h or "company" in h or "counter" in h:
                col_map["symbol"] = i
            elif "close" in h or "price" in h or "last" in h:
                col_map.setdefault("price", i)
            elif "volume" in h or "qty" in h:
                col_map["volume"] = i
            elif "date" in h:
                col_map["date"] = i
        return col_map

    def _row_to_price_record(self, cells: list, col_map: dict[str, int]) -> RawPriceRecord | None:
        def cell_text(key: str) -> str:
            idx = col_map.get(key)
            if idx is not None and idx < len(cells):
                return cells[idx].get_text(strip=True)
            return ""

        symbol = cell_text("symbol").upper().strip()
        if not symbol:
            return None

        price = self._parse_amount(cell_text("price"))
        if price is None:
            return None

        volume_text = cell_text("volume")
        volume = None
        if volume_text:
            try:
                volume = int(volume_text.replace(",", ""))
            except ValueError:
                pass

        price_date = self._parse_date(cell_text("date"))

        return RawPriceRecord(
            symbol=symbol,
            price=price,
            volume=volume,
            date=price_date,
        )
