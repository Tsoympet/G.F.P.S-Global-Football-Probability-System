from backend.data_providers import (
    ApiFootballProvider,
    DataMode,
    DataSourceSettings,
    FootballDataOrgProvider,
    OpenFootballCSVProvider,
    ProviderRegistry,
    ProviderToggle,
)
from backend.odds_abstraction import resolve_odds_from_sources


def test_free_only_filters_premium():
    settings = DataSourceSettings(
        mode=DataMode.FREE_ONLY,
        provider_overrides={
            "openfootball-csv": ProviderToggle(priority=1),
            "api-football-premium": ProviderToggle(enabled=True, priority=2),
        },
    )
    registry = ProviderRegistry(settings)
    registry.register(OpenFootballCSVProvider())
    registry.register(ApiFootballProvider(api_key="secret"))
    providers = registry.active(data_types={"fixtures"})
    assert any(isinstance(p, OpenFootballCSVProvider) for p in providers)
    assert not any(isinstance(p, ApiFootballProvider) for p in providers)


def test_hybrid_mode_keeps_free_first():
    settings = DataSourceSettings(
        mode=DataMode.HYBRID,
        provider_overrides={
            "openfootball-csv": ProviderToggle(priority=1),
            "football-data.org": ProviderToggle(priority=2),
        },
    )
    registry = ProviderRegistry(settings)
    registry.register(OpenFootballCSVProvider())
    registry.register(FootballDataOrgProvider(api_key=None))
    providers = registry.active(data_types={"fixtures"})
    assert isinstance(providers[0], OpenFootballCSVProvider)
    assert any(isinstance(p, FootballDataOrgProvider) for p in providers)


def test_odds_abstraction_falls_back_to_model_probabilities():
    probabilities = {"home": 0.52, "draw": 0.28, "away": 0.2}
    resolved = resolve_odds_from_sources(None, probabilities, target_overround=1.05)
    assert set(resolved.keys()) == {"home", "draw", "away"}
    # more likely outcomes should carry shorter odds
    assert resolved["home"] < resolved["draw"]
    assert resolved["draw"] < resolved["away"]

