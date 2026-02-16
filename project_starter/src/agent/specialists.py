# from src.agent.observable_agent import ObservableAgent
# from src.tools.registry import registry

def create_researcher(model: str = "gpt-4o", max_steps: int = 15):
    """
    The Researcher: finds, retrieves, and extracts information.
    
    This function implements the Factory Pattern, returning a configured ObservableAgent
    specialized for research tasks.
    """
    # TODO: Implement this factory
    # 1. Define system prompt (e.g. "You are a world-class researcher...")
    # 2. Get research tools from registry (e.g. registry.get_tools_by_category("research"))
    # 3. Create and return ObservableAgent with these tools and prompt
    pass

def create_analyst(model: str = "gpt-4o", max_steps: int = 20):
    """
    The Analyst: evaluates, cross-references, and identifies patterns.
    """
    # TODO: Implement this factory
    pass

def create_writer(model: str = "gpt-4o", max_steps: int = 4):
    """
    The Writer: synthesizes analysis into polished, readable output.
    """
    # TODO: Implement this factory
    pass
