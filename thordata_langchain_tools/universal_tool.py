"""
ThordataUniversalTool - LangChain tool for Universal Scraping API.

More advanced scraping with JS rendering, screenshots, and geo-targeting.
"""

from __future__ import annotations

import os
from typing import Optional, Type, Union

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import ThordataClient


class UniversalScrapeInput(BaseModel):
    """Input schema for universal scraping."""
    
    url: str = Field(
        description="The URL to scrape."
    )
    js_render: bool = Field(
        default=True,
        description="Enable JavaScript rendering (recommended for modern sites)."
    )
    output_format: str = Field(
        default="html",
        description="Output format: 'html' for content or 'png' for screenshot."
    )
    country: Optional[str] = Field(
        default=None,
        description="Country code for geo-targeted request (e.g., 'us', 'gb')."
    )
    wait_for: Optional[str] = Field(
        default=None,
        description="CSS selector to wait for before returning content."
    )


class ThordataUniversalTool(BaseTool):
    """
    LangChain tool for advanced web scraping via Thordata Universal API.
    
    Provides more control over scraping including:
    - JavaScript rendering
    - Screenshots (PNG output)
    - Geo-targeting
    - Wait for specific elements
    
    Example:
        >>> tool = ThordataUniversalTool()
        >>> html = tool.invoke({
        ...     "url": "https://example.com",
        ...     "js_render": True,
        ...     "country": "us",
        ...     "wait_for": ".main-content"
        ... })
    """
    
    name: str = "thordata_universal_scrape"
    description: str = (
        "Advanced web scraping with JavaScript rendering, geo-targeting, and more. "
        "Use this for complex pages that require JS or specific location access. "
        "Can also take screenshots by setting output_format='png'."
    )
    args_schema: Type[BaseModel] = UniversalScrapeInput
    
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
        js_render: bool = True,
        output_format: str = "html",
        country: Optional[str] = None,
        wait_for: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, bytes]:
        """Execute universal scraping."""
        client = self._get_client()
        
        try:
            result = client.universal_scrape(
                url=url,
                js_render=js_render,
                output_format=output_format,
                country=country,
                wait_for=wait_for,
            )
            
            # For HTML output, ensure it's a string
            if output_format.lower() == "html" and isinstance(result, bytes):
                return result.decode("utf-8", errors="ignore")
            
            return result
            
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"