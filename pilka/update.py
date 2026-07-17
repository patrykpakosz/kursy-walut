import json
import urllib.request
import xml.etree.ElementTree as ET
import time
from datetime import datetime, date
from zoneinfo import ZoneInfo

BASE = "https://www.thesportsdb.com/api/v1/json/3/"

def get(path):
    for attempt in range(4):
        try:
            request = urllib.request.Request(
                BASE + path,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(request, timeout=35) as response:
                return json.load(response)

        except Exception:
            time.sleep(12 + attempt * 10)

    return {}

def event_result_text(event):
    return (
        f"{event.get('strHomeTeam', '?')} "
        f"{event.get('intHomeScore', '-')} : "
        f"{event.get('intAwayScore', '-')} "
        f"{event.get('strAwayTeam', '?')}"
    )

def event_next_text(event):
    return (
        f"{event.get('strHomeTeam', '?')} — "
        f"{event.get('strAwayTeam', '?')}"
    )

def event_date(event):
    return (
        event.get("dateEvent", "")
        + " • "
        + (event.get("strTime") or "")[:5]
    ).strip(" •")

def get_team(team_id, display_name, api_name):
    team_info = get(f"lookupteam.php?id={team_id}").get("teams", [{}])[0]

    time.sleep(3)

    last_events = get(
        f"eventslast.php?id={team_id}"
    ).get("results", [])

    time.sleep(3)

    next_events = get(
        f"eventsnext.php?id={team_id}"
    ).get("events", [])

    last = last_events[0] if last_events else {}

    form = []

    for event in last_events[:5]:
        home_score = event.get("intHomeScore")
        away_score = event.get("intAwayScore")

        if home_score is None or away_score is None:
            form.append("N")
            continue

        if event.get("strHomeTeam") == api_name:
            own_score = int(home_score)
            opponent_score = int(away_score)
        else:
            own_score = int(away_score)
            opponent_score = int(home_score)

        if own_score > opponent_score:
            form.append("W")
        elif own_score == opponent_score:
            form.append("R")
        else:
            form.append("P")

    while len(form) < 5:
        form.append("N")

    nexts = [
        {
            "text": event_next_text(event),
            "date": event_date(event)
        }
        for event in next_events[:3]
    ]

    return {
        "name": display_name,
        "badge": team_info.get("strBadge"),
        "last": {
            "text": event_result_text(last) if last else "Brak danych",
            "date": last.get("dateEvent", "")
        },
        "next": nexts[0] if nexts else {
            "text": "Brak zaplanowanego meczu",
            "date": ""
        },
        "nexts": nexts,
        "form": form
    }

def get_table(league_id, title, focus_team):
    league = get(
        f"lookupleague.php?id={league_id}"
    ).get("leagues", [{}])[0]

    time.sleep(3)

    season = league.get("strCurrentSeason", "2026-2027")

    standings = get(
        f"lookuptable.php?l={league_id}&s={season}"
    ).get("table", [])

    return {
        "title": title,
        "badge": league.get("strBadge"),
        "focus": focus_team,
        "rows": [
            {
                "rank": row.get("intRank"),
                "team": row.get("strTeam"),
                "played": row.get("intPlayed"),
                "goals": (
                    f"{row.get('intGoalsFor', 0)}:"
                    f"{row.get('intGoalsAgainst', 0)}"
                ),
                "points": row.get("intPoints")
            }
            for row in standings
        ]
    }

def get_news():
    feeds = [
        "https://www.espn.com/espn/rss/soccer/news",
        "https://feeds.bbci.co.uk/sport/football/rss.xml"
    ]

    for url in feeds:
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            xml = urllib.request.urlopen(
                request,
                timeout=30
            ).read()

            root = ET.fromstring(xml)

            titles = [
                item.findtext("title", "")
                for item in root.findall("./channel/item")
            ]

            if titles:
                return titles[:5]

        except Exception:
            continue

    return ["Brak bieżących nagłówków piłkarskich"]

data = {
    "updatedAt": datetime.now(
        ZoneInfo("Europe/Warsaw")
    ).strftime("%d.%m.%Y, %H:%M"),

    "teams": [
        get_team("135303", "WISŁA KRAKÓW", "Wisła Kraków"),
        get_team("133612", "MANCHESTER UNITED", "Manchester United"),
        get_team("133901", "POLSKA", "Poland")
    ],

    "tables": {
        "ekstra": get_table(
            "4422",
            "TABELA EKSTRAKLASY",
            "Wisła Kraków"
        ),

        "premier": get_table(
            "4328",
            "TABELA PREMIER LEAGUE",
            "Manchester United"
        )
    },

    "fifa": {
        "rows": [
            {"rank": 1, "team": "Argentyna"},
            {"rank": 2, "team": "Hiszpania"},
            {"rank": 3, "team": "Francja"},
            {"rank": 4, "team": "Anglia"},
            {"rank": 5, "team": "Brazylia"},
            {"rank": 36, "team": "Polska"}
        ]
    },

    "matches": [],
    "news": get_news()
}

with open(
    "pilka/football-data.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(data, file, ensure_ascii=False)
