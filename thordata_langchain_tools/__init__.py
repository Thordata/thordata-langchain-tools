"""
Thordata LangChain Tools

LangChain tools powered by Thordata for web scraping, SERP search,
and proxy-based requests.

Example:
    >>> from thordata_langchain_tools import ThordataSerpTool, ThordataScrapeTool
    >>> 
    >>> # Search the web
    >>> serp_tool = ThordataSerpTool()
    >>> results = serp_tool.invoke({"query": "python programming"})
    >>> 
    >>> # Scrape a webpage
    >>> scrape_tool = ThordataScrapeTool()
    >>> html = scrape_tool.invoke({"url": "https://example.com"})
"""

__version__ = "0.2.0"

from .serp_tool import ThordataSerpTool
from .scrape_tool import ThordataScrapeTool
from .universal_tool import ThordataUniversalTool
from .proxy_tool import ThordataProxyTool

__all__ = [
    "__version__",
    "ThordataSerpTool",
    "ThordataScrapeTool",
    "ThordataUniversalTool",
    "ThordataProxyTool",
]