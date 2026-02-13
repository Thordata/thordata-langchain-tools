"""
Comprehensive Tool Testing Script

Tests all Thordata LangChain tools to ensure they work correctly.
This script tests SERP, Scrape, Markdown, and Batch tools.

Usage:
    python examples/test_tools.py
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

if not os.getenv("THORDATA_SCRAPER_TOKEN"):
    print("❌ Error: Set THORDATA_SCRAPER_TOKEN in your .env file")
    sys.exit(1)

from thordata_langchain_tools import (
    ThordataSerpTool,
    ThordataScrapeTool,
    ThordataMarkdownTool,
    ThordataBatchScrapeTool,
    ThordataBatchSerpTool,
)


def test_serp_tool():
    """Test SERP search tool."""
    print("\n" + "=" * 70)
    print("TEST 1: SERP Search Tool")
    print("=" * 70)

    try:
        tool = ThordataSerpTool()
        print("✓ Tool initialized")

        result = tool.invoke(
            {
                "query": "Python programming",
                "engine": "google",
                "num": 3,
                "country": "us",
            }
        )

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False

        organic = result.get("organic", [])
        print(f"✓ Found {len(organic)} organic results")

        for i, item in enumerate(organic[:3], 1):
            print(f"  {i}. {item.get('title', 'No title')[:60]}")
            print(f"     {item.get('link', 'No link')[:60]}")

        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_scrape_tool():
    """Test web scraping tool."""
    print("\n" + "=" * 70)
    print("TEST 2: Web Scraping Tool")
    print("=" * 70)

    try:
        tool = ThordataScrapeTool()
        print("✓ Tool initialized")

        result = tool.invoke(
            {
                "url": "https://example.com",
                "js_render": False,
                "output_format": "html",
                "max_length": 1000,
            }
        )

        if isinstance(result, str) and result.startswith("Error"):
            print(f"❌ Error: {result}")
            return False

        print(f"✓ Scraped {len(result)} characters")
        print(f"  Preview: {result[:200]}...")

        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_markdown_tool():
    """Test Markdown conversion tool."""
    print("\n" + "=" * 70)
    print("TEST 3: Markdown Conversion Tool")
    print("=" * 70)

    try:
        tool = ThordataMarkdownTool()
        print("✓ Tool initialized")

        result = tool.invoke(
            {
                "url": "https://example.com",
                "js_render": False,
                "wait_ms": 1000,
                "max_chars": 2000,
            }
        )

        if result.startswith("Error"):
            print(f"❌ Error: {result}")
            return False

        print(f"✓ Converted {len(result)} characters to Markdown")
        print(f"  Preview: {result[:300]}...")

        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_batch_scrape():
    """Test batch scraping tool."""
    print("\n" + "=" * 70)
    print("TEST 4: Batch Scraping Tool")
    print("=" * 70)

    try:
        tool = ThordataBatchScrapeTool()
        print("✓ Tool initialized")

        result = tool.invoke(
            {
                "urls": [
                    "https://example.com",
                    "https://httpbin.org/html",
                ],
                "js_render": False,
                "concurrency": 2,
            }
        )

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False

        print(f"✓ Processed {result['total']} URLs")
        for item in result["results"]:
            status = "✓" if item["ok"] else "✗"
            print(f"  {status} {item['url']}")
            if not item["ok"]:
                print(f"    Error: {item.get('error', 'Unknown')}")

        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_batch_serp():
    """Test batch SERP search tool."""
    print("\n" + "=" * 70)
    print("TEST 5: Batch SERP Search Tool")
    print("=" * 70)

    try:
        tool = ThordataBatchSerpTool()
        print("✓ Tool initialized")

        result = tool.invoke(
            {
                "queries": ["Python", "JavaScript"],
                "engine": "google",
                "num": 2,
                "concurrency": 2,
            }
        )

        if result is None:
            print("❌ Error: Tool returned None")
            return False

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False

        print(f"✓ Processed {result['total']} queries")
        for item in result["results"]:
            status = "✓" if item["ok"] else "✗"
            print(f"  {status} '{item['query']}'")
            if item["ok"]:
                organic_count = len(item["output"].get("organic", []))
                print(f"    Found {organic_count} results")
            else:
                print(f"    Error: {item.get('error', 'Unknown')}")

        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("Thordata LangChain Tools - Comprehensive Test Suite")
    print("=" * 70)

    results = []

    # Run all tests
    results.append(("SERP Tool", test_serp_tool()))
    results.append(("Scrape Tool", test_scrape_tool()))
    results.append(("Markdown Tool", test_markdown_tool()))
    results.append(("Batch Scrape", test_batch_scrape()))
    results.append(("Batch SERP", test_batch_serp()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
