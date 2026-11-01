from datetime import date, datetime, timezone

from brief import config, ski

NOW = datetime(2026, 12, 2, 12, 0, tzinfo=timezone.utc)


def grid(*periods):
    values = [{"validTime": f"{start}/PT6H", "value": value} for start, value in periods]
    return {"properties": {"snowfallAmount": {"values": values}}}


def test_season():
    assert ski.in_season(date(2026, 11, 1))
    assert ski.in_season(date(2027, 4, 30))
    assert not ski.in_season(date(2026, 10, 31))
    assert not ski.in_season(date(2026, 7, 4))


def test_forecast_counts_only_the_next_three_days():
    data = grid(
        ("2026-12-02T06:00:00+00:00", 500),
        ("2026-12-02T18:00:00+00:00", 127),
        ("2026-12-05T06:00:00+00:00", 127),
        ("2026-12-05T18:00:00+00:00", 500),
        ("2026-12-03T00:00:00+00:00", None),
    )
    assert ski.forecast_inches(data, NOW) == 10


def test_station_row_measures_gain_from_the_latest_reading():
    values = [{"date": "a", "value": 20}, {"date": "b", "value": 24}, {"date": "c", "value": 22}, {"date": "d", "value": None}, {"date": "e", "value": 30}]
    assert ski.station_row("Snowbird", values) == {"name": "Snowbird", "base": '30"', "new24h": '8"', "new48h": '6"'}


def test_station_row_without_readings():
    assert ski.station_row("Park City", [])["base"] == "n/a"


def test_quiet_forecast_hides_the_section(monkeypatch):
    responses = iter([{"properties": {"forecastGridData": "url"}}, grid(("2026-12-02T18:00:00+00:00", 100))])
    monkeypatch.setattr(ski, "get_json", lambda *_args: next(responses))
    assert ski.fetch(NOW) is None


def test_off_season_makes_no_requests(monkeypatch):
    def fail(*_args):
        raise AssertionError

    monkeypatch.setattr(ski, "get_json", fail)
    assert ski.fetch(datetime(2026, 7, 4, 12, tzinfo=config.TIMEZONE)) is None


def test_storm_builds_a_report(monkeypatch):
    station = {"stationTriplet": "766:UT:SNTL", "data": [{"values": [{"value": 20}, {"value": 30}]}]}
    responses = iter([{"properties": {"forecastGridData": "url"}}, grid(("2026-12-02T18:00:00+00:00", 254)), [station]])
    monkeypatch.setattr(ski, "get_json", lambda *_args: next(responses))
    report = ski.fetch(NOW)
    assert report["summary"] == "About 10 inches of snow is forecast for the Cottonwoods by Saturday."
    assert report["resorts"][0] == {"name": "Snowbird", "base": '30"', "new24h": '10"', "new48h": '10"'}
    assert [row["name"] for row in report["resorts"]] == ["Snowbird", "Brighton and Solitude", "Park City"]
