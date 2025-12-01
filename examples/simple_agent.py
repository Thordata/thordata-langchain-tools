from __future__ import annotations

from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from thordata_langchain_tools import ThordataSerpTool, ThordataScrapeTool

load_dotenv()  # Load OPENAI_API_KEY and THORDATA_* from a local .env file


def find_thordata_homepage(max_results: int = 5) -> Optional[str]:
    """
    Use ThordataSerpTool to find the official Thordata homepage URL.

    Returns:
        The first organic result's link, or None if nothing is found.
    """
    serp_tool = ThordataSerpTool()

    serp_result: Dict[str, Any] = serp_tool.invoke(
        {
            "query": "Thordata official homepage",
            "engine": "google",
            "num": max_results,
        }
    )

    organic: List[Dict[str, Any]] = serp_result.get("organic") or []
    for item in organic:
        link = item.get("link")
        if link:
            return link

    return None


def scrape_url(url: str) -> str:
    """
    Use ThordataScrapeTool to fetch the HTML of a given URL.

    The tool itself truncates overly long HTML to avoid huge LLM inputs.
    """
    scrape_tool = ThordataScrapeTool()
    result = scrape_tool.invoke(
        {
            "url": url,
            "js_render": False,
            "output_format": "HTML",
        }
    )

    if isinstance(result, str):
        return result
    return str(result)


def summarize_html_with_llm(html: str) -> str:
    """
    Call OpenAI (via LangChain ChatOpenAI) exactly once to summarize the HTML.
    We deliberately truncate the HTML to keep the token count very small,
    so that it fits comfortably under strict TPM limits.
    """
    # Hard cap: we only keep the first 3000 characters of the HTML.
    # 3000 chars ~= 1000–1500 tokens, which is safe for your 60k TPM limit.
    MAX_HTML_FOR_LLM = 3000
    if len(html) > MAX_HTML_FOR_LLM:
        html = (
            html[:MAX_HTML_FOR_LLM]
            + "\n\n[Truncated to first "
            f"{MAX_HTML_FOR_LLM} characters before sending to the LLM]"
        )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = (
        "You are a technical writer.\n"
        "You will be given (a truncated portion of) the Thordata homepage HTML.\n"
        "Based on this excerpt, summarize Thordata's core products and services "
        "in at most 5 bullet points.\n"
        "Be concise and concrete, and avoid marketing fluff.\n\n"
        f"HTML content (truncated):\n{html}"
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


if __name__ == "__main__":
    homepage_url = find_thordata_homepage()

    if not homepage_url:
        print("Could not determine Thordata homepage URL from SERP results.")
        raise SystemExit(1)

    print(f"Detected Thordata homepage URL: {homepage_url}")

    html = scrape_url(homepage_url)

    summary = summarize_html_with_llm(html)

    print("\n=== Summary of Thordata Services ===")
    print(summary)