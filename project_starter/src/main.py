import asyncio
#import os
import sys

from dotenv import load_dotenv

from src.agent.orchestrator import Orchestrator
from src.observability.tracer import tracer # TODO: Unleash the tracer
from src.observability.cost_tracker import CostTracker
import litellm
import time
#litellm._turn_on_debug()

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
    
    cost_tracker = CostTracker()
    start_time = time.time() 
    trace_id = tracer.start_trace(agent_name="MainAgent", query=query)
    cost_tracker.start_query(query)

    try:
        orchestrator = Orchestrator()
        result = await orchestrator.run(query)

        if "error" in result:
            print(f"Failed: {result['error']}")
            tracer.end_trace(trace_id, output="", status="failed")
        else:
            print(result["answer"])
            print(f"\nTotal Cost: ${result['cost']:.6f}")
            tracer._traces[trace_id].total_duration_ms = (time.time() - start_time) * 1000
            tracer.end_trace(trace_id, output=result["answer"], status="completed")

    except Exception as e:
        tracer.end_trace(trace_id, output="", status="failed")
        print(f"Error: {e}")
    finally:
        cost_tracker.end_query()


if __name__ == "__main__":
    asyncio.run(main())