"""
Simple SERP Search Example

Demonstrates using ThordataSerpTool to search the web.

Usage:
    python examples/simple_serp.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required token
if not os.getenv("THORDATA_SCRAPER_TOKEN"):
    print("❌ Error: Set THORDATA_SCRAPER_TOKEN in your .env file")
    sys.exit(1)

from thordata_langchain_tools import ThordataSerpTool


def main():
    # Create the tool
    tool = ThordataSerpTool()

    print("🔍 Searching for: 'Python web scraping best practices'")
    print()

    # Execute search
    results = tool.invoke(
        {
            "query": "Python web scraping best practices",
            "engine": "google",
            "num": 5,
        }
    )

    # Check for errors
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return

    # Display organic results
    organic = results.get("organic", [])
    print(f"📊 Found {len(organic)} organic results:\n")

    for i, item in enumerate(organic, 1):
        title = item.get("title", "No title")
        link = item.get("link", "No link")
        snippet = item.get("snippet", "")[:100]

        print(f"{i}. {title}")
        print(f"   🔗 {link}")
        if snippet:
            print(f"   📝 {snippet}...")
        print()


if __name__ == "__main__":
    main()
