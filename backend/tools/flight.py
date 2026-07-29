"""Duffel flight search tool."""

import asyncio
import logging
from typing import List, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from backend.config import DuffelSettings
from ..services.duffel.client import DuffelClient
from ..agent.models import FlightOption
from ..utils import find_closest_flight, location_to_airport_code
from backend.config import llm

logger = logging.getLogger(__name__)


class FlightSearchArgs(BaseModel):
    """Flight search parameters."""
    originLocationCode: str = Field(description="Departure city IATA code")
    destinationLocationCode: str = Field(description="Arrival city IATA code")
    departureDate: str = Field(description="Departure date (YYYY-MM-DD)")
    returnDate: Optional[str] = Field(description="Return date (YYYY-MM-DD)")
    adults: int = Field(description="Number of adult passengers", default=1)


@tool(args_schema=FlightSearchArgs)
async def search_flights(
    originLocationCode: str,
    destinationLocationCode: str,
    departureDate: str,
    returnDate: Optional[str] = None,
    adults: int = 1,
    travelClass: Optional[str] = None,
    departureTime: Optional[str] = None,
) -> List[FlightOption]:
    """Search for flight offers using Duffel API."""
    print(f"Flight search: {originLocationCode} -> {destinationLocationCode}")

    if not DuffelSettings or not DuffelSettings.api_key:
        return [FlightOption(
            airline="Error",
            price="N/A",
            departure_time="N/A",
            arrival_time="Duffel client not available"
        )]
    
    try:
        origin_task = location_to_airport_code(originLocationCode)
        destination_task = location_to_airport_code(destinationLocationCode)
        actual_origin, actual_destination = await asyncio.gather(origin_task, destination_task)
        print(f"Converted to: {actual_origin} -> {actual_destination}")
    except Exception as e:
        print(f"Location conversion failed: {e}")
        return [FlightOption(airline="Location Error", price="N/A", departure_time="N/A", arrival_time=str(e))]

    
    
    try:
        client = DuffelClient(settings=DuffelSettings)

        # # Map cabin class to Duffel format
        cabin_class = None
        # if travelClass and travelClass.upper() in ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]:
        #     cabin_class = travelClass.lower()

        search_params = {
            'origin': actual_origin,
            'destination': actual_destination,
            'departure_date': departureDate,
            'return_date': returnDate,
            'adults': adults,
            'cabin_class': cabin_class,
            'max_connections': 1,
        }

        p
        top_3_offers = [item['option_object'] for item in final_sorted_offers[:3]]rint(f"Calling Duffel with params: {search_params}")

        all_offers = await client.search_offers(**search_params)

        if not all_offers:
            return []

        final_sorted_offers = sorted(all_offers, key=lambda x: x['price_numeric'])

        # time_windows = {
        #     "morning": "06:00-12:00",
        #     "afternoon": "12:00-18:00",
        #     "evening": "18:00-23:59",
        # }
        # if departureTime and departureTime.lower() in time_windows:
        #     print(f"Re-sorting by proximity to {departureTime} window")
        #     window_start = time_windows[departureTime.lower()].split("-")[0]
        #     final_sorted_offers = find_closest_flight(final_sorted_offers, window_start)

        if departureTime and ":" in departureTime:
            print(f"Re-sorting by proximity to {departureTime}")
            final_sorted_offers = find_closest_flight(final_sorted_offers, departureTime)
        top_3_offers = [item['option_object'] for item in final_sorted_offers[:3]]

        print(f"Returning top 3 of {len(all_offers)} flight options")
        return top_3_offers

    except Exception as e:
        print(f"Flight search error: {e}")
        return [FlightOption(
            airline="System Error",
            price="N/A",
            departure_time="N/A",
            arrival_time=str(e)
        )]