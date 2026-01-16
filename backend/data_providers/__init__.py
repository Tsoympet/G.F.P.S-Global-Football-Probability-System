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
    Provider,
)
from .openfootball import OpenFootballCSVProvider
from .key_based_stub import KeyBasedStubProvider

__all__ = [
    "ProviderMetadata",
    "FixtureRecord",
    "ResultRecord",
    "EventRecord",
    "LineupRecord",
    "Provider",
    "OpenFootballCSVProvider",
    "KeyBasedStubProvider",
]
