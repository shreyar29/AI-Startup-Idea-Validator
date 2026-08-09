import urllib.request
import json
import os

def render_diagram(diagram_str, output_path, diagram_type):
    url = f"https://kroki.io/{diagram_type}/png"
    print(f"Generating {diagram_type} diagram via POST...")
    data = json.dumps({"diagram_source": diagram_str}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully saved {output_path}")
    except Exception as e:
        print(f"Failed to generate {output_path}: {e}")

def render_mermaid(diagram_str, output_path):
    render_diagram(diagram_str, output_path, "mermaid")

def render_plantuml(diagram_str, output_path):
    render_diagram(diagram_str, output_path, "plantuml")

architecture_diagram = """
graph TD
    User([User]) -->|Inputs Idea| ReactFrontend[React Frontend]
    User -->|Login| ReactFrontend
    ReactFrontend -->|GET search| BackendAPI[FastAPI Backend]
    BackendAPI -->|SSE progress| ReactFrontend
    ReactFrontend -->|GET history| BackendAPI
    
    BackendAPI --> Orchestrator[Mesh Orchestrator]
    
    Orchestrator --> QueryStrategist[Query Strategist]
    QueryStrategist -->|LLM| BaseLLMProvider[BaseLLMProvider]
    BaseLLMProvider -.-> Gemini["Google Gemini: Primary"]
    BaseLLMProvider -.-> OpenRouter["OpenRouter: Fallback"]
    
    Orchestrator --> WebSearchAgent[Web Search Agent]
    WebSearchAgent --> TavilySearch[Tavily Search Service]
    WebSearchAgent --> ResultProcessor[Result Processor]
    
    Orchestrator --> MarketAgent[Market Agent]
    Orchestrator --> CustomerAgent[Customer Agent]
    Orchestrator --> CompetitorAgent[Competitor Agent]
    
    MarketAgent --> ComparisonAgent[Comparison Agent]
    CustomerAgent --> ComparisonAgent
    CompetitorAgent --> ComparisonAgent
    
    ComparisonAgent -->|LLM| BaseLLMProvider
    
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
    class BaseLLMProvider {
        <<interface>>
        +generate_content()
        +health_check()
    }
    class GeminiClient {
    }
    class OpenRouterClient {
    }
    
    BaseLLMProvider <|-- GeminiClient
    BaseLLMProvider <|-- OpenRouterClient
    
    StartupValidatorOrchestrator --> WebSearchAgent
    StartupValidatorOrchestrator --> MarketOpportunityAgent
    StartupValidatorOrchestrator --> CustomerAgent
    StartupValidatorOrchestrator --> CompetitorAgent
    StartupValidatorOrchestrator --> ComparisonAgent
    StartupValidatorOrchestrator --> GuardrailManager
    StartupValidatorOrchestrator --> BaseLLMProvider
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
  usecase "Authenticate (Login/Signup)" as UC8
  usecase "View Validation History" as UC9
}
user --> UC1
user --> UC2
user --> UC3
user --> UC4
user --> UC5
user --> UC6
user --> UC7
user --> UC8
user --> UC9
@enduml
'''

os.makedirs(r"c:\Users\Admin\Desktop\AI-Startup-Idea-Validator-main\docs", exist_ok=True)
render_mermaid(architecture_diagram, r"c:\Users\Admin\Desktop\AI-Startup-Idea-Validator-main\docs\milestone2_architecture_diagram.png")
render_mermaid(uml_class_diagram, r"c:\Users\Admin\Desktop\AI-Startup-Idea-Validator-main\docs\milestone2_uml_class_diagram.png")
render_plantuml(usecase_puml, r"c:\Users\Admin\Desktop\AI-Startup-Idea-Validator-main\docs\milestone2_use_case_diagram.png")
print("All diagrams generated successfully!")
