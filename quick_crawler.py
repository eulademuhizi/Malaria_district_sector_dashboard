import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

class QuickMalariaKnowledge:
    def __init__(self):
        self.sources = {
            "WHO Malaria": "https://www.who.int/news-room/fact-sheets/detail/malaria",
            "CDC Guidelines": "https://www.cdc.gov/malaria/diagnosis_treatment/treatment.html",
            "Rwanda Guidelines": "https://www.moh.gov.rw/"
        }
        self.knowledge_base = []
    
    def quick_scrape(self):
        """Get essential malaria knowledge FAST"""
        # Pre-defined essential knowledge (for speed)
        essential_knowledge = [
            {
                "title": "WHO Malaria Treatment Guidelines",
                "content": """
                First-line treatment for uncomplicated malaria:
                - Artemisinin-based combination therapies (ACTs)
                - Artemether-lumefantrine
                - Artesunate-amodiaquine
                
                Severe malaria treatment:
                - IV Artesunate (first choice)
                - Quinine if artesunate unavailable
                
                Prevention strategies:
                - Long-lasting insecticidal nets (LLINs)
                - Indoor residual spraying (IRS)
                - Seasonal malaria chemoprevention (SMC)
                """,
                "source": "WHO",
                "category": "treatment"
            },
            {
                "title": "Rwanda Malaria Interventions",
                "content": """
                Key interventions for Rwanda:
                - Community case management
                - Mass distribution of bed nets
                - Indoor residual spraying in high-risk areas
                - Seasonal malaria chemoprevention in children
                - Intermittent preventive treatment in pregnancy
                
                High-risk areas:
                - Eastern Province (especially during rainy season)
                - Southern Province lowlands
                - Areas near wetlands and rice paddies
                """,
                "source": "Rwanda MOH",
                "category": "interventions"
            },
            {
                "title": "Supply Chain Management",
                "content": """
                Essential medicines to stock:
                - Artemether-lumefantrine (AL) tablets
                - Artesunate injection
                - RDT test kits
                - Severe malaria treatment drugs
                
                Stock management:
                - Maintain 3-month buffer stock
                - Monitor expiry dates quarterly
                - Prioritize high-burden districts
                - Emergency procurement protocols
                """,
                "source": "Supply Chain Guidelines",
                "category": "supply_chain"
            }
        ]
        
        self.knowledge_base.extend(essential_knowledge)
        return len(essential_knowledge)
    
    def save_knowledge(self):
        """Save to JSON for quick loading"""
        with open('malaria_knowledge.json', 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
        print(f"Saved {len(self.knowledge_base)} knowledge entries")

# Run it
if __name__ == "__main__":
    collector = QuickMalariaKnowledge()
    count = collector.quick_scrape()
    collector.save_knowledge()
    print(f"✅ Collected {count} knowledge entries in seconds!")