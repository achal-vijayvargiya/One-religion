"""
Quick script to estimate token usage for batch processing.
Helps you find the right GROUPING_BATCH_SIZE and GROUPING_PREVIEW_LENGTH settings.
"""

def estimate_tokens(batch_size: int, preview_length: int) -> dict:
    """
    Estimate token usage for a batch.
    
    Args:
        batch_size: Number of chunks per batch
        preview_length: Characters per chunk preview
        
    Returns:
        Dictionary with estimates
    """
    # Rough estimates (actual usage may vary)
    chars_per_token = 3.5  # Conservative estimate for English text
    
    # Calculate token estimates
    chunk_data_chars = batch_size * preview_length
    chunk_data_tokens = chunk_data_chars / chars_per_token
    
    # JSON formatting overhead (roughly 30-50 chars per chunk)
    json_overhead_tokens = (batch_size * 40) / chars_per_token
    
    # Prompt template (system message + instructions)
    prompt_template_tokens = 500
    
    # Safety margin
    safety_margin = 1000
    
    # Total estimate
    total_tokens = (
        chunk_data_tokens +
        json_overhead_tokens +
        prompt_template_tokens +
        safety_margin
    )
    
    return {
        "batch_size": batch_size,
        "preview_length": preview_length,
        "chunk_data_tokens": int(chunk_data_tokens),
        "json_overhead_tokens": int(json_overhead_tokens),
        "prompt_template_tokens": prompt_template_tokens,
        "safety_margin": safety_margin,
        "total_estimated_tokens": int(total_tokens),
        "fits_in_131k_context": total_tokens < 131000,
        "fits_in_200k_context": total_tokens < 200000,
    }


def print_estimate(batch_size: int, preview_length: int):
    """Print token usage estimate."""
    result = estimate_tokens(batch_size, preview_length)
    
    print(f"\n{'='*60}")
    print(f"Token Usage Estimate")
    print(f"{'='*60}")
    print(f"Batch Size:           {result['batch_size']} chunks")
    print(f"Preview Length:       {result['preview_length']} characters")
    print(f"{'─'*60}")
    print(f"Chunk Data:           ~{result['chunk_data_tokens']:,} tokens")
    print(f"JSON Overhead:        ~{result['json_overhead_tokens']:,} tokens")
    print(f"Prompt Template:      ~{result['prompt_template_tokens']:,} tokens")
    print(f"Safety Margin:        ~{result['safety_margin']:,} tokens")
    print(f"{'─'*60}")
    print(f"TOTAL ESTIMATED:      ~{result['total_estimated_tokens']:,} tokens")
    print(f"{'─'*60}")
    
    if result['fits_in_131k_context']:
        print(f"✅ Should fit in 131K context (Claude Sonnet)")
    else:
        print(f"❌ Too large for 131K context!")
        print(f"   Exceeds by ~{result['total_estimated_tokens'] - 131000:,} tokens")
    
    if result['fits_in_200k_context']:
        print(f"✅ Should fit in 200K context (Claude 3.5 Sonnet)")
    else:
        print(f"❌ Too large for 200K context!")
    
    print(f"{'='*60}\n")


def find_optimal_settings(target_tokens: int = 130000):
    """Find optimal batch size and preview length for target token count."""
    print(f"\n🔍 Finding optimal settings for {target_tokens:,} token limit...\n")
    
    best_configs = []
    
    # Try different combinations
    for batch_size in [15, 20, 25, 30, 35, 40, 45, 50]:
        for preview_length in [60, 80, 100, 120, 140, 150]:
            result = estimate_tokens(batch_size, preview_length)
            if result['total_estimated_tokens'] < target_tokens:
                best_configs.append(result)
    
    # Sort by total tokens (descending) to find the largest safe config
    best_configs.sort(key=lambda x: x['total_estimated_tokens'], reverse=True)
    
    if best_configs:
        print("Top 5 recommended configurations:\n")
        for i, config in enumerate(best_configs[:5], 1):
            print(f"{i}. GROUPING_BATCH_SIZE={config['batch_size']}")
            print(f"   GROUPING_PREVIEW_LENGTH={config['preview_length']}")
            print(f"   Estimated: ~{config['total_estimated_tokens']:,} tokens")
            print(f"   Margin: {target_tokens - config['total_estimated_tokens']:,} tokens remaining")
            print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAG Pipeline - Token Usage Estimator")
    print("="*60)
    
    # Current defaults
    print("\n📊 CURRENT DEFAULTS:")
    print_estimate(30, 120)
    
    # Conservative settings
    print("\n🛡️  CONSERVATIVE SETTINGS:")
    print_estimate(20, 100)
    
    # Ultra-conservative
    print("\n🔒 ULTRA-CONSERVATIVE SETTINGS:")
    print_estimate(15, 80)
    
    # Previous defaults (for comparison)
    print("\n⚠️  PREVIOUS DEFAULTS (may fail):")
    print_estimate(50, 150)
    
    # Find optimal
    print("\n" + "="*60)
    find_optimal_settings(target_tokens=130000)
    
    print("\n💡 TIP: Run this script to check different configurations")
    print("   before updating your .env file!\n")

