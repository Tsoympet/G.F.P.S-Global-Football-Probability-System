"""Provider interfaces for ingesting football data.

Providers expose a small, synchronous surface so they can be orchestrated
by the ingestion pipeline without external dependencies. The default
implementation relies on a no-key, local OpenFootball CSV snapshot to
stay within legal/open data constraints.
"""

from .base import (
    ProviderMetadata,
    FixtureRecord,
    ResultRecord,
    EventRecord,
    LineupRecord,
    OddsRecord,
    Provider,
    ProviderTier,
)
from .openfootball import OpenFootballCSVProvider
from .key_based_stub import KeyBasedStubProvider
from .free_football_data_org import FootballDataOrgProvider
from .free_live_openligadb import OpenLigaDBLiveProvider
from .premium_api_football import ApiFootballProvider
from .registry import ProviderRegistry
from .settings import DataMode, DataSourceSettings, ProviderToggle, load_settings_from_env

__all__ = [
    "ProviderMetadata",
    "FixtureRecord",
    "ResultRecord",
    "EventRecord",
    "LineupRecord",
    "OddsRecord",
    "Provider",
    "ProviderTier",
    "OpenFootballCSVProvider",
    "KeyBasedStubProvider",
    "FootballDataOrgProvider",
    "OpenLigaDBLiveProvider",
    "ApiFootballProvider",
    "ProviderRegistry",
    "DataMode",
    "DataSourceSettings",
    "ProviderToggle",
    "load_settings_from_env",
]
