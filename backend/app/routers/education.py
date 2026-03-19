"""
Investment education — curated learning content for DSE investors.
"""

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/education", tags=["education"])


# ─── Static education content organized by category ─────────────

EDUCATION_CONTENT = {
    "basics": {
        "title": "Investment Basics",
        "description": "Start your investing journey with these fundamentals",
        "lessons": [
            {
                "id": "what-is-dse",
                "title": "What is the DSE?",
                "difficulty": "beginner",
                "read_time": 5,
                "content": (
                    "The **Dar es Salaam Stock Exchange (DSE)** is Tanzania's principal stock exchange, "
                    "established in 1996. It provides a platform for buying and selling shares of publicly "
                    "listed companies.\n\n"
                    "**Key facts:**\n"
                    "- Located in Dar es Salaam, Tanzania\n"
                    "- Regulated by the Capital Markets and Securities Authority (CMSA)\n"
                    "- Trades Monday to Friday, 10:00 AM to 2:00 PM EAT\n"
                    "- Has both equity and bond markets\n"
                    "- Cross-listed with Nairobi Securities Exchange (NSE)\n\n"
                    "**How to start investing:**\n"
                    "1. Open a CDS (Central Depository System) account through a licensed broker\n"
                    "2. Fund your brokerage account via bank transfer or mobile money\n"
                    "3. Place buy orders through your broker\n"
                    "4. Shares are settled T+3 (three business days after trade)"
                ),
                "key_takeaways": [
                    "DSE is Tanzania's main stock exchange",
                    "You need a CDS account to trade",
                    "Settlement takes 3 business days",
                ],
            },
            {
                "id": "what-are-shares",
                "title": "What are Shares?",
                "difficulty": "beginner",
                "read_time": 4,
                "content": (
                    "**Shares** (also called stocks or equities) represent ownership in a company. "
                    "When you buy shares of a DSE-listed company, you become a part-owner.\n\n"
                    "**Types of returns:**\n"
                    "1. **Capital gains** — profit when share price rises above your purchase price\n"
                    "2. **Dividends** — cash payments from company profits to shareholders\n\n"
                    "**Example:**\n"
                    "If you buy 1,000 shares of TBL at TZS 9,710 each:\n"
                    "- Total investment: TZS 9,710,000\n"
                    "- If TBL declares TZS 818/share dividend: You receive TZS 818,000 gross\n"
                    "- After 10% tax: You receive TZS 736,200 net\n"
                    "- Your dividend yield: 7.58%\n\n"
                    "**Important:** Share prices can go down as well as up. Never invest money you cannot afford to lose."
                ),
                "key_takeaways": [
                    "Shares = ownership in a company",
                    "Returns come from capital gains and dividends",
                    "Invest only what you can afford to lose",
                ],
            },
            {
                "id": "understanding-dividends",
                "title": "Understanding Dividends",
                "difficulty": "beginner",
                "read_time": 6,
                "content": (
                    "**Dividends** are payments companies make to shareholders from their profits. "
                    "On the DSE, dividends are a major source of investor returns.\n\n"
                    "**Dividend lifecycle:**\n"
                    "1. **Declaration** — Company announces dividend amount and dates\n"
                    "2. **Books closure** — Last day to own shares and qualify for dividend\n"
                    "3. **Payment** — Company distributes cash to qualifying shareholders\n\n"
                    "**Types of dividends:**\n"
                    "- **Interim dividend** — Paid mid-year from half-year profits\n"
                    "- **Final dividend** — Paid after year-end from full-year profits\n"
                    "- **Special dividend** — One-time extra payment\n\n"
                    "**Key dates to know:**\n"
                    "- **Announcement date** — When dividend is declared\n"
                    "- **Books closure date** — You must own shares BEFORE this date\n"
                    "- **Payment date** — When money hits your account\n\n"
                    "**Tax:** Tanzania withholds 10% for residents, 15% for non-residents."
                ),
                "key_takeaways": [
                    "Buy shares before books closure to qualify",
                    "Three types: interim, final, and special",
                    "10% withholding tax for residents",
                ],
            },
        ],
    },
    "analysis": {
        "title": "Stock Analysis",
        "description": "Learn how to evaluate DSE stocks for investment",
        "lessons": [
            {
                "id": "dividend-yield",
                "title": "Dividend Yield Explained",
                "difficulty": "intermediate",
                "read_time": 5,
                "content": (
                    "**Dividend yield** measures how much income a stock pays relative to its price.\n\n"
                    "**Formula:**\n"
                    "```\nDividend Yield = (Annual Dividend Per Share / Current Share Price) x 100\n```\n\n"
                    "**Example with NMB Bank:**\n"
                    "- Current price: TZS 14,370\n"
                    "- Last dividend: TZS 730/share\n"
                    "- Yield: (730 / 14,370) x 100 = 5.08%\n\n"
                    "**Interpreting yields on the DSE:**\n"
                    "- **Above 5%** — High yield, attractive for income investors\n"
                    "- **2% to 5%** — Moderate yield, balanced\n"
                    "- **Below 2%** — Low yield, may be a growth stock\n\n"
                    "**Warning:** Very high yields can be a trap. A falling share price artificially inflates yield. "
                    "Always check if the company can sustain its dividend payments."
                ),
                "key_takeaways": [
                    "Yield = Dividend / Price x 100",
                    "Above 5% is considered high yield on DSE",
                    "Beware of yield traps from falling prices",
                ],
            },
            {
                "id": "payout-ratio",
                "title": "Payout Ratio & Sustainability",
                "difficulty": "intermediate",
                "read_time": 5,
                "content": (
                    "The **payout ratio** shows what percentage of earnings a company pays as dividends.\n\n"
                    "**Formula:**\n"
                    "```\nPayout Ratio = (Dividends Per Share / Earnings Per Share) x 100\n```\n\n"
                    "**What it tells you:**\n"
                    "- **Below 50%** — Conservative, plenty of room to grow dividends\n"
                    "- **50% to 75%** — Balanced, sustainable for most companies\n"
                    "- **Above 75%** — Aggressive, may not be sustainable long-term\n"
                    "- **Above 100%** — Paying more than earned, red flag!\n\n"
                    "**DSE context:**\n"
                    "Many DSE companies like TBL and NMB maintain healthy payout ratios, "
                    "which is why they're considered reliable dividend payers. Always check "
                    "if a company has been consistently profitable before relying on its dividend."
                ),
                "key_takeaways": [
                    "Payout ratio shows dividend sustainability",
                    "50-75% is the sweet spot",
                    "Above 100% is a red flag",
                ],
            },
            {
                "id": "dividend-growth",
                "title": "Dividend Growth Rate (CAGR)",
                "difficulty": "intermediate",
                "read_time": 6,
                "content": (
                    "**Dividend growth rate** measures how fast a company increases its dividends over time. "
                    "Companies that consistently grow dividends are called **Dividend Aristocrats**.\n\n"
                    "**Formula (CAGR):**\n"
                    "```\nCAGR = (Latest Dividend / First Dividend)^(1/Years) - 1\n```\n\n"
                    "**Why it matters:**\n"
                    "- Growing dividends beat inflation\n"
                    "- Signal of company health and management confidence\n"
                    "- Compound your income over time\n\n"
                    "**Example:**\n"
                    "If a company paid TZS 100/share 5 years ago and now pays TZS 150/share:\n"
                    "- CAGR = (150/100)^(1/5) - 1 = 8.45% per year\n\n"
                    "**What to look for on DSE:**\n"
                    "- 3+ years of consecutive dividend increases\n"
                    "- CAGR above inflation rate (~5%)\n"
                    "- Consistent earnings growth supporting dividend growth"
                ),
                "key_takeaways": [
                    "CAGR measures compound annual dividend growth",
                    "Growing dividends protect against inflation",
                    "Look for 3+ years of consecutive increases",
                ],
            },
        ],
    },
    "strategy": {
        "title": "Investment Strategies",
        "description": "Proven approaches for DSE dividend investing",
        "lessons": [
            {
                "id": "dividend-investing",
                "title": "Dividend Investing Strategy",
                "difficulty": "intermediate",
                "read_time": 7,
                "content": (
                    "**Dividend investing** focuses on buying stocks that pay regular, growing dividends.\n\n"
                    "**Steps to build a dividend portfolio:**\n\n"
                    "1. **Set your goal** — Determine target monthly income\n"
                    "   Example: TZS 500,000/month = TZS 6,000,000/year needed\n\n"
                    "2. **Select stocks** — Choose 5-8 DSE stocks across different sectors\n"
                    "   Diversify between banking, manufacturing, telecoms, etc.\n\n"
                    "3. **Check sustainability** — Review:\n"
                    "   - Dividend history (3+ years of payments)\n"
                    "   - Yield vs sector average\n"
                    "   - Dividend growth trend\n\n"
                    "4. **Buy before books closure** — Time your purchases\n"
                    "   You must own shares before books close to receive dividend\n\n"
                    "5. **Reinvest dividends** — Use DRIP approach\n"
                    "   Buy more shares with dividend income to compound returns\n\n"
                    "**Sample TZS 10M portfolio:**\n"
                    "- TBL (30%) — TZS 3M at ~8.4% yield\n"
                    "- NMB (25%) — TZS 2.5M at ~5.1% yield\n"
                    "- CRDB (20%) — TZS 2M at ~2.7% yield\n"
                    "- TCC (15%) — TZS 1.5M at ~6.3% yield\n"
                    "- SWIS (10%) — TZS 1M at ~3.1% yield\n"
                    "- Blended yield: ~5.5%, Annual income: ~TZS 550,000"
                ),
                "key_takeaways": [
                    "Diversify across 5-8 stocks and sectors",
                    "Check 3+ years of dividend history",
                    "Reinvest dividends for compounding",
                ],
            },
            {
                "id": "risk-management",
                "title": "Managing Investment Risk",
                "difficulty": "intermediate",
                "read_time": 6,
                "content": (
                    "**Risk management** protects your capital while maximizing returns.\n\n"
                    "**Types of risk on the DSE:**\n\n"
                    "1. **Market risk** — Overall market decline\n"
                    "   Mitigation: Diversify, invest long-term\n\n"
                    "2. **Company risk** — Single company failure\n"
                    "   Mitigation: Don't put more than 25% in one stock\n\n"
                    "3. **Liquidity risk** — Difficulty selling shares\n"
                    "   Mitigation: Stick to actively traded stocks\n\n"
                    "4. **Dividend cut risk** — Company reduces or stops dividends\n"
                    "   Mitigation: Check payout ratio and earnings trends\n\n"
                    "5. **Inflation risk** — Returns below inflation rate\n"
                    "   Mitigation: Focus on dividend growth stocks\n\n"
                    "**Golden rules:**\n"
                    "- Never invest borrowed money\n"
                    "- Keep 3-6 months expenses in savings before investing\n"
                    "- Start small and learn as you go\n"
                    "- Don't panic sell during market dips\n"
                    "- Review your portfolio quarterly, not daily"
                ),
                "key_takeaways": [
                    "Diversify — max 25% in any single stock",
                    "Keep an emergency fund before investing",
                    "Review quarterly, not daily",
                ],
            },
            {
                "id": "tax-optimization",
                "title": "Tax-Smart Dividend Investing",
                "difficulty": "advanced",
                "read_time": 5,
                "content": (
                    "Understanding tax helps you keep more of your dividend income.\n\n"
                    "**Tanzania dividend tax:**\n"
                    "- Residents: 10% withholding tax\n"
                    "- Non-residents: 15% (reduced by DTA)\n"
                    "- Tax is deducted at source — you receive net amount\n\n"
                    "**Tax-smart strategies:**\n\n"
                    "1. **Yield on cost** — Buy at lower prices for higher effective yields\n"
                    "   If you bought at TZS 5,000 and dividend is TZS 500:\n"
                    "   Pre-tax yield on cost = 10%, After tax = 9%\n\n"
                    "2. **DTA benefits** — Non-residents from treaty countries\n"
                    "   Countries with DTAs: Canada, Denmark, Finland, India, Italy, "
                    "Norway, South Africa, Sweden, Zambia\n"
                    "   Can reduce withholding to 10%\n\n"
                    "3. **Reinvestment** — Reinvesting net dividends still compounds\n"
                    "   TZS 1M at 7% yield, reinvested for 10 years:\n"
                    "   Without tax: TZS 1,967,151\n"
                    "   With 10% tax (6.3% net): TZS 1,840,930\n\n"
                    "**Record keeping:**\n"
                    "Keep records of all dividend payments and tax withheld for your annual tax return."
                ),
                "key_takeaways": [
                    "Tax is withheld at source automatically",
                    "DTA countries get reduced rates",
                    "Keep records for tax returns",
                ],
            },
        ],
    },
    "glossary": {
        "title": "Investment Glossary",
        "description": "Key terms every DSE investor should know",
        "lessons": [
            {
                "id": "glossary",
                "title": "DSE Investment Glossary",
                "difficulty": "beginner",
                "read_time": 8,
                "content": (
                    "**Essential terms for DSE investors:**\n\n"
                    "**Books Closure Date** — Last date to buy shares and qualify for dividend. "
                    "If you buy after this date, you won't receive the declared dividend.\n\n"
                    "**CAGR** — Compound Annual Growth Rate. Average yearly growth rate over a period.\n\n"
                    "**CDS Account** — Central Depository System account. Required for holding shares electronically.\n\n"
                    "**CMSA** — Capital Markets and Securities Authority. Tanzania's market regulator.\n\n"
                    "**Dividend Per Share (DPS)** — Amount paid per share. Multiply by your shares to get total dividend.\n\n"
                    "**Dividend Yield** — Annual dividend as a percentage of share price.\n\n"
                    "**DTA** — Double Taxation Agreement. Treaty between countries to avoid taxing income twice.\n\n"
                    "**EPS** — Earnings Per Share. Company profit divided by number of shares.\n\n"
                    "**IPO** — Initial Public Offering. When a company first lists on the exchange.\n\n"
                    "**Market Cap** — Total market value of a company (share price x total shares).\n\n"
                    "**Payout Ratio** — Percentage of earnings paid as dividends.\n\n"
                    "**P/E Ratio** — Price-to-Earnings ratio. Share price divided by EPS.\n\n"
                    "**T+3 Settlement** — Shares are delivered 3 business days after trade.\n\n"
                    "**Withholding Tax** — Tax deducted from dividend before you receive it."
                ),
                "key_takeaways": [
                    "Learn these terms to understand market discussions",
                    "Books closure date is critical for dividends",
                    "CDS account is required to trade on DSE",
                ],
            },
        ],
    },
}


@router.get("/categories")
def get_categories():
    """Get all education categories with lesson summaries."""
    return [
        {
            "id": cat_id,
            "title": cat["title"],
            "description": cat["description"],
            "lesson_count": len(cat["lessons"]),
            "lessons": [
                {
                    "id": lesson["id"],
                    "title": lesson["title"],
                    "difficulty": lesson["difficulty"],
                    "read_time": lesson["read_time"],
                }
                for lesson in cat["lessons"]
            ],
        }
        for cat_id, cat in EDUCATION_CONTENT.items()
    ]


@router.get("/lesson/{lesson_id}")
def get_lesson(lesson_id: str):
    """Get a specific lesson by ID."""
    for cat in EDUCATION_CONTENT.values():
        for lesson in cat["lessons"]:
            if lesson["id"] == lesson_id:
                return lesson

    raise HTTPException(404, "Lesson not found")


@router.get("/search")
def search_lessons(q: str = Query(..., min_length=2)):
    """Search lessons by keyword."""
    q_lower = q.lower()
    results = []
    for cat_id, cat in EDUCATION_CONTENT.items():
        for lesson in cat["lessons"]:
            if (
                q_lower in lesson["title"].lower()
                or q_lower in lesson["content"].lower()
            ):
                results.append({
                    "id": lesson["id"],
                    "title": lesson["title"],
                    "category": cat["title"],
                    "difficulty": lesson["difficulty"],
                    "read_time": lesson["read_time"],
                    "snippet": _extract_snippet(lesson["content"], q_lower),
                })
    return results


def _extract_snippet(content: str, query: str, context_chars: int = 100) -> str:
    """Extract a snippet around the query match."""
    lower = content.lower()
    idx = lower.find(query)
    if idx == -1:
        return content[:context_chars] + "..."

    start = max(0, idx - context_chars // 2)
    end = min(len(content), idx + len(query) + context_chars // 2)
    snippet = content[start:end].strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."

    return snippet
