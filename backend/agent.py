from agent_tools import search_tool
from groq import Groq
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

from prompts import(
    BASE_SYSTEM_PROMPT,
    FULL_SYSTEM_PROMPT,
    SAFETY_RULES_INJECTION,
    CRISIS_RESPONSE_TEMPLATE,
    DANGEROUS_MESSAGE_TEMPLATE,
    CRISIS_KEYWORDS,
    DANGEROUS_ADVICE_BLOCKLIST,
    LOW_CONFIDENCE_TEMPLATE,
    is_crisis_message,
    is_dangerous_topic,
    PERSONALIZATION_TEMPLATE
)

load_dotenv()  # Load environment variables from .env file
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Default to gpt-4o if not set
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))  # Default to 0.7 if not set

class ConversationAgent:
    """A conversation agent that can use tools to generate responses to user queries and have long-term memory of the conversation history."""
    def __init__(self) -> None:
        self.conversation_history = []  # This will store the history of the conversation for context in future interactions
        self.client = InferenceClient(model="meta-llama/Meta-Llama-3-8B-Instruct", token=HF_TOKEN)  # Initialize Hugging Face Inference Client once in the constructor for reuse across interactions
        

    # def simple_groq_agent(query: str) -> str:
    #     """
    #     Basic agent using Groq LLM.
        
    #     Flow:
    #     1. Search knowledge base
    #     2. Format with Groq
    #     3. Return response
    #     """
        
    #     print(f"\n{'='*70}")
    #     print(f"👤 USER: {query}")
    #     print(f"{'='*70}\n")
        
    #     # Method 1: Directly call the search function (bypassing the Tool wrapper)
    #     print("🔍 Searching knowledge base...\n")
    #     raw_info = search_tool.run(query)
    #     print("✓ Search complete\n")
        
    #     # Step 2: Create Groq client
    #     print("🤖 Formatting response with Groq...\n")
    #     client = Groq(api_key=GROQ_API_KEY)

    #     # Step 3: Create simple prompt
    #     prompt = f"""You are a compassionate Alzheimer's caregiver assistant. 
    #     User asked: "{query}"
    #     Here's what I found in the knowledge base:
    #     {raw_info}
    #     Please provide a warm, helpful response in 2-3 paragraphs. Use the information above and keep a caring, supportive tone."""

    #     # Step 4: Call Groq
    #     response = client.chat.completions.create(
    #         model=LLM_MODEL,
    #         messages=[
    #             {
    #                 "role": "system", 
    #                 "content": "You are a helpful assistant."
    #             },
    #             {
    #                 "role": "user", 
    #                 "content": prompt
    #             }
    #         ],
    #         temperature=TEMPERATURE,
    #         max_tokens=200
    #     )

    #     print("✓ Groq response generated\n")

    #     return response.choices[0].message.content or ""

    def chat_agent(self, query: str) -> str:
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
        print(f"📚 Memory: {len(self.conversation_history)} messages\n")

        # =================================================================================
        # This is a basic hardcoded check for crisis keywords in the query before doing anything else.
        # This will be replaced

        system_message = ""

        check_status = self.basic_check_query_safety(query)
        if check_status == "CRISIS":
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": CRISIS_RESPONSE_TEMPLATE})
            return CRISIS_RESPONSE_TEMPLATE #Hard stop for crisis or dangerous queries. This will trigger the agent to respond with the crisis response and not attempt to answer the original question at all.
        elif check_status == "DANGEROUS":
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": DANGEROUS_MESSAGE_TEMPLATE})
            return DANGEROUS_MESSAGE_TEMPLATE #Hard stop for dangerous queries. This will trigger the agent to respond with a warning and not attempt to answer the original question at all.
        elif check_status == "SAFE":
            system_message = BASE_SYSTEM_PROMPT + SAFETY_RULES_INJECTION
        
    
        # Step 1: Search knowledge base
        print("🔍 Searching knowledge base...\n")
        raw_info = search_tool.run(query)
        print("✓ Search complete\n")
        
        # Step 2: Create HuggingFace client
        # print("🤖 Formatting response with HuggingFace...\n")
        # client = InferenceClient(model="meta-llama/Meta-Llama-3-8B-Instruct", token=HF_TOKEN)

        # Step 3: Create simple prompt
        user_message = f"""User asked: "{query}"
        Here's what I found in the knowledge base:
        {raw_info}
        """

        # Build the message with history
        messages = [    
            {"role": "system", "content": system_message}
        ]

        messages.extend(self.conversation_history)  # Add conversation history for context

        #Add in the current query
        messages.append({"role": "user", "content": user_message})

        # Step 4: Call Hugging Face model
        response = self.client.chat_completion(
            messages = messages, # Now includes conversation history for better context retention across interactions
            max_tokens=400,
            temperature=TEMPERATURE
        )

        response_context = response.choices[0].message.content 

        # Save to history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response_context})

        return response_context or ""

    def basic_check_query_safety(self, query: str) -> str:
        """Check if the query contains any crisis keywords."""
        if is_crisis_message(query):
            print("⚠️ Crisis keywords detected in query. Triggering crisis protocol.\n")
            return "CRISIS"
        elif is_dangerous_topic(query):
            print("⚠️ Dangerous topic detected in query. Triggering safety protocol.\n")
            return "DANGEROUS"
        else:
            return "SAFE"


    

if __name__ == "__main__":
    print("="*70)
    print("Testing Agent class with safety checks and conversation history")
    print("="*70)
    
    agent = ConversationAgent()

    # raw_info = search_tool.run("What are the symptoms of Alzheimer's disease?")
    # print(f"Raw info from search tool:\n{raw_info}\n")

    
    #Turn 1
    response1 = agent.chat_agent("What are symptoms of Alzheimer's disease?")
    print(f"Memory: {len(agent.conversation_history)} messages\n")
    print(response1 + "\n")
    
    # # Turn 2 (should remember Turn 1)
    # response2 = agent.chat_agent("How do they progress?")
    # print(f"Memory: {len(agent.conversation_history)} messages\n")
    # print(response2 + "\n")
    
    # # Turn 3 - Crisis (should still save)
    # response3 = agent.chat_agent("I want to hurt myself")
    # print(f"Memory: {len(agent.conversation_history)} messages\n")
    # print(response3 + "\n")
