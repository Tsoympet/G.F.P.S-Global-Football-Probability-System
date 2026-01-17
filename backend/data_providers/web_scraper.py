from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from .base import FixtureRecord, Provider, ProviderMetadata, ProviderTier, ResultRecord
from .utils import parse_utc_datetime

logger = logging.getLogger(__name__)


class WebScraperProvider(Provider):
    """Generic web scraper for football data from HTML sources.
    
    This provider allows scraping football fixtures and results from
    publicly available websites. It includes rate limiting, caching,
    and error handling to be a good web citizen.
    
    Configuration can be done via environment variables or by providing
    a configuration dictionary that maps CSS selectors to data fields.
    """

    meta = ProviderMetadata(
        name="web-scraper",
        description="Generic web scraper for football data from HTML sources",
        data_types={"fixtures", "results"},
        requires_api_key=False,
        rate_limit_per_minute=30,
        supports_live=False,
        tier=ProviderTier.FREE,
        reliability=0.6,
        refresh_seconds=3600,
        auth_note="Configure scraping targets via SCRAPER_CONFIG_PATH or provide config dict",
        priority=20,
    )

    def __init__(
        self,
        config: Optional[dict] = None,
        config_path: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
        allow_network: bool = True,
        user_agent: Optional[str] = None,
    ) -> None:
        """Initialize the web scraper provider.
        
        Args:
            config: Dictionary containing scraper configuration
            config_path: Path to JSON config file
            cache_dir: Directory for caching scraped data
            allow_network: Whether to allow network requests
            user_agent: Custom user agent string
        """
        self.allow_network = allow_network
        self.cache_dir = cache_dir or Path(__file__).resolve().parent.parent / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        self.user_agent = user_agent or (
            "Mozilla/5.0 (compatible; GFPS-WebScraper/1.0; "
            "+https://github.com/Tsoympet/G.F.P.S-Global-Football-Probability-System)"
        )
        
        # Load configuration
        self.config = config or self._load_config(config_path)
        
        # Rate limiting state
        self._last_request_time = 0.0
        self._min_request_interval = 60.0 / self.meta.rate_limit_per_minute

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load scraper configuration from file or return default."""
        if config_path and config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        
        # Default configuration - empty, users must provide their own
        return {
            "fixtures_url": "",
            "results_url": "",
            "selectors": {
                "fixture_container": "",
                "fixture_id": "",
                "home_team": "",
                "away_team": "",
                "kickoff": "",
                "league": "",
                "season": "",
                "venue": "",
            },
            "result_selectors": {
                "home_score": "",
                "away_score": "",
                "status": "",
            }
        }

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _get_cache_path(self, url: str) -> Path:
        """Get cache file path for a URL."""
        # Simple hash of URL for cache filename
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"scraper_{url_hash}.html"

    def _fetch_html(self, url: str, use_cache: bool = True) -> Optional[str]:
        """Fetch HTML content from URL with caching.
        
        Args:
            url: URL to fetch
            use_cache: Whether to use cached content if available
            
        Returns:
            HTML content as string, or None if fetch failed
        """
        if not url:
            return None
            
        cache_path = self._get_cache_path(url)
        
        # Check cache first
        if use_cache and cache_path.exists():
            try:
                cache_age = time.time() - cache_path.stat().st_mtime
                if cache_age < self.meta.refresh_seconds:
                    logger.debug(f"Using cached content for {url}")
                    return cache_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"Failed to read cache for {url}: {e}")

        # Fetch from network
        if not self.allow_network:
            logger.debug(f"Network disabled, skipping fetch of {url}")
            return None

        try:
            self._rate_limit()
            headers = {"User-Agent": self.user_agent}
            
            logger.info(f"Fetching {url}")
            response = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
            response.raise_for_status()
            
            html = response.text
            
            # Cache the response
            try:
                cache_path.write_text(html, encoding="utf-8")
            except Exception as e:
                logger.warning(f"Failed to cache response for {url}: {e}")
            
            return html
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    def _extract_text(self, element, selector: str, default: str = "") -> str:
        """Safely extract text from an element using a CSS selector."""
        if not selector:
            return default
        try:
            found = element.select_one(selector)
            return found.get_text(strip=True) if found else default
        except Exception as e:
            logger.debug(f"Failed to extract text with selector '{selector}': {e}")
            return default

    def _extract_fixtures_from_html(self, html: str) -> list[FixtureRecord]:
        """Parse fixtures from HTML content.
        
        Args:
            html: HTML content to parse
            
        Returns:
            List of FixtureRecord objects
        """
        fixtures = []
        
        if not html:
            return fixtures
            
        try:
            soup = BeautifulSoup(html, "lxml")
            selectors = self.config.get("selectors", {})
            container_selector = selectors.get("fixture_container", "")
            
            if not container_selector:
                logger.warning("No fixture_container selector configured")
                return fixtures
            
            containers = soup.select(container_selector)
            logger.info(f"Found {len(containers)} fixture containers")
            
            for container in containers:
                try:
                    fixture_id = self._extract_text(container, selectors.get("fixture_id", ""), "unknown")
                    home_team = self._extract_text(container, selectors.get("home_team", ""), "TBD")
                    away_team = self._extract_text(container, selectors.get("away_team", ""), "TBD")
                    league = self._extract_text(container, selectors.get("league", ""), "unknown")
                    season = self._extract_text(container, selectors.get("season", ""), "2024")
                    venue = self._extract_text(container, selectors.get("venue", ""))
                    kickoff_str = self._extract_text(container, selectors.get("kickoff", ""))
                    
                    # Parse kickoff time
                    kickoff = parse_utc_datetime(kickoff_str, default_future=True)
                    
                    fixture = FixtureRecord(
                        fixture_id=fixture_id,
                        league=league,
                        season=season,
                        home_team=home_team,
                        away_team=away_team,
                        kickoff=kickoff,
                        venue=venue,
                        timezone="UTC",
                    )
                    fixtures.append(fixture)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse fixture container: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse HTML for fixtures: {e}")
        
        return fixtures

    def _extract_results_from_html(self, html: str) -> list[ResultRecord]:
        """Parse results from HTML content.
        
        Args:
            html: HTML content to parse
            
        Returns:
            List of ResultRecord objects
        """
        results = []
        
        if not html:
            return results
            
        try:
            soup = BeautifulSoup(html, "lxml")
            selectors = self.config.get("selectors", {})
            result_selectors = self.config.get("result_selectors", {})
            container_selector = selectors.get("fixture_container", "")
            
            if not container_selector:
                logger.warning("No fixture_container selector configured")
                return results
            
            containers = soup.select(container_selector)
            logger.info(f"Found {len(containers)} result containers")
            
            for container in containers:
                try:
                    fixture_id = self._extract_text(container, selectors.get("fixture_id", ""), "unknown")
                    home_team = self._extract_text(container, selectors.get("home_team", ""), "TBD")
                    away_team = self._extract_text(container, selectors.get("away_team", ""), "TBD")
                    league = self._extract_text(container, selectors.get("league", ""), "unknown")
                    season = self._extract_text(container, selectors.get("season", ""), "2024")
                    venue = self._extract_text(container, selectors.get("venue", ""))
                    kickoff_str = self._extract_text(container, selectors.get("kickoff", ""))
                    
                    home_score_str = self._extract_text(container, result_selectors.get("home_score", ""), "0")
                    away_score_str = self._extract_text(container, result_selectors.get("away_score", ""), "0")
                    status = self._extract_text(container, result_selectors.get("status", ""), "FT")
                    
                    # Parse scores
                    try:
                        home_score = int(home_score_str)
                        away_score = int(away_score_str)
                    except ValueError:
                        logger.warning(f"Invalid scores for fixture {fixture_id}: {home_score_str}-{away_score_str}")
                        continue
                    
                    # Parse kickoff time
                    kickoff = parse_utc_datetime(kickoff_str, default_future=False)
                    
                    result = ResultRecord(
                        fixture_id=fixture_id,
                        league=league,
                        season=season,
                        home_team=home_team,
                        away_team=away_team,
                        kickoff=kickoff,
                        venue=venue,
                        timezone="UTC",
                        home_score=home_score,
                        away_score=away_score,
                        status=status,
                    )
                    results.append(result)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse result container: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse HTML for results: {e}")
        
        return results

    def get_fixtures(self) -> Iterable[FixtureRecord]:
        """Scrape and yield fixtures from configured URL."""
        fixtures_url = self.config.get("fixtures_url", "")
        
        if not fixtures_url:
            logger.debug("No fixtures_url configured for web scraper")
            return []
        
        html = self._fetch_html(fixtures_url)
        if html:
            fixtures = self._extract_fixtures_from_html(html)
            logger.info(f"Scraped {len(fixtures)} fixtures from {fixtures_url}")
            return fixtures
        
        return []

    def get_results(self) -> Iterable[ResultRecord]:
        """Scrape and yield results from configured URL."""
        results_url = self.config.get("results_url", "")
        
        if not results_url:
            logger.debug("No results_url configured for web scraper")
            return []
        
        html = self._fetch_html(results_url)
        if html:
            results = self._extract_results_from_html(html)
            logger.info(f"Scraped {len(results)} results from {results_url}")
            return results
        
        return []
