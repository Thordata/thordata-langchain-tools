"""
ThordataAccountTool - LangChain tool for account management.

Check usage statistics and account balance.
"""

from __future__ import annotations

import os
from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from thordata import ThordataClient


class AccountInfoInput(BaseModel):
    """Input schema for account info."""

    start_time: Optional[int] = Field(
        default=None, description="Start timestamp (Unix time, optional)"
    )
    end_time: Optional[int] = Field(
        default=None, description="End timestamp (Unix time, optional)"
    )
    date: Optional[str] = Field(
        default=None, description="Date string (YYYY-MM-DD, optional)"
    )


class ThordataAccountTool(BaseTool):
    """
    LangChain tool for checking Thordata account information.

    Get usage statistics and account balance.

    Example:
        >>> tool = ThordataAccountTool()
        >>> info = tool.invoke({})
        >>> print(info["traffic_balance"])
    """

    name: str = "thordata_account_info"
    description: str = (
        "Get Thordata account information including usage statistics and balance. "
        "Use this to check your account status and remaining quota."
    )
    args_schema: Type[BaseModel] = AccountInfoInput

    _client: Optional[ThordataClient] = None

    def _get_client(self) -> ThordataClient:
        """Get or create the Thordata client."""
        if self._client is None:
            scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
            if not scraper_token:
                raise ValueError("THORDATA_SCRAPER_TOKEN is required")

            self._client = ThordataClient(
                scraper_token=scraper_token,
                public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
                public_key=os.getenv("THORDATA_PUBLIC_KEY"),
            )
        return self._client

    def _run(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        date: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict[str, Any]:
        """Get account information."""
        client = self._get_client()

        try:
            # Get balance (simple call, no parameters)
            balance = client.get_traffic_balance()

            # Get usage statistics using account namespace
            stats = client.account.get_usage_statistics(
                start_time=start_time,
                end_time=end_time,
                date=date,
            )

            return {
                "traffic_balance": balance,
                "usage_statistics": stats,
            }
        except Exception as e:
            # Fallback: just return balance if stats fail
            try:
                balance = client.get_traffic_balance()
                return {
                    "traffic_balance": balance,
                    "usage_statistics": None,
                    "note": "Usage statistics unavailable",
                }
            except Exception:
                return {
                    "error": str(e),
                }
