"""
ThordataProxyTool - LangChain tool for proxy requests.

Make HTTP requests through Thordata's proxy network with geo-targeting.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Type

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import ThordataClient, ProxyConfig


class ProxyRequestInput(BaseModel):
    """Input schema for proxy requests."""
    
    url: str = Field(
        description="The URL to request."
    )
    country: Optional[str] = Field(
        default=None,
        description="Country code for geo-targeting (e.g., 'us', 'de', 'jp')."
    )
    state: Optional[str] = Field(
        default=None,
        description="State for more specific targeting (e.g., 'california')."
    )
    city: Optional[str] = Field(
        default=None,
        description="City for most specific targeting (e.g., 'seattle')."
    )


class ThordataProxyTool(BaseTool):
    """
    LangChain tool for making geo-targeted HTTP requests via Thordata proxy.
    
    Use this to fetch content from a specific geographic location,
    useful for testing geo-restricted content or localized search results.
    
    Example:
        >>> tool = ThordataProxyTool()
        >>> response = tool.invoke({
        ...     "url": "https://httpbin.org/ip",
        ...     "country": "jp"
        ... })
        >>> print(response)  # Shows Japanese IP
    """
    
    name: str = "thordata_proxy_request"
    description: str = (
        "Make an HTTP request through Thordata's proxy network. "
        "Supports geo-targeting by country, state, and city. "
        "Use this to access content from a specific location."
    )
    args_schema: Type[BaseModel] = ProxyRequestInput
    
    _client: Optional[ThordataClient] = None
    
    def _get_client(self) -> ThordataClient:
        """Get or create the Thordata client."""
        if self._client is None:
            scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
            if not scraper_token:
                raise ValueError(
                    "THORDATA_SCRAPER_TOKEN environment variable is required."
                )
            
            self._client = ThordataClient(
                scraper_token=scraper_token,
                public_token=os.getenv("THORDATA_PUBLIC_TOKEN", ""),
                public_key=os.getenv("THORDATA_PUBLIC_KEY", ""),
            )
        return self._client
    
    def _run(
        self,
        url: str,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Make the proxy request."""
        client = self._get_client()
        
        try:
            # Build proxy config if geo-targeting specified
            proxy_config = None
            if country or state or city:
                username = os.getenv("THORDATA_USERNAME", "")
                password = os.getenv("THORDATA_PASSWORD", "")
                
                if username and password:
                    proxy_config = ProxyConfig(
                        username=username,
                        password=password,
                        country=country,
                        state=state,
                        city=city,
                    )
            
            response = client.get(url, proxy_config=proxy_config, timeout=30)
            response.raise_for_status()
            
            # Try to return JSON if possible, otherwise text
            try:
                return str(response.json())
            except Exception:
                return response.text[:50000]  # Limit response size
            
        except Exception as e:
            return f"Error requesting {url}: {str(e)}"