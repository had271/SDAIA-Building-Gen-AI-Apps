from src.agent.observable_agent import ObservableAgent
from src.tools.registry import registry
from dotenv import load_dotenv
import os
load_dotenv()
DEFAULT_MODEL = os.getenv("MODEL_NAME", "ollama/llama3.2")

def create_researcher(model: str = DEFAULT_MODEL, max_steps: int = 15):
    """
    The Researcher: finds, retrieves, and extracts information.
    
    This function implements the Factory Pattern, returning a configured ObservableAgent
    specialized for research tasks.
    """
    # TODO: Implement this factory
    # 1. Define system prompt (e.g. "You are a world-class researcher...")
    # 2. Get research tools from registry (e.g. registry.get_tools_by_category("research"))
    # 3. Create and return ObservableAgent with these tools and prompt
    RESEARCHER_PROMPT = """You are a researcher. Use the search_web tool to find information.
    After getting the search results, summarize what you found in plain text.
    - Call search_web once with the user's query.
    - Read the results carefully.
    - Write a plain text summary of the findings with sources.
    - Do NOT return JSON. Write normal sentences."""
    research_tools = registry.get_tools_by_category("research")
    return ObservableAgent(
        model=model,
        max_steps=max_steps,
        agent_name="Researcher",
        verbose=True,
        system_prompt=RESEARCHER_PROMPT,
        tools=research_tools
    )


def create_analyst(model: str = DEFAULT_MODEL, max_steps: int = 20):
    """
    The Analyst: evaluates, cross-references, and identifies patterns.
    """
    # TODO: Implement this factory
    ANALYST_PROMPT = """You are an analyst. Read the given information and extract key points.
    - List the main facts.
    - Note if anything is unclear or missing.
    - Rate each fact: High / Medium / Low confidence.
    - Be concise."""

    # Get analysis tools from registry
    analysis_tools = registry.get_tools_by_category("analysis")
    
    return ObservableAgent(
        model=model,
        max_steps=max_steps,
        agent_name="Analyst",
        verbose=True,
        system_prompt=ANALYST_PROMPT,
        tools=analysis_tools
    )

def create_writer(model: str = DEFAULT_MODEL, max_steps: int = 4):
    """
    The Writer: synthesizes analysis into polished, readable output.
    """
    # TODO: Implement this factory
    WRITER_PROMPT= """You are a writer. Write a clear and direct answer to the user's question using the verified key points.
    Keep the answer concise.

    Rules:
    - Write normal sentences, NOT JSON.
    - Start directly with the content.
    - Do not write a report."""
    writing_tools = registry.get_tools_by_category("Writing")
    return ObservableAgent(
        model=model,
        max_steps=max_steps,
        agent_name="Writing",
        verbose=True,
        system_prompt=WRITER_PROMPT,
        tools=writing_tools
    )
