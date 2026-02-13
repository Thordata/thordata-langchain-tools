"""
Thordata LangChain Tools

LangChain tools powered by Thordata for web scraping, SERP search,
and proxy-based requests. Uses the latest SDK API with namespace support.

Example:
    >>> from thordata_langchain_tools import (
    ...     ThordataSerpTool,
    ...     ThordataScrapeTool,
    ...     ThordataMarkdownTool,
    ...     ThordataBatchScrapeTool,
    ...     ThordataBatchSerpTool,
    ... )
    >>>
    >>> # Search the web
    >>> serp_tool = ThordataSerpTool()
    >>> results = serp_tool.invoke({"query": "python programming"})
    >>>
    >>> # Scrape a webpage
    >>> scrape_tool = ThordataScrapeTool()
    >>> html = scrape_tool.invoke({"url": "https://example.com"})
    >>>
    >>> # Convert to Markdown
    >>> markdown_tool = ThordataMarkdownTool()
    >>> markdown = markdown_tool.invoke({"url": "https://example.com"})
"""

__version__ = "1.1.0"

from .serp_tool import ThordataSerpTool
from .scrape_tool import ThordataScrapeTool
from .markdown_tool import ThordataMarkdownTool
from .batch_tool import ThordataBatchScrapeTool, ThordataBatchSerpTool
from .proxy_tool import ThordataProxyTool
from .task_tool import ThordataTaskTool
from .account_tool import ThordataAccountTool

__all__ = [
    "__version__",
    "ThordataSerpTool",
    "ThordataScrapeTool",
    "ThordataMarkdownTool",
    "ThordataBatchScrapeTool",
    "ThordataBatchSerpTool",
    "ThordataProxyTool",
    "ThordataTaskTool",
    "ThordataAccountTool",
]
