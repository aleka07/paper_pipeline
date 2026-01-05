import sys
import json
import re
from pathlib import Path
from openai import OpenAI
from pypdf import PdfReader

# --- CONFIGURATION ---
CLIENT = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
MODEL_NAME = "nvidia/Qwen3-32B-FP4"

def extract_text_from_pdf(pdf_path):
    """Reads a PDF and returns the full text content."""
    print(f"📄 Reading PDF: {pdf_path}...")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        print(f"   (Extracted {len(text)} characters)")
        return text
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return None

def clean_response(response_text):
    """
    Removes the <think>...</think> blocks from Qwen's output 
    and extracts the JSON part.
    """
    # 1. Remove the thinking block
    clean_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
    
    # 2. Extract JSON if wrapped in markdown code blocks
    # (Models often output ```json ... ```)
    json_match = re.search(r'```json\s*(.*?)\s*```', clean_text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # 3. If no code blocks, try to find the first '{' and last '}'
    start = clean_text.find('{')
    end = clean_text.rfind('}') + 1
    if start != -1 and end != -1:
        return clean_text[start:end]
        
    return clean_text

def process_pdf(pdf_path):
    # 1. Get Text
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return

    # 2. Prepare Prompt
    # We truncate text if it's wildly too long, but 16k tokens is a lot.
    prompt_content = f"""
    You are a data extraction assistant. 
    Analyze the following academic paper text and extract the key details into JSON format.
    
    Required JSON Structure:
    {{
        "title": "Paper Title",
        "authors": ["Author 1", "Author 2"],
        "summary": "A short summary of the paper (max 3 sentences).",
        "key_findings": ["finding 1", "finding 2"],
        "publication_year": "YYYY"
    }}

    PAPER TEXT:
    {text[:45000]} 
    """ 
    # Note: text[:45000] is a rough safety limit for ~12-15k tokens.

    print("🧠 Sending to Qwen model (this may take a moment)...")

    try:
        completion = CLIENT.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful API that outputs strict JSON only."},
                {"role": "user", "content": prompt_content}
            ],
            temperature=0.2, # Low temperature for more consistent JSON
        )
        
        raw_output = completion.choices[0].message.content
        
        # 3. Clean and Parse
        json_str = clean_response(raw_output)
        data = json.loads(json_str)
        
        # 4. Save to File
        output_filename = Path(pdf_path).stem + ".json"
        with open(output_filename, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        print(f"✅ Success! Saved to {output_filename}")
        print("\n--- PREVIEW ---")
        print(json.dumps(data, indent=2))
        
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON. Raw output was:")
        print(raw_output)
    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    # Create a dummy PDF if you don't have one to test
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_pdf>")
        print("Please provide a PDF file path.")
    else:
        process_pdf(sys.argv[1])