"""The shipped config: one ESPN league, Justin's team (espnTeamId 1), no Sleeper leagues.
These tests read the real config and the real raw cache. They do not use the three league fixture."""
import pytest

from pipeline import build as bd
from pipeline.common import CONFIG, RAW
from pipeline.ingest import load_config

SEASON, WEEK = 2026, 11
HAVE_RAW = (RAW / str(SEASON) / str(WEEK) / "status.json").exists()
needs_raw = pytest.mark.skipif(not HAVE_RAW, reason="no cached raw data")


def test_config_has_only_the_espn_league():
    cfg = load_config()
    assert cfg["espnTeamId"] == 1
    assert "sleeperUserId" not in cfg
    assert [(lg["key"], lg["platform"], lg["id"]) for lg in cfg["leagues"]] == [("fantasizing", "espn", 125685129)]
    assert cfg["leagues"][0]["shotguns"] is True


def test_no_sleeper_league_overrides_are_left():
    names = sorted(p.name for p in (CONFIG / "leagues").glob("*.overrides.yaml"))
    assert names == ["fantasizing.overrides.yaml"]


@needs_raw
def test_build_publishes_only_the_espn_league(tmp_path):
    res = bd.build(SEASON, WEEK, out_dir=tmp_path, save_idmap=False, recommended_root=tmp_path / "rec")
    assert set(res["leagues"]) == {"fantasizing"}
    lg = res["leagues"]["fantasizing"]
    assert lg["league"]["teamName"] == "Exempt List"
    assert lg["league"]["appName"] == "ESPN"
    assert lg["league"]["appUrl"] == "https://fantasy.espn.com/football/team?leagueId=125685129&teamId=1"
    assert lg["lineup"]["recommendedPoints"] > 0 and lg["lineup"]["gain"] >= 0
    assert [m["key"] for m in res["meta"]["leagues"]] == ["fantasizing"]
    assert sorted(p.name for p in tmp_path.glob("*.json")) == sorted(
        ["fantasizing.json", "pool-fantasizing.json", "trade-fantasizing.json", "meta.json"])


@needs_raw
def test_shotguns_block_for_the_espn_league(tmp_path):
    res = bd.build(SEASON, WEEK, out_dir=tmp_path, save_idmap=False, recommended_root=tmp_path / "rec")
    sg = res["leagues"]["fantasizing"]["shotguns"]
    assert sg is not None
