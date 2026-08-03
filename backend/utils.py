"""Helper functions: offer parsing, time sorting, default dates, representative sampling."""

from datetime import datetime, timedelta
from typing import List, Dict
from backend.config import llm
import re

from backend.agent.models import FlightOption, TravelPlan

def format_departure_time(departure_str: str) -> str:
    if not departure_str or not isinstance(departure_str, str):
        return "Unknown"
    
    try:
        dt = datetime.fromisoformat(departure_str)
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return "Unknown"
    

async def location_to_airport_code(location_name: str) -> str:
    """Convert location name to IATA airport code using LLM."""
    if not location_name:
        return ""

    if len(location_name) == 3 and location_name.isalpha() and location_name.isupper():
        return location_name

    conversion_prompt = f"""
    Convert this location to the main international airport IATA code.

    Examples:
    - "Seoul" -> "ICN"
    - "Tokyo" -> "NRT"
    - "Paris" -> "CDG"
    - "New York" -> "JFK"
    - "London" -> "LHR"

    Location: "{location_name}"
    
    Output only the three-letter IATA airport code. Do not include any additional text.
    """

    try:
        response = await llm.ainvoke(conversion_prompt)
        airport_code = response.content[0]["text"]

        return airport_code
    except Exception as e:
        print(f"Location conversion failed for {location_name}: {e}")
        return location_name

# def find_closest_flight(offers: List[Dict], target_time_str: str) -> List[Dict]:
#     """Sort flights by proximity to target departure time."""
#     try:
#         target_hour = int(target_time_str.split(':')[0])
#     except (ValueError, IndexError):
#         print(f"Invalid target time: {target_time_str}")
#         return offers

#     def get_time_difference(prepared_offer):
#         try:
#             departure_dt = datetime.fromisoformat(prepared_offer['option_object'].departure_time)
#             return abs(departure_dt.hour - target_hour)
#         except (ValueError, TypeError):
#             return float('inf')

#     return sorted(offers, key=get_time_difference)


def get_representative_options(prepared_offers: List[Dict], key_attr: str, max_items: int = 7) -> List:
    """Select representative sample (cheapest, mid-range, priciest)."""
    if not prepared_offers or len(prepared_offers) <= max_items:
        return [item["option_object"] for item in prepared_offers]

    cheapest = [item["option_object"] for item in prepared_offers[:2]]  

    most_expensive = [item["option_object"] for item in prepared_offers[-2:]]

    mid = len(prepared_offers) // 2
    mid_range = [
        item["option_object"]
        for item in prepared_offers[mid - 1: mid + 2]
    ]

    representative_sample = cheapest + mid_range + most_expensive
    seen = set()
    unique_sample = []
    for item in representative_sample:
        try:
            # Extract numeric price (e.g., "250 USD" -> 250.0)
            val = float(getattr(item, key_attr).split()[0])
        except (ValueError, AttributeError, IndexError):
            # Fallback to original attribute if parsing fails
            val = getattr(item, key_attr)

        if val not in seen:
            unique_sample.append(item)
            seen.add(val)
    return unique_sample


def calculate_default_dates(travel_plan: TravelPlan) -> tuple:
    """Calculate reasonable default dates for searches."""
    today = datetime.now()
    default_checkin = today + timedelta(days=30)
    default_checkout = default_checkin + timedelta(days=3)

    departure_date = travel_plan.departure_date
    return_date = travel_plan.return_date

    if not departure_date:
        departure_date = default_checkin.strftime('%Y-%m-%d')

    if not return_date:
        if travel_plan.duration_days:
            try:
                dep_dt = datetime.strptime(departure_date, '%Y-%m-%d')
                return_dt = dep_dt + timedelta(days=travel_plan.duration_days)
                return_date = return_dt.strftime('%Y-%m-%d')
            except ValueError:
                return_date = default_checkout.strftime('%Y-%m-%d')
        else:
            return_date = default_checkout.strftime('%Y-%m-%d')

    return departure_date, return_date



