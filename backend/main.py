from typing import Optional
from contextlib import asynccontextmanager


import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

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


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
