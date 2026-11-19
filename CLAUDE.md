# skene-weekly-board

Justin's start/sit dashboard for the ESPN league Fantasizing 2026. His team is Exempt List (ESPN teamId 1). Read `docs/SPEC.md` (what to build) and `docs/BACKTEST.md` (why the model is what it is) before changing anything. Read `docs/STATES.md` before touching source status, the ESPN roster file, season phase, routing or the Trade view. Each state machine there has one function that decides its state, so change that function, not its readers.

## Hard rules
- No credentials, tokens or cookies anywhere: repo, workflows, logs or site. The repo is public
- ESPN league data comes only from the public league endpoint, with no login, cookies or auth headers, and only through `pipeline/adapters/espn_league.py` (the league was made public 11/19/26). Never store owner names or member data from it. If the league goes private again, do not add credentials. The board falls back to `data/espn/rosters.json`, which is written by ingest from the public league, or by hand or a sync if the league goes private. ESPN default projections (leaguedefaults) are fine to fetch
- No owners' real names in data or UI. Team names only. The name Justin may appear in README, CLAUDE.md and docs only
- Site must ship a noindex meta tag and a robots.txt that disallows everything
- Projection model is the equal average of ESPN + Rotowire. Do not add weighting, calibration or a Vegas multiplier unless it beats the equal average in the cross-season backtest (fit last season, score this season)
- UI copy: no em dashes, no semicolons, plain and direct
- Times shown in Central (America/Chicago)
- Sleeper is used only as a data source (players, state, stats and the Rotowire projections). No Sleeper league is configured, and no Sleeper user id belongs in the repo

## Build principles (this should run for years with little care)
- Few dependencies. Python 3.12 + requests/pandas for the pipeline. Plain HTML/CSS/JS for the site, no build step
- One adapter per source in `pipeline/adapters/`, each with a contract test that fails loudly when a source changes shape
- If one source fails, the run still publishes with that source marked stale. Never publish an empty board
- Raw pulls cached to `data/raw/{season}/{week}/`, built outputs to `data/build/`, site reads only `data/build/`
- League settings come from the APIs, overrides in `config/leagues/*.overrides.yaml`
- Every output carries `generatedAt` and per-source `lastUpdated`

## Workflows
- `refresh.yml`: schedule (see SPEC refresh table, `timezone: America/Chicago`), `workflow_dispatch`, and push on `data/espn/**`. Fetch, build, commit data, deploy Pages
- Pages source is set to GitHub Actions. Workflow permissions are read and write

## Tests
- `tests/fixtures/three_league/` holds a copy of the old three league config and its Sleeper league pull. Tests for the Sleeper league code path load it through the `three_league` fixture in `tests/conftest.py`. Do not point the real config at it
- `tests/test_espn_only.py` checks the shipped config (one league, team 1)

## Done means
- Tests pass, a manual `workflow_dispatch` run succeeds, and the live page shows Fantasizing 2026 with Exempt List's starters and last-updated stamps
- README covers: what it is, how to run locally, preseason checklist (re-enable workflows, update league ID and espnTeamId, re-run backtest)
