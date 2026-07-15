import asyncio
import logging
import time
import re
from typing import Any, Dict, List, Optional
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

import httpx

from backend.agent.models import FlightOption
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
    def _base_url(self) -> str:
        return self._settings.base_url
    
    def _get_headers(self) -> dict:
        """Return standard Duffel API headers."""
        return {
            "Authorization": f"Bearer {self._settings.api_key}",
            "Duffel-Version": "v2",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip",
        }


    async def search_offers(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        cabin_class: Optional[str] = None,
        max_connections: Optional[int] = None,
    ) -> List[Dict]:
        """
        Search for flights by creating an offer request and returning raw response.

        Args:
            origin: 3-letter IATA code for departure
            destination: 3-letter IATA code for arrival
            departure_date: YYYY-MM-DD
            return_date: YYYY-MM-DD for round-trip
            adults: Number of adult passengers
            cabin_class: economy / premium_economy / business / first
            max_connections: 0=direct only, 1=max 1 stop, etc.

        Returns:
            Raw JSON response from Duffel API.
        """

        if not origin:
            raise ValueError("Please add the departure city.")
        if not destination:
            raise ValueError("Please add the destination city.")
        if not departure_date:
            raise ValueError("Please add the departure date to travel.")
       
        
        slices = [{
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
        }]

        if return_date:
            slices.append({
                "origin": destination,
                "destination": origin,
                "departure_date": return_date,
            })


        passengers = []
        for i in range(adults):
            passengers.append({"type": "adult"})

        # Build payload
        payload = {
            "data": {"slices": slices,"passengers": passengers,}
               }

        if cabin_class:
            payload["data"]["cabin_class"] = cabin_class

        if max_connections is not None:
            payload["data"]["max_connections"] = max_connections

        url = f"{self._base_url}/air/offer_requests"
    
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            offer_list = response.json()

        if not offer_list.get('data', {}).get('offers'):
            print("No offers are available for that flight")
            return []
        
        all_offers = self._parse_and_prepare_offers(offer_list)
        if not all_offers:
            return []
        
        return all_offers
    


    def _parse_and_prepare_offers(self, response_data: dict) -> List[Dict]:
        """Parse Duffel flight search response into sortable format."""

        prepared_offers = []

        for offer in response_data['data']['offers']:
            try:
                price_float = float(offer['total_amount'])

                # Duffel uses 'slices' instead of 'itineraries'
                slice_item = offer['slices'][0]
                
                # Get first and last segment for departure/arrival times
                first_segment = slice_item['segments'][0]
                last_segment = slice_item['segments'][-1]

                # Use marketing carrier name as the airline (the one selling the ticket)
                airline_name = offer['owner']['name']
                time_duration = self._parse_time(slice_item.get('duration'))


                option_obj = FlightOption(
                    airline=airline_name,
                    price=f"{offer['total_amount']} {offer['total_currency']}",
                    departure_time=first_segment['departing_at'],
                    arrival_time=last_segment['arriving_at'],
                    duration=self._parse_time(time_duration),
                )

                prepared_offers.append({"price_numeric": price_float, "option_object": option_obj})
            except (ValueError, KeyError, IndexError, TypeError) as e:
                print(f"Skipping malformed flight offer: {e}")
                continue

        return prepared_offers
    

    def _parse_time(self, iso_duration_str: str) -> str:
        """
        Convert an ISO-8601 duration (e.g. PT2H30M) into a human-readable string.

        Examples:
            PT2H30M -> "2 hours 30 minutes"
            PT3H    -> "3 hours"
            PT45M   -> "45 minutes"
        """
        try:
            # Validate input
            if not iso_duration_str:
                return "Unknown duration"
            iso_duration_str = iso_duration_str.strip()

            # Match ISO-8601 duration: PT#H#M
            match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso_duration_str)

            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)

            # Handle PT (no hours/minutes specified)
            if hours == 0 and minutes == 0:
                return "0 minutes"
            parts = []
            if hours:
                parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if minutes:
                parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

            return " ".join(parts)

        except (ValueError, TypeError):
            return "Invalid duration"
        except Exception:
            # Optional: log the exception here
            return "Unknown duration"








