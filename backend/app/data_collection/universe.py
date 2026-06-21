"""
The backtest universe: NSE-listed companies the data pipeline ingests.

This is a curated, editable list (not scraped) spanning large & mid caps
across 13+ sectors so that market-cap/sector filters in the backtest engine
have a meaningful spread to work with. Add/remove entries here to change the
universe - everything downstream (`fetch_prices.py`, `fetch_fundamentals.py`)
re-derives from this single source of truth.

`trading_symbol` is the bare NSE symbol; the Yahoo Finance ticker is built by
appending `settings.YF_SUFFIX` (".NS") in the fetch scripts.
"""
from typing import TypedDict

class UniverseEntry(TypedDict):
    trading_symbol: str
    name: str
    sector: str

UNIVERSE: list[UniverseEntry] = [
    # Banking & Financial Services 
    {"trading_symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "sector": "Financial Services"},
    {"trading_symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "sector": "Financial Services"},
    {"trading_symbol": "SBIN", "name": "State Bank of India", "sector": "Financial Services"},
    {"trading_symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Ltd", "sector": "Financial Services"},
    {"trading_symbol": "AXISBANK", "name": "Axis Bank Ltd", "sector": "Financial Services"},
    {"trading_symbol": "INDUSINDBK", "name": "IndusInd Bank Ltd", "sector": "Financial Services"},
    {"trading_symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd", "sector": "Financial Services"},
    {"trading_symbol": "BAJAJFINSV", "name": "Bajaj Finserv Ltd", "sector": "Financial Services"},
    {"trading_symbol": "HDFCLIFE", "name": "HDFC Life Insurance Co Ltd", "sector": "Financial Services"},
    {"trading_symbol": "SBILIFE", "name": "SBI Life Insurance Co Ltd", "sector": "Financial Services"},
    {"trading_symbol": "ICICIPRULI", "name": "ICICI Prudential Life Insurance", "sector": "Financial Services"},
    {"trading_symbol": "ICICIGI", "name": "ICICI Lombard General Insurance", "sector": "Financial Services"},
    {"trading_symbol": "PFC", "name": "Power Finance Corp Ltd", "sector": "Financial Services"},
    {"trading_symbol": "RECLTD", "name": "REC Ltd", "sector": "Financial Services"},
    {"trading_symbol": "BANKBARODA", "name": "Bank of Baroda", "sector": "Financial Services"},
    {"trading_symbol": "PNB", "name": "Punjab National Bank", "sector": "Financial Services"},
    {"trading_symbol": "CHOLAFIN", "name": "Cholamandalam Investment & Finance", "sector": "Financial Services"},
    {"trading_symbol": "SHRIRAMFIN", "name": "Shriram Finance Ltd", "sector": "Financial Services"},
    {"trading_symbol": "MUTHOOTFIN", "name": "Muthoot Finance Ltd", "sector": "Financial Services"},
    {"trading_symbol": "IDFCFIRSTB", "name": "IDFC First Bank Ltd", "sector": "Financial Services"},
    {"trading_symbol": "AUBANK", "name": "AU Small Finance Bank Ltd", "sector": "Financial Services"},
    {"trading_symbol": "FEDERALBNK", "name": "Federal Bank Ltd", "sector": "Financial Services"},
    {"trading_symbol": "LICI", "name": "Life Insurance Corp of India", "sector": "Financial Services"},
    {"trading_symbol": "ABCAPITAL", "name": "Aditya Birla Capital Ltd", "sector": "Financial Services"},

    # Information Technology 
    {"trading_symbol": "TCS", "name": "Tata Consultancy Services Ltd", "sector": "Information Technology"},
    {"trading_symbol": "INFY", "name": "Infosys Ltd", "sector": "Information Technology"},
    {"trading_symbol": "WIPRO", "name": "Wipro Ltd", "sector": "Information Technology"},
    {"trading_symbol": "HCLTECH", "name": "HCL Technologies Ltd", "sector": "Information Technology"},
    {"trading_symbol": "TECHM", "name": "Tech Mahindra Ltd", "sector": "Information Technology"},
    {"trading_symbol": "LTM", "name": "LTM Ltd (formerly LTIMindtree)", "sector": "Information Technology"},
    {"trading_symbol": "PERSISTENT", "name": "Persistent Systems Ltd", "sector": "Information Technology"},
    {"trading_symbol": "COFORGE", "name": "Coforge Ltd", "sector": "Information Technology"},
    {"trading_symbol": "MPHASIS", "name": "Mphasis Ltd", "sector": "Information Technology"},
    {"trading_symbol": "LTTS", "name": "L&T Technology Services Ltd", "sector": "Information Technology"},

    # Pharma & Healthcare 
    {"trading_symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries", "sector": "Healthcare"},
    {"trading_symbol": "DRREDDY", "name": "Dr Reddys Laboratories Ltd", "sector": "Healthcare"},
    {"trading_symbol": "CIPLA", "name": "Cipla Ltd", "sector": "Healthcare"},
    {"trading_symbol": "DIVISLAB", "name": "Divis Laboratories Ltd", "sector": "Healthcare"},
    {"trading_symbol": "APOLLOHOSP", "name": "Apollo Hospitals Enterprise Ltd", "sector": "Healthcare"},
    {"trading_symbol": "LUPIN", "name": "Lupin Ltd", "sector": "Healthcare"},
    {"trading_symbol": "AUROPHARMA", "name": "Aurobindo Pharma Ltd", "sector": "Healthcare"},
    {"trading_symbol": "TORNTPHARM", "name": "Torrent Pharmaceuticals Ltd", "sector": "Healthcare"},
    {"trading_symbol": "ALKEM", "name": "Alkem Laboratories Ltd", "sector": "Healthcare"},
    {"trading_symbol": "ZYDUSLIFE", "name": "Zydus Lifesciences Ltd", "sector": "Healthcare"},
    {"trading_symbol": "MAXHEALTH", "name": "Max Healthcare Institute Ltd", "sector": "Healthcare"},
    {"trading_symbol": "BIOCON", "name": "Biocon Ltd", "sector": "Healthcare"},

    # Automobile 
    {"trading_symbol": "MARUTI", "name": "Maruti Suzuki India Ltd", "sector": "Automobile"},
    {"trading_symbol": "TMPV", "name": "Tata Motors Passenger Vehicles Ltd", "sector": "Automobile"},
    {"trading_symbol": "M&M", "name": "Mahindra & Mahindra Ltd", "sector": "Automobile"},
    {"trading_symbol": "BAJAJ-AUTO", "name": "Bajaj Auto Ltd", "sector": "Automobile"},
    {"trading_symbol": "EICHERMOT", "name": "Eicher Motors Ltd", "sector": "Automobile"},
    {"trading_symbol": "HEROMOTOCO", "name": "Hero MotoCorp Ltd", "sector": "Automobile"},
    {"trading_symbol": "TVSMOTOR", "name": "TVS Motor Company Ltd", "sector": "Automobile"},
    {"trading_symbol": "ASHOKLEY", "name": "Ashok Leyland Ltd", "sector": "Automobile"},
    {"trading_symbol": "BHARATFORG", "name": "Bharat Forge Ltd", "sector": "Automobile"},
    {"trading_symbol": "MOTHERSON", "name": "Samvardhana Motherson International", "sector": "Automobile"},

    # FMCG 
    {"trading_symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "sector": "FMCG"},
    {"trading_symbol": "ITC", "name": "ITC Ltd", "sector": "FMCG"},
    {"trading_symbol": "NESTLEIND", "name": "Nestle India Ltd", "sector": "FMCG"},
    {"trading_symbol": "BRITANNIA", "name": "Britannia Industries Ltd", "sector": "FMCG"},
    {"trading_symbol": "DABUR", "name": "Dabur India Ltd", "sector": "FMCG"},
    {"trading_symbol": "GODREJCP", "name": "Godrej Consumer Products Ltd", "sector": "FMCG"},
    {"trading_symbol": "MARICO", "name": "Marico Ltd", "sector": "FMCG"},
    {"trading_symbol": "TATACONSUM", "name": "Tata Consumer Products Ltd", "sector": "FMCG"},
    {"trading_symbol": "COLPAL", "name": "Colgate Palmolive India Ltd", "sector": "FMCG"},
    {"trading_symbol": "VBL", "name": "Varun Beverages Ltd", "sector": "FMCG"},
    {"trading_symbol": "UNITDSPR", "name": "United Spirits Ltd", "sector": "FMCG"},

    # Energy / Oil & Gas / Power 
    {"trading_symbol": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Energy"},
    {"trading_symbol": "ONGC", "name": "Oil & Natural Gas Corp Ltd", "sector": "Energy"},
    {"trading_symbol": "BPCL", "name": "Bharat Petroleum Corp Ltd", "sector": "Energy"},
    {"trading_symbol": "IOC", "name": "Indian Oil Corp Ltd", "sector": "Energy"},
    {"trading_symbol": "GAIL", "name": "GAIL India Ltd", "sector": "Energy"},
    {"trading_symbol": "NTPC", "name": "NTPC Ltd", "sector": "Power"},
    {"trading_symbol": "POWERGRID", "name": "Power Grid Corp of India Ltd", "sector": "Power"},
    {"trading_symbol": "COALINDIA", "name": "Coal India Ltd", "sector": "Energy"},
    {"trading_symbol": "TATAPOWER", "name": "Tata Power Co Ltd", "sector": "Power"},
    {"trading_symbol": "ADANIGREEN", "name": "Adani Green Energy Ltd", "sector": "Power"},
    {"trading_symbol": "ADANIPOWER", "name": "Adani Power Ltd", "sector": "Power"},
    {"trading_symbol": "ADANIENT", "name": "Adani Enterprises Ltd", "sector": "Diversified"},

    # Metals & Mining 
    {"trading_symbol": "TATASTEEL", "name": "Tata Steel Ltd", "sector": "Metals & Mining"},
    {"trading_symbol": "JSWSTEEL", "name": "JSW Steel Ltd", "sector": "Metals & Mining"},
    {"trading_symbol": "HINDALCO", "name": "Hindalco Industries Ltd", "sector": "Metals & Mining"},
    {"trading_symbol": "VEDL", "name": "Vedanta Ltd", "sector": "Metals & Mining"},
    {"trading_symbol": "JINDALSTEL", "name": "Jindal Steel & Power Ltd", "sector": "Metals & Mining"},
    {"trading_symbol": "SAIL", "name": "Steel Authority of India Ltd", "sector": "Metals & Mining"},
    {"trading_symbol": "NMDC", "name": "NMDC Ltd", "sector": "Metals & Mining"},

    # Cement 
    {"trading_symbol": "ULTRACEMCO", "name": "UltraTech Cement Ltd", "sector": "Cement"},
    {"trading_symbol": "SHREECEM", "name": "Shree Cement Ltd", "sector": "Cement"},
    {"trading_symbol": "AMBUJACEM", "name": "Ambuja Cements Ltd", "sector": "Cement"},
    {"trading_symbol": "ACC", "name": "ACC Ltd", "sector": "Cement"},
    {"trading_symbol": "DALBHARAT", "name": "Dalmia Bharat Ltd", "sector": "Cement"},

    # Capital Goods / Infra 
    {"trading_symbol": "LT", "name": "Larsen & Toubro Ltd", "sector": "Capital Goods"},
    {"trading_symbol": "SIEMENS", "name": "Siemens Ltd", "sector": "Capital Goods"},
    {"trading_symbol": "ABB", "name": "ABB India Ltd", "sector": "Capital Goods"},
    {"trading_symbol": "CUMMINSIND", "name": "Cummins India Ltd", "sector": "Capital Goods"},
    {"trading_symbol": "HAVELLS", "name": "Havells India Ltd", "sector": "Capital Goods"},
    {"trading_symbol": "BEL", "name": "Bharat Electronics Ltd", "sector": "Capital Goods"},
    {"trading_symbol": "BHEL", "name": "Bharat Heavy Electricals Ltd", "sector": "Capital Goods"},
    {"trading_symbol": "POLYCAB", "name": "Polycab India Ltd", "sector": "Capital Goods"},

    # Telecom 
    {"trading_symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "sector": "Telecom"},
    {"trading_symbol": "IDEA", "name": "Vodafone Idea Ltd", "sector": "Telecom"},
    {"trading_symbol": "INDUSTOWER", "name": "Indus Towers Ltd", "sector": "Telecom"},

    # Consumer Durables / Retail 
    {"trading_symbol": "TITAN", "name": "Titan Company Ltd", "sector": "Consumer Durables"},
    {"trading_symbol": "DMART", "name": "Avenue Supermarts Ltd", "sector": "Retail"},
    {"trading_symbol": "TRENT", "name": "Trent Ltd", "sector": "Retail"},
    {"trading_symbol": "PIDILITIND", "name": "Pidilite Industries Ltd", "sector": "Chemicals"},
    {"trading_symbol": "VOLTAS", "name": "Voltas Ltd", "sector": "Consumer Durables"},
    {"trading_symbol": "ASIANPAINT", "name": "Asian Paints Ltd", "sector": "Consumer Durables"},
    {"trading_symbol": "BERGEPAINT", "name": "Berger Paints India Ltd", "sector": "Consumer Durables"},
    {"trading_symbol": "PAGEIND", "name": "Page Industries Ltd", "sector": "Consumer Durables"},

    # Chemicals 
    {"trading_symbol": "SRF", "name": "SRF Ltd", "sector": "Chemicals"},
    {"trading_symbol": "UPL", "name": "UPL Ltd", "sector": "Chemicals"},
    {"trading_symbol": "PIIND", "name": "PI Industries Ltd", "sector": "Chemicals"},
    {"trading_symbol": "DEEPAKNTR", "name": "Deepak Nitrite Ltd", "sector": "Chemicals"},
    {"trading_symbol": "ATUL", "name": "Atul Ltd", "sector": "Chemicals"},

    # Realty 
    {"trading_symbol": "DLF", "name": "DLF Ltd", "sector": "Realty"},
    {"trading_symbol": "GODREJPROP", "name": "Godrej Properties Ltd", "sector": "Realty"},
    {"trading_symbol": "OBEROIRLTY", "name": "Oberoi Realty Ltd", "sector": "Realty"},
    {"trading_symbol": "PRESTIGE", "name": "Prestige Estates Projects Ltd", "sector": "Realty"},

    # Diversified / Others 
    {"trading_symbol": "ADANIPORTS", "name": "Adani Ports & SEZ Ltd", "sector": "Infrastructure"},
    {"trading_symbol": "GRASIM", "name": "Grasim Industries Ltd", "sector": "Diversified"},
    {"trading_symbol": "INDIGO", "name": "InterGlobe Aviation Ltd", "sector": "Aviation"},
    {"trading_symbol": "ETERNAL", "name": "Eternal Ltd (Zomato)", "sector": "Internet"},
    {"trading_symbol": "NAUKRI", "name": "Info Edge India Ltd", "sector": "Internet"},
]

def get_universe_symbols() -> list[str]:
    """Bare NSE trading symbols, e.g. ['RELIANCE', 'TCS', ...]."""
    return [entry["trading_symbol"] for entry in UNIVERSE]

# Benchmark is modelled as a Company row too (is_benchmark=True) so it shares
# the exact same prices table/query path as every other instrument.
BENCHMARK_ENTRY: UniverseEntry = {
    "trading_symbol": "NIFTY50",
    "name": "Nifty 50 Index",
    "sector": "Index",
}
