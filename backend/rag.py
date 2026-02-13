from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Tuple

load_dotenv()
#Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HF_TOKEN")


# Load environment variables
embedding_model = os.getenv("EMBEDDING_MODEL")
llm_model = os.getenv("LLM_MODEL")
temperature = float(os.getenv("TEMPERATURE"))
vector_store_path = Path(os.getenv("VECTOR_STORE_PATH"))
vector_store_path.parent.mkdir(parents=True, exist_ok=True) # Ensure the directory exists
chunk_size = int(os.getenv("CHUNK_SIZE"))
chunk_overlap = int(os.getenv("CHUNK_OVERLAP"))

## Simulate vector store setup and retrieval
def simulate_vector_store_setup():
    print(f"Model: {embedding_model}")

    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": "cpu"}
    )

    # Step 1: Delete old# Make elaborate text to test the text splitter
    some_text = """
    Overview
    Alzheimer's disease is the most common cause of dementia. Alzheimer's disease is the biological process that begins with the appearance of a buildup of proteins in the form of amyloid plaques and neurofibrillary tangles in the brain. This causes brain cells to die over time and the brain to shrink.
    About 6.9 million people in the United States age 65 and older live with Alzheimer's disease. Among them, more than 70% are age 75 and older. Of the more than 55 million people in the world with dementia, 60% to 70% are estimated to have Alzheimer's disease.
    Early symptoms of Alzheimer's disease include forgetting recent events or conversations. Over time, Alzheimer's disease leads to serious memory loss and affects a person's ability to do everyday tasks.
    There is no cure for Alzheimer's disease. In advanced stages, loss of brain function can cause dehydration, poor nutrition or infection. These complications can result in death.
    But medicines may improve symptoms or slow the decline in thinking. Programs and services can help support people with the disease and their caregivers.
    Products & Services
    A Book: Day to Day: Living With Dementia
    Show more products from Mayo Clinic
    Symptoms
    Memory loss is the key symptom of Alzheimer's disease. Early in the disease, people may have trouble remembering recent events or conversations. Over time, memory gets worse and other symptoms occur.
    At first, someone with the disease may be aware of having trouble remembering things and thinking clearly. As signs and symptoms get worse, a family member or friend may be more likely to notice the issues.
    Brain changes from Alzheimer's disease lead to the following symptoms that get worse over time.
    Memory
    Everyone has trouble with memory at times, but the memory loss related to Alzheimer's disease is lasting. Over time, memory loss affects the ability to function at work and at home.
    People with Alzheimer's disease may:
    Repeat statements and questions over and over.
    Forget conversations, appointments or events.
    Misplace items, often putting them in places that don't make sense.
    Get lost in places they used to know well.
    Forget the names of family members and everyday objects.
    Have trouble finding the right words, expressing thoughts or having conversations.
    Thinking and reasoning
    Alzheimer's disease causes trouble concentrating and thinking, especially about abstract concepts such as numbers. Doing more than one task at once is especially hard. It may be challenging to manage finances, balance checkbooks and pay bills on time. Eventually people with Alzheimer's disease may not recognize numbers.
    Making judgments and decisions
    Alzheimer's disease makes it hard to make sensible decisions and judgments. People with Alzheimer's disease may make poor choices in social settings or wear clothes for the wrong type of weather. Everyday problems may be hard to solve. Someone with Alzheimer's disease may not know how to handle food burning on the stove or how to make decisions when driving.
    Planning and performing familiar tasks
    Routine activities that involve completing steps in a certain order also can be hard for people with Alzheimer's disease. They may have trouble planning and cooking a meal or playing a favorite game. As Alzheimer's disease becomes advanced, people forget how to do basic tasks such as dressing and bathing.
    Changes in personality and behavior
    Brain changes that occur in Alzheimer's disease can affect moods and behaviors. Symptoms may include:
    Depression.
    Loss of interest in activities.
    Social withdrawal.
    Mood swings.
    Not trusting others.
    Anger or aggression.
    Changes in sleeping habits.
    Wandering.
    Loss of inhibitions.
    Delusions, such as believing something has been stolen when it hasn't.
    Preserved skills
    Despite major changes to memory and skills, people with Alzheimer's disease are able to keep some skills even as symptoms get worse. These are known as preserved skills. They may include reading or listening to books, telling stories, sharing memories, singing, listening to music, dancing, drawing, or doing crafts.
    Preserved skills may last longer because they're managed by parts of the brain affected in later stages of the disease.
    When to see a doctor
    Several conditions can cause memory loss or other dementia symptoms. Some of those conditions can be treated. If you are concerned about your memory or other thinking skills, talk to your healthcare professional.
    If you are concerned about the thinking skills you notice in a family member or friend, ask about going together to talk to a healthcare professional.
    """

    # Initialize the text splitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(some_text)
    #print(chunks)

    # Delete old collection if exists
    try:
        client = chromadb.PersistentClient(path=str(vector_store_path))
        client.delete_collection(name="langchain")  # Default LangChain collection name
        print("✓ Deleted old collection")
    except Exception as e:
        print(f"No existing collection to delete: {e}")

    # Step 2: Create fresh vector store
    db = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory=str(vector_store_path)
    )

    #sample = db.get(limit=1, include=["documents"])
    print(f"✓ Created fresh database with {db._collection.count()} documents")
    #print(f"📝 First doc preview: {sample['documents'][0][:80]}...")

    return db


class RAGRetriever:
    """Handle retrieval of relevant documents from the vector store based on user queries."""

    def __init__(self):
        """
        Load the vector store from the database directory.

        """
        #Getting the configuration from environment variables
        self.vector_store_path = Path(os.getenv("VECTOR_STORE_PATH"))
        self.embedding_model = os.getenv("EMBEDDING_MODEL")

        print(f"📂 Loading vector store from: {self.vector_store_path}")

        # Check if database exists (teammate should have created it)
        if not self.vector_store_path.exists():
            raise FileNotFoundError(
                f"❌ Vector store not found at {self.vector_store_path}\n"
            )
        
        # Load the embedding model
        print(f"🤖 Loading embedding model: {self.embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={"device": "cpu"}
        )

        # Connect to the existing vector store
        self.db = Chroma(
            collection_name="langchain",
            embedding_function=self.embeddings,
            persist_directory=str(self.vector_store_path)
        )

        # Verify that it is loaded
        count = self.db._collection.count()
        print(f"✓ Vector store loaded with {count} documents")

        if count == 0:
            print("⚠️ Warning: Vector store is empty.")


    def simple_match_retrieval(self, query: str, k: int = 5) -> List[str]:
        """
        Basic similarity search - your starting point.
        
        Args:
            query: User's question
            k: Number of documents to retrieve
        
        Returns:
            List of document texts
        """
        docs = self.db.similarity_search(query, k=k)

        # Extracting just the text content
        results = [doc.page_content for doc in docs]
        return results
    
    def simple_match_retrieval_with_scores(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Similarity search that also returns relevance scores.
        
        Args:
            query: User's question
            k: Number of documents to retrieve
        
        Returns:
            List of tuples (document text, score)
        """
        print(f"🔍 Performing similarity search for query based on scores: '{query}' with k={k}")
        docs = self.db.similarity_search_with_score(query, k=k)

        
        
        return [(doc.page_content, score) for doc, score in docs]

    def advanced_mmr_retrieval(self, query: str, k: int = 10, lambda_mult: float = 0.8) -> List[str]:
        """
        MMR-based retrieval that balances relevance and diversity. This is a more complex retrieval method that can help surface a wider range of relevant documents.

        Args:
            query: User's question
            k: Number of documents to retrieve before re-ranking
            lambda_mult: Parameter to balance relevance vs diversity (0 = all relevance, 1 = all diversity)
        """
        print(f"🔍 Performing MMR retrieval for query: '{query}' with k={k} and lambda={lambda_mult}")

        results = self.db.max_marginal_relevance_search(
            query, 
            k=k,
            fetch_k=k*2,  # Fetch more documents to allow for re-ranking
            lambda_mult=lambda_mult
        )
        # Here you could add additional processing to re-rank or filter results
        return [doc.page_content for doc in results]  # Return top 5 after advanced processing

if __name__ == "__main__":
    
    # Only run simulated vector store once to create the database, then comment it out for normal retrieval testing
    #db = simulate_vector_store_setup()


    # Step 3: Test retrieval
    user_input = "What are the symptoms of Alzheimer's disease?"
    retriever = RAGRetriever()

    docs = retriever.advanced_mmr_retrieval(user_input, k=5, lambda_mult=0.8)

    print("🔍 Retrieved documents:")
    for doc in docs:
        print(f"Content: {doc[:80]}...")
    
