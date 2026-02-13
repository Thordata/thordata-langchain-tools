"""
ThordataMarkdownTool - LangChain tool for converting web pages to Markdown.

Fetches HTML and converts it to clean Markdown text, optimized for LLM consumption.
"""

from __future__ import annotations

import os
from typing import Optional, Type

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import ThordataClient
from html2text import HTML2Text


class MarkdownInput(BaseModel):
    """Input schema for markdown conversion."""

    url: str = Field(description="The URL of the webpage to convert to Markdown.")
    js_render: bool = Field(
        default=True,
        description="Whether to render JavaScript (recommended for modern sites).",
    )
    wait_ms: int = Field(
        default=2000,
        description="Wait time in milliseconds before capture (for JS rendering).",
    )
    max_chars: int = Field(
        default=20000,
        description="Maximum characters to return (to control token usage).",
    )
    country: Optional[str] = Field(
        default=None,
        description="Country code for geo-targeted request (e.g., 'us', 'gb', 'jp').",
    )
    block_resources: Optional[str] = Field(
        default=None,
        description="Comma-separated resource types to block (e.g., 'image,css').",
    )
    wait_for: Optional[str] = Field(
        default=None,
        description="CSS selector or text to wait for before returning content.",
    )


class ThordataMarkdownTool(BaseTool):
    """
    LangChain tool for converting web pages to clean Markdown text.

    This tool fetches HTML from any URL, converts it to Markdown,
    and returns clean text optimized for LLM consumption.
    Automatically bypasses anti-bot protections.

    Example:
        >>> tool = ThordataMarkdownTool()
        >>> markdown = tool.invoke({
        ...     "url": "https://example.com",
        ...     "js_render": True,
        ...     "max_chars": 10000
        ... })
        >>> print(markdown)
    """

    name: str = "thordata_fetch_markdown"
    description: str = (
        "Fetch a webpage and convert it to clean Markdown text. "
        "Automatically bypasses anti-bot protections. "
        "Returns text optimized for LLM consumption. "
        "Use this when you need to extract readable text content from a webpage."
    )
    args_schema: Type[BaseModel] = MarkdownInput

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

    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to clean Markdown."""
        # Use html2text for better conversion
        h = HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # Don't wrap lines
        markdown = h.handle(html)

        # Clean up extra whitespace
        lines = markdown.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1]:  # Keep single blank lines
                cleaned_lines.append("")

        return "\n".join(cleaned_lines)

    def _run(
        self,
        url: str,
        js_render: bool = True,
        wait_ms: int = 2000,
        max_chars: int = 20000,
        country: Optional[str] = None,
        block_resources: Optional[str] = None,
        wait_for: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Fetch webpage and convert to Markdown."""
        client = self._get_client()

        try:
            # Fetch HTML using the namespace API
            wait_time = int(wait_ms) if wait_ms is not None else None
            html = client.universal.scrape(
                url=url,
                js_render=js_render,
                country=country,
                wait_for=wait_for,
                wait_time=wait_time,
                output_format="html",
                block_resources=block_resources,
            )

            html_str = str(html) if not isinstance(html, str) else html

            # Convert to Markdown
            markdown = self._html_to_markdown(html_str)

            # Truncate if needed
            if len(markdown) > max_chars:
                markdown = markdown[:max_chars] + "\n\n[Content truncated...]"

            return markdown

        except Exception as e:
            return f"Error fetching markdown from {url}: {str(e)}"
