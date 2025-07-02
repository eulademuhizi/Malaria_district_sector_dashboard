# debug_system.py
print("🔍 Debugging Malaria System...")
print("=" * 50)

# Test 1: Check knowledge file
import os
import json

print("\n📚 KNOWLEDGE BASE CHECK:")
if os.path.exists('malaria_knowledge.json'):
    print("✅ Knowledge file exists")
    try:
        with open('malaria_knowledge.json', 'r') as f:
            data = json.load(f)
            print(f"✅ Knowledge entries: {len(data)}")
            if data:
                print(f"✅ First entry: {data[0]['title']}")
                print(f"✅ Categories: {set(entry['category'] for entry in data)}")
    except Exception as e:
        print(f"❌ Knowledge file error: {e}")
else:
    print("❌ Knowledge file missing")

# Test 2: Check vector database
print("\n🧠 VECTOR DATABASE CHECK:")
if os.path.exists('malaria_vector_db'):
    print("✅ Vector database directory exists")
    db_files = os.listdir('malaria_vector_db')
    print(f"✅ DB files: {db_files}")
else:
    print("❌ Vector database missing")

# Test 3: Check RAG imports
print("\n🔍 RAG SYSTEM CHECK:")
try:
    print("Testing imports...")
    
    # Test ChromaDB
    import chromadb
    print("✅ ChromaDB imported")
    
    # Test SentenceTransformers
    from sentence_transformers import SentenceTransformer
    print("✅ SentenceTransformers imported")
    
    # Test RAG module
    from fast_rag import FastMalariaRAG
    print("✅ FastMalariaRAG imported")
    
    # Test RAG initialization
    print("Initializing RAG system...")
    rag = FastMalariaRAG()
    print("✅ RAG system initialized")
    
    # Test RAG stats
    stats = rag.get_stats()
    print(f"✅ RAG stats: {stats}")
    
    # Test search
    print("Testing search...")
    results = rag.search("malaria treatment", n_results=1)
    if results:
        print(f"✅ Search works: Found {len(results)} results")
        print(f"   First result: {results[0]['metadata']['title']}")
    else:
        print("⚠️ Search returns no results")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Try: pip install chromadb sentence-transformers")
except Exception as e:
    print(f"❌ RAG error: {e}")

# Test 4: Check Ollama
print("\n🤖 OLLAMA CHECK:")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=3)
    if response.status_code == 200:
        models = response.json()
        print("✅ Ollama is running")
        print(f"✅ Available models: {[m['name'] for m in models.get('models', [])]}")
    else:
        print(f"❌ Ollama responding with status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Ollama not running")
    print("   Start with: ollama serve")
except Exception as e:
    print(f"❌ Ollama error: {e}")

# Test 5: Check main bot
print("\n🤖 BOT INTEGRATION CHECK:")
try:
    from malaria_bot import render_ai_assistant_page, get_rag_status
    print("✅ Bot module imported")
    
    status = get_rag_status()
    print(f"✅ RAG status: {status}")
    
except ImportError as e:
    print(f"❌ Bot import error: {e}")
except Exception as e:
    print(f"❌ Bot error: {e}")

print("\n" + "=" * 50)
print("🎯 SUMMARY & NEXT STEPS:")

print("\n📝 To fix issues:")
print("1. If RAG errors: pip install chromadb sentence-transformers")
print("2. If Ollama errors: ollama serve (in separate terminal)")
print("3. If knowledge missing: python quick_crawler.py")
print("4. If vector DB missing: python fast_rag.py")

print("\n🚀 Once all ✅, run: streamlit run main_dashboard.py")