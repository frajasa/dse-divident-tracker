import json
import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import httpx

from app.scrapers.base import BaseScraper

logger = logging.getLogger("dse.scraper.prices")

# The DSE exposes a JSON API for live market prices
DSE_LIVE_PRICES_API = "https://dse.co.tz/api/get/live/market/prices"


@dataclass
class RawPriceRecord:
    symbol: str
    price: Decimal
    change: Decimal | None
    date: date | None


class DSEPriceScraper(BaseScraper):
    """Scrapes current market prices from the DSE JSON API."""

    def scrape_market_prices(self) -> list[RawPriceRecord]:
        """Fetch prices from the DSE live prices API."""
        response_text = self._fetch_page(DSE_LIVE_PRICES_API)
        if not response_text:
            logger.error("Failed to fetch live market prices API")
            return []
        try:
            return self._parse_json_prices(response_text)
        except Exception:
            logger.exception("Error parsing live market prices JSON")
            return []

    def _parse_json_prices(self, response_text: str) -> list[RawPriceRecord]:
        """Parse the DSE live prices JSON response.

        Expected format:
        {
            "success": true,
            "data": [
                {"id": 0, "company": "MCB", "price": 1810, "change": -10},
                ...
            ]
        }
        """
        data = json.loads(response_text)

        if not data.get("success"):
            logger.warning("DSE API returned success=false")
            return []

        entries = data.get("data", [])
        records: list[RawPriceRecord] = []

        for entry in entries:
            symbol = entry.get("company", "").strip().upper()
            price_val = entry.get("price")

            if not symbol or price_val is None:
                continue

            try:
                price = Decimal(str(price_val))
            except Exception:
                logger.warning("Could not parse price for %s: %s", symbol, price_val)
                continue

            change = None
            change_val = entry.get("change")
            if change_val is not None:
                try:
                    change = Decimal(str(change_val))
                except Exception:
                    pass

            records.append(RawPriceRecord(
                symbol=symbol,
                price=price,
                change=change,
                date=date.today(),
            ))

        logger.info("Parsed %d price records from DSE API", len(records))
        return records
