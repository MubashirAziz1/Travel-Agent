"""Graph nodes: enhanced_travel_analysis, call_model, synthesize_results, generate_travel_packages."""

import json
from langchain_core.messages import AIMessage, ToolMessage

from backend.config import llm
from ..models import FlightOption, HotelOption
from ..tools.flights import search_flights
from ..tools.hotels import search_and_compare_hotels
from ..tools.activities import search_activities_by_city
from ..tools.crm import send_to_hubspot
from ..utils.helpers import get_representative_options, calculate_default_dates
from ..state import TravelAgentState


async def synthesize_results_node(state: TravelAgentState) -> dict:
    """Package generation and final response node."""
    print("NODE: Synthesis & Response")

    tool_results = {}
    for msg in state['messages']:
        if isinstance(msg, ToolMessage):
            try:
                tool_results[msg.name] = msg.content
            except Exception as e:
                print(f"Failed to process {msg.name}: {e}")
                tool_results[msg.name] = "[]"

    travel_plan = state.get('travel_plan')

    all_options = {'flights': [], 'hotels': []}
    for tool_name, content in tool_results.items():
        try:
            if content and content != "[]":
                parsed_data = json.loads(content)
                if tool_name == "search_flights":
                    all_options['flights'] = [FlightOption.model_validate(f) for f in parsed_data]
                elif tool_name == "search_and_compare_hotels":
                    all_options['hotels'] = [HotelOption.model_validate(h) for h in parsed_data]
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Failed to parse {tool_name}: {e}")

    packages = []
    if (travel_plan and
            travel_plan.user_intent == "full_plan" and
            travel_plan.total_budget and
            all_options['flights'] and
            all_options['hotels']):

        print("Generating travel packages")
        try:
            packages = await generate_travel_packages(travel_plan, all_options)
        except Exception as e:
            print(f"Package generation failed: {e}")
            packages = []

    synthesis_prompt = ""
    hubspot_recommendations = {}

    if packages:
        print(f"Preparing response with {len(packages)} packages")
        synthesis_prompt = f"""You are an AI travel assistant. Present these custom travel packages professionally.

**GENERATED PACKAGES:**
{json.dumps([p.model_dump() for p in packages], indent=2)}

**YOUR TASK:**
- Start with a warm greeting
- Present ALL packages with clear details (flight, hotel, activities)
- Highlight the "Balanced" package as recommended
- End with clear call to action
"""
        hubspot_recommendations = {"packages": [p.model_dump() for p in packages]}
    else:
        print("Preparing response with search results")
        has_results = any(all_options.values())

        if has_results:
            tool_results_for_prompt = {
                "flights": [f.model_dump() for f in all_options.get('flights', [])],
                "hotels": [h.model_dump() for h in all_options.get('hotels', [])],
                "activities": [a.model_dump() for a in all_options.get('activities', [])],
            }
            synthesis_prompt = f"""You are an AI travel assistant. Present these search results clearly.

**SEARCH RESULTS:**
{json.dumps(tool_results_for_prompt, indent=2)}

Organize and present options in a user-friendly format.
"""
            hubspot_recommendations = tool_results_for_prompt
        else:
            synthesis_prompt = """You are an AI travel assistant.
Apologize that no options were found and offer to help refine the search."""
            hubspot_recommendations = {"error": "No results found"}

    try:
        final_response = await llm.ainvoke(synthesis_prompt)
    except Exception as e:
        print(f"Response generation failed: {e}")
        final_response = AIMessage(content="I apologize, but I encountered an issue generating your recommendations. Please try again.")

    if state.get('customer_info') and travel_plan:
        try:
            await send_to_hubspot.ainvoke({
                'customer_info': state['customer_info'],
                'travel_plan': travel_plan,
                'recommendations': hubspot_recommendations,
                'original_request': state.get('original_request', ''),
            })
        except Exception as e:
            print(f"CRM integration warning: {e}")

    return {
        "messages": [final_response],
        "current_step": "complete",
    }