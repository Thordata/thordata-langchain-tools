"""
Simple Markdown Conversion Example

Demonstrates using ThordataMarkdownTool to fetch and convert webpages to Markdown.

Usage:
    python examples/simple_markdown.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("THORDATA_SCRAPER_TOKEN"):
    print("❌ Error: Set THORDATA_SCRAPER_TOKEN in your .env file")
    sys.exit(1)

from thordata_langchain_tools import ThordataMarkdownTool


def main():
    tool = ThordataMarkdownTool()

    url = "https://www.thordata.com"
    print(f"🌐 Fetching and converting to Markdown: {url}")
    print()

    # Convert to Markdown
    markdown = tool.invoke(
        {
            "url": url,
            "js_render": True,
            "wait_ms": 2000,
            "max_chars": 5000,
        }
    )

    if markdown.startswith("Error"):
        print(f"❌ {markdown}")
        return

    print("📝 Markdown Content:")
    print("-" * 50)
    print(markdown)
    print("-" * 50)
    print(f"\n✅ Successfully converted {len(markdown)} characters to Markdown")


if __name__ == "__main__":
    main()
