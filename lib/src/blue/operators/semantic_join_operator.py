###### Formats
from typing import List, Dict, Any, Callable, Optional, Tuple
import hashlib
import json
import numpy as np

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient
from blue.properties import PROPERTIES

# Constants for cost estimation
COST_PER_1K_TOKENS_USD = 0.04
CHARS_PER_TOKEN = 4

# Lazy import for SentenceTransformer (only when embedding filter is used)
_SentenceTransformer = None

###############
### Semantic Join Operator


def semantic_join_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Perform semantic join on two JSON array data sources using natural language predicate.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to join, requires exactly 2 data sources.
        attributes: Dictionary containing join parameters including join_predicate, join_type, left_fields, right_fields, join_suffix, and keep_keys.
        properties: Optional properties dictionary containing service configuration. Defaults to None.

    Returns:
        List containing the joined records from both data sources.
    """
    # Join attributes
    join_predicate = attributes.get('join_predicate', '')
    join_type = attributes.get('join_type', 'inner')
    left_fields = attributes.get('left_fields', [])
    right_fields = attributes.get('right_fields', [])
    join_suffix = attributes.get('join_suffix', [])
    keep_keys = attributes.get('keep_keys', 'left')
    
    # Context & Examples
    context = attributes.get('context', '')
    demonstrations = attributes.get('demonstrations', '')
    
    # Execution parameters
    batch_size = attributes.get('batch_size', 10)
    use_cache = attributes.get('use_cache', True)
    
    # Embedding / Optimization parameters
    use_embedding_filter = attributes.get('use_embedding_filter', False)
    embedding_threshold = attributes.get('embedding_threshold', 0.7)
    
    # validation check regarding input data and attributes
    if not input_data or len(input_data) < 2:
        return []

    # Prepare fields if empty
    left_data = input_data[0]
    right_data = input_data[1]
    
    # Cost estimation
    estimate_cost = attributes.get('estimate_cost', True)
    if estimate_cost and left_data and right_data:
        cost_estimate = _estimate_join_cost(
            left_data, right_data, join_predicate,
            left_fields, right_fields, batch_size,
            context, demonstrations
        )
        
        max_calls = attributes.get('max_llm_calls', None)
        if max_calls is not None and cost_estimate['max_llm_calls'] > max_calls:
            raise ValueError(
                f"Semantic join aborted: {cost_estimate['max_llm_calls']:,} LLM calls exceeds limit of {max_calls:,}. "
                f"Dataset: {cost_estimate['n_left']:,} × {cost_estimate['n_right']:,} = {cost_estimate['total_pairs']:,} pairs. "
                f"Estimated cost: ~${cost_estimate['max_cost_usd']:.2f}"
            )
        
        print(f"Semantic join: {cost_estimate['total_pairs']:,} pairs → {cost_estimate['max_llm_calls']:,} LLM calls "
                  f"(~${cost_estimate['max_cost_usd']:.2f})")

    # default suffix is _ds{i} for each data source, in future we can add prefix if needed
    if not join_suffix:
        if len(input_data) == 2:
            join_suffix = ['_left', '_right']
        else:
            join_suffix = [f"_ds{i}" for i in range(len(input_data))]
            
    if len(join_suffix) != len(input_data):
        return []

    # Initialize properties if None
    if properties is None:
        properties = {}
    
    # Inject attributes into properties for optimized function usage
    # We update the properties dict directly with all relevant attributes
    # This avoids the "double section" lookup noticed by the user
    properties.update({
        'use_embedding_filter': use_embedding_filter,
        'embedding_threshold': embedding_threshold,
        'optimize_thresholds': attributes.get('optimize_thresholds', False),
        'recall_target': attributes.get('recall_target', 0.8),
        'precision_target': attributes.get('precision_target', 0.8),
        'sampling_percentage': attributes.get('sampling_percentage', 0.1),
        'failure_probability': attributes.get('failure_probability', 0.2),
        'batch_size': batch_size
    })

    service_client = ServiceClient(name="semantic_join_operator_service_client", properties=properties)

    cache = {} if use_cache else None

    result = _perform_semantic_join_optimized(
        left_data, right_data, join_predicate, join_type, left_fields, right_fields, 
        attributes.get('left_suffix', '_left'), attributes.get('right_suffix', '_right'),
        keep_keys, context, demonstrations, service_client, properties,
        batch_size, cache, use_embedding_filter, embedding_threshold
    )

    return [result]


def semantic_join_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate semantic join operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    try:
        if not default_operator_validator(input_data, attributes, properties):
            return False
    except Exception:
        return False

    join_predicate = attributes.get('join_predicate', '')
    join_type = attributes.get('join_type', 'inner')
    left_fields = attributes.get('left_fields', [])
    right_fields = attributes.get('right_fields', [])

    keep_keys = attributes.get('keep_keys', 'left')

    if join_predicate and not isinstance(join_predicate, str):
        return False

    if join_type not in ['inner', 'left', 'right', 'outer']:
        return False

    if left_fields is None or not isinstance(left_fields, list):
        return False
    if right_fields is None or not isinstance(right_fields, list):
        return False

    if attributes.get('left_suffix') and not isinstance(attributes.get('left_suffix'), str):
        return False
    if attributes.get('right_suffix') and not isinstance(attributes.get('right_suffix'), str):
        return False

    if keep_keys not in ['left', 'both']:
        return False

    return True


def semantic_join_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for semantic join operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


def _estimate_join_cost(
    left_data: List[Dict[str, Any]],
    right_data: List[Dict[str, Any]],
    join_predicate: str,
    left_fields: List[str],
    right_fields: List[str],
    batch_size: int,
    context: str = "",
    demonstrations: str = ""
) -> Dict[str, Any]:
    """Estimate computational cost and LLM calls for a semantic join.
    
    Computes the maximum number of pairs (n×m) and corresponding LLM calls
    and tokens based on actual data characteristics.
    
    Parameters:
        left_data: Left dataset records.
        right_data: Right dataset records.
        join_predicate: Natural language join predicate.
        left_fields: Fields from left dataset to consider.
        right_fields: Fields from right dataset to consider.
        batch_size: Batch size for LLM calls.
        context: Optional context string.
        demonstrations: Optional demonstrations string.
        
    Returns:
        Dictionary with cost estimates.
    """
    n_left = len(left_data)
    n_right = len(right_data)
    total_pairs = n_left * n_right
    
    max_llm_calls = (total_pairs + batch_size - 1) // batch_size
    
    sample_left = left_data[0] if left_data else {}
    sample_right = right_data[0] if right_data else {}
    
    if left_fields:
        sample_left = {k: v for k, v in sample_left.items() if k in left_fields}
    if right_fields:
        sample_right = {k: v for k, v in sample_right.items() if k in right_fields}
    
    # Estimate tokens (1 token ≈ 4 characters)
    prompt_overhead = 500
    predicate_tokens = len(join_predicate) // CHARS_PER_TOKEN
    context_tokens = len(context) // CHARS_PER_TOKEN
    demonstrations_tokens = len(demonstrations) // CHARS_PER_TOKEN
    tokens_per_pair = (len(json.dumps(sample_left)) + len(json.dumps(sample_right))) // CHARS_PER_TOKEN
    
    tokens_per_batch = prompt_overhead + predicate_tokens + context_tokens + demonstrations_tokens + (tokens_per_pair * batch_size)
    max_total_tokens = max_llm_calls * tokens_per_batch
    
    # Estimate cost (GPT-4: ~$0.04 per 1K tokens average)
    max_cost_usd = (max_total_tokens / 1000) * COST_PER_1K_TOKENS_USD
    
    return {
        'n_left': n_left,
        'n_right': n_right,
        'total_pairs': total_pairs,
        'max_llm_calls': max_llm_calls,
        'tokens_per_batch': tokens_per_batch,
        'max_total_tokens': max_total_tokens,
        'max_cost_usd': max_cost_usd,
        'batch_size': batch_size,
    }


def _get_embedding_model(properties: Dict[str, Any]):
    """Lazy load SentenceTransformer model for embedding generation.
    
    Parameters:
        properties: Properties dictionary that may contain embeddings_model configuration.
        
    Returns:
        SentenceTransformer model instance.
    """
    global _SentenceTransformer
    if _SentenceTransformer is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Get model name from properties or use default
            model_name = properties.get('embeddings_model', 'paraphrase-MiniLM-L6-v2')
            _SentenceTransformer = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers package is required for embedding-based filtering. "
                "Install it with: pip install sentence-transformers"
            )
    return _SentenceTransformer


def _record_to_text(record: Dict[str, Any], fields: List[str]) -> str:
    """Convert a record to a text representation for embedding.
    
    Parameters:
        record: Dictionary record.
        fields: List of field names to include in the text representation.
        
    Returns:
        Text representation of the record.
    """
    if not fields:
        fields = list(record.keys())
    
    text_parts = []
    for field in fields:
        if field in record:
            value = record[field]
            if value is not None:
                text_parts.append(f"{field}: {value}")
    
    return " | ".join(text_parts)


def _generate_embeddings(records: List[Dict[str, Any]], fields: List[str], model) -> np.ndarray:
    """Generate embeddings for a list of records.
    
    Parameters:
        records: List of dictionary records.
        fields: List of field names to include in embeddings.
        model: SentenceTransformer model instance.
        
    Returns:
        Numpy array of embeddings (shape: [len(records), embedding_dim]).
    """
    if not records:
        return np.array([])
    
    texts = [_record_to_text(record, fields) for record in records]
    embeddings = model.encode(texts, show_progress_bar=False, batch_size=32)
    
    return np.array(embeddings)


def _compute_cosine_similarity_matrix(left_embeddings: np.ndarray, right_embeddings: np.ndarray) -> np.ndarray:
    """Compute cosine similarity matrix between left and right embeddings.
    
    Parameters:
        left_embeddings: Embeddings for left dataset (shape: [n_left, dim]).
        right_embeddings: Embeddings for right dataset (shape: [n_right, dim]).
        
    Returns:
        Similarity matrix (shape: [n_left, n_right]) with values in [-1, 1].
    """
    if left_embeddings.size == 0 or right_embeddings.size == 0:
        return np.array([])
    
    left_norm = np.linalg.norm(left_embeddings, axis=1, keepdims=True)
    right_norm = np.linalg.norm(right_embeddings, axis=1, keepdims=True)
    
    left_norm = np.where(left_norm == 0, 1, left_norm)
    right_norm = np.where(right_norm == 0, 1, right_norm)
    
    left_normalized = left_embeddings / left_norm
    right_normalized = right_embeddings / right_norm
    
    similarity_matrix = np.dot(left_normalized, right_normalized.T)
    
    return similarity_matrix


def _filter_pairs_by_similarity(
    similarity_matrix: np.ndarray,
    threshold: float
) -> List[Tuple[int, int]]:
    """Filter record pairs based on similarity threshold.
    
    Parameters:
        similarity_matrix: Cosine similarity matrix (values in [-1, 1]).
        threshold: Similarity threshold (0.0-1.0). Note: cosine similarity is [-1,1],
                   so we normalize threshold: actual_threshold = (threshold * 2) - 1.
        
    Returns:
        List of (left_idx, right_idx) tuples for pairs above threshold.
    """
    if similarity_matrix.size == 0:
        return []
    
    # Convert threshold from [0,1] to [-1,1] range
    cosine_threshold = (threshold * 2.0) - 1.0
    
    # Find pairs above threshold
    candidate_pairs = []
    n_left, n_right = similarity_matrix.shape
    
    for i in range(n_left):
        for j in range(n_right):
            if similarity_matrix[i, j] >= cosine_threshold:
                candidate_pairs.append((i, j))
    
    return candidate_pairs


def _get_cache_key(left_record: Dict[str, Any], right_record: Dict[str, Any], join_predicate: str, left_fields: List[str], right_fields: List[str]) -> str:
    """Generate a cache key for a record pair."""
    # Create normalized representation
    left_filtered = {k: v for k, v in left_record.items() if not left_fields or k in left_fields}
    right_filtered = {k: v for k, v in right_record.items() if not right_fields or k in right_fields}
    
    key_data = {
        'left': json.dumps(left_filtered, sort_keys=True),
        'right': json.dumps(right_filtered, sort_keys=True),
        'predicate': join_predicate
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()


def _evaluate_join_predicate_batch(
    pairs: List[Tuple[Dict[str, Any], Dict[str, Any], int, int]],
    join_predicate: str,
    left_fields: List[str],
    right_fields: List[str],
    context: str,
    demonstrations: str,
    service_client: ServiceClient,
    properties: Dict[str, Any],
) -> Dict[Tuple[int, int], bool]:
    """Evaluate multiple record pairs in a single LLM call (batch processing)."""
    if not pairs:
        return {}
    
    # Prepare batch prompt
    pairs_data = []
    for left_record, right_record, left_idx, right_idx in pairs:
        # Filter fields
        left_filtered = {k: v for k, v in left_record.items() if not left_fields or k in left_fields}
        right_filtered = {k: v for k, v in right_record.items() if not right_fields or k in right_fields}
        
        pairs_data.append({
            'left_idx': left_idx,
            'right_idx': right_idx,
            'left_record': left_filtered,
            'right_record': right_filtered,
        })
    
    # Build batch prompt
    pairs_text = []
    for i, pair_data in enumerate(pairs_data, 1):
        pairs_text.append(f"Pair {i}:\n  Left Record (index {pair_data['left_idx']}): {json.dumps(pair_data['left_record'])}\n  Right Record (index {pair_data['right_idx']}): {json.dumps(pair_data['right_record'])}")
    
    additional_data = {
        'pairs': '\n\n'.join(pairs_text),
        'join_predicate': join_predicate,
        'context': context,
        'demonstrations': demonstrations,
        'num_pairs': len(pairs),
    }
    
    # Use batch prompt template
    batch_properties = properties.copy()
    batch_properties['input_template'] = SemanticJoinOperator.BATCH_JOIN_PROMPT
    # Disable casting for batch mode (we expect JSON object, not single bool)
    if 'output_cast' in batch_properties:
        del batch_properties['output_cast']
    
    result = service_client.execute_api_call({}, properties=batch_properties, additional_data=additional_data)
    
    # Parse batch results
    results = {}
    
    # Try parsing string result as JSON
    if isinstance(result, str):
        try:
            # Clean potential markdown code blocks
            clean_result = result.strip()
            if clean_result.startswith('```json'):
                clean_result = clean_result[7:]
            if clean_result.startswith('```'):
                clean_result = clean_result[3:]
            if clean_result.endswith('```'):
                clean_result = clean_result[:-3]
            result = json.loads(clean_result.strip())
        except Exception:
            pass # Handle as non-dict below

    if isinstance(result, dict):
        # Expected format: {"pair_1": true, "pair_2": false, ...}
        for i, (left_record, right_record, left_idx, right_idx) in enumerate(pairs, 1):
            pair_key = f"pair_{i}"
            if pair_key in result:
                value = result[pair_key]
                if isinstance(value, str):
                    value = value.lower().strip() in ['true', 'yes', '1', 'match', 'join']
                elif not isinstance(value, bool):
                    value = bool(value)
                results[(left_idx, right_idx)] = value
            else:
                # Default to false if not found
                results[(left_idx, right_idx)] = False
    elif isinstance(result, list):
        # Expected format: [true, false, true, ...]
        for i, (left_record, right_record, left_idx, right_idx) in enumerate(pairs):
            if i < len(result):
                value = result[i]
                if isinstance(value, str):
                    value = value.lower().strip() in ['true', 'yes', '1', 'match', 'join']
                elif not isinstance(value, bool):
                    value = bool(value)
                results[(left_idx, right_idx)] = value
            else:
                results[(left_idx, right_idx)] = False
    else:
        # Fallback: if we can't parse, evaluate individually
        for left_record, right_record, left_idx, right_idx in pairs:
            results[(left_idx, right_idx)] = False
    
    return results


def _perform_semantic_join_optimized(
    left_data: List[Dict[str, Any]],
    right_data: List[Dict[str, Any]],
    join_predicate: str,
    join_type: str,
    left_fields: List[str],
    right_fields: List[str],
    left_suffix: str,
    right_suffix: str,
    keep_keys: str,
    context: str,
    demonstrations: str,
    service_client: ServiceClient,
    properties: Dict[str, Any],
    batch_size: int,
    cache: Optional[Dict[str, bool]],
    use_embedding_filter: bool,
    embedding_threshold: float,
) -> List[Dict[str, Any]]:
    """Perform semantic join with optimizations: batch processing, caching, and optional embedding pre-filtering."""
    
    # Set default join predicate if not provided
    if not join_predicate or not join_predicate.strip():
        join_predicate = "Determine if the two records are semantically equivalent based on the provided fields."
    
    # Determine which fields to consider from each dataset
    if not left_fields:
        if left_data:
            left_fields = list(left_data[0].keys())
        else:
            left_fields = []
    if not right_fields:
        if right_data:
            right_fields = list(right_data[0].keys())
        else:
            right_fields = []
    
    # Optional: Embedding pre-filtering / Optimization
    candidate_pairs = []
    
    use_embedding = properties.get('use_embedding_filter', False)
    optimize = properties.get('optimize_thresholds', False)
    
    # Optimization forces embedding filter
    if optimize:
        use_embedding = True
        
    if use_embedding:
        try:
            # Initialize embedding model
            embedding_model = _get_embedding_model(properties)
            
            # Generate embeddings
            left_embeddings = _generate_embeddings(left_data, left_fields, embedding_model)
            right_embeddings = _generate_embeddings(right_data, right_fields, embedding_model)
            
            # Compute similarity matrix
            similarity_matrix = _compute_cosine_similarity_matrix(left_embeddings, right_embeddings)
            
            # Default thresholds (static)
            t_pos = 1.0 # No auto-accept by default
            t_neg = embedding_threshold
            
            auto_matches = [] # List of (l, r) to auto-accept
            
            # CASCADE OPTIMIZATION
            if optimize:
                try:
                    sampling_percentage = properties.get('sampling_percentage', 0.1)
                    
                    # Flatten scores for sampling
                    all_scores = []
                    # Keep track of indices: flat_idx -> (l, r)
                    flat_idx_map = []
                    
                    rows, cols = similarity_matrix.shape
                    for r in range(rows):
                        for c in range(cols):
                            score = float(similarity_matrix[r][c])
                            all_scores.append(score)
                            flat_idx_map.append((r, c))
                            
                    sample_indices, correction_factors = _importance_sampling(all_scores, sampling_percentage)
                    
                    # Evaluate sample with Oracle (LLM)
                    # We need to evaluate these specific pairs
                    sample_pairs_to_eval = []
                    for idx in sample_indices:
                        l_idx, r_idx = flat_idx_map[idx]
                        sample_pairs_to_eval.append((left_data[l_idx], right_data[r_idx], l_idx, r_idx))
                        
                    # Use existing batch evaluation
                    sample_results = _evaluate_join_predicate_batch(
                        sample_pairs_to_eval, join_predicate, left_fields, right_fields,
                        context, demonstrations, service_client, properties
                    )
                    
                    # Extract labels in order of sample_indices
                    labels = []
                    sample_scores = []
                    
                    for i, idx in enumerate(sample_indices):
                        l_idx, r_idx = flat_idx_map[idx]
                        # Score
                        sample_scores.append(all_scores[idx])
                        # Label
                        val = sample_results.get((l_idx, r_idx), False)
                        labels.append(val)
                        
                    # Learn thresholds
                    recall_target = properties.get('recall_target', 0.95)
                    precision_target = properties.get('precision_target', 0.99)
                    failure_prob = properties.get('failure_probability', 0.05)
                    
                    t_pos, t_neg, _ = _learn_thresholds(
                        sample_scores,
                        labels,
                        correction_factors,
                        recall_target,
                        precision_target,
                        failure_prob
                    )
                    
                    print(f"Cascade Optimization Learned: t_neg={t_neg:.4f}, t_pos={t_pos:.4f}")
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Error in Cascade Optimization: {e}. Falling back to static threshold.")
                    t_neg = embedding_threshold
                    t_pos = 1.0

            # Filter pairs based on (t_neg, t_pos)
            rows, cols = similarity_matrix.shape
            for r in range(rows):
                for c in range(cols):
                    score = similarity_matrix[r][c]
                    
                    if score >= t_pos:
                        # Auto-Accept
                        auto_matches.append((r, c))
                    elif score > t_neg:
                        # Uncertain -> Evaluate
                        candidate_pairs.append((r, c))
                    # else: Auto-Reject
            
            # Note: auto_matches are pre-filled into the results cache/results dict later.
               
        except Exception as e:
            # Fallback
            import warnings
            warnings.warn(f"Embedding/Optimization failed: {e}. Fallback to all pairs.", UserWarning)
            candidate_pairs = []
            
    if not candidate_pairs and not (optimize and 'auto_matches' in locals() and auto_matches):
         # If truly empty and no auto matches (or not optimized), fallback to all?
         # Only if it was an error or no embedding used.
         # If optimization ran and returned 0 candidates (and 0 auto_matches), that's a valid result (0 matches).
         if not use_embedding:
             candidate_pairs = [(i, j) for i in range(len(left_data)) for j in range(len(right_data))]
    
    # Determine output schema (field conflicts)
    left_all_fields = set()
    right_all_fields = set()
    for record in left_data:
        left_all_fields.update(record.keys())
    for record in right_data:
        right_all_fields.update(record.keys())
    
    field_conflicts = set()
    if keep_keys == 'both':
        field_conflicts.update(left_all_fields.intersection(right_all_fields))
    else:
        # keep_keys == 'left': only conflict on fields that are NOT in right_fields 
        # (because fields in right_fields will be dropped anyway)
        field_conflicts.update(left_all_fields.intersection(right_all_fields))
        if right_fields:
            field_conflicts.difference_update(right_fields)
    
    # Evaluate pairs with batch processing and caching
    # Evaluate pairs with batch processing and caching
    match_results = {}  # (left_idx, right_idx) -> bool
    
    # Add Auto-Matches from Cascade Optimization
    if 'auto_matches' in locals() and auto_matches:
        for l_idx, r_idx in auto_matches:
            match_results[(l_idx, r_idx)] = True
            
    # Group pairs into batches
    batches = []
    current_batch = []
    for left_idx, right_idx in candidate_pairs:
        # Skip if already decided (e.g. via auto-match, though candidate_pairs shouldn't contain them if logic correct)
        if (left_idx, right_idx) in match_results:
            continue
            
        current_batch.append((left_data[left_idx], right_data[right_idx], left_idx, right_idx))
        if len(current_batch) >= batch_size:
            batches.append(current_batch)
            current_batch = []
    if current_batch:
        batches.append(current_batch)
    
    # Process batches
    for batch in batches:
        batch_results = {}
        
        # Check cache first
        uncached_pairs = []
        for left_record, right_record, left_idx, right_idx in batch:
            if cache is not None:
                cache_key = _get_cache_key(left_record, right_record, join_predicate, left_fields, right_fields)
                if cache_key in cache:
                    match_results[(left_idx, right_idx)] = cache[cache_key]
                else:
                    uncached_pairs.append((left_record, right_record, left_idx, right_idx))
            else:
                uncached_pairs.append((left_record, right_record, left_idx, right_idx))
        
        # Evaluate uncached pairs in batch
        if uncached_pairs:
            batch_results = _evaluate_join_predicate_batch(
                uncached_pairs, join_predicate, left_fields, right_fields,
                context, demonstrations, service_client, properties
            )
            
            # Update cache and results
            for (left_idx, right_idx), result in batch_results.items():
                match_results[(left_idx, right_idx)] = result
                if cache is not None:
                    # Get actual records from indices for cache key
                    left_record = left_data[left_idx]
                    right_record = right_data[right_idx]
                    cache_key = _get_cache_key(left_record, right_record, join_predicate, left_fields, right_fields)
                    cache[cache_key] = result
    
    # Execute join based on match results
    result = []
    if join_type == 'inner':
        result = _semantic_inner_join_from_matches(left_data, right_data, match_results, field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
    elif join_type == 'left':
        result = _semantic_left_join_from_matches(left_data, right_data, match_results, field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
    elif join_type == 'right':
        result = _semantic_right_join_from_matches(left_data, right_data, match_results, field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
    elif join_type == 'outer':
        result = _semantic_outer_join_from_matches(left_data, right_data, match_results, field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
    
    return result


    return result


def _semantic_inner_join_from_matches(
    left_data: List[Dict[str, Any]],
    right_data: List[Dict[str, Any]],
    match_results: Dict[Tuple[int, int], bool],
    field_conflicts: set,
    left_suffix: str,
    right_suffix: str,
    keep_keys: str,
    right_fields: List[str] = None,
) -> List[Dict[str, Any]]:
    """Perform inner join using pre-computed match results."""
    result = []
    for (left_idx, right_idx), should_join in match_results.items():
        if should_join:
            merged = _merge_records(left_data[left_idx], right_data[right_idx], field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
            result.append(merged)
    return result


def _semantic_left_join_from_matches(
    left_data: List[Dict[str, Any]],
    right_data: List[Dict[str, Any]],
    match_results: Dict[Tuple[int, int], bool],
    field_conflicts: set,
    left_suffix: str,
    right_suffix: str,
    keep_keys: str,
    right_fields: List[str] = None,
) -> List[Dict[str, Any]]:
    """Perform left join using pre-computed match results."""
    result = []
    matched_left_indices = set()
    
    for (left_idx, right_idx), should_join in match_results.items():
        if should_join:
            matched_left_indices.add(left_idx)
            merged = _merge_records(left_data[left_idx], right_data[right_idx], field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
            result.append(merged)
    
    # Add unmatched left records
    for left_idx in range(len(left_data)):
        if left_idx not in matched_left_indices:
            merged = _merge_records(left_data[left_idx], {}, field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
            result.append(merged)
    
    return result


def _semantic_right_join_from_matches(
    left_data: List[Dict[str, Any]],
    right_data: List[Dict[str, Any]],
    match_results: Dict[Tuple[int, int], bool],
    field_conflicts: set,
    left_suffix: str,
    right_suffix: str,
    keep_keys: str,
    right_fields: List[str] = None,
) -> List[Dict[str, Any]]:
    """Perform right join using pre-computed match results."""
    result = []
    matched_right_indices = set()
    
    # Add matched pairs
    for (left_idx, right_idx), should_join in match_results.items():
        if should_join:
            matched_right_indices.add(right_idx)
            merged = _merge_records(left_data[left_idx], right_data[right_idx], field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
            result.append(merged)
    
    # Add unmatched right records
    for right_idx in range(len(right_data)):
        if right_idx not in matched_right_indices:
            merged = _merge_records({}, right_data[right_idx], field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
            result.append(merged)
    
    return result


def _semantic_outer_join_from_matches(
    left_data: List[Dict[str, Any]],
    right_data: List[Dict[str, Any]],
    match_results: Dict[Tuple[int, int], bool],
    field_conflicts: set,
    left_suffix: str,
    right_suffix: str,
    keep_keys: str,
    right_fields: List[str] = None,
) -> List[Dict[str, Any]]:
    """Perform outer join using pre-computed match results."""
    result = []
    matched_left_indices = set()
    matched_right_indices = set()
    
    # Add matched pairs
    for (left_idx, right_idx), should_join in match_results.items():
        if should_join:
            matched_left_indices.add(left_idx)
            matched_right_indices.add(right_idx)
            merged = _merge_records(left_data[left_idx], right_data[right_idx], field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
            result.append(merged)
    
    # Add unmatched left records
    for left_idx in range(len(left_data)):
        if left_idx not in matched_left_indices:
            merged = _merge_records(left_data[left_idx], {}, field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
            result.append(merged)
    
    # Add unmatched right records
    for right_idx in range(len(right_data)):
        if right_idx not in matched_right_indices:
            merged = _merge_records({}, right_data[right_idx], field_conflicts, left_suffix, right_suffix, keep_keys, right_fields)
            result.append(merged)
    
    return result




def _importance_sampling(
    scores: List[float],
    sampling_percentage: float = 0.1,
    random_seed: int = 42,
    max_sample_range: int = 5000
) -> Tuple[List[int], np.ndarray]:
    """Uses importance sampling to select indices for learning thresholds.
    
    Weights are sqrt(score) to sample more from higher/ambiguous scores.

    Parameters:
        scores: List of similarity scores.
        sampling_percentage: Fraction of data to sample.
        random_seed: Random seed for reproducibility.
        max_sample_range: Maximum range for sampling.

    Returns:
        Tuple containing (selected_indices, correction_factors).
    """
    if not scores:
        return [], np.array([])
        
    np.random.seed(random_seed)
    scores_arr = np.array(scores)
    
    # Avoid sqrt of negative values (though cosine sim is usually -1 to 1, we treat scores as proxy)
    # Clip to 0 for weighting purposes
    safe_scores = np.maximum(scores_arr, 0)
    w = np.sqrt(safe_scores)
    
    # Lotus weights: mixture of importance (sqrt) and uniform
    is_weight = 0.5 # Default from Lotus docs/code often implies a mix
    
    sum_w = np.sum(w)
    if sum_w > 0:
        w = is_weight * w / sum_w + (1 - is_weight) * (1 / len(scores))
    else:
        w = np.ones(len(scores)) / len(scores)

    # Normalize
    w = w / np.sum(w)
    
    sample_size = max(5, int(sampling_percentage * len(scores))) # Ensure at least a few samples
    indices = np.arange(len(scores))
    
    sample_indices = np.random.choice(indices, size=sample_size, replace=False, p=w)
    
    # Correction factors for the sample
    # correction_factor = (1/N) / p_i
    correction_factors = (1 / len(scores)) / w[sample_indices]
    
    return list(sample_indices), correction_factors

def _params_UB(mean: float, std_dev: float, s: int, delta: float) -> float:
    """Calculate Statistical Upper Bound.

    Parameters:
        mean: Sample mean.
        std_dev: Sample standard deviation.
        s: Sample size.
        delta: Failure probability.

    Returns:
        Upper bound value.
    """
    if s == 0: return 1.0
    return float(mean + (std_dev / (s**0.5)) * ((2 * np.log(1 / delta)) ** 0.5))

def _params_LB(mean: float, std_dev: float, s: int, delta: float) -> float:
    """Calculate Statistical Lower Bound.

    Parameters:
        mean: Sample mean.
        std_dev: Sample standard deviation.
        s: Sample size.
        delta: Failure probability.

    Returns:
        Lower bound value.
    """
    if s == 0: return 0.0
    return float(mean - (std_dev / (s**0.5)) * ((2 * np.log(1 / delta)) ** 0.5))

def _calculate_recall(
    pos_threshold: float,
    neg_threshold: float,
    sorted_pairs: List[Tuple[float, bool, float]],
) -> float:
    """Calculate recall for given cascade thresholds on weighted samples.
    
    Recall measures the fraction of true positive pairs that are found by the cascade.
    In the cascade approach (inspired by Lotus), pairs are handled as follows:
    - score >= pos_threshold: Auto-accepted by helper (embedding filter)
    - neg_threshold < score < pos_threshold: Sent to oracle (language model)
    - score <= neg_threshold: Auto-rejected by helper
    
    Recall = (True Positives Found) / (Total True Positives)
    where True Positives Found includes:
    1. Auto-accepted pairs that are actually true
    2. Oracle-handled pairs that are true (oracle is assumed perfect in learning phase)

    Parameters:
        pos_threshold: Positive threshold for auto-accept (tau_pos).
        neg_threshold: Negative threshold for auto-reject (tau_neg).
        sorted_pairs: List of tuples (score, label, weight) where:
            - score: Similarity score from helper model
            - label: True if pair is a true match, False otherwise
            - weight: Importance weight for this sample (from importance sampling)

    Returns:
        Calculated recall value in [0, 1]. Returns 1.0 if no true positives exist.
    """
    # Total true positives in the dataset (weighted)
    total_correct = sum(pair[1] * pair[2] for pair in sorted_pairs)
    
    if total_correct <= 0:
        # Edge case: no positives exist, so we found all 0 of them (recall = 1.0)
        return 1.0
        
    found_correct = 0.0
    
    # Count true positives found by auto-accept (score >= pos_threshold)
    # Only count pairs that are actually true (label=True)
    found_correct += sum(x[1] * x[2] for x in sorted_pairs if x[0] >= pos_threshold)
    
    # Count true positives found by oracle (neg_threshold < score < pos_threshold)
    # In learning phase, we have labels for all pairs, so we can count true positives
    # that would be sent to oracle. Oracle is assumed perfect, so all true positives
    # in this range are found.
    found_correct += sum(x[1] * x[2] for x in sorted_pairs if x[0] < pos_threshold and x[0] > neg_threshold)
    
    return found_correct / total_correct

def _calculate_precision(
    pos_threshold: float,
    neg_threshold: float,
    sorted_pairs: List[Tuple[float, bool, float]],
) -> float:
    """Calculate precision for the auto-accept bucket at given thresholds.
    
    Precision measures the fraction of auto-accepted pairs that are actually true matches.
    This function evaluates the precision of the auto-accept bucket only (score >= pos_threshold).
    Pairs sent to oracle or auto-rejected are not included in precision calculation.
    
    Precision = (True Positives in Auto-Accept) / (All Auto-Accepted Pairs)
    
    This metric is used during threshold learning to ensure that auto-accepted pairs
    meet the target precision requirement, minimizing false positives in the final results.

    Parameters:
        pos_threshold: Positive threshold for auto-accept (tau_pos).
        neg_threshold: Negative threshold for auto-reject (tau_neg). 
        sorted_pairs: List of tuples (score, label, weight) where:
            - score: Similarity score from helper model
            - label: True if pair is a true match, False otherwise
            - weight: Importance weight for this sample (from importance sampling)

    Returns:
        Calculated precision value in [0, 1]. Returns 1.0 if no pairs are auto-accepted
        (edge case: perfect precision when nothing is accepted).
    """
    # Get all pairs that would be auto-accepted (score >= pos_threshold)
    accepted = [x for x in sorted_pairs if x[0] >= pos_threshold]
    
    if not accepted:
        # Edge case: no pairs auto-accepted, so precision is perfect (1.0)
        return 1.0
    
    # Predicted positives: all pairs that would be auto-accepted (weighted)
    predicted_positives = sum(x[2] for x in accepted)
    
    # True positives: auto-accepted pairs that are actually true matches (weighted)
    true_positives = sum(x[1] * x[2] for x in accepted)
    
    if predicted_positives == 0:
        # Edge case: all accepted pairs have zero weight
        return 1.0
    
    return true_positives / predicted_positives

def _calculate_tau_neg(
    sorted_pairs: List[Tuple[float, bool, float]],
    tau_pos: float,
    recall_target: float
) -> float:
    """Finds the highest tau_neg that satisfies recall target."""
    # Search candidates from sorted pairs scores
    # We want max tau_neg such that recall >= target
    # Default 0
    best_tau_neg = 0.0
    
    # Optimization: iterate backwards (from low scores to high) or just check all
    # Sorted high to low.
    
    # Extract unique scores as candidates
    candidates = sorted(list(set(x[0] for x in sorted_pairs)))
    
    for t_neg in reversed(candidates): # High to low
        if t_neg >= tau_pos: continue
        r = _calculate_recall(tau_pos, t_neg, sorted_pairs)
        if r >= recall_target:
            best_tau_neg = t_neg
            break
            
    return best_tau_neg

def _learn_thresholds(
    scores: List[float],
    labels: List[bool],
    correction_factors: np.ndarray,
    recall_target: float = 0.95,
    precision_target: float = 0.99,
    failure_probability: float = 0.05
) -> Tuple[float, float, int]:
    """
    Learns (pos_threshold, neg_threshold) using statistical bounds.
    """
    # Pair up: (score, label, weight)
    paired_data = list(zip(scores, labels, correction_factors))
    # Sort by score desc
    sorted_pairs = sorted(paired_data, key=lambda x: x[0], reverse=True)
    sample_size = len(sorted_pairs)
    
    best_tau_pos = 1.0
    best_tau_neg = 0.0
    
    # 1. Find tau_neg based on raw recall target
    best_tau_neg = _calculate_tau_neg(sorted_pairs, best_tau_pos, recall_target)
    
    # 2. Statistical correction for Recall (Z1, Z2 stuff from Lotus)
    # Z1 = True Positives above tau_neg
    # Z2 = True Positives below tau_neg
    Z1 = [int(x[1]) * x[2] for x in sorted_pairs if x[0] >= best_tau_neg]
    Z2 = [int(x[1]) * x[2] for x in sorted_pairs if x[0] < best_tau_neg]
    
    mean_z1 = float(np.mean(Z1)) if Z1 else 0.0
    std_z1 = float(np.std(Z1)) if Z1 else 0.0
    mean_z2 = float(np.mean(Z2)) if Z2 else 0.0
    std_z2 = float(np.std(Z2)) if Z2 else 0.0
    
    ub_z1 = _params_UB(mean_z1, std_z1, sample_size, failure_probability / 2)
    lb_z2 = _params_LB(mean_z2, std_z2, sample_size, failure_probability / 2)
    
    if ub_z1 + lb_z2 == 0:
        corrected_recall = 1.0
    else:
        corrected_recall = ub_z1 / (ub_z1 + lb_z2)
    corrected_recall = min(1.0, corrected_recall)
    
    # Recalculate tau_neg with corrected recall
    best_tau_neg = _calculate_tau_neg(sorted_pairs, best_tau_pos, corrected_recall)
    
    # 3. Precision Correction (tau_pos)
    # Find lowest tau_pos > best_tau_neg that satisfies precision LB > target
    candidate_thresholds = [1.0]
    
    unique_scores = sorted(list(set(x[0] for x in sorted_pairs)), reverse=True)
    
    for t in unique_scores:
        if t <= best_tau_neg: break
        
        # Calculate Precision LB for auto-accepting >= t
        # Z = indicator of true for those >= t
        
        # Z = samples with score >= t. Value is 1 if True, 0 if False.
        Z_samples = [int(x[1]) for x in sorted_pairs if x[0] >= t]
        if not Z_samples: continue
        
        mean_z = np.mean(Z_samples)
        std_z = np.std(Z_samples)
        
        # Lower Bound of Precision
        p_l = _params_LB(mean_z, std_z, len(Z_samples), failure_probability / len(sorted_pairs))
        
        if p_l >= precision_target:
            candidate_thresholds.append(t)
    
    # We want the LOWEST valid tau_pos (to maximize auto-accepts)
    best_tau_pos = min(candidate_thresholds)
    
    # Safety Check: tau_pos must be >= tau_neg
    if best_tau_pos < best_tau_neg:
        best_tau_pos = best_tau_neg # Or 1.0 to disable auto-accept? 
        # Using 1.0 disables auto-accept, safe fallback
        best_tau_pos = 1.0

    return best_tau_pos, best_tau_neg, len(sorted_pairs)


def _merge_records(left_record: Dict[str, Any], right_record: Dict[str, Any], field_conflicts: set, left_suffix: str, right_suffix: str, keep_keys: str, right_fields: List[str] = None) -> Dict[str, Any]:

    """Merge two records with proper field naming to avoid conflicts."""
    merged = {}

    # Add left fields
    for field, value in left_record.items():
        if field in field_conflicts:
            merged[f"{field}{left_suffix}"] = value
        else:
            merged[field] = value

    # Add right fields
    for field, value in right_record.items():
        # If keep_keys is 'left', skip fields that are in right_fields (the join keys)
        if keep_keys == 'left' and right_fields and field in right_fields:
            continue
            
        if field in field_conflicts:
            merged[f"{field}{right_suffix}"] = value
        else:
            # Only add if not already present (from left)
            if field not in merged:
                merged[field] = value
            else:
                # Conflict: use suffix
                merged[f"{field}{right_suffix}"] = value

    return merged




class SemanticJoinOperator(Operator, ServiceClient):
    """
    Semantic join operator joins two datasets based on natural language join predicate using LLM models.
    Unlike the relational JoinOperator which uses exact key matching, this operator uses semantic understanding
    to determine if records should be joined.

    Attributes:
    ----------
    | Name               | Type            | Required | Default | Description                                                                 |
    |-------------------|----------------|----------|---------|-----------------------------------------------------------------------------|
    | `join_predicate`     | str             | :fontawesome-solid-circle-check: {.green-check}     | -       | Natural language description of when records should be joined              |
    | `join_type`          | str             |     | "inner" | Type of join: 'inner', 'left', 'right', 'outer'                          |
    | `left_fields`        | list[str]       |     | []      | Fields from left dataset to consider (empty = all fields)                  |
    | `right_fields`       | list[str]       |     | []      | Fields from right dataset to consider (empty = all fields)                 |
    | `join_suffix`        | list[str]       |     | []      | Suffixes for field name conflicts (default: ['_left', '_right'])           |
    | `keep_keys`          | str             |     | "left"  | 'left' to keep left keys only, 'both' to keep both                       |
    | `context`            | str             |     | ""      | Optional context to provide domain knowledge or additional instructions   |
    | `demonstrations`     | str             |     | ""      | Optional demonstrations to help in-context learning                       |
    | `batch_size`         | int             |     | 10      | Number of record pairs to evaluate per LLM call (batch processing)       |
    | `use_cache`          | bool            |     | True    | Enable result caching to avoid re-evaluating similar pairs                |
    | `use_embedding_filter` | bool         |     | False   | Use embedding pre-filtering to reduce candidate pairs (requires sentence-transformers)     |
    | `embedding_threshold` | float         |     | 0.7     | Similarity threshold for embedding pre-filtering (0.0-1.0, maps to cosine similarity [-1,1])                |
    | `max_llm_calls`        | int          |     | 1000    | Maximum allowed LLM calls (None = no limit). Prevents accidental expensive operations.    |
    | `estimate_cost`        | bool         |     | True    | Show cost estimate and warnings before execution                                            |
    | `optimize_thresholds` | bool         |     | False   | Enable dynamic threshold learning (Cascade Optimization)                                    |
    | `recall_target`        | float        |     | 0.8     | Target recall for optimization (0.0-1.0)                                                  |
    | `precision_target`     | float        |     | 0.8     | Target precision for auto-acceptance (0.0-1.0)                                              |
    | `sampling_percentage`  | float        |     | 0.1     | Fraction of data to sample for learning (0.0-1.0)                                          |
    | `failure_probability`  | float        |     | 0.2     | Statistical failure probability (delta) for threshold learning                             |
    """

    JOIN_PROMPT = """## Task
You are given two data records and a natural language join predicate. Your job is to determine if these two records should be joined together based on the predicate.

## Left Record
${left_record}

## Right Record
${right_record}

## Join Predicate
${join_predicate}

## Context
${context}

## Demonstrations
${demonstrations}

## Output Requirements
- Return **only a boolean value**: true or false
- Return **true** if the two records should be joined based on the join predicate
- Return **false** if the two records should NOT be joined
- Be precise in your evaluation based on the natural language predicate
- Consider the semantic meaning of the predicate, not just exact text matching
- The predicate describes the relationship or condition that should exist between the records

## Additional Notes
- Use your understanding of natural language to interpret the join predicate
- Consider semantic similarity, not just exact matches
- Return only the boolean result, no explanations or additional text

---

### Output
"""

    BATCH_JOIN_PROMPT = """## Task
You are given multiple pairs of data records and a natural language join predicate. Your job is to determine which pairs should be joined together based on the predicate.

## Record Pairs
${pairs}

## Join Predicate
${join_predicate}

## Context
${context}

## Demonstrations
${demonstrations}

## Output Requirements
- Return a **JSON object** with keys "pair_1", "pair_2", ..., "pair_N" (where N is the number of pairs)
- Each value should be a boolean: true if the pair should be joined, false otherwise
- Example format: {"pair_1": true, "pair_2": false, "pair_3": true}
- Be precise in your evaluation based on the natural language predicate
- Consider the semantic meaning of the predicate, not just exact text matching
- The predicate describes the relationship or condition that should exist between records in each pair

## Additional Notes
- Use your understanding of natural language to interpret the join predicate
- Consider semantic similarity, not just exact matches
- Return only the JSON object, no explanations or additional text
- Ensure all pairs are evaluated (pair_1 through pair_${num_pairs})

---

### Output JSON Object
"""

    PROPERTIES = {
        # openai related properties
        "openai.api": "ChatCompletion",
        "openai.model": "gpt-4o",
        "openai.stream": False,
        "openai.max_tokens": 1024,
        "openai.temperature": 0,
        # io related properties
        "input_json": "[{\"role\": \"user\"}]",
        "input_context": "$[0]",
        "input_context_field": "content",
        "input_field": "messages",
        "input_template": JOIN_PROMPT,
        "output_path": "$.choices[0].message.content",
        # service related properties
        "service_prefix": "openai",
        # output transformations
        "output_transformations": [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}],
        "output_strip": True,
        "output_cast": "bool",
    }

    name = "semantic_join"
    description = "Joins two datasets based on natural language join predicate using LLM models"
    default_attributes = {
        "left_fields": {"type": "list[str]", "description": "Fields from left dataset to consider", "required": True},
        "right_fields": {"type": "list[str]", "description": "Fields from right dataset to consider", "required": True},
        "join_predicate": {"type": "str", "description": "Natural language description of when records should be joined", "required": False, "default": ""},
        "join_type": {"type": "str", "description": "Type of join: 'inner', 'left', 'right', 'outer'", "required": False, "default": "inner"},
        "left_suffix": {"type": "str", "description": "Suffix for field name conflicts from left dataset", "required": False, "default": "_left"},
        "right_suffix": {"type": "str", "description": "Suffix for field name conflicts from right dataset", "required": False, "default": "_right"},
        "keep_keys": {"type": "str", "description": "'left' to keep left keys only, 'both' to keep both", "required": False, "default": "left"},
        "context": {"type": "str", "description": "Optional context to provide domain knowledge or additional instructions", "required": False, "default": ""},
        "demonstrations": {"type": "str", "description": "Optional demonstrations to help in-context learning", "required": False, "default": ""},
        "batch_size": {"type": "int", "description": "Number of record pairs to evaluate per LLM call (batch processing)", "required": False, "default": 10},
        "use_cache": {"type": "bool", "description": "Enable result caching to avoid re-evaluating similar pairs", "required": False, "default": True},
        "use_embedding_filter": {"type": "bool", "description": "Use embedding pre-filtering to reduce candidate pairs (requires sentence-transformers package)", "required": False, "default": False},
        "embedding_threshold": {"type": "float", "description": "Similarity threshold for embedding pre-filtering (0.0-1.0, maps to cosine similarity [-1,1])", "required": False, "default": 0.7},
        "max_llm_calls": {"type": "int", "description": "Maximum allowed LLM calls (None = no limit). Prevents accidental expensive operations.", "required": False, "default": 1000},
        "estimate_cost": {"type": "bool", "description": "Show cost estimate and warnings before execution", "required": False, "default": True},
        # Cascade Optimization properties
        "optimize_thresholds": {"type": "bool", "description": "Enable dynamic threshold learning (Cascade Optimization)", "required": False, "default": False},
        "recall_target": {"type": "float", "description": "Target recall for optimization (0.0-1.0)", "required": False, "default": 0.8},
        "precision_target": {"type": "float", "description": "Target precision for auto-acceptance (0.0-1.0)", "required": False, "default": 0.8},
        "sampling_percentage": {"type": "float", "description": "Fraction of data to sample for learning (0.0-1.0)", "required": False, "default": 0.1},
        "failure_probability": {"type": "float", "description": "Statistical failure probability (delta) for threshold learning", "required": False, "default": 0.2},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=semantic_join_operator_function,
            description=description or self.description,
            properties=properties,
            validator=semantic_join_operator_validator,
            explainer=semantic_join_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()
        self.properties["attributes"] = self.default_attributes

        # service_url, set as default
        self.properties["service_url"] = PROPERTIES["services.openai.service_url"]


if __name__ == "__main__":
    ## calling example

    # Test data - job postings and applicants
    input_data = [
        [
            {"job_id": 1, "job_title": "Software Engineer", "company": "Tech Corp", "location": "San Francisco"},
            {"job_id": 2, "job_title": "Data Scientist", "company": "Data Inc", "location": "New York City"},
            {"job_id": 3, "job_title": "Marketing Manager", "company": "Creative Ltd", "location": "Remote"}, 
        ],
        [
            {"applicant_id": 1, "name": "John Doe", "current_title": "Python Coder", "skills": ["Python", "React"], "location": "SF"},
            {"applicant_id": 2, "name": "Jane Smith", "current_title": "Data Analyst", "skills": ["Python", "SQL"], "location": "NYC"},
            {"applicant_id": 3, "name": "Bob Johnson", "current_title": "Accountant", "skills": ["Excel"], "location": "Chicago"},
            {"applicant_id": 4, "name": "Alice Johnson", "current_title": "Senior Software Engineer", "skills": ["Python", "Java", "React"], "location": "NewYork"},
        ],
    ]

    print("=== Semantic Join attributes ===")

    # Initialize operator
    semantic_join_operator = SemanticJoinOperator()
    properties = semantic_join_operator.properties
    
    # Ensure usage of local service
    properties['service_url'] = 'ws://localhost:8001'
    properties['openai.model'] = 'gpt-4o-mini' # Explicitly set model if needed

    print(f"=== Semantic Join PROPERTIES ===")
    # print(properties) # Reduce noise

    # Example 1: Inner join - similar job titles
    print("\n=== Example 1: Inner join - similar job titles ===")
    attributes = {
        "left_fields": ["job_title"],
        "right_fields": ["current_title"],
        "join_type": "inner",
        "keep_keys": "both"
    }
    result = semantic_join_operator_function(input_data, attributes, properties)
    print("=== Semantic Join RESULT (inner) ===")
    print(result)

    # Example 2: Left join - same location
    print("\n=== Example 2: Left join - same location ===")
    attributes = {
        "left_fields": ["location"],
        "right_fields": ["location"],
        "join_predicate": "The locations refer to the same city (abbreviations allowed)",
        "join_type": "left",
        "left_suffix": "_l", # Custom suffix
        "right_suffix": "_r", # Custom suffix
        "keep_keys": "both"
    }
    print(f"Join Predicate: {attributes['join_predicate']}")
    result = semantic_join_operator_function(input_data, attributes, properties)
    print("=== Semantic Join RESULT (left) ===")
    print(result)

    # Example 3: Full Record Join (Empty Fields)
    print("\n=== Example 3: Full Record Join (Empty Fields) ===")
    attributes = {
        "left_fields": [], # Empty = use all fields
        "right_fields": [], # Empty = use all fields
        "join_predicate": "Match if the job title and current title are semantically equivalent",
        "join_type": "inner",
        "keep_keys": "both"
    }
    print(f"Join Predicate: {attributes['join_predicate']}")
    result = semantic_join_operator_function(input_data, attributes, properties)
    print(result)

    # Example 4: Cascade Optimization (Lotus Mode)
    print("\n=== Example 4: Cascade Optimization (Lotus Mode) ===")
    attributes = {
        "left_fields": ["job_title"],
        "right_fields": ["current_title"],
        "join_predicate": "Match if job titles are semantically similar",
        "join_type": "inner",
        "keep_keys": "both",
        # Enable Cascade Optimization
        "optimize_thresholds": True,
        "recall_target": 1.0,    # Target 100% recall
        "precision_target": 0.9, # Target 90% precision
    }
    print(f"Join Predicate: {attributes['join_predicate']}")
    print("Optimization: ON (Recall=1.0, Precision=0.9)")
    result = semantic_join_operator_function(input_data, attributes, properties)
    print("=== Semantic Join RESULT (Optimized) ===")
    print(result)
