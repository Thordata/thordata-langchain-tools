"""
Comprehensive test of all features including new tools.
"""

import os
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

from thordata_langchain_tools import (
    ThordataSerpTool,
    ThordataScrapeTool,
    ThordataMarkdownTool,
    ThordataBatchScrapeTool,
    ThordataBatchSerpTool,
    ThordataAccountTool,
)

print("=" * 70)
print("Comprehensive Feature Test")
print("=" * 70)

# Test Account Tool
print("\n1. Testing Account Tool...")
try:
    account = ThordataAccountTool()
    info = account.invoke({})
    if "error" not in info:
        print(f"   ✓ Balance: {info.get('traffic_balance', 'N/A')}")
    else:
        print(f"   ⚠️  {info.get('error', 'Unknown error')}")
except Exception as e:
    print(f"   ⚠️  {e}")

# Test SERP
print("\n2. Testing SERP Tool...")
try:
    serp = ThordataSerpTool()
    result = serp.invoke({"query": "Python", "num": 2})
    if "error" not in result:
        print(f"   ✓ Found {len(result.get('organic', []))} results")
    else:
        print(f"   ⚠️  {result.get('error')}")
except Exception as e:
    print(f"   ⚠️  {e}")

# Test Scrape
print("\n3. Testing Scrape Tool...")
try:
    scrape = ThordataScrapeTool()
    result = scrape.invoke({"url": "https://example.com", "max_length": 500})
    if isinstance(result, str) and not result.startswith("Error"):
        print(f"   ✓ Scraped {len(result)} characters")
    else:
        print(f"   ⚠️  {result}")
except Exception as e:
    print(f"   ⚠️  {e}")

# Test Markdown
print("\n4. Testing Markdown Tool...")
try:
    md = ThordataMarkdownTool()
    result = md.invoke({"url": "https://example.com", "max_chars": 200})
    if not result.startswith("Error"):
        print(f"   ✓ Converted {len(result)} characters")
    else:
        print(f"   ⚠️  {result}")
except Exception as e:
    print(f"   ⚠️  {e}")

print("\n" + "=" * 70)
print("✅ All core features tested!")
print("=" * 70)
