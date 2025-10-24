"""
Simple script to find YOUR optimal batch size based on YOUR .env settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load your .env
load_dotenv()

# Get your model
model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-sonnet")
preview_length = int(os.getenv("GROUPING_PREVIEW_LENGTH", "120"))

# Model limits
MODEL_LIMITS = {
    "anthropic/claude-3-opus": 200000,
    "anthropic/claude-3.5-sonnet": 200000,
    "anthropic/claude-3-sonnet": 200000,
    "anthropic/claude-3-haiku": 200000,
    "openai/gpt-4-turbo-preview": 128000,
    "openai/gpt-4": 8192,
    "openai/gpt-3.5-turbo": 16385,
    "google/gemini-pro-1.5": 1000000,
    "google/gemini-pro": 32000,
    "google/gemma-2-27b-it": 8192,
    "meta-llama/llama-3-70b-instruct": 8192,
}

def calculate():
    context_limit = MODEL_LIMITS.get(model, 8192)
    
    # Conservative calculation
    usable = int(context_limit * 0.85)  # 85% safety margin
    overhead = 2500  # Fixed overhead
    available = usable - overhead
    
    tokens_per_chunk = int(preview_length / 3.5) + 14  # text + JSON overhead
    
    max_batch = int(available / tokens_per_chunk)
    recommended = int(max_batch * 0.9)  # 90% of max
    conservative = int(max_batch * 0.7)  # 70% of max
    
    return {
        "model": model,
        "context": context_limit,
        "preview": preview_length,
        "max": max_batch,
        "recommended": recommended,
        "conservative": conservative,
    }

if __name__ == "__main__":
    result = calculate()
    
    print("\n" + "="*60)
    print("YOUR OPTIMAL BATCH SIZE")
    print("="*60)
    print(f"\nBased on your .env settings:")
    print(f"  Model: {result['model']}")
    print(f"  Context: {result['context']:,} tokens")
    print(f"  Preview Length: {result['preview']} chars")
    print(f"\nRecommended batch sizes:")
    print(f"  [FAST]   {result['max']} chunks (maximum safe)")
    print(f"  [GOOD]   {result['recommended']} chunks  <-- USE THIS")
    print(f"  [SAFE]   {result['conservative']} chunks (ultra-conservative)")
    print(f"\nTo update your .env:")
    print(f"  GROUPING_BATCH_SIZE={result['recommended']}")
    print(f"  GROUPING_PREVIEW_LENGTH={result['preview']}")
    print("\n" + "="*60 + "\n")

