import asyncio
import os
import sys

from dotenv import load_dotenv

from src.agent.specialists import create_researcher, create_analyst, create_writer
# from src.observability.tracer import tracer # TODO: Unleash the tracer
# from src.observability.cost_tracker import CostTracker

# Load environment variables
load_dotenv()

async def main():
    """
    Main entry point for the AI Agent system.
    """
    # 1. Get the query
    if len(sys.argv) < 2:
        print("Usage: python -m src.main \"Your research query\"")
        sys.exit(1)

    query = sys.argv[1]
    print(f"Starting research on: {query}")

    # TODO: Initialize your agents here
    # Use the Factory Pattern to create agents.
    # The 'create_researcher' function (and others) acts as a factory, encapsulating 
    # the creation logic (prompt selection, tool assignment) for each agent type.
    # researcher = create_researcher()
    # analyst = create_analyst()
    # writer = create_writer()

    # TODO: Create the orchestrator or main loop
    # In the final project, we might use an ArchitectureDecisionEngine here to decide
    # which agent architecture (Single vs Multi-Agent) to run. 
    # For this starter, you can implement a simple linear chain (Researcher -> Analyst -> Writer)
    # or a loop.
    # ...

    print("Project Starter: Not implemented yet. Check the TODOs!")

if __name__ == "__main__":
    asyncio.run(main())
