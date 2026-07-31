from typing import Optional
from contextlib import asynccontextmanager


import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from routers import ping


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Travel AI Assistant - Server Starting")
    print("Agent graph initialized")
    print("CORS configured")
    print("Ready to accept requests")

    yield

    # Shutdown
    print("Server shutting down")

app = FastAPI(
    title = "Travel AI Assistant API",
    description="Async multi-agent system for intelligent travel planning",
    version="1.0.0",
    lifespan=lifespan
    )

# In-memory job store (replace with Redis for production scale)
jobs = {}

# In-memory customer data (replace with database for production)
customer_data = {}


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_agent_in_background(task_id: str, thread_id: str, message: str, is_continuation: bool = False):
    """Execute agent graph in background to prevent request timeout."""
    print(f"Background task {task_id} started (continuation: {is_continuation})")

    try:
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "messages": [HumanMessage(content=message)],
            "is_continuation": is_continuation,
        }

        if thread_id in customer_data:
            initial_state["customer_info"] = customer_data[thread_id]
            initial_state["current_step"] = "info_collected"
            print(f"Using stored customer info for thread {thread_id}")
        else:
            initial_state["current_step"] = "initial"

        final_state = await agent_graph.ainvoke(initial_state, config)

        last_message = final_state['messages'][-1]
        reply = str(last_message.content) if last_message.content else "I've processed the information."

        result_data = {"status": "completed", "result": {"reply": reply}}

        if final_state.get('form_to_display'):
            result_data["form_to_display"] = final_state['form_to_display']

        jobs[task_id] = result_data
        print(f"Background task {task_id} completed")

    except Exception as e:
        traceback.print_exc()
        jobs[task_id] = {"status": "failed", "result": {"error": str(e)}}
        print(f"Background task {task_id} failed: {e}")

@app.get("/", tags=["Status"])
def root():
    """Root endpoint - health check."""
    return {
        "status": "ok",
        "service": "Travel AI Assistant",
        "architecture": "async",
        "version": "1.0.0",
    }

app.include_router(ping.router)



if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
