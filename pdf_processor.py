import json
import re
import os
from pathlib import Path
from openai import OpenAI
from pypdf import PdfReader

class LocalPDFProcessor:
    def __init__(self, base_url="http://localhost:8000/v1", model_name="nvidia/Qwen3-32B-FP4"):
        self.client = OpenAI(base_url=base_url, api_key="EMPTY")
        self.model_name = model_name
        self.system_prompt = self._load_prompt()

    def _load_prompt(self):
        """Loads the prompt instruction from prompt.md"""
        try:
            with open("prompt.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("⚠️ prompt.md not found. Using default minimal prompt.")
            return "You are a JSON extractor."

    def extract_text(self, pdf_path, max_chars=120000):
        """Extracts text from PDF and truncates to safe limit."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            
            # Safety Truncation: 50k chars is approx 12k-15k tokens.
            # Adjust this based on your --max_model_len docker setting.
            if len(text) > max_chars:
                print(f"   ✂️ Truncating text ({len(text)} -> {max_chars} chars)")
                return text[:max_chars]
            return text
        except Exception as e:
            print(f"   ❌ Error reading PDF: {e}")
            return None

    def clean_json_response(self, response_text):
        """Removes <think> tags and markdown blocks to get raw JSON."""
        # 1. Remove <think> blocks (Chain of Thought)
        clean_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        
        # 2. Remove Markdown code blocks if present
        json_match = re.search(r'```json\s*(.*?)\s*```', clean_text, re.DOTALL)
        if json_match:
            clean_text = json_match.group(1)
        
        # 3. Strip whitespace
        return clean_text.strip()

    def process_pdf(self, pdf_path, category_code, sequence_id):
        """Main pipeline: Read -> Prompt -> Generate -> Parse -> Save"""
        path_obj = Path(pdf_path)
        paper_id = f"{category_code}-{sequence_id:03d}"
        
        # 1. Extract Text
        print(f"   📖 Reading: {path_obj.name}")
        text = self.extract_text(path_obj)
        if not text:
            return False

        # 2. Prepare Prompt
        # We inject the specific ID into the user message so the model knows it.
        user_message = f"""
        PAPER ID: {paper_id}
        CATEGORY: {category_code}
        
        PAPER TEXT:
        {text}
        """

        # 3. Call Local API
        print(f"   🧠 Analyzing with {self.model_name}...")
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,  # Low temp for strict JSON
                max_tokens=2048
            )
            
            raw_output = completion.choices[0].message.content
            
            # 4. Parse JSON
            json_str = self.clean_json_response(raw_output)
            data = json.loads(json_str)
            
            # Ensure paper_id is correct in the JSON
            data['paper_id'] = paper_id
            
            # 5. Save
            output_dir = Path("data/output") / category_code
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{paper_id}.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            print(f"   ✅ Saved: {output_file}")
            return True

        except json.JSONDecodeError:
            print("   ❌ JSON Parsing Failed. Model output was not valid JSON.")
            # Optional: Save the raw output to debug
            with open(f"logs/failed_{paper_id}.txt", "w") as f:
                f.write(raw_output)
            return False
        except Exception as e:
            print(f"   ❌ API/Network Error: {e}")
            return False