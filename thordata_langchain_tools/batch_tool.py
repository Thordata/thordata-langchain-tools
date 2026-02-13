"""
ThordataBatchTool - LangChain tool for batch operations.

Supports batch scraping and batch SERP searches for processing multiple URLs/queries efficiently.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import AsyncThordataClient, Engine, SerpRequest


class BatchScrapeInput(BaseModel):
    """Input schema for batch scraping."""

    urls: list[str] = Field(description="List of URLs to scrape.")
    js_render: bool = Field(
        default=True,
        description="Whether to render JavaScript for all requests.",
    )
    output_format: str = Field(
        default="html",
        description="Output format: 'html' or 'png'.",
    )
    concurrency: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of concurrent requests (1-20).",
    )
    country: Optional[str] = Field(
        default=None,
        description="Country code for geo-targeted requests.",
    )


class BatchSerpInput(BaseModel):
    """Input schema for batch SERP search."""

    queries: list[str] = Field(description="List of search queries.")
    engine: str = Field(
        default="google",
        description="Search engine: google, bing, yandex, etc.",
    )
    num: int = Field(default=10, description="Number of results per query.")
    concurrency: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of concurrent requests (1-20).",
    )
    output_format: str = Field(
        default="json",
        description="Output format: 'json', 'html', or 'light_json'.",
    )


class ThordataBatchScrapeTool(BaseTool):
    """
    LangChain tool for batch web scraping.

    Scrapes multiple URLs concurrently for efficient processing.
    Uses async operations internally for better performance.

    Example:
        >>> tool = ThordataBatchScrapeTool()
        >>> results = tool.invoke({
        ...     "urls": ["https://example.com", "https://example.org"],
        ...     "js_render": True,
        ...     "concurrency": 3
        ... })
    """

    name: str = "thordata_batch_scrape"
    description: str = (
        "Scrape multiple webpages concurrently. "
        "Efficiently processes multiple URLs in parallel. "
        "Use this when you need to scrape multiple pages at once."
    )
    args_schema: Type[BaseModel] = BatchScrapeInput

    _client: Optional[AsyncThordataClient] = None

    def _get_client(self) -> AsyncThordataClient:
        """Get or create the async Thordata client."""
        if self._client is None:
            scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
            if not scraper_token:
                raise ValueError(
                    "THORDATA_SCRAPER_TOKEN environment variable is required."
                )

            self._client = AsyncThordataClient(
                scraper_token=scraper_token,
                public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
                public_key=os.getenv("THORDATA_PUBLIC_KEY"),
            )
        return self._client

    def _run(
        self,
        urls: list[str],
        js_render: bool = True,
        output_format: str = "html",
        concurrency: int = 5,
        country: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict[str, Any]:
        """Execute batch scraping."""

        async def _batch_scrape() -> dict[str, Any]:
            client = self._get_client()
            # Ensure client is initialized
            async with client:
                sem = asyncio.Semaphore(concurrency)
                results = []

                async def _one(i: int, url: str) -> dict[str, Any]:
                    async with sem:
                        try:
                            data = await client.universal.scrape_async(
                                url=url,
                                js_render=js_render,
                                country=country,
                                output_format=output_format,
                            )
                            return {
                                "index": i,
                                "url": url,
                                "ok": True,
                                "output": (
                                    str(data)
                                    if not isinstance(data, (dict, bytes))
                                    else data
                                ),
                            }
                        except Exception as e:
                            return {
                                "index": i,
                                "url": url,
                                "ok": False,
                                "error": str(e),
                            }

                tasks = [_one(i, url) for i, url in enumerate(urls)]
                results = await asyncio.gather(*tasks)
                return {"results": results, "total": len(urls)}

        # Run async function
        try:
            return asyncio.run(_batch_scrape())
        except Exception as e:
            return {
                "error": str(e),
                "results": [],
                "total": 0,
            }


class ThordataBatchSerpTool(BaseTool):
    """
    LangChain tool for batch SERP searches.

    Searches multiple queries concurrently for efficient processing.
    Uses async operations internally for better performance.

    Example:
        >>> tool = ThordataBatchSerpTool()
        >>> results = tool.invoke({
        ...     "queries": ["python", "javascript", "rust"],
        ...     "engine": "google",
        ...     "concurrency": 3
        ... })
    """

    name: str = "thordata_batch_serp"
    description: str = (
        "Search multiple queries concurrently using SERP API. "
        "Efficiently processes multiple search queries in parallel. "
        "Use this when you need to search multiple topics at once."
    )
    args_schema: Type[BaseModel] = BatchSerpInput

    _client: Optional[AsyncThordataClient] = None

    def _get_client(self) -> AsyncThordataClient:
        """Get or create the async Thordata client."""
        if self._client is None:
            scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
            if not scraper_token:
                raise ValueError(
                    "THORDATA_SCRAPER_TOKEN environment variable is required."
                )

            self._client = AsyncThordataClient(
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
        else:
            try:
                return Engine[engine.upper()]
            except (KeyError, AttributeError):
                return Engine.GOOGLE

    def _run(
        self,
        queries: list[str],
        engine: str = "google",
        num: int = 10,
        concurrency: int = 5,
        output_format: str = "json",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict[str, Any]:
        """Execute batch SERP search."""

        async def _batch_serp() -> dict[str, Any]:
            client = self._get_client()
            # Ensure client is initialized
            async with client:
                sem = asyncio.Semaphore(concurrency)
                engine_enum = self._normalize_engine(engine)
                results = []

                async def _one(i: int, query: str) -> dict[str, Any]:
                    async with sem:
                        try:
                            request = SerpRequest(
                                query=query,
                                engine=engine_enum,
                                num=num,
                                output_format=output_format,
                            )
                            data = await client.serp_search_advanced(request)
                            return {
                                "index": i,
                                "query": query,
                                "ok": True,
                                "output": data,
                            }
                        except Exception as e:
                            return {
                                "index": i,
                                "query": query,
                                "ok": False,
                                "error": str(e),
                            }

                tasks = [_one(i, query) for i, query in enumerate(queries)]
                results = await asyncio.gather(*tasks)
                return {"results": results, "total": len(queries)}

        # Run async function
        try:
            return asyncio.run(_batch_serp())
        except Exception as e:
            return {
                "error": str(e),
                "results": [],
                "total": 0,
            }
