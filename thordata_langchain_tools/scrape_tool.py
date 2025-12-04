from __future__ import annotations

import base64
from typing import Any, Dict, Optional, Type, Union

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

# Same import strategy as in serp_tool.py
try:
    from thordata import ThordataClient  # type: ignore
except ImportError:  # pragma: no cover
    from thordata.client import ThordataClient  # type: ignore

from .serp_tool import _build_client_from_env

# Limit the amount of HTML we pass back to the LLM to avoid huge prompts
MAX_HTML_CHARS = 10_000  # ~2–3k tokens, safe for most models


class ThordataScrapeInput(BaseModel):
    """Input schema for ThordataScrapeTool."""

    url: str = Field(
        ...,
        description="The absolute URL of the page to scrape.",
    )
    js_render: bool = Field(
        default=False,
        description="Whether to enable JavaScript rendering (headless browser).",
    )
    output_format: str = Field(
        default="HTML",
        description=(
            "Output format requested from the Universal API. "
            "Supported values in the SDK are 'HTML' and 'PNG'. "
            "For 'PNG' this tool returns a base64-encoded PNG string."
        ),
    )
    country: Optional[str] = Field(
        default=None,
        description="Optional two-letter country code used for geo-targeting, e.g. 'us'.",
    )
    block_resources: bool = Field(
        default=False,
        description=(
            "If true, block heavy resources (images, CSS, etc.) in order "
            "to speed up page loading. Only applicable for HTML output."
        ),
    )


class ThordataScrapeTool(BaseTool):
    """
    LangChain Tool: Universal scraping via Thordata.

    This tool calls `ThordataClient.universal_scrape` to unlock and fetch
    a single web page behind anti-bot protections.

    The tool returns either:
      * A (possibly truncated) HTML string (for output_format='HTML'), or
      * A JSON dict with a base64-encoded PNG (for output_format='PNG').

    Example:
        from thordata_langchain_tools import ThordataScrapeTool

        tool = ThordataScrapeTool()
        html = tool.invoke({"url": "https://www.thordata.com"})
    """

    name: str = "thordata_universal_scrape"
    description: str = (
        "Use Thordata Universal Scraper to fetch the content of a single web page. "
        "Supports optional JavaScript rendering and basic geo-targeting. "
        "Returns HTML (truncated to a safe length) or a base64-encoded PNG screenshot."
    )
    args_schema: Type[BaseModel] = ThordataScrapeInput

    client: ThordataClient  # initialized in __init__

    def __init__(self, client: Optional[ThordataClient] = None, **kwargs: Any) -> None:
        if client is None:
            client = _build_client_from_env()
        super().__init__(client=client, **kwargs)

    def _run(
        self,
        url: str,
        js_render: bool = False,
        output_format: str = "HTML",
        country: Optional[str] = None,
        block_resources: bool = False,
    ) -> Union[str, Dict[str, str]]:
        """Synchronous tool call."""
        result = self.client.universal_scrape(
            url=url,
            js_render=js_render,
            output_format=output_format,
            country=country,
            block_resources=block_resources,
        )

        # PNG / binary: return a base64-encoded payload in a small JSON wrapper.
        if isinstance(result, bytes):
            encoded = base64.b64encode(result).decode("utf-8")
            return {
                "output_format": "PNG",
                "data_base64": encoded,
            }

        # HTML / text: truncate to avoid huge LLM inputs.
        if isinstance(result, str):
            if len(result) > MAX_HTML_CHARS:
                truncated = result[:MAX_HTML_CHARS]
                truncated += (
                    "\n\n[Truncated to first "
                    f"{MAX_HTML_CHARS} characters by ThordataScrapeTool]"
                )
                return truncated
            return result

        # Fallback: convert unexpected types to string.
        return str(result)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Async interface is not implemented in this initial version."""
        raise NotImplementedError("ThordataScrapeTool does not support async yet.")