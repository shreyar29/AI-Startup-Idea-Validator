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
        
        payload = report_data.get('analysis_payload', {})
        
        # Map the frontend analysis payload to the ReportContext structure expected by ReportGenerator
        mapped_context = {
            "idea": {"description": report_data.get('startup_idea', 'Unknown')},
            "final_evaluation": {
                "startup_score": payload.get('startup_score_agent', {}),
                "market": payload.get('market_analysis', {}),
                "competitor": {
                    "competitors": payload.get('competitor_analysis', {}).get('competitors', []),
                    "gap_analysis": payload.get('competitor_analysis', {}).get('gap_analysis', 'No gaps identified.')
                },
                "swot": {
                    "strengths": [s if isinstance(s, str) else s.get('title', '') for s in payload.get('swot_analysis', {}).get('strengths', [])],
                    "weaknesses": [s if isinstance(s, str) else s.get('title', '') for s in payload.get('swot_analysis', {}).get('weaknesses', [])],
                    "opportunities": [s if isinstance(s, str) else s.get('title', '') for s in payload.get('swot_analysis', {}).get('opportunities', [])],
                    "threats": [s if isinstance(s, str) else s.get('title', '') for s in payload.get('swot_analysis', {}).get('threats', [])]
                },
                "risk": payload.get('risk_analysis', {}),
                "mvp": {"core_features": [f.get('feature', '') if isinstance(f, dict) else f for f in payload.get('gtm_analysis', {}).get('mvp_features', [])]},
                "gtm": payload.get('gtm_analysis', {}),
                "executive_summary": payload.get('startup_score_agent', {}).get('executive_summary', '')
            }
        }
        
        generator = ReportGenerator(output_dir="reports")
        filename = generator.generate(report_data.get('startup_idea', 'Unknown')[:30], mapped_context)
        
        filepath = os.path.join(generator.base_path, filename)
        return filepath
