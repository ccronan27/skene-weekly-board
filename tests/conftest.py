import copy
import shutil
import json
from pathlib import Path

import pytest

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def load():
    """Load a fixture. Always returns a deep copy so tests can mutate it."""
    def _load(name):
        p = FIX / name
        if name.endswith(".json"):
            return copy.deepcopy(json.loads(p.read_text(encoding="utf-8")))
        return p.read_text(encoding="utf-8")
    return _load


# ---- the three league board (before the switch to ESPN only) ----
# The real config is ESPN only now, so the Sleeper league code paths are tested on this fixture set:
# the old three league config, its overrides, and the Sleeper league pull from the same week.

THREE = FIX / "three_league"


def copy_season_with_sleeper_leagues(dst_root, season=2026, week=11):
    """Copy the cached season from data/raw into dst_root, with the Sleeper league pull from the fixture.
    Returns dst_root. Build reads dst_root/{season}/{week}/..."""
    from pipeline.common import RAW
    shutil.copytree(RAW / str(season), dst_root / str(season))
    shutil.copy(THREE / "sleeper_leagues.json", dst_root / str(season) / str(week) / "sleeper_leagues.json")
    return dst_root


@pytest.fixture(scope="session")
def three_raw(tmp_path_factory):
    return copy_season_with_sleeper_leagues(tmp_path_factory.mktemp("three_raw") / "raw")


@pytest.fixture(scope="module")
def three_league(three_raw):
    """Points the config loaders at the three league fixture and makes build() default to the raw copy with
    the Sleeper leagues. Tests in a module that use this fixture (autouse there) see three leagues, team 14."""
    import functools

    from pipeline import build as bd
    from pipeline import ingest, scoring
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(ingest, "CONFIG", THREE)
        mp.setattr(scoring, "CONFIG", THREE)
        mp.setattr(bd, "build", functools.partial(bd.build, raw_root=three_raw))
        yield three_raw
