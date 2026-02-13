"""
ThordataTaskTool - LangChain tool for Web Scraper Tasks.

Supports running pre-built scraping tasks for ecommerce, social media, etc.
"""

from __future__ import annotations

import os
from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import ThordataClient


class TaskRunInput(BaseModel):
    """Input schema for task execution."""

    tool_key: str = Field(
        description="Tool key (e.g., 'amazon.product_by_url', 'youtube.video_info')"
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Task parameters as dictionary",
    )


class ThordataTaskTool(BaseTool):
    """
    LangChain tool for running Thordata Web Scraper tasks.

    Supports various pre-built tools for:
    - Ecommerce (Amazon, eBay, etc.)
    - Social media (YouTube, Instagram, etc.)
    - Travel (Booking, Airbnb, etc.)
    - Professional (LinkedIn, etc.)

    Example:
        >>> tool = ThordataTaskTool()
        >>> result = tool.invoke({
        ...     "tool_key": "amazon.product_by_url",
        ...     "parameters": {"url": "https://amazon.com/product/..."}
        ... })
    """

    name: str = "thordata_run_task"
    description: str = (
        "Run a Thordata Web Scraper task. "
        "Supports ecommerce, social media, travel, and professional tools. "
        "Use this for specialized data extraction from specific platforms."
    )
    args_schema: Type[BaseModel] = TaskRunInput

    _client: Optional[ThordataClient] = None

    def _get_client(self) -> ThordataClient:
        """Get or create the Thordata client."""
        if self._client is None:
            scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
            public_token = os.getenv("THORDATA_PUBLIC_TOKEN")
            public_key = os.getenv("THORDATA_PUBLIC_KEY")

            if not scraper_token:
                raise ValueError("THORDATA_SCRAPER_TOKEN is required")

            self._client = ThordataClient(
                scraper_token=scraper_token,
                public_token=public_token,
                public_key=public_key,
            )
        return self._client

    def _run(
        self,
        tool_key: str,
        parameters: dict[str, Any] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict[str, Any]:
        """Execute the task."""
        if parameters is None:
            parameters = {}

        client = self._get_client()

        try:
            # Use SDK's run_tool_by_key method
            task_id = client.run_tool_by_key(tool_key, parameters)
            return {
                "task_id": task_id,
                "status": "created",
                "message": f"Task {task_id} created. Use get_task_status to check progress.",
            }
        except Exception as e:
            return {
                "error": str(e),
                "tool_key": tool_key,
            }
