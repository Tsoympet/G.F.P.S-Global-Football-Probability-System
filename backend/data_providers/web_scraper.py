from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Iterable, Optional, Callable, Dict, List, Any
from collections import Counter

import httpx
from bs4 import BeautifulSoup

from .base import FixtureRecord, Provider, ProviderMetadata, ProviderTier, ResultRecord
from .utils import parse_utc_datetime

logger = logging.getLogger(__name__)

# Playwright imports - optional dependency
try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.debug("Playwright not available. JavaScript rendering disabled.")


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
        
        # JavaScript rendering support
        self.use_js_rendering = self.config.get("use_js_rendering", False) and PLAYWRIGHT_AVAILABLE
        self._playwright = None
        self._browser = None
        
        # HTML structure tracking for change detection
        self._html_structure_cache = {}
        
        # Captcha handler hook
        self.captcha_handler: Optional[Callable[[str], str]] = None

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load scraper configuration from file or return default."""
        # Check for config_path from environment if not provided
        if config_path is None:
            env_path = os.getenv("SCRAPER_CONFIG_PATH")
            if env_path:
                config_path = Path(env_path)
        
        if config_path and config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        
        # Default configuration - empty, users must provide their own
        return {
            "fixtures_url": "",
            "results_url": "",
            "use_js_rendering": False,
            "js_wait_time": 2000,  # milliseconds to wait for JS to load
            "pagination": {
                "enabled": False,
                "type": "click",  # "click", "url_pattern", or "scroll"
                "next_button_selector": "",
                "url_pattern": "",  # e.g., "?page={page}"
                "max_pages": 10,
            },
            "proxy": {
                "enabled": False,
                "server": "",
                "username": "",
                "password": "",
            },
            "captcha_detection": {
                "enabled": False,
                "indicators": ["captcha", "recaptcha", "hcaptcha"],
            },
            "structure_monitoring": {
                "enabled": False,
                "similarity_threshold": 0.8,
            },
            "auto_selector_learning": {
                "enabled": False,
            },
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
        # Use SHA-256 for better security and collision resistance
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        return self.cache_dir / f"scraper_{url_hash}.html"

    def _init_browser(self) -> None:
        """Initialize Playwright browser for JavaScript rendering."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available. Cannot initialize browser.")
            return
        
        if self._browser is None:
            try:
                self._playwright = sync_playwright().start()
                
                # Configure proxy if enabled
                proxy_config = None
                if self.config.get("proxy", {}).get("enabled", False):
                    proxy = self.config["proxy"]
                    proxy_config = {
                        "server": proxy.get("server", ""),
                    }
                    if proxy.get("username"):
                        proxy_config["username"] = proxy["username"]
                    if proxy.get("password"):
                        proxy_config["password"] = proxy["password"]
                
                # Launch browser with configuration
                self._browser = self._playwright.chromium.launch(
                    headless=True,
                    proxy=proxy_config,
                )
                logger.info("Browser initialized for JavaScript rendering")
            except Exception as e:
                logger.error(f"Failed to initialize browser: {e}")
                self._browser = None

    def _cleanup_browser(self) -> None:
        """Clean up Playwright browser resources."""
        if self._browser:
            try:
                self._browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self._browser = None
        
        if self._playwright:
            try:
                self._playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
            finally:
                self._playwright = None

    def _detect_captcha(self, html: str) -> bool:
        """Detect if page contains a captcha challenge.
        
        Args:
            html: HTML content to check
            
        Returns:
            True if captcha detected, False otherwise
        """
        if not self.config.get("captcha_detection", {}).get("enabled", False):
            return False
        
        indicators = self.config.get("captcha_detection", {}).get("indicators", [])
        html_lower = html.lower()
        
        for indicator in indicators:
            if indicator.lower() in html_lower:
                logger.warning(f"Captcha detected: '{indicator}' found in HTML")
                return True
        
        return False

    def _handle_captcha(self, url: str, html: str) -> Optional[str]:
        """Handle captcha challenge if handler is configured.
        
        Args:
            url: URL that triggered captcha
            html: HTML content with captcha
            
        Returns:
            HTML content after captcha solved, or None if failed
        """
        if self.captcha_handler is None:
            logger.error(f"Captcha detected at {url} but no handler configured")
            return None
        
        try:
            logger.info(f"Attempting to solve captcha for {url}")
            return self.captcha_handler(url)
        except Exception as e:
            logger.error(f"Captcha handler failed: {e}")
            return None

    def _compute_html_structure_signature(self, html: str) -> Dict[str, Any]:
        """Compute a signature of the HTML structure for change detection.
        
        Args:
            html: HTML content to analyze
            
        Returns:
            Dictionary with structure metrics
        """
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Count tag types
            tag_counts = Counter(tag.name for tag in soup.find_all())
            
            # Extract class distribution
            class_counts = Counter()
            for tag in soup.find_all():
                if tag.get('class'):
                    for cls in tag.get('class', []):
                        class_counts[cls] += 1
            
            return {
                "tag_counts": dict(tag_counts.most_common(20)),
                "class_counts": dict(class_counts.most_common(20)),
                "total_tags": len(soup.find_all()),
            }
        except Exception as e:
            logger.warning(f"Failed to compute HTML structure signature: {e}")
            return {}

    def _detect_structure_change(self, url: str, html: str) -> bool:
        """Detect if HTML structure has significantly changed.
        
        Args:
            url: URL being scraped
            html: Current HTML content
            
        Returns:
            True if structure changed significantly, False otherwise
        """
        if not self.config.get("structure_monitoring", {}).get("enabled", False):
            return False
        
        current_sig = self._compute_html_structure_signature(html)
        if not current_sig:
            return False
        
        # Get cached signature
        cache_key = hashlib.sha256(url.encode()).hexdigest()
        cached_sig = self._html_structure_cache.get(cache_key)
        
        if cached_sig is None:
            # First time seeing this URL, cache it
            self._html_structure_cache[cache_key] = current_sig
            return False
        
        # Compare signatures
        threshold = self.config.get("structure_monitoring", {}).get("similarity_threshold", 0.8)
        
        # Simple similarity check based on tag counts
        cached_tags = set(cached_sig.get("tag_counts", {}).keys())
        current_tags = set(current_sig.get("tag_counts", {}).keys())
        
        if not cached_tags or not current_tags:
            return False
        
        intersection = cached_tags.intersection(current_tags)
        union = cached_tags.union(current_tags)
        similarity = len(intersection) / len(union) if union else 1.0
        
        if similarity < threshold:
            logger.warning(
                f"HTML structure change detected for {url}: "
                f"similarity={similarity:.2f}, threshold={threshold}"
            )
            # Update cache with new structure
            self._html_structure_cache[cache_key] = current_sig
            return True
        
        return False

    def _learn_selectors(self, html: str) -> Dict[str, str]:
        """Automatically learn potential selectors from HTML.
        
        This is a simple heuristic-based approach that suggests selectors
        based on common patterns in football data websites.
        
        Args:
            html: HTML content to analyze
            
        Returns:
            Dictionary of suggested selectors
        """
        if not self.config.get("auto_selector_learning", {}).get("enabled", False):
            return {}
        
        try:
            soup = BeautifulSoup(html, "lxml")
            suggestions = {}
            
            # Look for common container patterns
            container_candidates = []
            for pattern in [".match", ".fixture", ".game", "[data-match]", "tr.match-row"]:
                matches = soup.select(pattern)
                if matches:
                    container_candidates.append((pattern, len(matches)))
            
            if container_candidates:
                # Suggest the pattern that matches multiple items
                container_candidates.sort(key=lambda x: x[1], reverse=True)
                suggestions["fixture_container"] = container_candidates[0][0]
                logger.info(f"Suggested container selector: {suggestions['fixture_container']}")
            
            # Look for team name patterns
            for pattern in [".team", ".home", ".away", "[data-team]"]:
                if soup.select(pattern):
                    logger.info(f"Found potential team selector: {pattern}")
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Failed to learn selectors: {e}")
            return {}

    def _fetch_html_with_js(self, url: str) -> Optional[str]:
        """Fetch HTML content using Playwright for JavaScript rendering.
        
        Args:
            url: URL to fetch
            
        Returns:
            Rendered HTML content as string, or None if fetch failed
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available, falling back to basic fetch")
            return None
        
        try:
            # Initialize browser if needed
            if self._browser is None:
                self._init_browser()
            
            if self._browser is None:
                return None
            
            # Create a new page
            context = self._browser.new_context(user_agent=self.user_agent)
            page = context.new_page()
            
            try:
                # Navigate to URL
                logger.info(f"Fetching {url} with JavaScript rendering")
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Wait for JavaScript to execute
                wait_time = self.config.get("js_wait_time", 2000)
                page.wait_for_timeout(wait_time)
                
                # Get rendered HTML
                html = page.content()
                
                return html
                
            finally:
                page.close()
                context.close()
                
        except Exception as e:
            logger.error(f"Error fetching with JavaScript rendering: {e}")
            return None

    def _fetch_paginated_content(self, base_url: str, use_js: bool = False) -> List[str]:
        """Fetch content from multiple pages with pagination support.
        
        Args:
            base_url: Base URL to start pagination from
            use_js: Whether to use JavaScript rendering
            
        Returns:
            List of HTML content from all pages
        """
        pagination_config = self.config.get("pagination", {})
        if not pagination_config.get("enabled", False):
            # No pagination, return single page
            html = self._fetch_html_single_page(base_url, use_js)
            return [html] if html else []
        
        pages_html = []
        max_pages = pagination_config.get("max_pages", 10)
        pagination_type = pagination_config.get("type", "click")
        
        if pagination_type == "url_pattern":
            # URL-based pagination
            url_pattern = pagination_config.get("url_pattern", "")
            if not url_pattern:
                logger.warning("URL pattern pagination enabled but no pattern provided")
                return pages_html
            
            for page_num in range(1, max_pages + 1):
                url = base_url + url_pattern.format(page=page_num)
                html = self._fetch_html_single_page(url, use_js)
                
                if html:
                    pages_html.append(html)
                    # Check if this looks like an empty page
                    if len(html.strip()) < 100:
                        logger.info(f"Page {page_num} appears empty, stopping pagination")
                        break
                else:
                    logger.info(f"Failed to fetch page {page_num}, stopping pagination")
                    break
                    
        elif pagination_type == "click" and use_js:
            # Click-based pagination (requires JavaScript)
            pages_html.extend(self._fetch_with_click_pagination(base_url))
            
        elif pagination_type == "scroll" and use_js:
            # Infinite scroll pagination (requires JavaScript)
            html = self._fetch_with_scroll_pagination(base_url)
            if html:
                pages_html.append(html)
        else:
            logger.warning(f"Unsupported pagination type or JS required: {pagination_type}")
            html = self._fetch_html_single_page(base_url, use_js)
            if html:
                pages_html.append(html)
        
        return pages_html

    def _fetch_html_single_page(self, url: str, use_js: bool = False) -> Optional[str]:
        """Fetch a single page with or without JavaScript rendering.
        
        Args:
            url: URL to fetch
            use_js: Whether to use JavaScript rendering
            
        Returns:
            HTML content or None
        """
        if use_js:
            return self._fetch_html_with_js(url)
        else:
            return self._fetch_html_basic(url)

    def _fetch_html_basic(self, url: str) -> Optional[str]:
        """Fetch HTML using basic HTTP request (no JavaScript).
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None
        """
        try:
            self._rate_limit()
            headers = {"User-Agent": self.user_agent}
            
            # Configure proxy if enabled
            proxies = None
            if self.config.get("proxy", {}).get("enabled", False):
                proxy_server = self.config["proxy"].get("server", "")
                if proxy_server:
                    # httpx expects a dict mapping protocols to proxy URLs
                    proxies = {
                        "http://": proxy_server,
                        "https://": proxy_server,
                    }
            
            logger.info(f"Fetching {url}")
            response = httpx.get(
                url,
                headers=headers,
                timeout=15,
                follow_redirects=True,
                proxies=proxies,
            )
            response.raise_for_status()
            
            return response.text
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    def _fetch_with_click_pagination(self, url: str) -> List[str]:
        """Fetch multiple pages using click-based pagination.
        
        Args:
            url: Initial URL to start from
            
        Returns:
            List of HTML content from all pages
        """
        if not PLAYWRIGHT_AVAILABLE or self._browser is None:
            logger.warning("Browser not available for click pagination")
            return []
        
        pagination_config = self.config.get("pagination", {})
        next_button = pagination_config.get("next_button_selector", "")
        max_pages = pagination_config.get("max_pages", 10)
        
        if not next_button:
            logger.warning("Click pagination enabled but no next_button_selector provided")
            return []
        
        pages_html = []
        
        try:
            context = self._browser.new_context(user_agent=self.user_agent)
            page = context.new_page()
            
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                for page_num in range(max_pages):
                    # Wait for content to load
                    wait_time = self.config.get("js_wait_time", 2000)
                    page.wait_for_timeout(wait_time)
                    
                    # Get current page HTML
                    html = page.content()
                    pages_html.append(html)
                    
                    # Try to find and click next button
                    try:
                        next_btn = page.query_selector(next_button)
                        if next_btn and next_btn.is_visible():
                            next_btn.click()
                            page.wait_for_load_state("networkidle")
                        else:
                            logger.info(f"No more pages after page {page_num + 1}")
                            break
                    except Exception as e:
                        logger.info(f"Pagination ended at page {page_num + 1}: {e}")
                        break
                        
            finally:
                page.close()
                context.close()
                
        except Exception as e:
            logger.error(f"Error in click pagination: {e}")
        
        return pages_html

    def _fetch_with_scroll_pagination(self, url: str) -> Optional[str]:
        """Fetch content with infinite scroll pagination.
        
        Args:
            url: URL to fetch
            
        Returns:
            Complete HTML content after scrolling
        """
        if not PLAYWRIGHT_AVAILABLE or self._browser is None:
            logger.warning("Browser not available for scroll pagination")
            return None
        
        pagination_config = self.config.get("pagination", {})
        max_scrolls = pagination_config.get("max_pages", 10)  # Reuse max_pages as max_scrolls
        
        try:
            context = self._browser.new_context(user_agent=self.user_agent)
            page = context.new_page()
            
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                previous_height = 0
                for _ in range(max_scrolls):
                    # Scroll to bottom
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    
                    # Wait for new content to load
                    wait_time = self.config.get("js_wait_time", 2000)
                    page.wait_for_timeout(wait_time)
                    
                    # Check if height changed
                    current_height = page.evaluate("document.body.scrollHeight")
                    if current_height == previous_height:
                        logger.info("Reached end of infinite scroll")
                        break
                    previous_height = current_height
                
                return page.content()
                
            finally:
                page.close()
                context.close()
                
        except Exception as e:
            logger.error(f"Error in scroll pagination: {e}")
            return None

    def _fetch_html(self, url: str, use_cache: bool = True) -> Optional[str]:
        """Fetch HTML content from URL with caching and advanced features.
        
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
            # Determine if we need JavaScript rendering
            use_js = self.use_js_rendering
            
            # Check if pagination is enabled
            pagination_enabled = self.config.get("pagination", {}).get("enabled", False)
            
            if pagination_enabled:
                # Fetch multiple pages
                pages_html = self._fetch_paginated_content(url, use_js)
                if not pages_html:
                    return None
                
                # Combine all pages
                html = "\n".join(pages_html)
            else:
                # Fetch single page
                html = self._fetch_html_single_page(url, use_js)
            
            if not html:
                return None
            
            # Check for captcha
            if self._detect_captcha(html):
                html = self._handle_captcha(url, html)
                if not html:
                    return None
            
            # Detect HTML structure changes
            self._detect_structure_change(url, html)
            
            # Try to learn selectors if enabled
            if self.config.get("auto_selector_learning", {}).get("enabled", False):
                learned = self._learn_selectors(html)
                if learned:
                    logger.info(f"Learned selectors: {learned}")
            
            # Cache the response
            try:
                cache_path.write_text(html, encoding="utf-8")
            except Exception as e:
                logger.warning(f"Failed to cache response for {url}: {e}")
            
            return html
            
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

    def __del__(self):
        """Cleanup browser resources on deletion."""
        self._cleanup_browser()

    def set_captcha_handler(self, handler: Callable[[str], str]) -> None:
        """Set a custom captcha handler function.
        
        Args:
            handler: A callable that takes a URL and returns HTML after solving captcha
        """
        self.captcha_handler = handler
        logger.info("Captcha handler registered")
