"""
Simple Web Scraping Example

Demonstrates using ThordataScrapeTool to fetch webpage content.

Usage:
    python examples/simple_scrape.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("THORDATA_SCRAPER_TOKEN"):
    print("❌ Error: Set THORDATA_SCRAPER_TOKEN in your .env file")
    sys.exit(1)

from thordata_langchain_tools import ThordataScrapeTool


def main():
    tool = ThordataScrapeTool()

    url = "https://example.com"
    print(f"🌐 Scraping: {url}")
    print()

    # Scrape the page
    html = tool.invoke({
        "url": url,
        "js_render": False,
        "max_length": 2000,
    })

    if html.startswith("Error"):
        print(f"❌ {html}")
        return

    print("📄 HTML Content (first 1000 chars):")
    print("-" * 50)
    print(html[:1000])
    print("-" * 50)
    print(f"\n✅ Successfully scraped {len(html)} characters")


if __name__ == "__main__":
    main()