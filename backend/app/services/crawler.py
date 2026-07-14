import time
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings


@dataclass
class FetchResult:
    url: str
    access_status: str
    text: str = ""
    title: str = ""
    error: str | None = None


class CompliantCrawler:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._last_fetch_by_domain: dict[str, float] = {}
        self._robots_cache: dict[str, RobotFileParser] = {}

    def _robots_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return False
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = self._robots_cache.get(robots_url)
        if not parser:
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception:
                return True
            self._robots_cache[robots_url] = parser
        return parser.can_fetch(self.settings.crawl_user_agent, url)

    def fetch(self, url: str) -> FetchResult:
        parsed = urlparse(url)
        domain = parsed.netloc
        if not self._robots_allowed(url):
            return FetchResult(url=url, access_status="blocked_by_robots", error="robots.txt disallows this URL")

        last_fetch = self._last_fetch_by_domain.get(domain, 0)
        wait = self.settings.crawl_min_domain_delay_seconds - (time.monotonic() - last_fetch)
        if wait > 0:
            time.sleep(wait)

        try:
            with httpx.Client(
                timeout=self.settings.crawl_timeout_seconds,
                headers={"User-Agent": self.settings.crawl_user_agent},
                follow_redirects=True,
            ) as client:
                response = client.get(url)
            self._last_fetch_by_domain[domain] = time.monotonic()
            if response.status_code in {401, 403}:
                return FetchResult(url=url, access_status="blocked_login_or_forbidden", error=f"HTTP {response.status_code}")
            response.raise_for_status()
            text = response.text[:250_000]
            lowered = text.lower()
            if any(signal in lowered for signal in ["captcha", "sign in to continue", "subscribe to continue", "paywall"]):
                return FetchResult(url=url, access_status="blocked_access_control", error="captcha/login/paywall signal detected")
            soup = BeautifulSoup(text, "html.parser")
            title = soup.title.get_text(" ", strip=True) if soup.title else url
            page_text = soup.get_text(" ", strip=True)
            return FetchResult(url=url, access_status="fetched", title=title, text=page_text[:50_000])
        except Exception as exc:
            return FetchResult(url=url, access_status="fetch_failed", error=str(exc))
