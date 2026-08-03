from backend.agent.state import TravelAgentState
from backend.agent.nodes.response import response
from langchain_core.messages import HumanMessage, ToolMessage
from backend.agent.state import TravelPlan
import asyncio


state = TravelAgentState(
    messages= [HumanMessage(content="Find me flights from New York to Paris tomorrow."),ToolMessage(content='[{"airline": "Duffel Airways", "price": "225.34 AUD", "departure_time": "2026-08-04T02:19:00", "arrival_time": "2026-08-04T16:40:00", "duration": "8 hours 21 minutes"}, {"airline": "Iberia", "price": "226.49 AUD", "departure_time": "2026-08-04T02:19:00", "arrival_time": "2026-08-04T16:40:00", "duration": "8 hours 21 minutes"}, {"airline": "Lufthansa", "price": "1564.59 AUD", "departure_time": "2026-08-04T17:30:00", "arrival_time": "2026-08-05T11:15:00", "duration": "11 hours 45 minutes"}, {"airline": "Finnair", "price": "1578.38 AUD", "departure_time": "2026-08-04T17:45:00", "arrival_time": "2026-08-05T07:20:00", "duration": "7 hours 35 minutes"}, {"airline": "Lufthansa", "price": "1595.48 AUD", "departure_time": "2026-08-04T21:50:00", "arrival_time": "2026-08-05T18:50:00", "duration": "15 hours"}, {"airline": "Lufthansa", "price": "24395.61 AUD", "departure_time": "2026-08-04T15:40:00", "arrival_time": "2026-08-05T08:45:00", "duration": "11 hours 5 minutes"}, {"airline": "Lufthansa", "price": "25471.52 AUD", "departure_time": "2026-08-04T17:30:00", "arrival_time": "2026-08-05T11:15:00", "duration": "11 hours 45 minutes"}]', name='search_flights', tool_call_id='call_search_flights_0')]
    current_step="synthesizing",
    is_continuation=True,
    travel_plan= TravelPlan(origin='New York', destination='Paris', departure_date='2026-08-04', return_date=None, duration_days=None, adults=1, travel_class='ECONOMY', departure_time_pref=None, arrival_time_pref=None, total_budget=None, user_intent='flights_only')
    )

node = asyncio.run(response(state))

print(node)
print("**************")
print("**************")

print("**************")

print(state)
