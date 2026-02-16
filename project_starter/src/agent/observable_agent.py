#import asyncio
#import json
import os
#import time

import structlog
from litellm import acompletion#, completion_cost
# from pydantic import ValidationError

from src.observability.cost_tracker import CostTracker
from src.observability.loop_detector import AdvancedLoopDetector
from src.observability.tracer import AgentTracer # AgentStep, ToolCallRecord
from src.tools.registry import registry

logger = structlog.get_logger()

class ObservableAgent:
    """
    Production-grade agent with full observability.
    
    This agent implements the ReAct pattern (Reasoning + Acting) but enhances it 
    with "Observability" - the ability to track, trace, and debug the agent's 
    internal state and actions.
    """
    def __init__(
        self,
        model: str = None,
        max_steps: int = 10,
        agent_name: str = "ObservableAgent",
        verbose: bool = True,
        system_prompt: str = None,
        tools: list = None,
    ):
        self.model = model or os.getenv("MODEL_NAME", "gpt-4o")
        self.max_steps = max_steps
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools if tools is not None else registry.get_all_tools()

        # TODO: Initialize observability components
        # Observability includes:
        # 1. Tracing: Recording every step (reasoning, tool calls, results).
        # 2. Loop Detection: Preventing the agent from repeating the same actions.
        # 3. Cost Tracking: Monitoring token usage and cost.
        # self.tracer = ...
        # self.loop_detector = ...
        # self.cost_tracker = ...
        self.tracer = AgentTracer(verbose=verbose)
        self.loop_detector = AdvancedLoopDetector(stagnation_window=5, exact_threshold=2)
        self.cost_tracker = CostTracker()
        self.messages = []

    async def run(self, user_query: str) -> dict:
        """Execute the agent loop with full observability."""
        # TODO: Implement the agent loop
        # 1. Start trace and cost tracking
        # 2. Loop until max_steps
        # 3. Call LLM (using acompletion)
        # 4. Log completion and cost
        # 5. Handle tool calls (execute in parallel?)
        # 6. Check for loops
        # 7. Return final answer
        # 8. Handle errors and end trace
        try:
            # 1. Start trace and cost tracking
            trace_id = self.tracer.start_trace(agent_name=self.agent_name, query=user_query, model=self.model)
            self.cost_tracker.start_query(user_query)
            
            # Initialize messages with system prompt and user query
            self.messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_query}
            ]
            
            # 2. Loop until max_steps
            for step in range(1, self.max_steps + 1):
                self.tracer.log_step(step, "calling_llm")
                
                # 3. Call LLM (using acompletion)
                response = await acompletion(
                    model=self.model,
                    messages=self.messages,
                    tools=self._format_tools() if self.tools else None,
                )
                
                # 4. Log completion and cost
                self.cost_tracker.log_completion(step, response)
                self.tracer.log_llm_response(step, response)
                
                # Get the assistant message
                assistant_message = response.choices[0].message
                self.messages.append(assistant_message.model_dump())
                
                # Check if we're done (no tool calls)
                if not assistant_message.tool_calls:
                    final_answer = assistant_message.content
                    self.tracer.log_final_answer(final_answer)
                    
                    # 8. End trace
                    self.tracer.end_trace(trace_id=trace_id,output=final_answer,status="completed")
                    self.cost_tracker.end_query()
                    
                    return {
                        "answer": final_answer,
                        "steps": step,
                        "cost": self.cost_tracker.get_total_cost(),
                        "trace": self.tracer.get_trace(self.tracer._active_trace_id)
                    }
                
                # 5. Handle tool calls (execute in parallel)
                tool_calls = assistant_message.tool_calls
                self.tracer.log_tool_calls(step, tool_calls)
                
                # 6. Check for loops
                tool_signatures = [f"{tc.function.name}({tc.function.arguments})" 
                                 for tc in tool_calls]
                if self.loop_detector.detect_loop(tool_signatures):
                    error_msg = "Loop detected: Agent is repeating the same actions"
                    logger.error(error_msg)
                    self.tracer.end_trace(trace_id=self.tracer._active_trace_id,output=error_msg,status="failed",error="loop_detected")
                    self.cost_tracker.end_query()
                    return {
                        "answer": error_msg,"steps": step, 
                        "cost": self.cost_tracker._current_query.total_cost_usd if self.cost_tracker._current_query else 0.0,
                        "error": "loop_detected","trace": self.tracer.get_trace(self.tracer._active_trace_id)
                        }
                # Execute tool calls in parallel
                tool_results = await self._execute_tools_parallel(tool_calls)
                
                # Add tool results to messages
                for tool_result in tool_results:
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_result["tool_call_id"],
                        "content": tool_result["content"]
                    })
                
                self.tracer.log_tool_results(step, tool_results)
            
            # Max steps reached
            error_msg = f"Max steps ({self.max_steps}) reached without completion"
            print(error_msg)
            self.tracer.end_trace(
            trace_id=self.tracer._active_trace_id,
            output=error_msg,
            status="failed",
            error="max_steps_reached"
            )
            self.cost_tracker.end_query()
            return {
            "answer": error_msg,
            "steps": self.max_steps,
            "cost": self.cost_tracker._current_query.total_cost_usd if self.cost_tracker._current_query else 0.0,
            "error": "max_steps_reached",
            "trace": self.tracer.get_trace(self.tracer._active_trace_id)
            }

        except Exception as e:
            # 8. Handle errors and end trace
            error_msg = f"Error during execution: {str(e)}"
            print(f"Error: {str(e)}")
            self.tracer.end_trace(
                trace_id=self.tracer._active_trace_id,
                output=error_msg,
                status="failed",
                error=str(e)
            )
            self.cost_tracker.end_query()
            
            return {
                "answer": error_msg,
                "error": str(e),
                "cost": self.cost_tracker._current_query.total_cost_usd if self.cost_tracker._current_query else 0.0,
                "trace": self.tracer.get_trace(self.tracer._active_trace_id)
            }