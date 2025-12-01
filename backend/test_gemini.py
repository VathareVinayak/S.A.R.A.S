import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from saras_engine.src.services.gemini_client import generate_text_flash

if __name__ == "__main__":
    print("Testing Gemini Flash...")
    res = generate_text_flash("What is AI?")
    print(res)
