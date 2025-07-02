import streamlit as st
import pandas as pd
import geopandas as gpd
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import requests

# Import RAG system
try:
    from fast_rag import FastMalariaRAG
    RAG_AVAILABLE = True
    print("✅ RAG system imported successfully")
except ImportError:
    RAG_AVAILABLE = False
    print("❌ RAG system not available")

class MalariaDataAnalyzer:
    """Analyze malaria data to provide context for AI recommendations"""
    
    def __init__(self, data: gpd.GeoDataFrame, admin_level: str):
        self.data = data
        self.admin_level = admin_level
        self.entity_col = 'District' if admin_level == 'districts' else 'Sector'
        
    def get_current_situation(self, year: int, month: int) -> Dict:
        """Get comprehensive current situation analysis"""
        current_data = self.data[(self.data['year'] == year) & (self.data['month'] == month)]
        
        if current_data.empty:
            return {"error": "No data available for selected period"}
        
        if self.admin_level == 'districts':
            total_cases = current_data['all cases'].sum()
            severe_cases = current_data['Severe cases/Deaths'].sum()
            avg_incidence = current_data['all cases incidence'].mean()
            population = current_data['Population'].sum()
            
            # Top 3 for faster processing
            top_cases = current_data.nlargest(3, 'all cases')[['District', 'all cases']].to_dict('records')
            top_incidence = current_data.nlargest(3, 'all cases incidence')[['District', 'all cases incidence']].to_dict('records')
            
            return {
                "period": f"{self.get_month_name(month)} {year}",
                "total_cases": int(total_cases),
                "severe_cases": int(severe_cases),
                "avg_incidence": round(avg_incidence, 1),
                "severity_rate": round((severe_cases / total_cases * 100) if total_cases > 0 else 0, 1),
                "top_districts": top_cases,
                "high_incidence": top_incidence,
                "admin_level": "districts"
            }
        else:
            simple_cases = current_data['Simple malaria cases'].sum()
            avg_incidence = current_data['incidence'].mean()
            
            top_cases = current_data.nlargest(3, 'Simple malaria cases')[['Sector', 'District', 'Simple malaria cases']].to_dict('records')
            
            return {
                "period": f"{self.get_month_name(month)} {year}",
                "simple_cases": int(simple_cases),
                "avg_incidence": round(avg_incidence, 1),
                "top_sectors": top_cases,
                "admin_level": "sectors"
            }
    
    def get_month_name(self, month: int) -> str:
        """Convert month number to name"""
        months = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        return months.get(month, str(month))

class OllamaMalariaAI:
    """Clean Ollama-only AI Assistant for malaria analysis"""
    
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.ollama_available = self._test_ollama_connection()
        
        # Initialize RAG system
        if RAG_AVAILABLE:
            try:
                print("🧠 Initializing RAG system...")
                self.rag = FastMalariaRAG()
                self.rag_enabled = True
                print("✅ RAG system ready!")
            except Exception as e:
                print(f"⚠️ RAG system failed: {e}")
                self.rag = None
                self.rag_enabled = False
        else:
            self.rag = None
            self.rag_enabled = False
    
    def _test_ollama_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def _call_ollama(self, prompt: str, max_tokens: int = 300) -> str:
        """Call Ollama with the given prompt"""
        if not self.ollama_available:
            return "🤖 Local AI not available. Please start Ollama: `ollama serve`"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "num_predict": max_tokens,
                        "num_ctx": 2048,
                        "stop": ["Human:", "User:", "\n\n\n"]
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["response"].strip()
            else:
                return f"❌ Error: Ollama returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "⏱️ Response took too long. Try a simpler question."
        except Exception as e:
            return f"❌ Error: {str(e)[:100]}"

    def answer_with_rag(self, question: str, data_context: Dict) -> str:
        """Answer questions using RAG + Ollama"""
        
        # Get RAG context if available
        rag_context = ""
        rag_sources = []
        
        if self.rag_enabled:
            try:
                print(f"🔍 Searching knowledge base for: {question}")
                results = self.rag.search(question, n_results=2)
                
                if results:
                    rag_context = "Medical Knowledge:\n"
                    for result in results:
                        title = result['metadata']['title']
                        source = result['metadata']['source']
                        content = result['content'][:300] + "..." if len(result['content']) > 300 else result['content']
                        
                        rag_context += f"- {title} ({source}): {content}\n"
                        rag_sources.append(f"{title} - {source}")
                    
                    print(f"✅ Found {len(results)} relevant knowledge entries")
                else:
                    rag_context = "No specific medical knowledge found for this query.\n"
                    
            except Exception as e:
                print(f"⚠️ RAG search failed: {e}")
                rag_context = "RAG system temporarily unavailable.\n"
        
        # Create concise data summary
        if data_context.get('admin_level') == 'districts':
            data_summary = f"Current Rwanda data ({data_context['period']}): {data_context['total_cases']} cases, {data_context['severe_cases']} severe cases, {data_context['severity_rate']}% severity rate. Top affected: {', '.join([d['District'] for d in data_context['top_districts']])}"
        else:
            data_summary = f"Current Rwanda data ({data_context['period']}): {data_context['simple_cases']} simple cases, {data_context['avg_incidence']} avg incidence. Top affected: {', '.join([s['Sector'] for s in data_context['top_sectors']])}"
        
        # Build enhanced but concise prompt
        enhanced_prompt = f"""You are a Rwanda malaria expert with access to WHO guidelines and medical knowledge.

{rag_context}

Current surveillance data: {data_summary}

Question: {question}

Provide a focused, actionable answer (max 250 words) with:
1. Key insights from the data
2. Evidence-based recommendations
3. Practical next steps for Rwanda's health system

Be specific and cite medical sources when relevant."""
        
        response = self._call_ollama(enhanced_prompt, max_tokens=350)
        
        # Add sources if RAG was used
        if rag_sources and "Error" not in response and "took too long" not in response:
            response += f"\n\n📚 Sources: {', '.join(rag_sources[:2])}"
            
        return response

    def answer_custom_question(self, question: str, data_context: Dict) -> str:
        """Main method to answer questions"""
        if self.rag_enabled:
            return self.answer_with_rag(question, data_context)
        else:
            return self._answer_without_rag(question, data_context)
    
    def _answer_without_rag(self, question: str, data_context: Dict) -> str:
        """Answer without RAG (fallback)"""
        if data_context.get('admin_level') == 'districts':
            data_summary = f"Rwanda {data_context['period']}: {data_context['total_cases']} cases, {data_context['severe_cases']} severe, {data_context['severity_rate']}% severity rate. Top districts: {', '.join([d['District'] for d in data_context['top_districts']])}"
        else:
            data_summary = f"Rwanda {data_context['period']}: {data_context['simple_cases']} cases, {data_context['avg_incidence']} avg incidence. Top sectors: {', '.join([s['Sector'] for s in data_context['top_sectors']])}"
        
        prompt = f"""You are a Rwanda malaria expert. Current data: {data_summary}

Question: {question}

Give a brief, actionable answer (max 200 words) focused on practical recommendations for Rwanda's health system."""
        
        return self._call_ollama(prompt, max_tokens=250)
    
    def get_status(self) -> Dict:
        """Get AI system status"""
        return {
            "ollama_available": self.ollama_available,
            "model": self.model_name,
            "rag_enabled": self.rag_enabled,
            "base_url": self.base_url
        }

class CleanMalariaBotUI:
    """Clean UI with only Ollama integration"""
    
    def __init__(self, data: gpd.GeoDataFrame, admin_level: str, selected_year: int, selected_month: int):
        self.data_analyzer = MalariaDataAnalyzer(data, admin_level)
        self.ai_assistant = OllamaMalariaAI()
        self.admin_level = admin_level
        self.selected_year = selected_year
        self.selected_month = selected_month
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def render_ai_status(self):
        """Show AI system status"""
        status = self.ai_assistant.get_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if status['ollama_available']:
                st.success(f"🤖 Ollama: ✅ Ready ({status['model']})")
            else:
                st.error("🤖 Ollama: ❌ Not Available")
                st.info("Start Ollama: `ollama serve`")
        
        with col2:
            if status['rag_enabled']:
                st.success("🧠 Knowledge Base: ✅ Active")
            else:
                st.warning("📚 Knowledge Base: ⚠️ Not Available")
    
    def render_chatbot(self):
        """Main chatbot interface"""
        
        # AI Status
        self.render_ai_status()
        
        st.markdown("## 💬 Rwanda Malaria AI Assistant")
        st.markdown("*Powered by local Ollama + medical knowledge base*")
        
        # Quick example questions
        with st.expander("💡 Example Questions"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📍 Priority districts?"):
                    self._ask_preset("Which districts need immediate priority attention based on current data?")
                if st.button("💊 Treatment recommendations?"):
                    self._ask_preset("What are the recommended treatments for our current malaria situation?")
                if st.button("🏥 Supply priorities?"):
                    self._ask_preset("What should be our medication and supply priorities?")
            with col2:
                if st.button("🦟 Prevention strategies?"):
                    self._ask_preset("What prevention interventions work best for Rwanda's current situation?")
                if st.button("📊 Risk assessment?"):
                    self._ask_preset("What is our current outbreak risk and what should we monitor?")
                if st.button("🎯 Resource allocation?"):
                    self._ask_preset("How should we allocate resources based on current case distribution?")
        
        # Question input
        user_question = st.text_input(
            "Your Question:",
            placeholder="Ask about treatments, interventions, or specific recommendations...",
            key="user_question"
        )
        
        # Action buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🧠 Ask AI", type="primary"):
                if user_question.strip():
                    self._process_question(user_question)
                else:
                    st.warning("Please enter a question first.")
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Chat history
        self._render_chat_history()
    
    def _ask_preset(self, question: str):
        """Ask a preset question"""
        self._process_question(question)
    
    def _process_question(self, question: str):
        """Process user question"""
        with st.spinner("🧠 Thinking... (this may take 30-60 seconds)"):
            data_context = self.data_analyzer.get_current_situation(self.selected_year, self.selected_month)
            response = self.ai_assistant.answer_custom_question(question, data_context)
            self._add_chat_entry(question, response)
            st.rerun()
    
    def _add_chat_entry(self, question: str, response: str):
        """Add entry to chat history"""
        chat_entry = {
            "question": question,
            "response": response,
            "timestamp": datetime.now().strftime("%H:%M"),
            "rag_used": self.ai_assistant.rag_enabled
        }
        st.session_state.chat_history.append(chat_entry)
        
        # Keep only last 5 conversations
        if len(st.session_state.chat_history) > 5:
            st.session_state.chat_history = st.session_state.chat_history[-5:]
    
    def _render_chat_history(self):
        """Render chat history"""
        if not st.session_state.chat_history:
            st.info("👋 Ask a question or try the quick buttons above!")
            return
        
        st.markdown("---")
        st.markdown("## 📜 Recent Conversations")
        
        for chat in reversed(st.session_state.chat_history):
            with st.container():
                ai_indicator = "🧠" if chat.get('rag_used', False) else "🤖"
                
                st.markdown(f"**❓ {chat['question']}** {ai_indicator} _{chat['timestamp']}_")
                st.markdown(f"{chat['response']}")
                st.markdown("---")
    
    def render_full_interface(self):
        """Render the complete interface"""
        self.render_chatbot()

# Integration function for main dashboard
def render_ai_assistant_page(data: gpd.GeoDataFrame, admin_level: str, selected_year: int, selected_month: int):
    """Main function to render AI assistant page"""
    st.markdown("# 🤖 Rwanda Malaria AI Assistant")
    st.markdown("Powered by local Ollama for complete privacy and control")
    
    # Performance tip
    if RAG_AVAILABLE:
        st.success("✅ **Enhanced Mode**: Responses include WHO guidelines and medical evidence!")
    else:
        st.warning("⚠️ **Basic Mode**: Install RAG system for enhanced medical knowledge")
    
    st.info("💡 **Privacy First**: All AI processing happens locally on your machine")
    
    # Create and render the bot interface
    bot_ui = CleanMalariaBotUI(data, admin_level, selected_year, selected_month)
    bot_ui.render_full_interface()

# Backward compatibility
MalariaAIAssistant = OllamaMalariaAI
MalariaBotUI = CleanMalariaBotUI

# Main execution for testing
if __name__ == "__main__":
    print("🧪 Testing Clean Ollama Malaria Bot...")
    print("=" * 50)
    
    # Test Ollama connection
    ai = OllamaMalariaAI()
    status = ai.get_status()
    
    print(f"Ollama Status: {'✅ Ready' if status['ollama_available'] else '❌ Not Available'}")
    print(f"Model: {status['model']}")
    print(f"RAG: {'✅ Active' if status['rag_enabled'] else '❌ Not Available'}")
    
    print("\n✅ Clean Ollama Bot ready!")
    print("🎯 No API keys required - fully local AI")
    print("🔒 Complete privacy and data control")