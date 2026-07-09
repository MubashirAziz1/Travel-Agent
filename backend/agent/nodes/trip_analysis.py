"""Graph node: trip_analysis. """

import traceback
from datetime import datetime
from langchain_core.messages import AIMessage

from backend.config import llm
from ..models import TravelPlan
from ..state import TravelAgentState


async def trip_analysis(state: TravelAgentState) -> dict:
    """First entry point: analyzes user request and creates travel plan."""

    print("NODE: Travel Analysis on user request")

    is_continuation = state.get("is_continuation", False)

    if (not is_continuation and
            not state.get('customer_info') and
            state.get('current_step') in [None, "initial"] and
            len(state.get('messages', [])) <= 1):

        return {
            "messages": [],
            "current_step": "collecting_info",
            "form_to_display": "customer_info",
            "original_request": state['messages'][-1].content,
        }

    user_request = state['messages'][-1].content
    customer_info = state.get('customer_info', {})

    try:
        print("Phase 1: Analyzing request")
        analysis_prompt = f"""
        You are a world-class travel analyst AI. Extract structured trip information
        from the user's request and output valid JSON matching the provided schema.

        **User Request:** "{user_request}"

        **Today's Date:** {datetime.now().strftime('%Y-%m-%d')}

        **Instructions:**

        1. **Determine User Intent (`user_intent`):**
            - "full_plan": Combination of flights and hotels
            - "flights_only": Only asking for flights
            - "hotels_only": Only asking for hotels

        2. **Extract Core Details:**
            - `origin`: Starting location (can be null)
            - `destination`: Final destination (mandatory)
            - `departure_date` & `return_date`: Calculate absolute dates in YYYY-MM-DD format
            - `duration_days`: Calculate days between departure and return
            - `adults`: Number of travelers (default 1)

        3. **Extract Preferences:**
            - `travel_class`: Look for "business", "first class", etc. (default "ECONOMY")
            - `departure_time_pref` & `arrival_time_pref`: Look for time preferences
            - `total_budget`: Extract monetary value as float

        **CRITICAL: Output MUST be valid JSON matching this schema:**
        {TravelPlan.model_json_schema()}

        **JSON Output:**
        """

        response = await llm.ainvoke(analysis_prompt)

        content = response.content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()

        travel_plan = TravelPlan.model_validate_json(content)
        print(f"Travel plan extracted: intent={travel_plan.user_intent}")

        if customer_info.get('budget'):
            try:
                budget_str = customer_info['budget'].upper().replace("USD", "").replace("$", "").strip()
                travel_plan.total_budget = float(budget_str)
                print(f"Budget injected: ${travel_plan.total_budget}")
            except (ValueError, TypeError):
                print(f"Could not parse budget: {customer_info.get('budget')}")

        return {
            "travel_plan": travel_plan,
            "current_step": "analysis_complete",
        }

    except ValueError as e:
        print(f"Analysis failed: {e}")
        response = AIMessage(content="I'm sorry, I had trouble understanding your request. Could you rephrase it?")
        return {"messages": [response], "current_step": "complete"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        response = AIMessage(content="I apologize, but a system error occurred. Please try again.")
        return {"messages": [response], "current_step": "complete"}

