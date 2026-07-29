"""Helper functions: offer parsing, time sorting, default dates, representative sampling."""

from datetime import datetime, timedelta
from typing import List, Dict


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
    IATA Code:
    """

    try:
        response = await llm.ainvoke(conversion_prompt)
        airport_code = response.content.strip().upper()

        if len(airport_code) == 3 and airport_code.isalpha():
            return airport_code
        codes = re.findall(r'[A-Z]{3}', response.content.upper())
        return codes[0] if codes else location_name

    except Exception as e:
        print(f"Location conversion failed for {location_name}: {e}")
        return location_name

def find_closest_flight(offers: List[Dict], target_time_str: str) -> List[Dict]:
    """Sort flights by proximity to target departure time."""
    try:
        target_hour = int(target_time_str.split(':')[0])
    except (ValueError, IndexError):
        print(f"Invalid target time: {target_time_str}")
        return offers

    def get_time_difference(prepared_offer):
        try:
            departure_dt = datetime.fromisoformat(prepared_offer['option_object'].departure_time)
            return abs(departure_dt.hour - target_hour)
        except (ValueError, TypeError):
            return float('inf')

    return sorted(offers, key=get_time_difference)


def get_representative_options(options: List, key_attr: str, max_items: int = 7) -> List:
    """Select representative sample (cheapest, mid-range, priciest)."""
    if not options or len(options) <= max_items:
        return options

    try:
        if key_attr == 'price':
            options.sort(key=lambda x: float(getattr(x, key_attr).split(' ')[0]))
    except (ValueError, TypeError, IndexError):
        pass

    cheapest = options[:2]
    most_expensive = options[-2:]
    mid_index = len(options) // 2
    mid_range = options[mid_index - 1: mid_index + 2]

    representative_sample = cheapest + mid_range + most_expensive
    seen = set()
    unique_sample = []
    for item in representative_sample:
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

