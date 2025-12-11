"""
Tests for Thordata LangChain tools.
"""

from unittest.mock import MagicMock, patch

from thordata_langchain_tools import (
    ThordataSerpTool,
    ThordataScrapeTool,
    ThordataUniversalTool,
    ThordataProxyTool,
)


class TestThordataSerpTool:
    """Tests for ThordataSerpTool."""

    def test_tool_name(self):
        """Test tool has correct name."""
        tool = ThordataSerpTool()
        assert tool.name == "thordata_serp_search"

    def test_tool_description(self):
        """Test tool has description."""
        tool = ThordataSerpTool()
        assert "search" in tool.description.lower()
        assert len(tool.description) > 20

    def test_tool_has_args_schema(self):
        """Test tool has args schema defined."""
        tool = ThordataSerpTool()
        assert tool.args_schema is not None

    @patch("thordata_langchain_tools.serp_tool.ThordataClient")
    def test_run_success(self, mock_client_class):
        """Test successful SERP search."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.serp_search.return_value = {
            "organic": [{"title": "Test Result", "link": "https://example.com"}]
        }
        mock_client_class.return_value = mock_client

        # Run tool
        tool = ThordataSerpTool()
        result = tool._run(query="test query", engine="google", num=5)

        # Verify
        assert "organic" in result
        assert len(result["organic"]) == 1
        mock_client.serp_search.assert_called_once()

    @patch("thordata_langchain_tools.serp_tool.ThordataClient")
    def test_run_error_handling(self, mock_client_class):
        """Test error handling in SERP search."""
        mock_client = MagicMock()
        mock_client.serp_search.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        tool = ThordataSerpTool()
        result = tool._run(query="test", engine="google", num=5)

        assert "error" in result


class TestThordataScrapeTool:
    """Tests for ThordataScrapeTool."""

    def test_tool_name(self):
        """Test tool has correct name."""
        tool = ThordataScrapeTool()
        assert tool.name == "thordata_scrape_webpage"

    def test_tool_description(self):
        """Test tool has description."""
        tool = ThordataScrapeTool()
        assert "scrape" in tool.description.lower()

    @patch("thordata_langchain_tools.scrape_tool.ThordataClient")
    def test_run_success(self, mock_client_class):
        """Test successful scrape."""
        mock_client = MagicMock()
        mock_client.universal_scrape.return_value = "<html><body>Test</body></html>"
        mock_client_class.return_value = mock_client

        tool = ThordataScrapeTool()
        result = tool._run(url="https://example.com", js_render=False, max_length=1000)

        assert "html" in result.lower()
        mock_client.universal_scrape.assert_called_once()

    @patch("thordata_langchain_tools.scrape_tool.ThordataClient")
    def test_run_truncates_long_content(self, mock_client_class):
        """Test that long content is truncated."""
        mock_client = MagicMock()
        mock_client.universal_scrape.return_value = "x" * 100000
        mock_client_class.return_value = mock_client

        tool = ThordataScrapeTool()
        result = tool._run(url="https://example.com", js_render=False, max_length=1000)

        assert len(result) < 2000
        assert "truncated" in result.lower()


class TestThordataUniversalTool:
    """Tests for ThordataUniversalTool."""

    def test_tool_name(self):
        """Test tool has correct name."""
        tool = ThordataUniversalTool()
        assert tool.name == "thordata_universal_scrape"

    def test_tool_description(self):
        """Test tool has description."""
        tool = ThordataUniversalTool()
        assert (
            "scrape" in tool.description.lower()
            or "scraping" in tool.description.lower()
        )

    @patch("thordata_langchain_tools.universal_tool.ThordataClient")
    def test_run_with_js_render(self, mock_client_class):
        """Test scrape with JS rendering."""
        mock_client = MagicMock()
        mock_client.universal_scrape.return_value = "<html>Rendered</html>"
        mock_client_class.return_value = mock_client

        tool = ThordataUniversalTool()
        result = tool._run(
            url="https://example.com",
            js_render=True,
            output_format="html",
            country="us",
            wait_for=".content",
        )

        assert "html" in result.lower()
        mock_client.universal_scrape.assert_called_once_with(
            url="https://example.com",
            js_render=True,
            output_format="html",
            country="us",
            wait_for=".content",
        )


class TestThordataProxyTool:
    """Tests for ThordataProxyTool."""

    def test_tool_name(self):
        """Test tool has correct name."""
        tool = ThordataProxyTool()
        assert tool.name == "thordata_proxy_request"

    def test_tool_description(self):
        """Test tool has description."""
        tool = ThordataProxyTool()
        assert "proxy" in tool.description.lower()

    @patch("thordata_langchain_tools.proxy_tool.ThordataClient")
    def test_run_basic_request(self, mock_client_class):
        """Test basic proxy request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"origin": "1.2.3.4"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        tool = ThordataProxyTool()
        result = tool._run(url="https://httpbin.org/ip")

        assert "1.2.3.4" in result
