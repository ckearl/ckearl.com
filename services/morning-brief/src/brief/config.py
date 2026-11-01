"""What the brief covers. Change teams and places here."""

from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("America/Denver")
LATITUDE = 40.2338
LONGITUDE = -111.6585

ALL_TEAMS = None

# ESPN path, strip label, days to look back, followed teams (lowercase ESPN abbreviations).
LEAGUES = {
    "nba": ("basketball/nba", "NBA", 1, ALL_TEAMS),
    "nfl": ("football/nfl", "NFL", 3, {"sea", "lar", "sf", "den", "min", "bal", "buf"}),
    "nhl": ("hockey/nhl", "NHL", 1, {"utah", "vgk", "col", "chi", "bos"}),
    "epl": ("soccer/eng.1", "Premier League", 3, ALL_TEAMS),
    "laliga": ("soccer/esp.1", "La Liga", 3, {"rma", "bar", "atm"}),
    "seriea": ("soccer/ita.1", "Serie A", 3, {"juv", "int", "mil", "nap", "roma"}),
    "bundesliga": ("soccer/ger.1", "Bundesliga", 3, {"mun", "dor", "b04"}),
    "ligue1": ("soccer/fra.1", "Ligue 1", 3, {"psg", "olm", "lyon"}),
    "mlb": ("baseball/mlb", "MLB", 1, {"wsh", "sea"}),
}

# ESPN's scoreboard and team list disagree on a few abbreviations. Logo files use the team list.
ABBREVIATION_ALIASES = {("nhl", "uta"): "utah"}

TEAMS = [
    {"path": "basketball/nba", "id": "utah", "abbr": "UTA", "name": "Utah Jazz", "bg": "#4e008e", "fg": "#ffffff"},
    {"path": "hockey/nhl", "id": "utah", "abbr": "UTA", "name": "Utah Mammoth", "bg": "#000000", "fg": "#7ab2e1"},
    {"path": "soccer/usa.1", "id": "4771", "abbr": "RSL", "name": "Real Salt Lake", "bg": "#a32035", "fg": "#ffffff"},
    {"path": "football/college-football", "id": "252", "abbr": "BYU", "name": "BYU", "bg": "#0047ba", "fg": "#ffffff"},
    {"path": "soccer/eng.1", "id": "367", "abbr": "TOT", "name": "Tottenham", "bg": "#ffffff", "fg": "#0b1426"},
]

# Newest stories from each feed until Claude ranks them.
NEWS = [
    {
        "label": "Utah and US",
        "limit": 3,
        "feeds": [
            ("KSL", "https://www.ksl.com/rss/news"),
            ("Deseret News", "https://www.deseret.com/arc/outboundfeeds/rss/"),
            ("NPR", "https://feeds.npr.org/1001/rss.xml"),
        ],
    },
    {
        "label": "World",
        "limit": 4,
        "feeds": [("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml")],
    },
]
