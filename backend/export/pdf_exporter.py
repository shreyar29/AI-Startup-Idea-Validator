import os
import uuid
import logging
from typing import Dict, Any
# import pdfkit or reportlab would go here in real implementation

logger = logging.getLogger("export.pdf")

class PDFExporter:
    @staticmethod
    async def generate_investor_report(report_data: Dict[str, Any]) -> str:
        """
        Generates a professional PDF Investor Report from the mesh analysis payload.
        Returns the file path to the generated PDF.
        """
        logger.info(f"Generating PDF report for idea: {report_data.get('startup_idea', 'Unknown')}")
        
        from services.reporting.generator import ReportGenerator
        from services.export_aggregator import ExportAggregator
        
        # Aggregate to FinalPresentationPayload
        raw_analysis = report_data.get('analysis_payload', {})
        payload = ExportAggregator.aggregate(raw_analysis)
        
        # Map the clean FinalPresentationPayload to ReportContext structure
        mapped_context = {
            "idea": {"description": report_data.get('startup_idea', 'Unknown')},
            "final_evaluation": {
                "startup_score": {
                    "overall_score": payload.get("overall_score", 0),
                    "verdict": payload.get("verdict", "Further Analysis Needed"),
                    "founder_recommendation": payload.get("executive_summary", {}).get("founder_recommendation", "")
                },
                "market": payload.get("market", {}),
                "customer": payload.get("customer", {}),
                "competitor": payload.get("competitor", {}),
                "swot": payload.get("strategy", {}),
                "risk": {
                    "top_risks": payload.get("risk_and_action", {}).get("top_risks", []),
                    "recommendations": payload.get("risk_and_action", {}).get("recommendations", [])
                },
                "mvp": {"core_features": payload.get("execution", {}).get("core_features", [])},
                "gtm": payload.get("execution", {}),
                "executive_summary": payload.get("executive_summary", {})
            }
        }
        
        generator = ReportGenerator(output_dir="reports")
        filename = generator.generate(report_data.get('startup_idea', 'Unknown')[:30], mapped_context)
        
        filepath = os.path.join(generator.base_path, filename)
        return filepath
