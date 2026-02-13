"""
ThordataSerpTool - LangChain tool for SERP API.

Searches Google, Bing, Yandex, DuckDuckGo, and more via Thordata.
Uses the latest SDK API with namespace support.
"""

from __future__ import annotations

import os
from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import ThordataClient, Engine, SerpRequest


class SerpSearchInput(BaseModel):
    """Input schema for SERP search."""

    query: str = Field(description="The search query/keywords to search for.")
    engine: str = Field(
        default="google",
        description="Search engine: google, bing, yandex, duckduckgo, baidu.",
    )
    num: int = Field(default=10, description="Number of results to return (1-100).")
    start: int = Field(
        default=0, description="Starting position for results (pagination)."
    )
    output_format: str = Field(
        default="json",
        description="Output format: 'json' (structured), 'html' (raw HTML), 'light_json' (minimal), or 'both'.",
    )
    country: Optional[str] = Field(
        default=None,
        description="Country code for localized results (e.g., 'us', 'gb', 'jp').",
    )
    language: Optional[str] = Field(
        default=None, description="Language code for results (e.g., 'en', 'es', 'ja')."
    )
    device: Optional[str] = Field(
        default=None, description="Device type: 'desktop', 'mobile', or 'tablet'."
    )
    search_type: Optional[str] = Field(
        default=None,
        description="Type of search: 'images', 'news', 'shopping', 'videos'.",
    )
    location: Optional[str] = Field(
        default=None,
        description="Location string for local search (e.g., 'New York, NY').",
    )
    google_domain: Optional[str] = Field(
        default=None, description="Google domain (e.g., 'google.com', 'google.co.jp')."
    )
    ai_overview: bool = Field(
        default=False, description="Enable AI Overview for Google search (Google only)."
    )
    render_js: Optional[bool] = Field(
        default=None, description="Enable JavaScript rendering."
    )
    no_cache: Optional[bool] = Field(
        default=None, description="Disable cache for fresh results."
    )


class ThordataSerpTool(BaseTool):
    """
    LangChain tool for searching the web via Thordata SERP API.

    This tool queries search engines (Google, Bing, etc.) and returns
    structured results including organic listings, ads, and more.
    Uses the latest SDK API with advanced features.

    Example:
        >>> tool = ThordataSerpTool()
        >>> results = tool.invoke({
        ...     "query": "best python libraries",
        ...     "engine": "google",
        ...     "num": 5,
        ...     "ai_overview": True
        ... })
        >>> for item in results.get("organic", []):
        ...     print(item["title"], item["link"])
    """

    name: str = "thordata_serp_search"
    description: str = (
        "Search the web using Thordata SERP API. "
        "Supports Google, Bing, Yandex, DuckDuckGo, and Baidu. "
        "Returns structured search results including titles, links, snippets, and AI overviews. "
        "Use this when you need to find information on the web. "
        "Supports advanced features like geo-targeting, device-specific results, and AI overviews."
    )
    args_schema: Type[BaseModel] = SerpSearchInput

    # Client instance (initialized lazily)
    _client: Optional[ThordataClient] = None

    def _get_client(self) -> ThordataClient:
        """Get or create the Thordata client."""
        if self._client is None:
            scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
            if not scraper_token:
                raise ValueError(
                    "THORDATA_SCRAPER_TOKEN environment variable is required. "
                    "Get your token from the Thordata Dashboard."
                )

            self._client = ThordataClient(
                scraper_token=scraper_token,
                public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
                public_key=os.getenv("THORDATA_PUBLIC_KEY"),
            )
        return self._client

    def _normalize_engine(self, engine: str) -> Engine:
        """Normalize engine string to Engine enum."""
        engine_lower = engine.lower()
        if engine_lower == "google":
            return Engine.GOOGLE
        elif engine_lower == "bing":
            return Engine.BING
        elif engine_lower == "yandex":
            return Engine.YANDEX
        elif engine_lower == "duckduckgo":
            return Engine.DUCKDUCKGO
        elif engine_lower == "baidu":
            return Engine.BAIDU
        else:
            # Try to match by name (case-insensitive)
            try:
                return Engine[engine.upper()]
            except (KeyError, AttributeError):
                return Engine.GOOGLE

    def _run(
        self,
        query: str,
        engine: str = "google",
        num: int = 10,
        start: int = 0,
        output_format: str = "json",
        country: Optional[str] = None,
        language: Optional[str] = None,
        device: Optional[str] = None,
        search_type: Optional[str] = None,
        location: Optional[str] = None,
        google_domain: Optional[str] = None,
        ai_overview: bool = False,
        render_js: Optional[bool] = None,
        no_cache: Optional[bool] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict[str, Any]:
        """Execute the SERP search using the latest SDK API."""
        client = self._get_client()

        # Normalize engine
        engine_enum = self._normalize_engine(engine)

        # Validate ai_overview (only for Google)
        if ai_overview and engine_enum != Engine.GOOGLE:
            return {
                "error": "ai_overview is only supported for Google engine",
                "query": query,
                "engine": engine,
            }

        try:
            # Create SerpRequest using the new API
            request = SerpRequest(
                query=query,
                engine=engine_enum,
                num=num,
                start=start,
                output_format=output_format,
                country=country,
                language=language,
                device=device,
                render_js=render_js,
                no_cache=no_cache,
                search_type=search_type,
                google_domain=google_domain,
                location=location,
                ai_overview=ai_overview if engine_enum == Engine.GOOGLE else None,
            )

            # Use the new serp_search_advanced method
            results = client.serp_search_advanced(request)
            return results

        except Exception as e:
            return {
                "error": str(e),
                "query": query,
                "engine": engine,
            }
