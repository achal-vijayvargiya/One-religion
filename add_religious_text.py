#!/usr/bin/env python3
"""
Script to help users add religious texts to the One Religion RAG system.
This script guides users through the process of adding PDF files and ingesting them.
"""

import os
import sys
from pathlib import Path
import subprocess

def print_banner():
    """Print a welcome banner."""
    print("=" * 60)
    print("🕉️  One Religion - Multi-Religious Text RAG System  ☪️")
    print("=" * 60)
    print()

def get_available_books():
    """Get list of available religious texts."""
    return {
        "1": {"id": "bhagavad_gita", "name": "Bhagavad Gita", "path": "resources/bhagavad_gita/"},
        "2": {"id": "bible", "name": "Bible", "path": "resources/bible/"},
        "3": {"id": "quran", "name": "Quran", "path": "resources/quran/"},
        "4": {"id": "custom", "name": "Custom Religious Text", "path": None}
    }

def display_books():
    """Display available religious texts."""
    books = get_available_books()
    print("📚 Available Religious Texts:")
    print()
    for key, book in books.items():
        if key != "4":
            status = "✅ Ready" if os.path.exists(book["path"]) else "📥 Not added"
            print(f"  {key}. {book['name']} - {status}")
        else:
            print(f"  {key}. {book['name']}")
    print()

def get_user_choice():
    """Get user's choice of religious text."""
    while True:
        try:
            choice = input("Select a religious text (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            else:
                print("❌ Please enter a number between 1-4")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)

def get_pdf_path():
    """Get PDF file path from user."""
    while True:
        pdf_path = input("Enter the path to your PDF file: ").strip()
        if os.path.exists(pdf_path) and pdf_path.lower().endswith('.pdf'):
            return pdf_path
        else:
            print("❌ Please enter a valid PDF file path")

def create_directory(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory: {path}")

def copy_pdf(source, destination):
    """Copy PDF file to the appropriate directory."""
    import shutil
    try:
        shutil.copy2(source, destination)
        print(f"✅ Copied PDF to: {destination}")
        return True
    except Exception as e:
        print(f"❌ Error copying PDF: {e}")
        return False

def ingest_pdf(book_id, pdf_path):
    """Ingest PDF into vector store."""
    print(f"\n🔄 Ingesting {book_id} into vector store...")
    try:
        cmd = ["python", "pipeline.py", pdf_path, "--book-id", book_id]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully ingested {book_id}!")
            print("📖 The book is now available in the web interface.")
        else:
            print(f"❌ Error ingesting PDF:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running ingestion: {e}")
        return False
    
    return True

def main():
    """Main function to guide user through adding religious texts."""
    print_banner()
    
    print("This script will help you add religious texts to the RAG system.")
    print("You can add PDF files and ingest them into vector stores.")
    print()
    
    display_books()
    
    choice = get_user_choice()
    books = get_available_books()
    selected_book = books[choice]
    
    if choice == "4":
        # Custom religious text
        book_id = input("Enter a unique ID for your religious text (e.g., 'tao_te_ching'): ").strip()
        book_name = input("Enter the display name (e.g., 'Tao Te Ching'): ").strip()
        book_path = f"resources/{book_id}/"
        
        print(f"\n📁 Creating directory for {book_name}...")
        create_directory(book_path)
    else:
        book_id = selected_book["id"]
        book_name = selected_book["name"]
        book_path = selected_book["path"]
        
        print(f"\n📖 Adding {book_name}...")
        create_directory(book_path)
    
    # Get PDF file
    print(f"\n📄 Please provide the PDF file for {book_name}:")
    pdf_path = get_pdf_path()
    
    # Copy PDF to appropriate directory
    pdf_filename = os.path.basename(pdf_path)
    destination = os.path.join(book_path, pdf_filename)
    
    print(f"\n📋 Copying PDF file...")
    if copy_pdf(pdf_path, destination):
        # Ask if user wants to ingest immediately
        ingest_now = input(f"\n🔄 Do you want to ingest {book_name} into the vector store now? (y/n): ").strip().lower()
        
        if ingest_now in ['y', 'yes']:
            if ingest_pdf(book_id, destination):
                print(f"\n🎉 {book_name} has been successfully added and is ready to use!")
                print("🌐 Run 'streamlit run app.py' to start the web interface.")
            else:
                print(f"\n⚠️  {book_name} was added but ingestion failed.")
                print("You can try ingesting manually later with:")
                print(f"python pipeline.py {destination} --book-id {book_id}")
        else:
            print(f"\n📝 {book_name} has been added to the project.")
            print("To ingest it later, run:")
            print(f"python pipeline.py {destination} --book-id {book_id}")
    else:
        print(f"\n❌ Failed to add {book_name}. Please try again.")

if __name__ == "__main__":
    main()
