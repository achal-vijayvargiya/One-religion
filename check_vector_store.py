"""
Quick script to check vector store status and quality.
"""

import pickle
from pathlib import Path

def check_vector_store():
    """Check the current vector store status."""
    vector_store_path = Path("vector_store")
    data_file = vector_store_path / "documents.pkl"
    
    if not data_file.exists():
        print("[X] No vector store found!")
        print("    Location checked: vector_store/documents.pkl")
        print("\n[!] You need to ingest a document first.")
        return
    
    print("[OK] Vector store found!\n")
    print("="*60)
    
    # Load and analyze
    with open(data_file, "rb") as f:
        data = pickle.load(f)
    
    documents = data.get("documents", [])
    metadata = data.get("metadata", [])
    
    print(f"VECTOR STORE STATISTICS")
    print("="*60)
    print(f"Total documents:     {len(documents)}")
    print(f"Embedding model:     {data.get('embedding_model', 'unknown')}")
    print()
    
    # Analyze document types
    regular_groups = 0
    fallback_groups = 0
    chunks = 0
    
    for doc in documents:
        doc_type = doc.metadata.get("type", "chunk")
        group_id = doc.metadata.get("group_id", "")
        
        if doc_type == "knowledge_group":
            if "fallback" in group_id:
                fallback_groups += 1
            else:
                regular_groups += 1
        else:
            chunks += 1
    
    print(f"DOCUMENT BREAKDOWN")
    print("="*60)
    print(f"[+] Proper groups:     {regular_groups} (from successful batches)")
    print(f"[~] Fallback groups:   {fallback_groups} (from failed batches)")
    print(f"[-] Raw chunks:        {chunks} (no grouping used)")
    print()
    
    # Quality assessment
    total_grouped = regular_groups + fallback_groups
    if total_grouped > 0:
        quality_ratio = (regular_groups / total_grouped) * 100
        print(f"QUALITY SCORE")
        print("="*60)
        print(f"Grouping quality:    {quality_ratio:.1f}%")
        
        if quality_ratio >= 90:
            print("[OK] Excellent! Most batches succeeded.")
            print("     No need to recreate.")
        elif quality_ratio >= 70:
            print("[!] Good, but some batches failed.")
            print("    Consider recreating for better quality.")
        elif quality_ratio >= 50:
            print("[!] Mixed quality - many batches failed.")
            print("    Recommend recreating with adjusted settings.")
        else:
            print("[X] Poor quality - most batches failed.")
            print("    Definitely recreate with fixed settings!")
        print()
    
    # Recommendations
    print(f"RECOMMENDATIONS")
    print("="*60)
    
    if fallback_groups > 0:
        print(f"\n[!] You have {fallback_groups} fallback groups (from failed batches)")
        print("\nOptions:")
        print("\n1. Keep current (works but not optimal):")
        print("   - Already functional")
        print("   - No need to do anything")
        print("   - Some results may be less relevant")
        
        print("\n2. Recreate for better quality:")
        print("   - Clear and re-ingest the PDF")
        print("   - Use adjusted settings to avoid failures")
        print("   - Get optimal knowledge groupings")
        
        print("\nTo recreate with better settings:")
        print("   1. Update .env:")
        print("      GROUPING_BATCH_SIZE=20")
        print("      GROUPING_PREVIEW_LENGTH=100")
        print("      OPENROUTER_MODEL=anthropic/claude-3-sonnet")
        print("   2. Clear in Streamlit UI: 'Clear Knowledge Base'")
        print("   3. Re-ingest your PDF")
        
    else:
        if regular_groups > 0:
            print("[OK] Perfect! All grouping batches succeeded.")
            print("     No need to recreate.")
        else:
            print("[i] No grouping was used (raw chunks only).")
            print("    This is fine if you disabled grouping intentionally.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("VECTOR STORE DIAGNOSTIC TOOL")
    print("="*60 + "\n")
    
    check_vector_store()
    
    print()

