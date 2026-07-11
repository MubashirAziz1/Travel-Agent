import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

import httpx

from backend.config import DuffelSettings
# from src.exceptions import (
#     DuffelAPIException,
#     DuffelAPITimeoutError,
#     DuffelAuthenticationError,
#     DuffelParseError,
#     DuffelRateLimitError,
#     DuffelValidationError,
#     OrderCreationError,
# )
# from src.schemas.duffel.models import Offer, OfferRequest, Order, PassengerRequest, SliceRequest

logger = logging.getLogger(__name__)


class DuffelClient:
    """Client for searching and booking flights via the Duffel API."""

    def __init__(self, settings: DuffelSettings):
        self._settings = settings

    @property
    def base_url(self) -> str:
        return self._settings.base_url


    async def offer_requests(
        self,
        origin: str,
        destination: str,
        departure_date: str
    ) -> dict:
        """
        Search for flights by creating an offer request and returning the offers

        Args:
            slices: One or more journey legs (one-way = 1 slice, round-trip = 2, etc.)
            passengers: Passengers to search for (defaults to a single adult)
            cabin_class: economy / premium_economy / business / first
            max_connections: Optional cap on connections per slice

        Returns:
            List of bookable Offer objects, as returned by Duffel.
        """

        if not origin:
            raise ValueError("Please add the departure city.")
        if not destination:
            raise ValueError("Please add the destination city.")
        if not departure_date:
            raise ValueError("Please add the departure date to travel.")
        
        payload = {
            "data": {
                "slices": [
                    {
                        "origin": origin,
                        "destination": destination,
                        "departure_date": departure_date
                    }
                ],
                "passengers": [
                    {
                        "type": "adult"
                    }
                ],
            }
        }

        headers = {
            "Authorization": f"Bearer {self._settings.api_key}",
            "Duffel-Version": "v2",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip",
        }
        
        url = f"{self.base_url}/air/offer_requests"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url,headers=headers,json=payload)
            response.raise_for_status()
        
        return response.json()








