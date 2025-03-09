import os
import json
from groq import Groq

def generate_text_with_groq(input_text,):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("groq_api_key environment variable not set")
    
    client = Groq(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="deepseek-r1-distill-qwen-32b",
            messages=[
                {"role": "user", "content": input_text}
            ],
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"error generating text with groq: {e}")
        return None


if __name__ == "__main__":
    sample_input = "explain the concept of quantum computing in simple terms."
    result = generate_text_with_groq(sample_input)
    print(result)
