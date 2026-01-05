import sys
from openai import OpenAI

# 1. Connect to your local vLLM server
# Note: vLLM usually ignores the API key locally, but we must provide a string.
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

def test_connection():
    print("📡 Connecting to local Qwen model...")
    
    try:
        # 2. Send a simple test message
        completion = client.chat.completions.create(
            model="nvidia/Qwen3-32B-FP4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'System Operational' if you can hear me."}
            ]
        )
        
        # 3. Print result
        result = completion.choices[0].message.content
        print(f"✅ Success! Model replied: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Is the Docker container running?")
        print("2. Is it mapped to port 8000? (-p 8000:8000)")
        return False

if __name__ == "__main__":
    test_connection()