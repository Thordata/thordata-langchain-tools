"""
ZhipuAI Agent Example with Thordata Tools

Demonstrates using Thordata tools with ZhipuAI GLM-4-flash model.
Complete workflow: search -> scrape -> summarize.

Requirements:
    pip install zhipuai

Usage:
    export ZHIPU_API_KEY=your_key
    python examples/zhipu_agent.py
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

# Check required environment variables
if not os.getenv("THORDATA_SCRAPER_TOKEN"):
    print("❌ Error: Set THORDATA_SCRAPER_TOKEN in your .env file")
    sys.exit(1)

if not os.getenv("ZHIPU_API_KEY"):
    print("❌ Error: Set ZHIPU_API_KEY in your .env file")
    sys.exit(1)

try:
    from zhipuai import ZhipuAI
except ImportError:
    print("❌ Error: Please install zhipuai: pip install zhipuai")
    sys.exit(1)

from thordata_langchain_tools import ThordataSerpTool, ThordataMarkdownTool


def search_for_topic(query: str) -> tuple[str, str]:
    """Use SERP tool to find relevant URLs."""
    print(f"🔍 Searching for: '{query}'")

    try:
        serp_tool = ThordataSerpTool()
        results = serp_tool.invoke(
            {
                "query": query,
                "engine": "google",
                "num": 3,
                "ai_overview": True,
            }
        )

        if "error" in results:
            print(f"   ❌ Search error: {results['error']}")
            return None, None

        # Get first organic result
        organic = results.get("organic", [])
        if not organic:
            print("   ⚠️  No organic results found")
            return None, None

        first_result = organic[0]
        title = first_result.get("title", "No title")
        link = first_result.get("link", "")

        print(f"   ✓ Found: {title}")
        print(f"   🔗 URL: {link}")

        return link, title

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return None, None


def scrape_as_markdown(url: str) -> str:
    """Use Markdown tool to get clean text."""
    print(f"📝 Converting to Markdown: {url}")

    try:
        markdown_tool = ThordataMarkdownTool()
        markdown = markdown_tool.invoke(
            {
                "url": url,
                "js_render": True,
                "wait_ms": 2000,
                "max_chars": 8000,
            }
        )

        if markdown.startswith("Error"):
            print(f"   ❌ Markdown error: {markdown}")
            return None

        print(f"   ✓ Converted {len(markdown)} characters to Markdown")
        return markdown

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return None


def summarize_with_zhipu(content: str, topic: str) -> str:
    """Use ZhipuAI GLM-4-flash to summarize the content."""
    print("🤖 Summarizing with ZhipuAI GLM-4-flash...")

    try:
        client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

        print("   ✓ Client initialized")

        prompt = f"""你是一个有用的助手，擅长总结网页内容。

基于以下关于"{topic}"的内容，请提供一个清晰简洁的总结。
重点关注关键要点、主要功能和重要信息。

请用3-5个要点来总结，每个要点应该信息丰富且具体。

内容：
{content[:6000]}

总结："""

        # Use glm-4-flash (free tier)
        print("   📤 Sending request to ZhipuAI...")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        print("   ✓ Received response")
        summary = response.choices[0].message.content
        return summary

    except Exception as e:
        print(f"   ❌ ZhipuAI error: {e}")
        import traceback

        traceback.print_exc()
        return None


def main():
    print("=" * 70)
    print("🚀 Thordata + ZhipuAI GLM-4-flash Agent Demo")
    print("=" * 70)
    print()

    try:
        # Step 1: Search for a topic
        query = "Thordata proxy network features"
        url, title = search_for_topic(query)

        if not url:
            print("\n❌ Failed to find a URL. Exiting.")
            sys.exit(1)

        print()

        # Step 2: Scrape as Markdown
        markdown = scrape_as_markdown(url)

        if not markdown:
            print("\n❌ Failed to scrape content. Exiting.")
            sys.exit(1)

        print()

        # Step 3: Summarize with ZhipuAI
        summary = summarize_with_zhipu(markdown, title or query)

        if not summary:
            print("\n❌ Failed to generate summary. Exiting.")
            sys.exit(1)

        print()
        print("=" * 70)
        print("📋 Summary:")
        print("=" * 70)
        print(summary)
        print()
        print("=" * 70)
        print("✅ Demo completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
