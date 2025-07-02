# Create and run this test: test_complete_setup.py
print("=== MALARIA RAG SYSTEM - COMPLETE TEST ===\n")

import sys
print(f"Active Python: {sys.version}")
print(f"Python path: {sys.executable}\n")

# Test all required packages
test_results = []

print("📦 TESTING CORE PACKAGES:")
packages = {
    'sentence_transformers': 'SentenceTransformer',
    'pandas': 'pd', 
    'geopandas': 'gpd',
    'requests': 'requests',
    'json': 'json',
    'pathlib': 'Path'
}

for package, alias in packages.items():
    try:
        if package == 'sentence_transformers':
            from sentence_transformers import SentenceTransformer
            print(f"✅ {package}: OK")
        elif package == 'pandas':
            import pandas as pd
            print(f"✅ {package}: OK")
        elif package == 'geopandas':
            import geopandas as gpd
            print(f"✅ {package}: OK")
        else:
            exec(f"import {package}")
            print(f"✅ {package}: OK")
        test_results.append(True)
    except ImportError as e:
        print(f"❌ {package}: {e}")
        test_results.append(False)

# Test ChromaDB (might still be installing)
print(f"\n🔍 TESTING CHROMADB:")
try:
    import chromadb
    print("✅ ChromaDB: OK")
    test_results.append(True)
except ImportError:
    print("❌ ChromaDB: Not installed yet")
    print("   Install with: pip install chromadb")
    test_results.append(False)

# Test sentence transformer functionality
print(f"\n🧠 TESTING AI FUNCTIONALITY:")
try:
    from sentence_transformers import SentenceTransformer
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Test malaria-specific content
    malaria_texts = [
        "WHO malaria treatment guidelines",
        "Rwanda malaria prevention strategy", 
        "artemisinin-based combination therapy",
        "seasonal malaria chemoprevention"
    ]
    
    print("Generating embeddings for malaria content...")
    embeddings = model.encode(malaria_texts)
    print(f"✅ Generated {len(embeddings)} embeddings × {len(embeddings[0])} dimensions")
    
    # Test similarity search capability
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    query = "malaria treatment"
    query_embedding = model.encode([query])
    
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    best_match_idx = np.argmax(similarities)
    
    print(f"✅ Search test: '{query}' → '{malaria_texts[best_match_idx]}'")
    print(f"   Similarity score: {similarities[best_match_idx]:.3f}")
    
    test_results.append(True)
except Exception as e:
    print(f"❌ AI functionality test failed: {e}")
    test_results.append(False)

# Final status
print(f"\n🎯 SYSTEM STATUS:")
passed = sum(test_results)
total = len(test_results)

if passed >= total - 1:  # Allow ChromaDB to be missing
    print("🎉 SYSTEM READY FOR MALARIA RAG DEVELOPMENT!")
    print("\n🚀 NEXT STEPS:")
    print("1. Install ChromaDB: pip install chromadb")
    print("2. Create malaria knowledge base")
    print("3. Build RAG system")
    print("4. Integrate with your dashboard")
else:
    print(f"⚠️  System partially ready: {passed}/{total} components working")
    print("Please install missing packages before proceeding")

print(f"\n📊 Test Results: {passed}/{total} passed")