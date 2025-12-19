# Thordata LangChain Tools

LangChain tools powered by [Thordata](https://www.thordata.com) SERP API and Universal Scraper API.

Use these tools to give your LangChain agents **real-time web search** and **robust web page scraping** via Thordata's global proxy network.

> Status: early preview. APIs may change slightly as the SDK evolves.

---

## ✨ Features

- **ThordataSerpTool**  
  Call Thordata's SERP API from LangChain to query Google, Bing, Yandex, DuckDuckGo, and more. Returns the full JSON SERP response.

- **ThordataScrapeTool**  
  Call Thordata's Universal Scraper API from LangChain to fetch HTML (or PNG screenshots) from almost any URL, including pages protected by anti-bot systems. HTML is truncated to a safe length to control LLM token usage.

- **Simple, environment-based configuration**  
  Read Thordata credentials directly from environment variables or a local `.env` file for easy local development.

- **Works with LangChain agents or as standalone tools**  
  Use `.invoke()` directly, or plug the tools into your LangChain agents.

---

## 📦 Installation

This package is not yet published to PyPI; install from GitHub (editable mode) while you iterate:

```bash
git clone https://github.com/Thordata/thordata-langchain-tools.git
cd thordata-langchain-tools

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install -e .
```

This will install:

- `thordata-sdk>=0.5.0` — official Python SDK for Thordata
- `langchain>=0.3.0` — LangChain core
- `python-dotenv` — for loading local .env files

For the Agent example, you will also need:

```bash
python -m pip install "langchain-openai>=0.2.0" "openai>=1.0.0"
```

---

## 🔐 Configuration

The tools read Thordata credentials from environment variables:

- `THORDATA_SCRAPER_TOKEN` (required)
- `THORDATA_PUBLIC_TOKEN` (optional, for async task APIs)
- `THORDATA_PUBLIC_KEY` (optional, for async task APIs)

You can either export them directly:

```bash
export THORDATA_SCRAPER_TOKEN=sk-...
export THORDATA_PUBLIC_TOKEN=pt-...
export THORDATA_PUBLIC_KEY=pk-...
```

or use the provided `.env.example` as a template:

```bash
cp .env.example .env
# then edit .env with your credentials
```

The tools use python-dotenv to load `.env` automatically in local development.

---

## 🚀 Quick Start

### 1. SERP search tool

```python
from dotenv import load_dotenv
from thordata_langchain_tools import ThordataSerpTool

load_dotenv()  # Load THORDATA_* from .env

tool = ThordataSerpTool()

result = tool.invoke(
    {
        "query": "Thordata proxy network",
        "engine": "google",
        "num": 3,
        # Optional:
        # "location": "United States",
        # "search_type": "news",
    }
)

organic = result.get("organic", [])
for item in organic:
    print(item.get("position"), item.get("title"), "->", item.get("link"))
```

### 2. Universal Scraper tool

```python
from dotenv import load_dotenv
from thordata_langchain_tools import ThordataScrapeTool

load_dotenv()

tool = ThordataScrapeTool()

html = tool.invoke(
    {
        "url": "https://www.thordata.com",
        "js_render": False,
        "output_format": "html",
    }
)

print(html[:1000])  # HTML is truncated to a safe length
```

---

## 🤖 Using the tools in a LangChain agent

The `examples/simple_agent.py` script shows how to build a small LangChain pipeline that:

1. Uses ThordataSerpTool to find the Thordata homepage
2. Uses ThordataScrapeTool to scrape the homepage HTML
3. Uses an OpenAI chat model to summarize Thordata's services

**Minimal example** (without full error handling):

```python
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from thordata_langchain_tools import ThordataSerpTool, ThordataScrapeTool

load_dotenv()

def find_homepage() -> str:
    serp_tool = ThordataSerpTool()
    res = serp_tool.invoke({"query": "Thordata official homepage", "num": 3})
    organic = res.get("organic", [])
    for item in organic:
        link = item.get("link")
        if link:
            return link
    raise RuntimeError("Could not find homepage from SERP results.")

def scrape_homepage(url: str) -> str:
    scrape_tool = ThordataScrapeTool()
    html = scrape_tool.invoke({"url": url, "js_render": False})
    return html if isinstance(html, str) else str(html)

def summarize_html(html: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Truncate HTML to keep token usage safe
    MAX_HTML_CHARS = 3000
    if len(html) > MAX_HTML_CHARS:
        html = html[:MAX_HTML_CHARS] + "\n\n[Truncated by example script]"

    prompt = (
        "You are a technical writer.\n"
        "You will be given (a truncated portion of) the Thordata homepage HTML.\n"
        "Summarize Thordata's core products and services in at most 5 bullet points.\n\n"
        f"HTML:\n{html}"
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content

if __name__ == "__main__":
    url = find_homepage()
    print(f"Detected Thordata homepage URL: {url}")

    html = scrape_homepage(url)
    summary = summarize_html(html)

    print("\n=== Summary of Thordata Services ===")
    print(summary)
```

---

## 📂 Project structure

```
thordata-langchain-tools/
├── thordata_langchain_tools/
│   ├── __init__.py
│   ├── serp_tool.py        # ThordataSerpTool
│   └── scrape_tool.py      # ThordataScrapeTool
├── examples/
│   ├── simple_serp.py      # Basic SERP usage
│   ├── simple_scrape.py    # Basic Universal Scraper usage
│   └── simple_agent.py     # SERP + Scraper + LLM summarization pipeline
├── .env.example
├── pyproject.toml
└── README.md
```

---

## ❓ FAQ

**Q: Does this package support async LangChain tools?**  
A: Not yet. The current tools implement the synchronous LangChain BaseTool interface. Async support may be added in a future release.

**Q: Which Python versions are supported?**  
A: The project targets Python 3.8+ for standard usage. For LangChain ≥ 0.3 and Pydantic v2, Python 3.10–3.12 is recommended.

**Q: How do I get Thordata credentials?**  
A: Create an account at Thordata, then go to the Dashboard and copy your Scraper Token, Public Token, and Public Key from the API / credentials section.

---

## 📜 License

This project is licensed under the MIT License.  
See the LICENSE file for details.
