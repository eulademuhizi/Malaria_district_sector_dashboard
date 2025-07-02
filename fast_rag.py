import chromadb
from sentence_transformers import SentenceTransformer
import json
from typing import List, Dict
import os

class FastMalariaRAG:
    """Fast, local RAG system for malaria knowledge"""
    
    def __init__(self):
        print("🧠 Initializing Fast Malaria RAG System...")
        
        # Use lightweight but effective model (perfect for your i7)
        print("📥 Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded!")
        
        # ChromaDB client (local, persistent)
        print("💾 Connecting to local vector database...")
        self.client = chromadb.PersistentClient(path="./malaria_vector_db")
        self.collection = self.client.get_or_create_collection(
            name="malaria_knowledge",
            metadata={"description": "Rwanda Malaria Surveillance Knowledge Base"}
        )
        print("✅ Vector database connected!")
        
        # Load and embed knowledge base
        self.load_knowledge()
    
    def load_knowledge(self):
        """Load and embed the malaria knowledge base"""
        
        # Check if knowledge file exists
        if not os.path.exists('malaria_knowledge.json'):
            print("❌ malaria_knowledge.json not found!")
            print("   Please run: python quick_crawler.py first")
            return
        
        # Check if already embedded
        if self.collection.count() > 0:
            print(f"✅ Knowledge base already loaded! ({self.collection.count()} documents)")
            return
        
        print("📚 Loading malaria knowledge from JSON...")
        with open('malaria_knowledge.json', 'r', encoding='utf-8') as f:
            knowledge = json.load(f)
        
        if not knowledge:
            print("❌ Knowledge base is empty!")
            return
        
        print(f"📖 Found {len(knowledge)} knowledge entries")
        print("🔄 Creating embeddings...")
        
        # Prepare documents for embedding
        documents = []
        metadatas = []
        ids = []
        
        for i, item in enumerate(knowledge):
            # Combine title and content for richer embeddings
            text = f"Title: {item['title']}\n\nContent: {item['content']}"
            
            documents.append(text)
            metadatas.append({
                'title': item['title'],
                'source': item['source'],
                'category': item['category'],
                'text_length': len(text),
                'entry_id': i
            })
            ids.append(f"malaria_doc_{i}")
        
        # Generate embeddings (this is fast on your machine!)
        print("⚡ Generating embeddings with SentenceTransformer...")
        embeddings = self.embedder.encode(documents, show_progress_bar=True).tolist()
        
        # Store in vector database
        print("💾 Storing in ChromaDB...")
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
        
        print(f"✅ Successfully embedded {len(documents)} documents!")
        print(f"📊 Vector dimensions: {len(embeddings[0])}")
        print(f"💾 Database location: ./malaria_vector_db")
    
    def search(self, query: str, n_results: int = 3, category_filter: str = None) -> List[Dict]:
        """Search the malaria knowledge base"""
        
        if self.collection.count() == 0:
            print("❌ No knowledge base loaded!")
            return []
        
        print(f"🔍 Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embedder.encode([query]).tolist()[0]
        
        # Prepare search parameters
        search_params = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, self.collection.count())
        }
        
        # Add category filter if specified
        if category_filter:
            search_params["where"] = {"category": category_filter}
            print(f"🏷️ Filtering by category: {category_filter}")
        
        # Perform search
        results = self.collection.query(**search_params)
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'relevance_score': 1 - results['distances'][0][i],  # Convert distance to relevance
                'distance': results['distances'][0][i]
            })
        
        print(f"✅ Found {len(formatted_results)} relevant results")
        return formatted_results
    
    def get_context(self, query: str, n_results: int = 3) -> str:
        """Get formatted context for AI assistant"""
        
        results = self.search(query, n_results)
        
        if not results:
            return "No relevant malaria knowledge found."
        
        context = "🦟 RELEVANT MALARIA KNOWLEDGE:\n\n"
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            relevance = result['relevance_score']
            
            context += f"{i}. {metadata['title']}\n"
            context += f"   Source: {metadata['source']} | Category: {metadata['category']}\n"
            context += f"   Relevance: {relevance:.3f}\n\n"
            
            # Add content (truncated if too long)
            content = result['content']
            if len(content) > 800:
                content = content[:800] + "...\n[Content truncated for brevity]"
            
            context += f"{content}\n\n"
            context += "-" * 80 + "\n\n"
        
        return context
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        if self.collection.count() == 0:
            return []
        
        results = self.collection.get()
        categories = set()
        for metadata in results['metadatas']:
            categories.add(metadata['category'])
        
        return sorted(list(categories))
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        if self.collection.count() == 0:
            return {"error": "No knowledge base loaded"}
        
        results = self.collection.get()
        
        categories = {}
        sources = {}
        total_length = 0
        
        for metadata in results['metadatas']:
            cat = metadata['category']
            source = metadata['source']
            length = metadata.get('text_length', 0)
            
            categories[cat] = categories.get(cat, 0) + 1
            sources[source] = sources.get(source, 0) + 1
            total_length += length
        
        return {
            "total_documents": self.collection.count(),
            "categories": categories,
            "sources": sources,
            "total_text_length": total_length,
            "avg_document_length": total_length / self.collection.count(),
            "vector_dimensions": 384  # all-MiniLM-L6-v2 dimensions
        }

def test_rag_system():
    """Test the RAG system with sample queries"""
    print("🧪 TESTING MALARIA RAG SYSTEM")
    print("=" * 50)
    
    # Initialize RAG system
    rag = FastMalariaRAG()
    
    # Test queries
    test_queries = [
        "treatment for severe malaria",
        "bed net distribution strategy",
        "supply chain management",
        "Rwanda malaria interventions",
        "artemisinin combination therapy"
    ]
    
    print(f"\n📊 Knowledge Base Stats:")
    stats = rag.get_stats()
    if "error" not in stats:
        print(f"  Documents: {stats['total_documents']}")
        print(f"  Categories: {list(stats['categories'].keys())}")
        print(f"  Vector dimensions: {stats['vector_dimensions']}")
    
    print(f"\n🔍 Testing search queries:")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: '{query}' ---")
        
        results = rag.search(query, n_results=2)
        
        for j, result in enumerate(results, 1):
            title = result['metadata']['title']
            source = result['metadata']['source']
            relevance = result['relevance_score']
            
            print(f"  {j}. {title}")
            print(f"     Source: {source} | Relevance: {relevance:.3f}")
    
    print(f"\n🎯 Context Generation Test:")
    context = rag.get_context("malaria treatment guidelines", n_results=2)
    print(f"Context length: {len(context)} characters")
    print(f"Preview: {context[:200]}...")
    
    print(f"\n✅ RAG system test complete!")
    return rag

def main():
    """Main function to initialize and test RAG system"""
    try:
        rag = test_rag_system()
        
        print(f"\n🎉 FAST MALARIA RAG SYSTEM READY!")
        print(f"🔧 Usage:")
        print(f"  from fast_rag import FastMalariaRAG")
        print(f"  rag = FastMalariaRAG()")
        print(f"  results = rag.search('your query here')")
        print(f"  context = rag.get_context('your query here')")
        
        return rag
        
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        print(f"💡 Make sure you've installed: pip install chromadb")
        return None

if __name__ == "__main__":
    main()