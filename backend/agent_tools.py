from langchain_core.tools import Tool
from rag import RAGRetriever

# Global cache for the retriever instance to avoid reinitialization on every search
_retriever_cache = None

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

def search_function(query: str) -> str:
    """Search function with safety warnings."""

    print(f"Performing search for query: {query}\n")

    #Create an instance of the RAGRetriever
    retriever = get_retriever() # This will use the cached instance if available, or load it if not already cached

    # Perform the search using the retriever's smart_search method
    results = retriever.smart_search(query, k=5)

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

    for idx, doc in enumerate(documents, 1):
        doc_content = doc['content'][:200]  # Show only the first 200 characters for brevity
        doc_score = doc.get('score', 'N/A') # Score may not be available for MMR results, so we use get() with a default value
        doc_confidence = doc['confidence']

        if doc_score not in [None, 'N/A']:
            output += f"{idx}. [Score: {doc_score:.4f}, Confidence: {doc_confidence}]\n"
        else:
            output += f"{idx}. [Confidence: {doc_confidence}]\n"
        
        output += f"   {doc_content}...\n\n"

        
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

    query = "What are the symptoms of Alzheimer's disease?"

    # Method 1: Call function directly
    print("--- Test 1: Relevant Query ---")
    result1 = search_tool.run(query)
    print(result1[:] + "...\n")
    
    query2 = "What is the capital of France?"  # This is an out-of-scope query for the Alzheimer's knowledge base
    # Method 2: Use the Tool
    print("--- Test 2: Out of scope testing for warning ---")
    result2 = search_tool.run(query2)
    print(result2[:] + "...\n")

