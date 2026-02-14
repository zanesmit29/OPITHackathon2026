from agent_tools import search_tool
from groq import Groq
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Default to gpt-4o if not set
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))  # Default to 0.7 if not set

def simple_groq_agent(query: str) -> str:
    """
    Basic agent using Groq LLM.
    
    Flow:
    1. Search knowledge base
    2. Format with Groq
    3. Return response
    """
    
    print(f"\n{'='*70}")
    print(f"👤 USER: {query}")
    print(f"{'='*70}\n")
    
    # Method 1: Directly call the search function (bypassing the Tool wrapper)
    print("🔍 First search the knowledge base directly using the search function...\n")
    raw_info = search_tool.run(query)
    print("✓ Search complete\n")
    
    # Step 2: Create Groq client
    print("🤖 Step 2: Formatting response with Groq...")
    client = Groq(api_key=GROQ_API_KEY)

    # Step 3: Create simple prompt
    prompt = f"""You are a compassionate Alzheimer's caregiver assistant. 
    User asked: "{query}"
    Here's what I found in the knowledge base:
    {raw_info}
    Please provide a warm, helpful response in 2-3 paragraphs. Use the information above and keep a caring, supportive tone."""

    # Step 4: Call Groq
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system", 
                "content": "You are a helpful assistant."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        temperature=TEMPERATURE,
        max_tokens=200
    )

    print("✓ Groq response generated\n")

    return response.choices[0].message.content or ""

def simple_hf_agent(query: str) -> str:
    """
    Basic agent using Hugging Face LLM.
    
    Flow:
    1. Search knowledge base
    2. Format with Hugging Face model
    3. Return responseS
    """
    # This function can be implemented similarly to the Groq version, but using a Hugging Face model instead.
    print(f"\n{'='*70}")
    print(f"👤 USER: {query}")
    print(f"{'='*70}\n")
    
    # Step 1: Search knowledge base
    print("🔍 Step 1: Searching knowledge base...")
    raw_info = search_tool.run(query)
    print("✓ Search complete\n")
    
    # Step 2: Create HuggingFace client
    print("🤖 Step 2: Formatting response with HuggingFace...")
    client = InferenceClient(model="meta-llama/Meta-Llama-3-8B-Instruct", token=HF_TOKEN)

    # Step 3: Create simple prompt
    system_message = "You are a compassionate Alzheimer's caregiver assistant."
    user_message = f"""User asked: "{query}"
    Here's what I found in the knowledge base:
    {raw_info}
    Please provide a warm, helpful response in 2-3 paragraphs. Use the information above and keep a caring, supportive tone."""

    # Step 4: Call Hugging Face model
    response = client.chat_completion(
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        max_tokens=200,
        temperature=TEMPERATURE
    )

    return response.choices[0].message.content or ""

if __name__ == "__main__":
    # Example query for testing
    print("="*70)
    print("Agent Test: Simple Agent with Search Tool")
    print("="*70 + "\n")

    query = "What are the symptoms of Alzheimer's disease?"
    
    #response = simple_groq_agent(query)
    response = simple_hf_agent(query)
    # Display
    print("="*70)
    print("🤖 AGENT RESPONSE")
    print("="*70)
    print(response)
    print("\n" + "="*70)
