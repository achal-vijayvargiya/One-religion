"""
Quick start script to verify installation and configuration.
"""

import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor} (requires 3.9+)")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("\n📦 Checking dependencies...")
    
    required = [
        "langchain",
        "langchain_community",
        "pypdf",
        "faiss",
        "sentence_transformers",
        "openai",
        "streamlit",
        "dotenv",
        "pydantic",
    ]
    
    missing = []
    
    for package in required:
        try:
            if package == "dotenv":
                __import__("dotenv")
            elif package == "faiss":
                __import__("faiss")
            else:
                __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n   Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\n🔐 Checking environment configuration...")
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("   ✗ .env file not found")
        print("   Create one from env.example:")
        print("   cp env.example .env")
        return False
    
    print("   ✓ .env file exists")
    
    # Check for API key
    with open(env_file, "r") as f:
        content = f.read()
        if "OPENROUTER_API_KEY" in content:
            if "your_openrouter_api_key_here" in content:
                print("   ⚠ OPENROUTER_API_KEY not set (using placeholder)")
                print("   Update it with your actual API key from openrouter.ai")
                return False
            else:
                print("   ✓ OPENROUTER_API_KEY configured")
                return True
    
    print("   ✗ OPENROUTER_API_KEY not found in .env")
    return False


def check_pdf_file():
    """Check if the Bhagavad Gita PDF exists."""
    print("\n📄 Checking PDF file...")
    
    pdf_path = Path("resources/Bhagavad-gita-As-It-Is.pdf")
    
    if pdf_path.exists():
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"   ✓ PDF found ({size_mb:.2f} MB)")
        return True
    else:
        print("   ⚠ PDF not found at resources/Bhagavad-gita-As-It-Is.pdf")
        print("   You can use any PDF file for testing")
        return True  # Not critical


def check_src_modules():
    """Check if source modules are importable."""
    print("\n📚 Checking source modules...")
    
    modules = [
        "src.config",
        "src.pdf_extractor",
        "src.semantic_chunker",
        "src.agentic_grouper",
        "src.vector_store",
        "src.retrieval_engine",
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"   ✓ {module}")
        except Exception as e:
            print(f"   ✗ {module}: {str(e)}")
            return False
    
    return True


def print_next_steps():
    """Print instructions for next steps."""
    print("\n" + "="*60)
    print("✅ Setup verification complete!")
    print("="*60)
    print("\n🚀 Next Steps:\n")
    print("1. Launch the Streamlit app:")
    print("   streamlit run app.py\n")
    print("2. Or use the CLI to process a PDF:")
    print('   python pipeline.py "resources/Bhagavad-gita-As-It-Is.pdf"\n')
    print("3. Or use the Python API:")
    print("   python -c \"from pipeline import RAGPipeline; p = RAGPipeline()\"\n")
    print("📖 See README.md for detailed documentation")
    print("="*60 + "\n")


def main():
    """Run all checks."""
    print("="*60)
    print("RAG Pipeline - Quick Start Verification")
    print("="*60 + "\n")
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_env_file(),
        check_pdf_file(),
        check_src_modules(),
    ]
    
    if all(checks):
        print_next_steps()
        return 0
    else:
        print("\n" + "="*60)
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

