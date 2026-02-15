from langchain_core.tools import Tool
from rag import RAGRetriever

# Global cache for the retriever instance to avoid reinitialization on every search
_retriever_cache = None

VAGUE_QUERY_REWRITES = {
        # === GENERAL OVERVIEW QUERIES ===
        r"tell me about (?:alzheimer'?s?|dementia)": 
            "What is Alzheimer's disease? What are the main symptoms and causes?",
        
        r"what is (?:alzheimer'?s?|dementia)\??$": 
            "What is Alzheimer's disease? What are the main symptoms?",
        
        r"explain (?:alzheimer'?s?|dementia)": 
            "What is Alzheimer's disease? What are its causes and symptoms?",
        
        r"(?:alzheimer'?s?|dementia) info(?:rmation)?": 
            "What is Alzheimer's disease? Symptoms and treatment",
        
        r"(?:give me|provide) (?:an? )?overview of (?:alzheimer'?s?|dementia)":
            "What is Alzheimer's disease? Main symptoms, causes, and progression",
        
        # === HELP/SUPPORT QUERIES ===
        r"how (?:do i|can i|to) help (?:someone|a person|my (?:mom|dad|parent|loved one))":
            "What are effective caregiving strategies for Alzheimer's patients?",
        
        r"(?:i need|need) help with (?:my )?(?:mom|dad|parent|husband|wife|loved one)":
            "What caregiving support and strategies are available for Alzheimer's?",
        
        r"how (?:do i|to) (?:care for|take care of|look after)":
            "What are best practices for caring for someone with Alzheimer's?",
        
        r"caring for (?:someone|a person) with (?:alzheimer'?s?|dementia)":
            "What are effective caregiving strategies and daily care tips for Alzheimer's?",
        
        # === SYMPTOM QUERIES (VAGUE) ===
        r"what (?:are|is) (?:the )?symptoms?\??$":
            "What are the symptoms of Alzheimer's disease?",
        
        r"signs? of (?:alzheimer'?s?|dementia)$":
            "What are the early signs and symptoms of Alzheimer's disease?",
        
        r"how (?:do i|to) (?:know|tell) if (?:someone has|they have)":
            "What are the early warning signs and symptoms of Alzheimer's disease?",
        
        r"(?:my )?(?:mom|dad|parent|loved one) is (?:forgetting|confused)":
            "What are memory loss and confusion symptoms in Alzheimer's disease?",
        
        # === TREATMENT QUERIES (VAGUE) ===
        r"(?:what|any) treatment[s]?\??$":
            "What are the available treatments for Alzheimer's disease?",
        
        r"how (?:is it|to) treat(?:ed)?\??":
            "What are the treatment options for Alzheimer's disease?",
        
        r"(?:is there a )?cure\??$":
            "What are current treatment options and research for Alzheimer's disease?",
        
        r"can (?:alzheimer'?s?|dementia) be (?:cured|treated|stopped)":
            "What are treatment options and can Alzheimer's progression be slowed?",
        
        # === PROGRESSION QUERIES ===
        r"how (?:fast|quickly) (?:does it|will (?:it|they))":
            "What is the progression timeline and stages of Alzheimer's disease?",
        
        r"what (?:are|is) (?:the )?stages?\??$":
            "What are the stages of Alzheimer's disease progression?",
        
        r"how (?:does|will) (?:it|the disease) progress":
            "What is the progression and timeline of Alzheimer's disease?",
        
        # === BEHAVIORAL QUERIES ===
        r"(?:dealing with|handling) (?:behavior|aggression|anger|wandering)":
            "How to manage behavioral symptoms in Alzheimer's patients?",
        
        r"(?:my )?(?:mom|dad|parent|loved one) is (?:aggressive|angry|agitated|wandering)":
            "How to handle behavioral changes and aggression in Alzheimer's patients?",
        
        r"behavior(?:al)? (?:changes|problems|issues)":
            "What are behavioral symptoms of Alzheimer's and how to manage them?",
        
        # === CAUSE/RISK QUERIES ===
        r"what causes (?:alzheimer'?s?|dementia)\??$":
            "What are the causes and risk factors of Alzheimer's disease?",
        
        r"why (?:do people|does someone) get (?:alzheimer'?s?|dementia)":
            "What are the causes and risk factors of Alzheimer's disease?",
        
        r"(?:am i|is (?:my )?(?:mom|dad|parent)) at risk\??":
            "What are the risk factors for developing Alzheimer's disease?",
        
        # === PREVENTION QUERIES ===
        r"how (?:to|can i) prevent (?:alzheimer'?s?|dementia)":
            "What are prevention strategies and risk reduction for Alzheimer's disease?",
        
        r"can (?:alzheimer'?s?|dementia) be prevented\??":
            "What are known prevention strategies and risk factors for Alzheimer's?",
        
        # === DIAGNOSIS QUERIES ===
        r"how (?:is it|to (?:get|be)) diagnos(?:ed|is)":
            "What is the diagnosis process and tests for Alzheimer's disease?",
        
        r"what (?:are|is) (?:the )?(?:tests?|exams?)":
            "What diagnostic tests and evaluations are used for Alzheimer's?",
        
        # === DAILY LIVING QUERIES ===
        r"daily (?:life|living|activities|routine)":
            "How to manage daily activities and routines for Alzheimer's patients?",
        
        r"(?:eating|feeding|bathing|dressing) (?:problems|difficulties|issues)":
            "How to help with daily living activities for Alzheimer's patients?",
        
        # === COMMUNICATION QUERIES ===
        r"how (?:to|do i) (?:talk to|communicate with|speak to)":
            "What are effective communication strategies for Alzheimer's patients?",
        
        r"(?:they )?(?:can't|cannot|won't) (?:talk|speak|communicate)":
            "How to communicate with Alzheimer's patients with language difficulties?",
        
        # === RESOURCES/SUPPORT QUERIES ===
        r"(?:where|how) (?:to|can i) (?:get|find) (?:help|support|resources)":
            "What support resources are available for Alzheimer's caregivers?",
        
        r"support (?:for|groups?|services?)":
            "What caregiver support services and resources are available for Alzheimer's?",
        
        # === SAFETY QUERIES ===
        r"(?:home )?safety (?:concerns|tips|issues)":
            "What are home safety modifications for Alzheimer's patients?",
        
        r"how (?:to|do i) (?:keep|make) (?:them |the house |home )?safe":
            "What safety precautions and home modifications for Alzheimer's patients?",
    }

def get_retriever() -> RAGRetriever:
    """Get or create retriever (singleton)."""
    global _retriever_cache

    if _retriever_cache is None:
        print("🔧 Loading retriever (first time - slow)...\n")
        _retriever_cache = RAGRetriever()
        print("✅ Retriever loaded and cached for future use.\n")
    else:
        print("⚡ Using cached retriever for fast response.\n")

    return _retriever_cache

def rewrite_query(query: str) -> str:
    """Rewrite vague queries to be more specific."""
    query_lower = query.lower().strip()
    
    # Pattern matching for common vague queries
    vague_patterns = VAGUE_QUERY_REWRITES
    
    import re
    for pattern, rewrite in vague_patterns.items():
        if re.search(pattern, query_lower):
            print(f"🔄 Rewriting query: '{query}' → '{rewrite}'")
            return rewrite
    
    return query

def search_function(query: str) -> str:
    """Search function with safety warnings."""

    # Rewrite vague queries
    rewritten_query = rewrite_query(query)

    print(f"Performing search for query: {rewritten_query}\n")

    #Create an instance of the RAGRetriever
    retriever = get_retriever() # This will use the cached instance if available, or load it if not already cached

    # Perform the search using the retriever's smart_search method
    results = retriever.smart_search(rewritten_query, k=5)

    # Format the results into a string for output
    method = results["method"]
    confidence = results['confidence']
    recommendation = results['recommendation']
    documents = results['results']

    

    output = f"Search Method: {method}\nConfidence Level: {confidence}\nRecommendation: {recommendation}\n\nRetrieved Documents:\n"

    if recommendation == 'DO_NOT_ANSWER':
        output += "⚠️  SAFETY WARNING ⚠️\n"
        output += "="*60 + "\n"
        output += "Low confidence in available information.\n"
        output += "This query may be outside the knowledge base scope.\n\n"
        output += "RECOMMENDED ACTIONS:\n"
        output += "- Advise user to consult healthcare professional\n"
        output += "- Provide Alzheimer's Association Helpline: 1-800-272-3900 (24/7)\n"
        output += "- DO NOT provide medical advice based on this information\n"
        output += "="*60 + "\n\n"
        return output

    for idx, doc in enumerate(documents[:2], 1): # Only show top 2 results as this is the most confident information and we want to keep the output concise
        doc_content = doc['content'] 
        doc_score = doc.get('score', 'N/A') # Score may not be available for MMR results, so we use get() with a default value
        doc_confidence = doc['confidence']
        doc_title = doc.get('title', 'Untitled')  # ← ADD THIS
        doc_source = doc.get('source', 'No URL')  # ← ADD THIS

        output += f"\n{idx}. {doc_title}\n"  # ← ADDED
        
        if doc_score not in [None, 'N/A']:
            output += f"   Score: {doc_score:.4f} | Confidence: {doc_confidence}\n"
        else:
            output += f"   Confidence: {doc_confidence}\n"
        
        output += f"   Source: {doc_source}\n"  # ← ADDED
        output += f"   Content: {doc_content}...\n"

    return output

# Wrap the search function as a LangChain Tool
search_tool = Tool(
    name="medical_search_tool",
    func=search_function,
    description=(
        "Search the Alzheimer's caregiver knowledge base for accurate medical information. "
        "Use this tool to answer questions about Alzheimer's symptoms, disease progression, "
        "caregiving strategies, behavioral management, and patient care. "
        "Automatically provides safety warnings for low-confidence information. "
        "Input: A clear question about Alzheimer's disease or caregiving."
    )
)

if __name__ == "__main__":
    # Example query for testing

    print("="*70)
    print("Tool Test: Medical Search Tool")
    print("="*70 + "\n")

    #query = "What are the symptoms of Alzheimer's disease?"

    # Add debug logging in your agent code:
    query = "tell me about alzheimers"
    search_results = search_tool.run(query)
    print(f"DEBUG - Search tool output:\n{search_results}\n")

    # # Method 1: Call function directly
    # print("--- Test 1: Relevant Query ---")
    # result1 = search_tool.run(query)
    # print(result1[:] + "...\n")
    
    # query2 = "What is the capital of France?"  # This is an out-of-scope query for the Alzheimer's knowledge base
    # # Method 2: Use the Tool
    # print("--- Test 2: Out of scope testing for warning ---")
    # result2 = search_tool.run(query2)
    # print(result2[:] + "...\n")

