import src.tools.search_tool
from src.tools.registry import registry
from src.agent.specialists import create_researcher, create_analyst, create_writer
import json
def format_answer(answer: str) -> str:
    try:
        data = json.loads(answer.strip())
        output = ""
        
        def process_dict(d, depth=0):
            result = ""
            for key, value in d.items():
                if key.startswith("/") or key.startswith("#"):
                    continue # Skip metadata keys
                if isinstance(value, str) and value.strip():
                    result += f"## {key}\n{value}\n\n"
                elif isinstance(value, list):
                    result += f"## {key}\n"
                    for item in value:
                        if isinstance(item, dict):
                            fact = item.get('fact') or item.get('Fact') or item.get('text') or str(item)
                            result += f"- {fact}\n"
                        elif isinstance(item, str):
                            result += f"- {item}\n"
                    result += "\n"
                elif isinstance(value, dict):
                    result += f"## {key}\n"
                    result += process_dict(value, depth+1)
            return result
        
        output = process_dict(data)
        return output.strip() if output else answer
    except:
        return answer

class Orchestrator:
    def __init__(self):
        self.researcher = create_researcher()
        self.analyst = create_analyst()
        self.writer = create_writer()

    async def run(self, query: str) -> dict:
        # Stage 1
        research_result = await self.researcher.run(query)
        if "Loop detected" in str(research_result.get("answer", "")):
            return {"error": "Research failed: agent stuck in loop"}
        if "error" in research_result:
            return {"error": f"Research failed: {research_result['error']}"}

        # Stage 2
        analysis_result = await self.analyst.run(
            f"Analyze these findings: {research_result['answer']}"
        )
        if "error" in analysis_result:
            return {"error": f"Analysis failed: {analysis_result['error']}"}

        # Stage 3
        writing_result = await self.writer.run(
            f"Write a report based on: {analysis_result['answer']}"
        )
        if "error" in writing_result:
            return {"error": f"Writing failed: {writing_result['error']}"}

        total_cost = (
            research_result.get("cost", 0.0) +
            analysis_result.get("cost", 0.0) +
            writing_result.get("cost", 0.0)
        )

        return {
            "answer": format_answer(writing_result["answer"]),
            "cost": total_cost,
            "stages": {
                "research": research_result["answer"],
                "analysis": analysis_result["answer"],
                "writing": writing_result["answer"],
            }
        }
        
    async def run_with_retry(self, agent, query, retries=2):
        for attempt in range(retries):
            result = await agent.run(query)
            if "error" not in result:
                return result
            print(f"Attempt {attempt+1} failed, retrying...")
        return result