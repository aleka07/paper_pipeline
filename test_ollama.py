"""
Test Ollama with Nemotron-3-Nano for JSON generation.
This is an alternative to vLLM for Phase 2 (Markdown → JSON).
"""

import json
import re
import time
from pathlib import Path
from openai import OpenAI

# --- CONFIG ---
OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL_NAME = "nemotron-large-ctx"  # Custom model with 131K context (created via Modelfile)
MARKDOWN_DIR = Path("data/markdown")
OUTPUT_DIR = Path("data/output_ollama")  # Separate output for testing

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_prompt():
    """Load system prompt from prompt.md"""
    try:
        with open("prompt.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a JSON extractor for academic papers."


def clean_json_response(response_text):
    """Cleans <think> tags and markdown to extract raw JSON."""
    # Remove Chain of Thought
    clean = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
    
    # Extract from Markdown blocks if present
    json_match = re.search(r'```json\s*(.*?)\s*```', clean, re.DOTALL)
    if json_match:
        clean = json_match.group(1)
    
    return clean.strip()


def test_ollama_connection():
    """Test if Ollama is running and model is available."""
    print("🔍 Testing Ollama connection...")
    
    try:
        client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        
        # Quick test
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Say 'OK' if you're working."}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ Ollama connected! Model response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("\n💡 Make sure Ollama is running:")
        print("   ollama serve")
        print(f"   ollama pull {MODEL_NAME}")
        return False


def generate_json_from_markdown(md_path: str):
    """Generate JSON from a markdown file using Ollama."""
    md_path = Path(md_path)
    
    if not md_path.exists():
        print(f"❌ Markdown file not found: {md_path}")
        return None
    
    print(f"\n📄 Processing: {md_path.name}")
    
    # Read markdown
    with open(md_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()
    
    print(f"   📝 Markdown size: {len(markdown_text)} chars")
    
    # Load prompt
    system_prompt = load_prompt()
    
    # Extract paper ID and category from filename
    paper_id = md_path.stem
    category = md_path.parent.name
    
    # More explicit JSON-only prompt for Ollama models
    user_message = f"""PAPER ID: {paper_id}
CATEGORY: {category}

IMPORTANT: Output ONLY valid JSON. No explanations, no markdown, no text before or after the JSON.

DOCUMENT CONTENT:
{markdown_text[:30000]}

OUTPUT ONLY THE JSON:"""
    
    # Connect to Ollama
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    
    print(f"   🧠 Generating JSON with {MODEL_NAME}...")
    start_time = time.time()
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=8192,
            extra_body={
                "num_ctx": 256128  # Increase context window (default is 2048)
            }
        )
        
        elapsed = time.time() - start_time
        raw_output = completion.choices[0].message.content
        json_str = clean_json_response(raw_output)
        
        # Parse and validate
        data = json.loads(json_str)
        data['paper_id'] = paper_id
        
        # Save to output
        output_dir = OUTPUT_DIR / category
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{paper_id}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        print(f"   ✅ Saved: {output_file}")
        print(f"   ⏱️  Time: {elapsed:.1f}s")
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON Parse Error: {e}")
        print(f"   Raw output (first 500 chars):\n{raw_output[:500]}")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def main():
    print("="*60)
    print("🧪 Ollama + Nemotron-3-Nano Test")
    print("="*60)
    
    # Test connection
    if not test_ollama_connection():
        return
    
    # Find a markdown file to test
    test_files = list(MARKDOWN_DIR.glob("**/*.md"))
    
    if not test_files:
        print("❌ No markdown files found in data/markdown/")
        print("   Run Phase 1 first to generate markdown.")
        return
    
    # Use the first available file
    test_file = test_files[0]
    print(f"\n📂 Found {len(test_files)} markdown files")
    print(f"🎯 Testing with: {test_file}")
    
    # Generate JSON
    result = generate_json_from_markdown(test_file)
    
    if result:
        print("\n" + "="*60)
        print("✅ TEST SUCCESSFUL!")
        print("="*60)
        print("\n📊 Generated JSON preview:")
        print(json.dumps(result, indent=2)[:1000] + "...")
    else:
        print("\n❌ TEST FAILED")


if __name__ == "__main__":
    main()
