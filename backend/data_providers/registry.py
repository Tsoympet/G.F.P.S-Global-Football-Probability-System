from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Set

from .base import Provider, ProviderTier
from .settings import DataMode, DataSourceSettings, ProviderToggle


class ProviderRegistry:
    """Simple in-memory registry for active providers."""

    def __init__(self, settings: DataSourceSettings):
        self.settings = settings
        self._providers: List[Provider] = []

    def register(self, provider: Provider) -> None:
        self._providers.append(provider)

    def _toggle_for(self, provider: Provider) -> ProviderToggle:
        return self.settings.provider_overrides.get(
            provider.meta.name, ProviderToggle(priority=provider.meta.priority)
        )

    def _is_enabled(self, provider: Provider) -> bool:
        toggle = self._toggle_for(provider)
        if not toggle.enabled:
            return False
        if self.settings.mode == DataMode.FREE_ONLY and provider.meta.tier == ProviderTier.PREMIUM:
            return False
        return True

    def active(
        self,
        data_types: Optional[Set[str]] = None,
        live_only: bool = False,
    ) -> Sequence[Provider]:
        candidates: List[tuple[int, Provider]] = []
        for provider in self._providers:
            if not self._is_enabled(provider):
                continue
            if live_only and not provider.meta.supports_live:
                continue
            # Providers must declare support for at least one of the requested data types.
            if data_types and provider.meta.data_types.isdisjoint(data_types):
                continue
            priority = self._toggle_for(provider).priority
            candidates.append((priority, provider))
        candidates.sort(key=lambda p: p[0])
        return [p for _, p in candidates]

    def reliability(self, provider: Provider) -> float:
        return provider.meta.reliability
