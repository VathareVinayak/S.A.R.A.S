import sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from saras_engine.src.services.gemini_client import generate_text_flash

prompt = """
Return ONLY valid JSON. No text outside JSON.

{
  "title": "string",
  "summary": "string"
}

Fill in the values based on: Explain Artificial Intelligence simply.
"""

res = generate_text_flash(prompt)
print(res["output_text"])
