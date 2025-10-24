"""
Calculate optimal batch size for agentic grouping based on your model and document.
This helps you maximize efficiency while avoiding context limit errors.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


# Model context limits (in tokens)
MODEL_LIMITS = {
    # Anthropic Claude
    "anthropic/claude-3-opus": 200000,
    "anthropic/claude-3.5-sonnet": 200000,
    "anthropic/claude-3-sonnet": 200000,
    "anthropic/claude-3-haiku": 200000,
    
    # OpenAI
    "openai/gpt-4-turbo-preview": 128000,
    "openai/gpt-4": 8192,
    "openai/gpt-3.5-turbo": 16385,
    "openai/gpt-3.5-turbo-16k": 16385,
    
    # Google
    "google/gemini-pro-1.5": 1000000,
    "google/gemini-pro": 32000,
    "google/gemma-2-27b-it": 8192,
    "google/gemma-2-9b-it": 8192,
    
    # Meta
    "meta-llama/llama-3-70b-instruct": 8192,
    "meta-llama/llama-3-8b-instruct": 8192,
    
    # Mistral
    "mistralai/mistral-large": 32000,
    "mistralai/mistral-medium": 32000,
    "mistralai/mixtral-8x7b-instruct": 32000,
}


def estimate_tokens_per_chunk(preview_length: int, avg_chars_per_token: float = 3.5) -> int:
    """
    Estimate tokens per chunk based on preview length.
    
    Args:
        preview_length: Characters in chunk preview
        avg_chars_per_token: Average characters per token (conservative: 3.5 for English)
    
    Returns:
        Estimated tokens per chunk
    """
    # Text content
    text_tokens = preview_length / avg_chars_per_token
    
    # JSON structure overhead per chunk
    # {"id": 123, "text": "...", "page": 45}
    json_overhead = 50 / avg_chars_per_token  # ~14 tokens
    
    return int(text_tokens + json_overhead)


def calculate_optimal_batch_size(
    model_name: str,
    preview_length: int = 120,
    safety_margin: float = 0.85,  # Use only 85% of context to be safe
) -> Dict:
    """
    Calculate optimal batch size for a given model and settings.
    
    Args:
        model_name: OpenRouter model name
        preview_length: Preview length setting
        safety_margin: Safety factor (0.85 = use 85% of context)
    
    Returns:
        Dictionary with recommendations
    """
    # Get model's context limit
    context_limit = MODEL_LIMITS.get(model_name, 8192)  # Default to conservative 8K
    
    # Apply safety margin
    usable_tokens = int(context_limit * safety_margin)
    
    # Subtract fixed overhead
    prompt_template_tokens = 500  # System prompt + instructions
    response_buffer = 2000  # Space for model's JSON response
    
    available_for_chunks = usable_tokens - prompt_template_tokens - response_buffer
    
    # Calculate tokens per chunk
    tokens_per_chunk = estimate_tokens_per_chunk(preview_length)
    
    # Calculate maximum batch size
    max_batch_size = int(available_for_chunks / tokens_per_chunk)
    
    # Recommended batch size (slightly conservative)
    recommended_batch_size = max(1, int(max_batch_size * 0.9))  # Use 90% of max
    
    # Conservative batch size (very safe)
    conservative_batch_size = max(1, int(max_batch_size * 0.7))  # Use 70% of max
    
    return {
        "model": model_name,
        "context_limit": context_limit,
        "usable_tokens": usable_tokens,
        "preview_length": preview_length,
        "tokens_per_chunk": tokens_per_chunk,
        "max_batch_size": max_batch_size,
        "recommended_batch_size": recommended_batch_size,
        "conservative_batch_size": conservative_batch_size,
        "efficiency_note": f"Using {recommended_batch_size} chunks = ~{recommended_batch_size * tokens_per_chunk:,} tokens (~{(recommended_batch_size * tokens_per_chunk / context_limit * 100):.1f}% of context)"
    }


def print_recommendations(model_name: str, preview_length: int = 120):
    """Print batch size recommendations for a model."""
    result = calculate_optimal_batch_size(model_name, preview_length)
    
    print(f"\n{'='*70}")
    print(f"BATCH SIZE CALCULATOR - {model_name}")
    print(f"{'='*70}")
    print(f"\nModel Configuration:")
    print(f"  Context Limit:        {result['context_limit']:,} tokens")
    print(f"  Preview Length:       {result['preview_length']} characters")
    print(f"  Tokens per Chunk:     ~{result['tokens_per_chunk']} tokens")
    print(f"\nCalculated Batch Sizes:")
    print(f"  Maximum:              {result['max_batch_size']} chunks (theoretical max)")
    print(f"  Recommended:          {result['recommended_batch_size']} chunks [*] (USE THIS)")
    print(f"  Conservative:         {result['conservative_batch_size']} chunks (ultra-safe)")
    print(f"\nEfficiency:")
    print(f"  {result['efficiency_note']}")
    print(f"{'='*70}\n")
    
    return result


def compare_models(preview_length: int = 120):
    """Compare batch sizes across different models."""
    print(f"\n{'='*70}")
    print(f"MODEL COMPARISON - Preview Length: {preview_length} chars")
    print(f"{'='*70}\n")
    
    print(f"{'Model':<35} {'Context':<10} {'Max':<8} {'Recommended':<12} {'Conservative'}")
    print(f"{'-'*70}")
    
    models_to_compare = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-sonnet",
        "openai/gpt-4-turbo-preview",
        "openai/gpt-3.5-turbo",
        "google/gemini-pro-1.5",
        "google/gemini-pro",
        "meta-llama/llama-3-70b-instruct",
        "mistralai/mistral-large",
    ]
    
    for model in models_to_compare:
        result = calculate_optimal_batch_size(model, preview_length)
        context_str = f"{result['context_limit']:,}"
        print(f"{model:<35} {context_str:<10} {result['max_batch_size']:<8} {result['recommended_batch_size']:<12} {result['conservative_batch_size']}")
    
    print(f"{'-'*70}\n")


def analyze_your_document(chunk_file_path: str = None):
    """
    Analyze your actual document to provide personalized recommendations.
    """
    print(f"\n{'='*70}")
    print(f"DOCUMENT-SPECIFIC ANALYSIS")
    print(f"{'='*70}\n")
    
    # TODO: This would analyze actual chunks from your processing
    # For now, provide guidelines
    
    print("To get document-specific recommendations:")
    print("\n1. Look at your chunking output after running:")
    print("   logs/rag_pipeline_*.log")
    print("\n2. Find lines like:")
    print("   'Chunking complete: 450 total chunks created'")
    print("   'Average chunk size: 623 characters'")
    print("\n3. Use that average chunk size here:")
    print("   python calculate_optimal_batch.py --preview-length <avg_size>")
    print()


def why_20_is_default():
    """Explain why we chose 20 as the default."""
    print(f"\n{'='*70}")
    print(f"WHY IS THE DEFAULT BATCH SIZE 20?")
    print(f"{'='*70}\n")
    
    print("The default of 20 chunks per batch is chosen because:\n")
    
    print("1. Works with SMALLEST common models (8K context)")
    print("   - Llama 3, Gemma: ~8,000 tokens")
    print("   - With preview_length=120: 20 chunks = ~4,000 tokens")
    print("   - Safely fits in 8K with room for overhead\n")
    
    print("2. Universal compatibility")
    print("   - If it works with 8K models, works with ALL models")
    print("   - Users can increase for larger-context models\n")
    
    print("3. Better error recovery")
    print("   - Smaller batches = more granular processing")
    print("   - If one batch fails, you lose less progress")
    print("   - Easier to identify problematic content\n")
    
    print("4. Real-world testing")
    print("   - Tested with Bhagavad Gita (200 pages)")
    print("   - Works reliably across different models")
    print("   - Good balance of speed vs. safety\n")
    
    print("BUT: You can (and should!) increase it for better models:\n")
    
    results = []
    for model, recommended in [
        ("anthropic/claude-3.5-sonnet", "60-80"),
        ("openai/gpt-4-turbo-preview", "50-70"),
        ("google/gemini-pro-1.5", "200+"),
    ]:
        results.append(f"  {model:<35} -> {recommended} chunks")
    
    for r in results:
        print(r)
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("OPTIMAL BATCH SIZE CALCULATOR")
    print("="*70)
    
    # Example for Claude Sonnet (most common)
    print("\n1. YOUR CURRENT SETTINGS (likely):")
    print_recommendations("anthropic/claude-3-sonnet", preview_length=120)
    
    # Show why 20 is default
    why_20_is_default()
    
    # Compare all models
    compare_models(preview_length=120)
    
    # Analyze document
    analyze_your_document()
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS:")
    print("="*70)
    print("\nBased on your model, update .env with:")
    print()
    
    # Get user's model from args or default
    model = "anthropic/claude-3-sonnet"
    if len(sys.argv) > 1:
        model = sys.argv[1]
    
    result = calculate_optimal_batch_size(model, 120)
    
    print(f"# For {model}:")
    print(f"GROUPING_BATCH_SIZE={result['recommended_batch_size']}")
    print(f"GROUPING_PREVIEW_LENGTH=120")
    print()
    print("Or for ultra-safe (if you still get errors):")
    print(f"GROUPING_BATCH_SIZE={result['conservative_batch_size']}")
    print(f"GROUPING_PREVIEW_LENGTH=100")
    print()
    
    print("="*70 + "\n")

