import asyncio

from backend.config import DuffelSettings
from backend.services.duffel.client import DuffelClient

async def main():
    settings = DuffelSettings()  # Loads your configuration

    client = DuffelClient(settings)

    try:
        response = await client.offer_requests(
            origin="LHR",
            destination="JFK",
            departure_date="2026-07-12",
        )

        print("Success!")
        print(response)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())