"""
ThordataScrapeTool - LangChain tool for web scraping.

Fetches and returns HTML content from URLs via Thordata Universal API.
"""

from __future__ import annotations

import os
from typing import Optional, Type

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import ThordataClient


class ScrapeInput(BaseModel):
    """Input schema for web scraping."""

    url: str = Field(description="The URL of the webpage to scrape.")
    js_render: bool = Field(
        default=False,
        description="Whether to render JavaScript (uses headless browser).",
    )
    max_length: int = Field(
        default=50000,
        description="Maximum characters to return (to control token usage).",
    )


class ThordataScrapeTool(BaseTool):
    """
    LangChain tool for scraping web pages via Thordata Universal API.

    This tool fetches HTML content from any URL, automatically bypassing
    anti-bot protections like Cloudflare and CAPTCHAs.

    Example:
        >>> tool = ThordataScrapeTool()
        >>> html = tool.invoke({
        ...     "url": "https://example.com",
        ...     "js_render": True
        ... })
        >>> print(html[:500])
    """

    name: str = "thordata_scrape_webpage"
    description: str = (
        "Scrape a webpage and return its HTML content. "
        "Automatically bypasses anti-bot protections. "
        "Set js_render=True for JavaScript-heavy pages. "
        "Use this when you need to read the content of a specific webpage."
    )
    args_schema: Type[BaseModel] = ScrapeInput

    # Client instance
    _client: Optional[ThordataClient] = None

    def _get_client(self) -> ThordataClient:
        """Get or create the Thordata client."""
        if self._client is None:
            scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
            if not scraper_token:
                raise ValueError(
                    "THORDATA_SCRAPER_TOKEN environment variable is required."
                )

            self._client = ThordataClient(
                scraper_token=scraper_token,
                public_token=os.getenv("THORDATA_PUBLIC_TOKEN", ""),
                public_key=os.getenv("THORDATA_PUBLIC_KEY", ""),
            )
        return self._client

    def _run(
        self,
        url: str,
        js_render: bool = False,
        max_length: int = 50000,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Scrape the webpage and return HTML."""
        client = self._get_client()

        try:
            result = client.universal_scrape(
                url=url,
                js_render=js_render,
                output_format="html",
            )

            # Convert to string if needed
            if isinstance(result, bytes):
                result = result.decode("utf-8", errors="ignore")

            # Truncate to max_length to control token usage
            if len(result) > max_length:
                result = result[:max_length] + "\n\n[Content truncated...]"

            return result

        except Exception as e:
            return f"Error scraping {url}: {str(e)}"
