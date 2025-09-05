"""
Similarity utilities for search and discovery.
"""

import numpy as np
from typing import Union


def compute_bm25_score(query, document, additional_context=None):
    """Compute BM25 score manually for a query and document, optionally including additional context."""
    if not query:
        return 0.0
        
    doc_score = _compute_bm25_score_single(query, document)
    if additional_context:
        context_score = _compute_bm25_score_single(query, additional_context)
        return max(doc_score, context_score)
    
    return doc_score


def _compute_bm25_score_single(query, document, k1=1.2, b=0.75, avg_doc_length=100):
    """Compute BM25 score for a single document."""
    if not document:
        return 0.0
        
    query_terms = query.lower().split()
    doc_terms = document.lower().split()
    
    # Count term frequencies
    doc_term_freq = {}
    for term in doc_terms:
        doc_term_freq[term] = doc_term_freq.get(term, 0) + 1
    
    # Calculate BM25 score
    doc_length = len(doc_terms)
    
    score = 0.0
    for term in query_terms:
        if term in doc_term_freq:
            tf = doc_term_freq[term]
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
            score += numerator / denominator
    
    return score


def normalize_bm25_scores(scores, method='minmax', max_score=20.0):
    """
    Normalize BM25 scores using different methods.
    Args:
        scores (list): List of BM25 scores to normalize
        method (str): Normalization method ('linear', 'log', 'minmax')
        max_score (float): Maximum score for linear normalization
    Returns:
        list: List of normalized scores in the same order as input scores
    """
    if not scores:
        return []
        
    # Validate method
    valid_methods = ['linear', 'log', 'minmax']
    if method not in valid_methods:
        method = 'minmax'
        
    scores = np.array(scores, dtype=float)
    
    if method == 'linear':
        # Linear normalization with max score
        normalized = np.minimum(scores / max_score, 1.0)
    elif method == 'log':
        # Log scaling
        log_scores = np.log1p(scores)
        # Min-max scaling to [0,1]
        score_range = log_scores.max() - log_scores.min()
        if score_range < 1e-8:  # Single score or identical scores
            normalized = np.ones_like(log_scores)  # Return 1.0 for all scores
        else:
            normalized = (log_scores - log_scores.min()) / score_range
    elif method == 'minmax':
        # Min-max scaling to [0,1]
        score_range = scores.max() - scores.min()
        if score_range < 1e-8:  # Single score or identical scores
            normalized = np.ones_like(scores)  # Return 1.0 for all scores
        else:
            normalized = (scores - scores.min()) / score_range
    else:
        # Default to minmax
        score_range = scores.max() - scores.min()
        if score_range < 1e-8:
            normalized = np.ones_like(scores)
        else:
            normalized = (scores - scores.min()) / score_range
    
    # Return list of normalized scores in the same order as input
    return [float(norm) for norm in normalized]


def compute_vector_score(query_vector: Union[bytes, np.ndarray], doc_vector: Union[bytes, np.ndarray], normalize_score: bool = True) -> float:
    """Compute semantic similarity between two embedding vectors using cosine similarity.
    Return similarity score in [0,1] if normalize_score=True, otherwise [-1,1]"""
    if not query_vector or not doc_vector:
        return 0.0
    
    # Convert bytes back to numpy arrays
    if isinstance(query_vector, bytes):
        query_array = np.frombuffer(query_vector, dtype=np.float32)
    else:
        query_array = query_vector
    if isinstance(doc_vector, bytes):
        doc_array = np.frombuffer(doc_vector, dtype=np.float32)
    else:
        doc_array = doc_vector

    # Compute norms
    query_norm = np.linalg.norm(query_array)
    doc_norm = np.linalg.norm(doc_array)
    if query_norm == 0 or doc_norm == 0:
        return 0.0
    
    # L2 normalize
    query_array = query_array / query_norm
    doc_array = doc_array / doc_norm

    # Cosine similarity
    similarity = float(np.dot(query_array, doc_array))

    # Normalize to [0,1]
    if normalize_score:
        similarity = (similarity + 1.0) / 2.0

    return similarity
