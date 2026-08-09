import base64
import zlib
import urllib.request
import os

def render_mermaid(diagram_str, output_path):
    compressed = zlib.compress(diagram_str.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    url = f"https://kroki.io/mermaid/png/{encoded}"
    print(f"Downloading from {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
        out_file.write(response.read())

def render_plantuml(diagram_str, output_path):
    compressed = zlib.compress(diagram_str.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    url = f"https://kroki.io/plantuml/png/{encoded}"
    print(f"Downloading from {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
        out_file.write(response.read())

architecture_diagram = """
graph TD
    User([User]) -->|Inputs Idea| ReactFrontend[React Frontend]
    ReactFrontend -->|POST /api/search| BackendAPI[FastAPI Backend]
    ReactFrontend <-->|SSE /api/progress| BackendAPI
    
    BackendAPI --> Orchestrator[Mesh Orchestrator]
    
    Orchestrator --> QueryStrategist[Query Strategist]
    QueryStrategist -->|LLM| GoogleGemini[Google Gemini API]
    
    Orchestrator --> WebSearchAgent[Web Search Agent]
    WebSearchAgent --> TavilySearch[Tavily Search Service]
    WebSearchAgent --> ResultProcessor[Result Processor]
    
    Orchestrator --> MarketAgent[Market Agent]
    Orchestrator --> CustomerAgent[Customer Agent]
    Orchestrator --> CompetitorAgent[Competitor Agent]
    
    MarketAgent --> ComparisonAgent[Comparison Agent]
    CustomerAgent --> ComparisonAgent
    CompetitorAgent --> ComparisonAgent
    
    ComparisonAgent -->|LLM| GoogleGemini
    
    Orchestrator --> GuardrailManager[Guardrail Manager]
    GuardrailManager --> FinalReport[Executive Report]
    FinalReport --> ReactFrontend
"""

uml_class_diagram = """
classDiagram
    class StartupValidatorOrchestrator {
        +validate_idea(startup_idea, request_id)
        -_format_error_response()
    }
    class QueryStrategist {
        +run(idea)
    }
    class WebSearchAgent {
        +run(idea)
        -_execute_searches()
        -_process_results()
    }
    class MarketOpportunityAgent {
        +get_analysis()
        -_perform_analysis()
    }
    class CustomerAgent {
        +get_analysis()
        -_perform_analysis()
    }
    class CompetitorAgent {
        +get_analysis()
        -_perform_analysis()
    }
    class ComparisonAgent {
        +get_analysis()
        -_perform_analysis()
    }
    class GuardrailManager {
        +validate_agent_output()
        +verify_facts_and_hallucinations()
        +verify_final_response()
    }
    
    StartupValidatorOrchestrator --> WebSearchAgent
    StartupValidatorOrchestrator --> MarketOpportunityAgent
    StartupValidatorOrchestrator --> CustomerAgent
    StartupValidatorOrchestrator --> CompetitorAgent
    StartupValidatorOrchestrator --> ComparisonAgent
    StartupValidatorOrchestrator --> GuardrailManager
    WebSearchAgent --> QueryStrategist
"""

usecase_puml = '''
@startuml
left to right direction
actor "Founder / Investor" as user
package "VentureLens AI Validation Platform" {
  usecase "Submit Startup Idea" as UC1
  usecase "View Live Execution Progress" as UC2
  usecase "View Market Analysis" as UC3
  usecase "View Customer Insights" as UC4
  usecase "View Competitor Analysis" as UC5
  usecase "View Executive Report" as UC6
  usecase "Toggle Theme (Light/Dark)" as UC7
}
user --> UC1
user --> UC2
user --> UC3
user --> UC4
user --> UC5
user --> UC6
user --> UC7
@enduml
'''

os.makedirs(r"c:\Users\Admin\Desktop\AI-Startup-Idea-Validator-main\docs", exist_ok=True)
render_mermaid(architecture_diagram, r"c:\Users\Admin\Desktop\AI-Startup-Idea-Validator-main\docs\architecture_diagram.png")
render_mermaid(uml_class_diagram, r"c:\Users\Admin\Desktop\AI-Startup-Idea-Validator-main\docs\uml_class_diagram.png")
render_plantuml(usecase_puml, r"c:\Users\Admin\Desktop\AI-Startup-Idea-Validator-main\docs\use_case_diagram.png")
print("All diagrams generated successfully!")
