"""Travel package and plan models."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field




class FlightOption(BaseModel):
    """Structured flight offer data."""
    airline: str = Field(description="Airline name")
    price: str = Field(description="Total flight cost")
    departure_time: str = Field(description="Departure time (YYYY-MM-DDTHH:MM:SS)")
    arrival_time: str = Field(description="Arrival time (YYYY-MM-DDTHH:MM:SS)")
    duration: Optional[str] = Field(description="Flight duration", default=None)


class TravelPackage(BaseModel):
    """Complete travel package including flight data."""
    name: str = Field(description="Package name, e.g., 'Smart Explorer'")
    grade: Literal["Budget", "Balanced", "Premium"] = Field(description="Package tier")
    total_cost: float = Field(description="Total package cost in USD")
    budget_comment: str = Field(description="Budget comparison comment")
    selected_flight: FlightOption = Field(description="Selected flight option")


class TravelPlan(BaseModel):
    """Structured travel plan extracted from user request."""
    origin: Optional[str] = Field(None, description="Origin city or airport code")
    destination: str = Field(..., description="Destination city or airport code")
    departure_date: Optional[str] = Field(None, description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD)")
    duration_days: Optional[int] = Field(None, description="Trip duration in days")
    adults: int = Field(1, description="Number of adult travelers")
    travel_class: Optional[Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]] = "ECONOMY"
    departure_time_pref: Optional[str] = Field(None, description="Preferred departure time")
    arrival_time_pref: Optional[str] = Field(None, description="Preferred arrival time")
    total_budget: Optional[float] = Field(None, description="Total budget in USD")
