from typing import Dict, Any, Optional
import time

from saras_engine.src.memory.session_store import SessionStore
from saras_engine.src.memory.long_term_memory import LongTermMemory


class ManagerAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key

        # minimal required memory
        self.session = SessionStore(max_messages=8)
        self.long_memory = LongTermMemory()

    def handle_request(self, task: str, rag_context: Optional[str] = None) -> Dict[str, Any]:
        start = time.time()

        # store last message
        self.session.add_message("user", task)

        # define mode
        mode = "RAG" if rag_context else "Non-RAG"

         
        # ResearchAgent
         
        from saras_engine.src.agents.researcher_agent import ResearcherAgent
        researcher = ResearcherAgent(api_key=self.api_key)

        research_result = researcher.run_research(task)

         
        # Prepare writer context
         
        writer_context = {
            "research_summary": research_result.get("summary", ""),
            "keywords": research_result.get("keywords", []),
            "final_answer_context": rag_context or ""
        }

         
        # WriterAgent
         
        from saras_engine.src.agents.writer_agent import WriterAgent
        writer = WriterAgent(api_key=self.api_key)

        writer_output = writer.write_article(
            task_prompt=task,
            context=writer_context,
            mode=mode
        )

         
        # Store a simple fact
         
        self.long_memory.store_fact(task, f"Solved: {task}")

         
        # final structure (internal)
         
        elapsed = round(time.time() - start, 3)

        return {
            "status": "success",
            "task": task,
            "mode": mode,
            "research_agent_output": research_result,
            "writer_agent_output": writer_output,
            "time_taken": elapsed
        }
