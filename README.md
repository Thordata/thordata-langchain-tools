# Thordata LangChain Tools

LangChain tools powered by [Thordata](https://www.thordata.com) - SERP API, Universal Scraping API, and Proxy Network.

Use these tools to give your LangChain agents **real-time web search**, **robust web page scraping**, **batch processing**, and **AI-powered analysis** capabilities via Thordata's global proxy network.

---

## ✨ Features

### Core Tools

- **ThordataSerpTool**  
  Search Google, Bing, Yandex, DuckDuckGo, and more. Returns structured JSON results with support for AI Overview, geo-targeting, and device-specific results.

- **ThordataScrapeTool**  
  Scrape any webpage with automatic anti-bot bypass. Supports HTML, PNG screenshots, and multiple output formats. Includes geo-targeting, custom headers/cookies, and JavaScript rendering.

- **ThordataMarkdownTool**  
  Fetch webpages and convert them to clean Markdown text, optimized for LLM consumption.

- **ThordataBatchScrapeTool**  
  Scrape multiple URLs concurrently for efficient batch processing.

- **ThordataBatchSerpTool**  
  Search multiple queries concurrently for efficient batch processing.

- **ThordataProxyTool**  
  Make HTTP requests through Thordata's proxy network with geo-targeting. Useful for accessing geo-restricted content or testing location-specific behavior.

- **ThordataTaskTool**  
  Run pre-built Web Scraper tasks for ecommerce (Amazon, eBay), social media (YouTube, Instagram), travel (Booking, Airbnb), and professional platforms (LinkedIn).

- **ThordataAccountTool**  
  Check account balance and usage statistics.

### Key Capabilities

- **Simple, environment-based configuration**  
  Read Thordata credentials directly from environment variables or a local `.env` file.

- **Works with LangChain agents or as standalone tools**  
  Use `.invoke()` directly, or plug the tools into your LangChain agents.

- **AI Integration**  
  Supports ZhipuAI (GLM-4-flash) and OpenRouter (30+ free models) for content summarization and analysis.

---

## 📦 Installation

Install from GitHub (editable mode recommended for development):

```bash
git clone https://github.com/Thordata/thordata-langchain-tools.git
cd thordata-langchain-tools

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install -e .
```

This will install:

- `thordata-sdk>=1.8.4` — official Python SDK for Thordata
- `langchain-core>=0.3.0` — LangChain core
- `python-dotenv` — for loading local .env files
- `markdownify` & `html2text` — for Markdown conversion

For the Agent examples, you will also need:

```bash
# For ZhipuAI (recommended, free tier available)
python -m pip install zhipuai

# Or for OpenRouter (multiple free models)
python -m pip install openai
```

---

## 🔐 Configuration

The tools read Thordata credentials from environment variables:

- `THORDATA_SCRAPER_TOKEN` (required)
- `THORDATA_PUBLIC_TOKEN` (optional, for async task APIs)
- `THORDATA_PUBLIC_KEY` (optional, for async task APIs)
- `ZHIPU_API_KEY` (optional, for LLM summarization with ZhipuAI)
- `OPENROUTER_API_KEY` (optional, for LLM summarization with OpenRouter)

You can either export them directly:

```bash
export THORDATA_SCRAPER_TOKEN=sk-...
export THORDATA_PUBLIC_TOKEN=pt-...
export THORDATA_PUBLIC_KEY=pk-...
export ZHIPU_API_KEY=your_key
export OPENROUTER_API_KEY=your_key
```

or use the provided `.env.example` as a template:

```bash
cp .env.example .env
# then edit .env with your credentials
```

The tools use python-dotenv to load `.env` automatically in local development.

---

## 🚀 Quick Start

### 1. SERP Search Tool

```python
from dotenv import load_dotenv
from thordata_langchain_tools import ThordataSerpTool

load_dotenv()

tool = ThordataSerpTool()

result = tool.invoke({
    "query": "Thordata proxy network",
    "engine": "google",
    "num": 10,
    "ai_overview": True,
    "country": "us",
})

organic = result.get("organic", [])
for item in organic:
    print(f"{item.get('position')}. {item.get('title')} -> {item.get('link')}")
```

### 2. Universal Scraper Tool

```python
from dotenv import load_dotenv
from thordata_langchain_tools import ThordataScrapeTool

load_dotenv()

tool = ThordataScrapeTool()

# Get HTML
html = tool.invoke({
    "url": "https://www.thordata.com",
    "js_render": True,
    "output_format": "html",
    "country": "us",
})

print(html[:1000])  # HTML is truncated to a safe length

# Or get screenshot
screenshot = tool.invoke({
    "url": "https://www.thordata.com",
    "js_render": True,
    "output_format": "png",
})
print(screenshot["png_base64"][:100])  # Base64 encoded PNG
```

### 3. Markdown Tool

```python
from dotenv import load_dotenv
from thordata_langchain_tools import ThordataMarkdownTool

load_dotenv()

tool = ThordataMarkdownTool()

markdown = tool.invoke({
    "url": "https://www.thordata.com",
    "js_render": True,
    "wait_ms": 2000,
    "max_chars": 10000,
})

print(markdown)
```

### 4. Batch Operations

```python
from dotenv import load_dotenv
from thordata_langchain_tools import ThordataBatchScrapeTool, ThordataBatchSerpTool

load_dotenv()

# Batch scraping
scrape_tool = ThordataBatchScrapeTool()
results = scrape_tool.invoke({
    "urls": [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ],
    "js_render": True,
    "concurrency": 3,
})

for result in results["results"]:
    if result["ok"]:
        print(f"✓ {result['url']}")
    else:
        print(f"✗ {result['url']}: {result['error']}")

# Batch SERP search
serp_tool = ThordataBatchSerpTool()
results = serp_tool.invoke({
    "queries": ["python", "javascript", "rust"],
    "engine": "google",
    "num": 5,
    "concurrency": 3,
})

for result in results["results"]:
    if result["ok"]:
        print(f"✓ {result['query']}: {len(result['output'].get('organic', []))} results")
```

### 5. Account Information

```python
from dotenv import load_dotenv
from thordata_langchain_tools import ThordataAccountTool

load_dotenv()

tool = ThordataAccountTool()
info = tool.invoke({})

print(f"Traffic Balance: {info.get('traffic_balance')}")
print(f"Usage Statistics: {info.get('usage_statistics')}")
```

---

## 🤖 Using the tools in a LangChain agent

The `examples/` directory contains comprehensive examples showing how to use these tools with LangChain agents.

### ZhipuAI Example (Recommended - Free Tier)

```python
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from thordata_langchain_tools import ThordataSerpTool, ThordataMarkdownTool
import os

load_dotenv()

# Search and scrape
serp = ThordataSerpTool()
results = serp.invoke({"query": "Python programming", "num": 3})
url = results["organic"][0]["link"]

markdown = ThordataMarkdownTool()
content = markdown.invoke({"url": url, "max_chars": 5000})

# Summarize with ZhipuAI
client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))
response = client.chat.completions.create(
    model="glm-4-flash",
    messages=[{"role": "user", "content": f"Summarize: {content[:2000]}"}],
)
print(response.choices[0].message.content)
```

### OpenRouter Example (Multiple Free Models)

```python
from dotenv import load_dotenv
from openai import OpenAI
from thordata_langchain_tools import ThordataSerpTool, ThordataMarkdownTool
import os

load_dotenv()

# Search and scrape
serp = ThordataSerpTool()
results = serp.invoke({"query": "Python programming", "num": 3})
url = results["organic"][0]["link"]

markdown = ThordataMarkdownTool()
content = markdown.invoke({"url": url, "max_chars": 5000})

# Summarize with OpenRouter
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
response = client.chat.completions.create(
    model="openrouter/free",  # Free model
    messages=[{"role": "user", "content": f"Summarize: {content[:2000]}"}],
)
print(response.choices[0].message.content)
```

See `examples/zhipu_agent.py` and `examples/openrouter_agent.py` for complete working examples.

---

## 📂 Project Structure

```
thordata-langchain-tools/
├── thordata_langchain_tools/
│   ├── __init__.py
│   ├── serp_tool.py           # ThordataSerpTool
│   ├── scrape_tool.py         # ThordataScrapeTool
│   ├── markdown_tool.py        # ThordataMarkdownTool
│   ├── batch_tool.py           # Batch operations
│   ├── proxy_tool.py           # ThordataProxyTool
│   ├── task_tool.py            # ThordataTaskTool
│   └── account_tool.py          # ThordataAccountTool
├── examples/
│   ├── test_tools.py           # Comprehensive test suite
│   ├── test_all_features.py    # Test all features
│   ├── zhipu_agent.py          # ZhipuAI agent example
│   ├── openrouter_agent.py     # OpenRouter agent example
│   ├── simple_serp.py          # Basic SERP usage
│   ├── simple_scrape.py        # Basic scraping usage
│   ├── simple_markdown.py      # Basic Markdown conversion
│   ├── batch_example.py        # Batch operations example
│   └── simple_agent.py         # Simple agent example
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 💡 What is ThordataProxyTool?

**ThordataProxyTool** allows you to make HTTP requests through Thordata's proxy network with geographic targeting. This is useful for:

- **Accessing geo-restricted content**: View content as if you're in a specific country
- **Testing location-specific behavior**: See how websites behave for users in different locations
- **Bypassing IP-based restrictions**: Use residential proxies from specific regions

**Example use case**:
```python
tool = ThordataProxyTool()
# Request from Japan
response = tool.invoke({
    "url": "https://httpbin.org/ip",
    "country": "jp"
})
# Returns response showing Japanese IP address
```

**Note**: This tool requires separate proxy credentials (`THORDATA_USERNAME` and `THORDATA_PASSWORD`) which are different from your API tokens. It's primarily for advanced use cases where you need direct proxy access rather than using the Universal Scraper API.

---

## 🔧 Advanced Usage

### Custom Configuration

Tools automatically read credentials from environment variables. For custom client usage, you may need to extend the tool classes.

### Error Handling

All tools return error information in a consistent format:

```python
result = tool.invoke({"url": "invalid-url"})
if "error" in result:
    print(f"Error: {result['error']}")
```

### Rate Limiting

- Batch tools have a concurrency limit of 20 to prevent overwhelming the API
- For large-scale operations, consider implementing delays between batches
- Monitor your account balance using `ThordataAccountTool`

---

## 📊 Use Cases

### Market Research
1. Use SERP tool to search for competitors
2. Use Scrape tool to extract product pages
3. Use AI to analyze prices and features
4. Generate comparison reports

### Content Collection
1. Use SERP tool to search for topics
2. Use Batch Scrape tool to collect multiple pages
3. Convert to Markdown format
4. Use AI to summarize each article

### Data Monitoring
1. Regularly scrape price pages using Scrape tool
2. Store data over time
3. Analyze trends

### Information Summarization
1. Use Markdown tool to extract article content
2. Use AI to generate summaries
3. Get concise overviews

---

## ❓ FAQ

**Q: Does this package support async LangChain tools?**  
A: The batch tools use async operations internally for better performance. For full async support in LangChain agents, you may need to use async-compatible agent frameworks.

**Q: Which Python versions are supported?**  
A: The project requires Python 3.10+ for modern type hints and async support.

**Q: How do I get Thordata credentials?**  
A: Create an account at [Thordata](https://www.thordata.com), then go to the Dashboard and copy your Scraper Token, Public Token, and Public Key from the API / credentials section.

**Q: What's the difference between ThordataScrapeTool and ThordataMarkdownTool?**  
A: `ThordataScrapeTool` returns raw HTML (or PNG screenshots), while `ThordataMarkdownTool` converts HTML to clean Markdown text optimized for LLM consumption.

**Q: Can I use batch tools for large-scale scraping?**  
A: Yes, but be mindful of rate limits and your account's traffic quota. The concurrency parameter is capped at 20 to prevent overwhelming the API.

**Q: What is ThordataProxyTool used for?**  
A: It makes HTTP requests through Thordata's proxy network with geo-targeting. Useful for accessing geo-restricted content or testing location-specific behavior. Requires separate proxy credentials.

**Q: Which search engines are supported?**  
A: Google (primary), Bing, Yandex, DuckDuckGo, and Baidu.

**Q: Can I scrape websites that require login?**  
A: Basic version doesn't support login. You can use custom headers and cookies via the Scrape tool parameters.

**Q: How does it handle anti-bot protection?**  
A: Tools include built-in anti-bot bypass capabilities. JavaScript rendering handles dynamic content. If issues persist, adjust parameters.

**Q: Are the AI summaries accurate?**  
A: Depends on the AI model quality. Free models (ZhipuAI, OpenRouter) are usually sufficient for daily use. Paid models offer better accuracy.

**Q: Can I use this commercially?**  
A: Code is MIT licensed and can be used commercially. However, you must comply with Thordata and AI service usage terms. Check each service's commercial use policies.

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python examples/test_tools.py
```

Test all features including new tools:

```bash
python examples/test_all_features.py
```

---

## 📜 License

This project is licensed under the MIT License.  
See the LICENSE file for details.

---

## 🔗 Links

- [Thordata Website](https://www.thordata.com)
- [Thordata Python SDK](https://github.com/Thordata/thordata-python-sdk)
- [Thordata MCP Server](https://github.com/Thordata/thordata-mcp-server)
- [LangChain Documentation](https://python.langchain.com/)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Happy coding!** 🚀
