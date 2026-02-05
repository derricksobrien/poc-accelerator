"""
Module C: Vector Store - RAG Memory
Lightweight in-memory semantic search with metadata filtering.
Uses cosine similarity for document matching.
"""

from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field
import math
from collections import defaultdict
from models.schemas import CatalogItem


@dataclass
class Document:
    """Internal document representation for vector search."""
    id: str
    text: str
    tokens: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class SimpleVectorStore:
    """
    Lightweight in-memory vector store for semantic search.
    Uses TF-IDF inspired token matching for simplicity.
    Supports filtering by solution_area and complexity_level.
    """
    
    def __init__(self, persist_dir: Optional[Path] = None):
        """
        Initialize in-memory vector store.
        
        Args:
            persist_dir: Ignored in MVP (included for API compatibility)
        """
        self.documents: Dict[str, Document] = {}
        self.metadata_index: Dict[str, List[str]] = defaultdict(list)  # field -> [ids]
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for keyword matching."""
        # Convert to lowercase and split on whitespace/punctuation
        import re
        tokens = re.findall(r'\w+', text.lower())
        # Remove common stop words for better matching
        stop_words = {'the', 'a', 'an', 'and', 'or', 'is', 'in', 'to', 'of', 'for', 'with'}
        return [t for t in tokens if t not in stop_words and len(t) > 2]
    
    def _compute_similarity(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        """Compute simple token overlap similarity."""
        if not query_tokens or not doc_tokens:
            return 0.0
        
        query_set = set(query_tokens)
        doc_set = set(doc_tokens)
        
        # Jaccard similarity
        intersection = len(query_set & doc_set)
        union = len(query_set | doc_set)
        
        return intersection / union if union > 0 else 0.0
    
    def ingest_accelerators(self, accelerators: List[CatalogItem]) -> None:
        """
        Index a list of CatalogItem objects into the vector store.
        
        Args:
            accelerators: List of CatalogItem objects to index
        """
        if not accelerators:
            return
        
        for acc in accelerators:
            # Combine name and description for search
            doc_text = f"{acc.name}. {acc.description}. {' '.join(acc.products_and_services)}"
            tokens = self._tokenize(doc_text)
            
            doc = Document(
                id=acc.id,
                text=doc_text,
                tokens=tokens,
                metadata={
                    "name": acc.name,
                    "solution_area": acc.solution_area,
                    "technical_complexity": acc.technical_complexity,
                    "repository_url": acc.repository_url,
                    "responsible_ai_tag": str(acc.responsible_ai_tag),
                    "deployment_type": acc.deployment_type
                }
            )
            
            self.documents[acc.id] = doc
            
            # Build metadata indices for filtering
            self.metadata_index[f"area:{acc.solution_area}"].append(acc.id)
            self.metadata_index[f"complexity:{acc.technical_complexity}"].append(acc.id)
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        solution_area: Optional[str] = None,
        complexity: Optional[str] = None
    ) -> Dict[str, List]:
        """
        Semantic search over accelerators with optional metadata filtering.
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            solution_area: Optional filter by solution area
            complexity: Optional filter by complexity level
            
        Returns:
            Dict with 'ids', 'documents', 'metadatas', 'distances'
        """
        if not self.documents:
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        # Get candidate IDs based on filters
        candidate_ids = set(self.documents.keys())
        
        if solution_area:
            # Filter by solution area (handle both string and enum values)
            filtered_ids = {
                doc_id for doc_id in candidate_ids
                if str(self.documents[doc_id].metadata.get("solution_area", "")).endswith(solution_area)
            }
            candidate_ids &= filtered_ids if filtered_ids else set()
        
        if complexity:
            # Filter by complexity (handle both string and enum values)
            filtered_ids = {
                doc_id for doc_id in candidate_ids
                if str(self.documents[doc_id].metadata.get("technical_complexity", "")).endswith(complexity)
            }
            candidate_ids &= filtered_ids if filtered_ids else set()
        
        if not candidate_ids:
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}
        
        # Score documents
        scores = []
        for doc_id in candidate_ids:
            doc = self.documents[doc_id]
            similarity = self._compute_similarity(query_tokens, doc.tokens)
            scores.append((doc_id, similarity))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-n results
        results = scores[:n_results]
        
        ids = [doc_id for doc_id, _ in results]
        documents = [self.documents[doc_id].text for doc_id in ids]
        metadatas = [self.documents[doc_id].metadata for doc_id in ids]
        distances = [1.0 - score for _, score in results]  # Convert similarity to distance
        
        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "distances": distances
        }
    
    def get_by_id(self, accelerator_id: str) -> Optional[Dict]:
        """
        Retrieve a specific accelerator by ID.
        
        Args:
            accelerator_id: The unique ID of the accelerator
            
        Returns:
            Dict with document and metadata or None
        """
        if accelerator_id not in self.documents:
            return None
        
        doc = self.documents[accelerator_id]
        return {
            "id": doc.id,
            "document": doc.text,
            "metadata": doc.metadata
        }
    
    def list_all(self) -> List[Dict]:
        """
        Get all items in the vector store.
        
        Returns:
            List of all indexed accelerators with metadata
        """
        items = []
        for doc in self.documents.values():
            items.append({
                "id": doc.id,
                "document": doc.text,
                "metadata": doc.metadata
            })
        
        return items
    
    def clear(self) -> None:
        """Delete all items from the vector store."""
        self.documents.clear()
        self.metadata_index.clear()


# For API compatibility, export as VectorStore
VectorStore = SimpleVectorStore
