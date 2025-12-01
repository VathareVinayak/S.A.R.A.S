from typing import Dict, Any

from saras_engine.src.tools.google_search import search as google_search
from saras_engine.src.tools.extract_keywords import extract_keywords


class ResearcherAgent:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def run_research(self, query: str) -> Dict[str, Any]:
        # mock search results
        results = google_search(query=query)

        # keyword extraction
        summary_text = results.get("top_snippet", "")
        keywords = extract_keywords(summary_text)

        return {
            "summary": summary_text,
            "keywords": keywords,
            "results": results.get("results", [])
        }
