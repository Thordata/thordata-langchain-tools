"""
Batch Operations Example

Demonstrates using ThordataBatchScrapeTool and ThordataBatchSerpTool
for efficient concurrent processing.

Usage:
    python examples/batch_example.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("THORDATA_SCRAPER_TOKEN"):
    print("❌ Error: Set THORDATA_SCRAPER_TOKEN in your .env file")
    sys.exit(1)

from thordata_langchain_tools import ThordataBatchScrapeTool, ThordataBatchSerpTool


def main():
    print("=" * 60)
    print("🚀 Thordata Batch Operations Demo")
    print("=" * 60)
    print()

    # Example 1: Batch Scraping
    print("📦 Example 1: Batch Scraping")
    print("-" * 60)

    scrape_tool = ThordataBatchScrapeTool()

    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ]

    print(f"Scraping {len(urls)} URLs concurrently...")
    results = scrape_tool.invoke(
        {
            "urls": urls,
            "js_render": True,
            "concurrency": 3,
        }
    )

    print(f"\n✅ Completed {results['total']} requests")
    for result in results["results"]:
        status = "✓" if result["ok"] else "✗"
        print(f"  {status} {result['url']}")
        if not result["ok"]:
            print(f"    Error: {result['error']}")

    print()

    # Example 2: Batch SERP Search
    print("🔍 Example 2: Batch SERP Search")
    print("-" * 60)

    serp_tool = ThordataBatchSerpTool()

    queries = [
        "Python programming",
        "JavaScript frameworks",
        "Rust language",
    ]

    print(f"Searching {len(queries)} queries concurrently...")
    results = serp_tool.invoke(
        {
            "queries": queries,
            "engine": "google",
            "num": 5,
            "concurrency": 3,
        }
    )

    print(f"\n✅ Completed {results['total']} searches")
    for result in results["results"]:
        status = "✓" if result["ok"] else "✗"
        print(f"  {status} '{result['query']}'")
        if result["ok"]:
            organic_count = len(result["output"].get("organic", []))
            print(f"    Found {organic_count} organic results")
        else:
            print(f"    Error: {result['error']}")


if __name__ == "__main__":
    main()
