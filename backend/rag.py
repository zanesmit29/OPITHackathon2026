import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import io
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Tuple, Dict
import warnings
import logging
from contextlib import redirect_stderr

# === CLEAN UP CONSOLE OUTPUT ===
warnings.filterwarnings('ignore')
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('sentence_transformers').setLevel(logging.WARNING)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Load environment variables
project_root = Path(__file__).parent.parent  # Go up one level from backend/ to OPITHackathon2026/
faiss_index_path = project_root / os.getenv("FAISS_INDEX_PATH", "backend/data/alzheimer_faiss_deepl_hybrid.index")
faiss_metadata_path = project_root / os.getenv("FAISS_METADATA_PATH", "backend/data/alzheimer_metadata_deepl_hybrid.json")
llm_model = os.getenv("LLM_MODEL")
temperature = float(os.getenv("TEMPERATURE", "0.7"))


class RAGRetriever:
    """
    FAISS-based RAG retrieval with BGE-M3 embeddings.

    Supports three retrieval strategies:
    1. safe_search: Quick retrieval with confidence scoring
    2. advanced_mmr_retrieval: Diverse retrieval balancing relevance and diversity
    3. smart_search: Intelligent routing based on confidence levels
    """

    def __init__(self):
        """Load FAISS index, metadata, and BGE-M3 embedding model."""
        logger.info("⏳ Loading RAG system...")

        # Validate paths
        if not faiss_index_path.exists():
            raise FileNotFoundError(
                f"❌ FAISS index not found at {faiss_index_path}\n"
                f"Expected: alzheimer_faiss_deepl_hybrid.index"
            )

        if not faiss_metadata_path.exists():
            raise FileNotFoundError(
                f"❌ FAISS metadata not found at {faiss_metadata_path}\n"
                f"Expected: alzheimer_metadata_deepl_hybrid.json"
            )

        # Load FAISS index
        self.index = faiss.read_index(str(faiss_index_path))

        # Load metadata
        with open(faiss_metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        # Load BGE-M3 model (suppress logs)
        with redirect_stderr(io.StringIO()):
            self.model = SentenceTransformer('BAAI/bge-m3', device='cpu')

        logger.info(f"✓ Loaded {self.index.ntotal} embeddings from FAISS")
        logger.info(f"✓ Loaded {len(self.metadata)} metadata records")
        logger.info(f"✓ BGE-M3 model ready (supports 100+ languages)\n")

        if self.index.ntotal == 0:
            logger.warning("⚠️ Warning: FAISS index is empty")

    def safe_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve documents with confidence scoring.

        Args:
            query: User's question (English or Spanish)
            k: Number of documents to retrieve

        Returns:
            List of dicts with keys: content, score, confidence, source, title
        """
        logger.info(f"🔍 Safe search: '{query}' (k={k})\n")

        # Encode query
        query_embedding = self.model.encode([query], normalize_embeddings=True)

        # Search FAISS (returns L2 distances)
        distances, indices = self.index.search(
            np.array(query_embedding, dtype='float32'), k
        )

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx >= len(self.metadata):
                continue

            # Categorize confidence based on L2 distance
            # Adjusted thresholds for cross-lingual BGE-M3
            if dist < 0.5:  # Off-topic query
                confidence = "Low Confidence"
            elif dist <= 0.8:
                confidence = "Highly Confident"
            elif dist <= 1.2:
                confidence = "Moderately Confident"
            else:
                confidence = "Low Confidence"

            results.append({
                "content": self.metadata[idx].get("chunk_text_en", ""),
                "score": float(dist),
                "confidence": confidence,
                "source": self.metadata[idx].get("url", ""),
                "title": self.metadata[idx].get("title", "")
            })

        if not results:
            logger.warning("⚠️ No matches found - recommend expert review")

        return results

    def advanced_mmr_retrieval(self, query: str, k: int = 10, 
                              lambda_mult: float = 0.8) -> List[Dict]:
        """
        Maximal Marginal Relevance retrieval for diverse results.

        Args:
            query: User's question
            k: Number of diverse documents to return
            lambda_mult: Balance factor (1.0 = pure relevance, 0.0 = pure diversity)

        Returns:
            List of dicts with keys: content, source, title
        """
        logger.info(f"🔍 MMR retrieval: '{query}' (k={k}, λ={lambda_mult})\n")

        # Encode query
        query_embedding = self.model.encode([query], normalize_embeddings=True)[0]

        # Fetch candidate documents (2x more than needed)
        fetch_k = min(k * 2, self.index.ntotal)
        distances, indices = self.index.search(
            np.array([query_embedding], dtype='float32'), fetch_k
        )

        candidate_indices = indices[0]

        # Reconstruct embeddings for MMR calculation
        try:
            candidate_embeddings = np.array([
                self.index.reconstruct(int(idx)) for idx in candidate_indices
            ], dtype='float32')
        except RuntimeError:
            logger.warning("⚠️ Index doesn't support reconstruction - returning top-k")
            return [
                {
                    "content": self.metadata[idx].get("chunk_text_en", ""),
                    "source": self.metadata[idx].get("url", ""),
                    "title": self.metadata[idx].get("title", "")
                }
                for idx in candidate_indices[:k] if idx < len(self.metadata)
            ]

        # MMR selection algorithm
        selected_indices = []
        selected_embeddings = []

        for _ in range(min(k, len(candidate_indices))):
            if not selected_indices:
                # First document: most relevant to query
                best_idx = 0
            else:
                # Calculate MMR scores
                mmr_scores = []
                for i, cand_idx in enumerate(candidate_indices):
                    if cand_idx in selected_indices:
                        mmr_scores.append(-np.inf)
                        continue

                    # Relevance: cosine similarity to query
                    relevance = np.dot(query_embedding, candidate_embeddings[i])

                    # Diversity: maximum similarity to already selected docs
                    diversity = max([
                        np.dot(candidate_embeddings[i], sel_emb)
                        for sel_emb in selected_embeddings
                    ]) if selected_embeddings else 0

                    # MMR formula: balance relevance and diversity
                    mmr_scores.append(lambda_mult * relevance - (1 - lambda_mult) * diversity)

                best_idx = int(np.argmax(mmr_scores))

            selected_indices.append(candidate_indices[best_idx])
            selected_embeddings.append(candidate_embeddings[best_idx])

        # Build results
        results = [
            {
                "content": self.metadata[idx].get("chunk_text_en", ""),
                "source": self.metadata[idx].get("url", ""),
                "title": self.metadata[idx].get("title", "")
            }
            for idx in selected_indices if idx < len(self.metadata)
        ]

        logger.info(f"✓ Retrieved {len(results)} diverse documents\n")
        return results

    def smart_search(self, query: str, k: int = 5) -> Dict:
        """
        Intelligent search with automatic strategy selection.

        Strategy:
        1. Run safe_search to assess confidence
        2. If high confidence (≥50% highly confident) → return safe results
        3. If low confidence (≥50% low confident) → recommend expert review
        4. If medium confidence → switch to MMR for diverse perspectives

        Args:
            query: User's question
            k: Number of results to retrieve

        Returns:
            Dict with keys: method, confidence, recommendation, results
        """
        logger.info(f"🧠 Smart search: '{query[:50]}...'\n")

        # Initial safe search
        safe_results = self.safe_search(query, k=k)
        
        # ✅ OFF-TOPIC DETECTION
        if safe_results and safe_results[0]['score'] < 0.55:
            logger.warning(f"⚠️ Query outside knowledge base (score: {safe_results[0]['score']:.3f})\n")
            # Override all confidences to "Low"
            for result in safe_results:
                result['confidence'] = "Low Confidence"
            
            return {
                "method": "safe_search",
                "confidence": "low",
                "recommendation": "DO_NOT_ANSWER",
                "results": safe_results
            }

        # Analyze confidence distribution
        high_count = sum(1 for r in safe_results if r["confidence"] == "Highly Confident")
        low_count = sum(1 for r in safe_results if r["confidence"] == "Low Confidence")

        # Decision logic
        if high_count >= k // 2:
            logger.info(f"✓ High confidence ({high_count}/{k}) - using safe search\n")
            return {
                "method": "safe_search",
                "confidence": "high",
                "recommendation": "SAFE_TO_ANSWER",
                "results": safe_results
            }

        elif low_count >= k // 2:
            logger.warning(f"⚠️ Low confidence ({low_count}/{k}) - expert review needed\n")
            return {
                "method": "safe_search",
                "confidence": "low",
                "recommendation": "DO_NOT_ANSWER",
                "results": safe_results
            }

        else:
            logger.info(f"⚠️ Medium confidence - switching to MMR for diversity\n")
            mmr_results = self.advanced_mmr_retrieval(query, k=k*2, lambda_mult=0.5)
            return {
                "method": "mmr_retrieval",
                "confidence": "medium",
                "recommendation": "REVIEW_BEFORE_ANSWERING",
                "results": [
                    {**r, "score": None, "confidence": "medium"} 
                    for r in mmr_results
                ]
            }


if __name__ == "__main__":
    
    print("="*70)
    print("🚀 Testing FAISS RAG Retrieval System")
    print("="*70)

    retriever = RAGRetriever()

    # Test 1: Smart search with English query
    print("\n" + "="*70)
    print("TEST 1: Smart Search (English → Spanish)")
    print("="*70)

    query1 = "What are the symptoms of Alzheimer's disease?"
    results1 = retriever.smart_search(query1, k=3)

    print(results1)
    # print(f"Method: {results1['method']}")
    # print(f"Confidence: {results1['confidence']}")
    # print(f"Recommendation: {results1['recommendation']}\n")

    # for i, doc in enumerate(results1["results"], 1):
    #     print(f"--- Document {i} ---")
    #     print(f"Confidence: {doc['confidence']}")
    #     if doc.get('score') is not None:
    #         print(f"Score: {doc['score']:.3f}")
    #     if doc.get('title'):
    #         print(f"Title: {doc['title']}")
    #     print(f"Content: {doc['content']}...")
    #     print()

    # # Test 2: Spanish query
    # print("\n" + "="*70)
    # print("TEST 2: Safe Search (Spanish → Spanish)")
    # print("="*70)

    # query2 = "¿Cuáles son los tratamientos para el Alzheimer?"
    # results2 = retriever.safe_search(query2, k=3)

    # for i, doc in enumerate(results2, 1):
    #     print(f"--- Document {i} ---")
    #     print(f"Confidence: {doc['confidence']} (Score: {doc['score']:.3f})")
    #     print(f"Content: {doc['content']}...")
    #     print()

    # # Test 3: MMR for diversity
    # print("\n" + "="*70)
    # print("TEST 3: MMR Retrieval (Diverse Perspectives)")
    # print("="*70)

    # query3 = "early signs of dementia"
    # results3 = retriever.advanced_mmr_retrieval(query3, k=5, lambda_mult=0.7)

    # for i, doc in enumerate(results3, 1):
    #     print(f"--- Document {i} ---")
    #     print(f"Content: {doc['content'][:150]}...")
    #     print()
