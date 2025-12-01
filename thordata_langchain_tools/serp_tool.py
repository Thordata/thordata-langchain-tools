from __future__ import annotations

import os
from typing import Any, Dict, Optional, Type

from dotenv import load_dotenv
from langchain_core.tools import BaseTool

from pydantic import BaseModel, Field

# Try top-level imports first (future SDK versions),
# fall back to module imports (current SDK layout).
try:
    from thordata import ThordataClient, Engine  # type: ignore
except ImportError:  # pragma: no cover - defensive fallback
    from thordata.client import ThordataClient  # type: ignore
    from thordata.enums import Engine  # type: ignore

# Load environment variables from a local .env file (for local development)
load_dotenv()


def _build_client_from_env() -> ThordataClient:
    """
    Construct a ThordataClient instance from environment variables.

    Expected environment variables:
        THORDATA_SCRAPER_TOKEN (required)
        THORDATA_PUBLIC_TOKEN  (optional, for async task APIs)
        THORDATA_PUBLIC_KEY    (optional, for async task APIs)
    """
    scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
    public_token = os.getenv("THORDATA_PUBLIC_TOKEN", "")
    public_key = os.getenv("THORDATA_PUBLIC_KEY", "")

    if not scraper_token:
        raise RuntimeError(
            "THORDATA_SCRAPER_TOKEN is missing. "
            "Set it in your environment or in a local .env file."
        )

    return ThordataClient(
        scraper_token=scraper_token,
        public_token=public_token,
        public_key=public_key,
    )


class ThordataSerpInput(BaseModel):
    """Input schema for ThordataSerpTool."""

    query: str = Field(
        ...,
        description="Search query string for the search engine.",
    )
    engine: str = Field(
        default="google",
        description=(
            "Search engine to use, e.g. 'google', 'bing', 'yandex', "
            "'duckduckgo', 'google_news', etc."
        ),
    )
    num: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of organic results to fetch (1–50).",
    )
    location: Optional[str] = Field(
        default=None,
        description="Optional location string (e.g. 'United States', 'London').",
    )
    search_type: Optional[str] = Field(
        default=None,
        description=(
            "Optional search vertical, passed through as the 'type' parameter. "
            "Examples: 'news', 'shopping', 'images', 'videos'."
        ),
    )


class ThordataSerpTool(BaseTool):
    """
    LangChain Tool: Web search via Thordata SERP API.

    This tool queries commercial search engines (Google/Bing/Yandex/DDG, etc.)
    through Thordata's SERP API and returns the raw JSON response.

    Example:
        from thordata_langchain_tools import ThordataSerpTool

        tool = ThordataSerpTool()
        result = tool.invoke(
            {
                "query": "Thordata proxies",
                "engine": "google",
                "num": 3,
            }
        )
    """

    name: str = "thordata_serp_search"
    description: str = (
        "Use Thordata SERP API to search the web (Google/Bing/Yandex/DuckDuckGo). "
        "Returns the full JSON SERP response, including organic results, ads, "
        "and metadata. Useful for real-time web search."
    )
    args_schema: Type[BaseModel] = ThordataSerpInput

    client: ThordataClient  # initialized in __init__

    def __init__(self, client: Optional[ThordataClient] = None, **kwargs: Any) -> None:
        if client is None:
            client = _build_client_from_env()
        super().__init__(client=client, **kwargs)

    def _run(
        self,
        query: str,
        engine: str = "google",
        num: int = 5,
        location: Optional[str] = None,
        search_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synchronous tool call."""
        engine_key = engine.lower()

        # Map common engine strings to the Engine enum.
        engine_enum: Any = {
            "google": Engine.GOOGLE,
            "bing": Engine.BING,
            "yandex": Engine.YANDEX,
            "duckduckgo": Engine.DUCKDUCKGO,
        }.get(engine_key, engine_key)  # fall back to plain string, e.g. "google_news"

        extra_params: Dict[str, Any] = {}
        if location:
            extra_params["location"] = location
        if search_type:
            extra_params["type"] = search_type

        results = self.client.serp_search(
            query=query,
            engine=engine_enum,
            num=num,
            **extra_params,
        )
        # Return the raw JSON dict; the LLM can decide which fields to use.
        return results

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Async interface is not implemented in this initial version."""
        raise NotImplementedError("ThordataSerpTool does not support async yet.")