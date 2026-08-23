import os
import uuid
import logging
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from .theme import get_theme_styles, BRAND_PRIMARY, BRAND_GRAY
from .models import ReportContext
from . import sections

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Orchestrates the assembly of the investor-grade PDF report."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", self.output_dir))
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def _create_header_footer(self, canvas, doc):
        canvas.saveState()
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(BRAND_PRIMARY)
        canvas.drawString(0.75 * inch, 10.5 * inch, "VentureLens AI")
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(BRAND_GRAY)
        canvas.drawRightString(7.75 * inch, 10.5 * inch, "Confidential Startup Intelligence Report")
        
        # Footer
        canvas.line(0.75 * inch, 0.75 * inch, 7.75 * inch, 0.75 * inch)
        canvas.setFont('Helvetica', 9)
        canvas.drawString(0.75 * inch, 0.5 * inch, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
        canvas.drawRightString(7.75 * inch, 0.5 * inch, f"Page {doc.page}")
        canvas.restoreState()

    def generate(self, report_id: str, raw_context: dict) -> str:
        """Parses data and generates the PDF."""
        # Convert dictionary to strongly-typed Pydantic model
        context = ReportContext(**raw_context)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"venturelens_report_{timestamp}_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(self.base_path, filename)

        doc = SimpleDocTemplate(
            filepath, 
            pagesize=letter, 
            title="VentureLens Intelligence Report", 
            author="VentureLens AI",
            leftMargin=0.75*inch, rightMargin=0.75*inch,
            topMargin=1.25*inch, bottomMargin=1.25*inch
        )
        
        styles = get_theme_styles()
        story = []

        # Orchestrate Section Generation
        sections.build_cover_page(story, styles, report_id, context)
        sections.build_toc(story, styles)
        
        sections.build_executive_dashboard(story, styles, context)
        sections.build_startup_scorecard(story, styles, context)
        sections.build_market_intelligence(story, styles, context)
        sections.build_competitor_matrix(story, styles, context)
        sections.build_swot_matrix(story, styles, context)
        sections.build_risk_assessment(story, styles, context)
        sections.build_action_plan(story, styles, context)
        sections.build_appendix(story, styles, raw_context)

        try:
            doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
            logger.info(f"PDF successfully generated: {filename}")
            return filename
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise e
