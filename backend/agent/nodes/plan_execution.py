"""Graph node: plan_execute"""

import asyncio
import json
import traceback
from datetime import datetime
from typing import Dict

from langchain_core.messages import AIMessage, ToolMessage

from backend.utils import calculate_default_dates
from ..state import TravelAgentState
from ...tools.flight import search_flights


async def plan_execute(state: TravelAgentState) -> Dict:
    """Tool preparation and execution node."""

    print("NODE: Plan & Execution")

    travel_plan = state.get('travel_plan')

    if not travel_plan:
        print("No travel plan available")
        return {
            "messages": [AIMessage(content="I've understood your request, but there's no specific search I can perform. How else can I help?")],
            "current_step": "complete",
        }

    try:
        print(f"Phase 1: Preparing tools (intent: {travel_plan.user_intent})")

        tasks_and_names = []

        if travel_plan.user_intent in ["full_plan", "flights_only"] and travel_plan.origin and travel_plan.destination:
            task = search_flights.ainvoke({
                "originLocationCode": travel_plan.origin,
                "destinationLocationCode": travel_plan.destination,
                "departureDate": travel_plan.departure_date ,
                "returnDate": travel_plan.return_date,
                "adults": travel_plan.adults,
                "currencyCode": "USD",
                "travelClass": travel_plan.travel_class,
                "departureTime": travel_plan.departure_time_pref,
                "arrivalTime": travel_plan.arrival_time_pref,
            })
            tasks_and_names.append((task, "search_flights"))

        # if travel_plan.user_intent in ["full_plan", "hotels_only"] and travel_plan.destination:
        #     task = search_and_compare_hotels.ainvoke({
        #         "city_code": travel_plan.destination,
        #         "check_in_date": departure_date,
        #         "check_out_date": return_date,
        #         "adults": travel_plan.adults,
        #     })
        #     tasks_and_names.append((task, "search_and_compare_hotels"))

        if not tasks_and_names:
            print("No tools to call")
            return {
                "messages": [AIMessage(content="I've understood your request, but there's no specific search I can perform. How else can I help?")],
                "current_step": "complete",
                "travel_plan": travel_plan,
            }

        print(f"Phase 2: Executing {len(tasks_and_names)} tools in parallel")

        tasks = [task for task, name in tasks_and_names]
        tool_results = await asyncio.gather(*tasks, return_exceptions=True)
        processed_messages = []

        for i, (result, (_, tool_name)) in enumerate(zip(tool_results, tasks_and_names)):
            if isinstance(result, Exception):
                print(f"Tool {tool_name} failed: {result}")
                content = "[]"
            else:
                try:
                    content = json.dumps([item.model_dump() for item in result])
                except Exception as e:
                    print(f"Serialization failed for {tool_name}: {e}")
                    content = "[]"

            processed_messages.append(ToolMessage(
                content=content,
                name=tool_name,
                tool_call_id=f"call_{tool_name}_{i}",
            ))

        print("All tools executed")
        return {
            "messages": processed_messages,
            "current_step": "synthesizing",
            "travel_plan": travel_plan,
        }

    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        response = AIMessage(content="I apologize, but a system error occurred. Please try again.")
        return {"messages": [response], "current_step": "complete"}