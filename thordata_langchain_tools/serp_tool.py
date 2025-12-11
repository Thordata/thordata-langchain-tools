"""
ThordataSerpTool - LangChain tool for SERP API.

Searches Google, Bing, Yandex, DuckDuckGo, and more via Thordata.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Type

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import ThordataClient


class SerpSearchInput(BaseModel):
    """Input schema for SERP search."""
    
    query: str = Field(
        description="The search query/keywords to search for."
    )
    engine: str = Field(
        default="google",
        description="Search engine: google, bing, yandex, duckduckgo, baidu."
    )
    num: int = Field(
        default=10,
        description="Number of results to return (1-100)."
    )
    country: Optional[str] = Field(
        default=None,
        description="Country code for localized results (e.g., 'us', 'gb')."
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code for results (e.g., 'en', 'es')."
    )
    search_type: Optional[str] = Field(
        default=None,
        description="Type of search: images, news, shopping, videos."
    )


class ThordataSerpTool(BaseTool):
    """
    LangChain tool for searching the web via Thordata SERP API.
    
    This tool queries search engines (Google, Bing, etc.) and returns
    structured results including organic listings, ads, and more.
    
    Example:
        >>> tool = ThordataSerpTool()
        >>> results = tool.invoke({
        ...     "query": "best python libraries",
        ...     "engine": "google",
        ...     "num": 5
        ... })
        >>> for item in results.get("organic", []):
        ...     print(item["title"], item["link"])
    """
    
    name: str = "thordata_serp_search"
    description: str = (
        "Search the web using Thordata SERP API. "
        "Supports Google, Bing, Yandex, DuckDuckGo, and Baidu. "
        "Returns structured search results including titles, links, and snippets. "
        "Use this when you need to find information on the web."
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
                public_token=os.getenv("THORDATA_PUBLIC_TOKEN", ""),
                public_key=os.getenv("THORDATA_PUBLIC_KEY", ""),
            )
        return self._client
    
    def _run(
        self,
        query: str,
        engine: str = "google",
        num: int = 10,
        country: Optional[str] = None,
        language: Optional[str] = None,
        search_type: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Execute the SERP search."""
        client = self._get_client()
        
        try:
            results = client.serp_search(
                query=query,
                engine=engine,
                num=num,
                country=country,
                language=language,
                search_type=search_type,
            )
            return results
        except Exception as e:
            return {
                "error": str(e),
                "query": query,
                "engine": engine,
            }