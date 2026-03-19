import logging
from datetime import datetime, timezone, date

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.dividend import Dividend
from app.models.sync_log import SyncLog
from app.models.watchlist import PriceAlert
from app.scrapers.dse_dividend_scraper import DSEDividendScraper
from app.scrapers.dse_price_scraper import DSEPriceScraper

logger = logging.getLogger("dse.sync")


def _now():
    return datetime.now(timezone.utc)


def sync_dividends(db: Session, triggered_by: str = "scheduler") -> SyncLog:
    """Scrape dividend data from DSE and upsert into the database."""
    log = SyncLog(sync_type="dividends", status="started", triggered_by=triggered_by, started_at=_now())
    db.add(log)
    db.commit()

    try:
        scraper = DSEDividendScraper()
        raw_records = scraper.scrape_corporate_actions()
        log.records_found = len(raw_records)

        # Build symbol -> company lookup
        companies = {c.symbol: c for c in db.query(Company).all()}

        created = updated = skipped = 0

        for rec in raw_records:
            company = companies.get(rec.symbol)
            if not company:
                logger.warning("Unknown company symbol: %s — skipping", rec.symbol)
                skipped += 1
                continue

            # Deduplicate on (company_id, financial_year, dividend_type)
            existing = (
                db.query(Dividend)
                .filter_by(
                    company_id=company.id,
                    financial_year=rec.financial_year,
                    dividend_type=rec.dividend_type,
                )
                .first()
            )

            if existing:
                # Update if any field changed
                changed = False
                if rec.dividend_per_share != existing.dividend_per_share:
                    existing.dividend_per_share = rec.dividend_per_share
                    changed = True
                if rec.announcement_date and rec.announcement_date != existing.announcement_date:
                    existing.announcement_date = rec.announcement_date
                    changed = True
                if rec.books_closure_date and rec.books_closure_date != existing.books_closure_date:
                    existing.books_closure_date = rec.books_closure_date
                    changed = True
                if rec.payment_date and rec.payment_date != existing.payment_date:
                    existing.payment_date = rec.payment_date
                    changed = True
                if rec.source_url and rec.source_url != existing.source_url:
                    existing.source_url = rec.source_url
                    changed = True

                if changed:
                    updated += 1
                else:
                    skipped += 1
            else:
                dividend = Dividend(
                    company_id=company.id,
                    financial_year=rec.financial_year,
                    dividend_per_share=rec.dividend_per_share,
                    announcement_date=rec.announcement_date,
                    books_closure_date=rec.books_closure_date,
                    payment_date=rec.payment_date,
                    dividend_type=rec.dividend_type,
                    status="announced",
                    source_url=rec.source_url,
                )
                db.add(dividend)
                created += 1

        db.commit()
        log.records_created = created
        log.records_updated = updated
        log.records_skipped = skipped
        log.status = "completed"
        log.completed_at = _now()
        logger.info("Dividend sync complete: found=%d created=%d updated=%d skipped=%d",
                     log.records_found, created, updated, skipped)

    except Exception as e:
        logger.exception("Dividend sync failed")
        log.status = "failed"
        log.error_message = str(e)[:2000]
        log.completed_at = _now()

    db.commit()
    return log


def sync_prices(db: Session, triggered_by: str = "scheduler") -> SyncLog:
    """Scrape market prices from DSE and update company current_price."""
    log = SyncLog(sync_type="prices", status="started", triggered_by=triggered_by, started_at=_now())
    db.add(log)
    db.commit()

    try:
        scraper = DSEPriceScraper()
        raw_records = scraper.scrape_market_prices()
        log.records_found = len(raw_records)

        companies = {c.symbol: c for c in db.query(Company).all()}
        updated = skipped = 0

        for rec in raw_records:
            company = companies.get(rec.symbol)
            if not company:
                logger.warning("Unknown company symbol for price: %s — skipping", rec.symbol)
                skipped += 1
                continue

            if company.current_price != rec.price:
                company.current_price = rec.price
                updated += 1
            else:
                skipped += 1

        db.commit()

        # Check and trigger price alerts
        triggered_alerts = _check_price_alerts(db, companies)

        log.records_updated = updated
        log.records_skipped = skipped
        log.status = "completed"
        log.completed_at = _now()
        logger.info("Price sync complete: found=%d updated=%d skipped=%d alerts_triggered=%d",
                     log.records_found, updated, skipped, triggered_alerts)

    except Exception as e:
        logger.exception("Price sync failed")
        log.status = "failed"
        log.error_message = str(e)[:2000]
        log.completed_at = _now()

    db.commit()
    return log


def _check_price_alerts(db: Session, companies: dict[str, Company]) -> int:
    """Check active price alerts against current prices and trigger matching ones."""
    active_alerts = db.query(PriceAlert).filter_by(is_active=True, is_triggered=False).all()
    triggered = 0

    for alert in active_alerts:
        company = db.query(Company).get(alert.company_id)
        if not company or company.current_price is None:
            continue

        should_trigger = False
        if alert.alert_type == "above" and company.current_price >= alert.target_value:
            should_trigger = True
        elif alert.alert_type == "below" and company.current_price <= alert.target_value:
            should_trigger = True

        if should_trigger:
            alert.is_triggered = True
            alert.triggered_at = _now()
            triggered += 1

    if triggered:
        db.commit()

    return triggered


def update_dividend_statuses(db: Session, triggered_by: str = "scheduler") -> SyncLog:
    """Transition dividend statuses based on current date. No scraping needed."""
    log = SyncLog(sync_type="status_update", status="started", triggered_by=triggered_by, started_at=_now())
    db.add(log)
    db.commit()

    try:
        today = date.today()
        updated = 0

        # announced → books_closed (when books_closure_date <= today)
        announced = (
            db.query(Dividend)
            .filter(Dividend.status == "announced", Dividend.books_closure_date <= today)
            .all()
        )
        for div in announced:
            div.status = "books_closed"
            updated += 1

        # books_closed → paid (when payment_date <= today)
        books_closed = (
            db.query(Dividend)
            .filter(Dividend.status == "books_closed", Dividend.payment_date <= today)
            .all()
        )
        for div in books_closed:
            div.status = "paid"
            updated += 1

        db.commit()

        log.records_found = len(announced) + len(books_closed)
        log.records_updated = updated
        log.status = "completed"
        log.completed_at = _now()
        logger.info("Status update complete: %d dividends transitioned", updated)

    except Exception as e:
        logger.exception("Status update failed")
        log.status = "failed"
        log.error_message = str(e)[:2000]
        log.completed_at = _now()

    db.commit()
    return log
