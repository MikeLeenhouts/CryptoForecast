"""Data configuration constants for Yahoo Finance API."""

class DataFormat:
    """Data format constants."""
    RAW = "raw"
    JSON = "json"
    CSV = "csv"

class Locale:
    """Locale constants for different Yahoo Finance domains."""
    US = "us"
    UK = "uk"
    CA = "ca"
    AU = "au"
    DE = "de"
    FR = "fr"
    IT = "it"
    ES = "es"
    IN = "in"
    JP = "jp"
    HK = "hk"
    SG = "sg"
    
    @staticmethod
    def locale_url(locale):
        """Get the Yahoo Finance URL for a given locale."""
        locale_urls = {
            "us": "https://finance.yahoo.com/quote",
            "uk": "https://uk.finance.yahoo.com/quote",
            "ca": "https://ca.finance.yahoo.com/quote",
            "au": "https://au.finance.yahoo.com/quote",
            "de": "https://de.finance.yahoo.com/quote",
            "fr": "https://fr.finance.yahoo.com/quote",
            "it": "https://it.finance.yahoo.com/quote",
            "es": "https://es.finance.yahoo.com/quote",
            "in": "https://in.finance.yahoo.com/quote",
            "jp": "https://finance.yahoo.co.jp/quote",
            "hk": "https://hk.finance.yahoo.com/quote",
            "sg": "https://sg.finance.yahoo.com/quote"
        }
        return locale_urls.get(locale, locale_urls["us"])

class DataEvent:
    """Data event constants."""
    HISTORICAL_PRICES = "history"
    DIVIDENDS = "div"
    SPLITS = "split"

class DataFrequency:
    """Data frequency constants."""
    DAILY = "1d"
    WEEKLY = "1wk"
    MONTHLY = "1mo"
    QUARTERLY = "3mo"
    YEARLY = "1y"
