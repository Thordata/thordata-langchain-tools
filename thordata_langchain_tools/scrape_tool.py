"""
ThordataScrapeTool - LangChain tool for Universal Scraping API.

Fetches and returns HTML content from URLs via Thordata Universal API.
Uses the latest SDK API with namespace support.
"""

from __future__ import annotations

import base64
import os
from typing import Any, Optional, Type, Union

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import ThordataClient


class ScrapeInput(BaseModel):
    """Input schema for web scraping."""

    url: str = Field(description="The URL of the webpage to scrape.")
    js_render: bool = Field(
        default=True,
        description="Whether to render JavaScript (uses headless browser). Recommended for modern sites.",
    )
    output_format: str = Field(
        default="html",
        description="Output format: 'html' (HTML content), 'png' (screenshot), or comma-separated like 'png,html'.",
    )
    country: Optional[str] = Field(
        default=None,
        description="Country code for geo-targeted request (e.g., 'us', 'gb', 'jp').",
    )
    wait_for: Optional[str] = Field(
        default=None,
        description="CSS selector or text to wait for before returning content.",
    )
    wait_ms: Optional[int] = Field(
        default=None, description="Wait time in milliseconds before capture."
    )
    block_resources: Optional[str] = Field(
        default=None,
        description="Comma-separated resource types to block (e.g., 'image,css').",
    )
    follow_redirect: Optional[bool] = Field(
        default=None, description="Control redirect following behavior."
    )
    clean_content: Optional[bool] = Field(
        default=None, description="Clean JavaScript/CSS from responses."
    )
    headers: Optional[list[str]] = Field(
        default=None,
        description="Custom request headers as list of 'Key: Value' strings.",
    )
    cookies: Optional[list[str]] = Field(
        default=None, description="Custom cookies as list of 'name=value' strings."
    )
    header: Optional[bool] = Field(
        default=None, description="Include response headers in output."
    )
    max_length: int = Field(
        default=50000,
        description="Maximum characters to return for HTML (to control token usage).",
    )


class ThordataScrapeTool(BaseTool):
    """
    LangChain tool for scraping web pages via Thordata Universal API.

    This tool fetches HTML content from any URL, automatically bypassing
    anti-bot protections like Cloudflare and CAPTCHAs.
    Uses the latest SDK API with namespace support.

    Example:
        >>> tool = ThordataScrapeTool()
        >>> html = tool.invoke({
        ...     "url": "https://example.com",
        ...     "js_render": True,
        ...     "country": "us"
        ... })
        >>> print(html[:500])
    """

    name: str = "thordata_scrape_webpage"
    description: str = (
        "Scrape a webpage and return its HTML content or screenshot. "
        "Automatically bypasses anti-bot protections like Cloudflare and CAPTCHAs. "
        "Set js_render=True for JavaScript-heavy pages. "
        "Supports geo-targeting, custom headers/cookies, and multiple output formats. "
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
                    "THORDATA_SCRAPER_TOKEN environment variable is required. "
                    "Get your token from the Thordata Dashboard."
                )

            self._client = ThordataClient(
                scraper_token=scraper_token,
                public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
                public_key=os.getenv("THORDATA_PUBLIC_KEY"),
            )
        return self._client

    def _run(
        self,
        url: str,
        js_render: bool = True,
        output_format: str = "html",
        country: Optional[str] = None,
        wait_for: Optional[str] = None,
        wait_ms: Optional[int] = None,
        block_resources: Optional[str] = None,
        follow_redirect: Optional[bool] = None,
        clean_content: Optional[bool] = None,
        headers: Optional[list[str]] = None,
        cookies: Optional[list[str]] = None,
        header: Optional[bool] = None,
        max_length: int = 50000,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, dict[str, Any]]:
        """Scrape the webpage and return HTML or screenshot."""
        client = self._get_client()

        try:
            # Build kwargs for additional parameters
            kwargs: dict[str, Any] = {}
            if follow_redirect is not None:
                kwargs["follow_redirect"] = follow_redirect
            if clean_content is not None:
                kwargs["clean_content"] = clean_content
            if headers is not None:
                kwargs["headers"] = headers
            if cookies is not None:
                kwargs["cookies"] = cookies
            if header is not None:
                kwargs["header"] = header

            # Use the new namespace API
            wait_time = int(wait_ms) if wait_ms is not None else None
            data = client.universal.scrape(
                url=url,
                js_render=js_render,
                country=country,
                wait_for=wait_for,
                wait_time=wait_time,
                output_format=output_format,
                block_resources=block_resources,
                **kwargs,
            )

            # Handle multiple output formats (e.g., "png,html")
            if isinstance(data, dict) and len(data) > 1:
                result: dict[str, Any] = {}
                for fmt, content in data.items():
                    if fmt == "png" and isinstance(content, (bytes, bytearray)):
                        result["png_base64"] = base64.b64encode(content).decode("utf-8")
                        result["png_size"] = len(content)
                    elif fmt == "html":
                        html_str = (
                            str(content) if not isinstance(content, str) else content
                        )
                        # Truncate HTML if needed
                        if len(html_str) > max_length:
                            html_str = (
                                html_str[:max_length] + "\n\n[Content truncated...]"
                            )
                        result["html"] = html_str
                    else:
                        result[fmt] = (
                            str(content)
                            if not isinstance(content, (str, bytes))
                            else content
                        )
                return result

            # Single format output
            if output_format.lower() == "png" or isinstance(data, (bytes, bytearray)):
                if isinstance(data, (bytes, bytearray)):
                    png_base64 = base64.b64encode(data).decode("utf-8")
                    return {
                        "png_base64": png_base64,
                        "size": len(data),
                        "format": "png",
                    }
                return {"png_base64": str(data), "format": "png"}

            # HTML output
            html = str(data) if not isinstance(data, str) else data
            # Truncate to max_length to control token usage
            if len(html) > max_length:
                html = html[:max_length] + "\n\n[Content truncated...]"
            return html

        except Exception as e:
            return f"Error scraping {url}: {str(e)}"
