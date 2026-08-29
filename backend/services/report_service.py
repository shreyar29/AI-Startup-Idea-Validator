import logging
from .reporting.generator import ReportGenerator

logger = logging.getLogger(__name__)

class ReportService:
    """
    Facade for the investor-grade Startup Intelligence Reporting System.
    Delegates PDF generation to the modular reporting package.
    """

    def __init__(self, output_dir: str = "reports"):
        self.generator = ReportGenerator(output_dir)

    def generate_pdf(self, report_id: str, context: dict) -> str:
        """Generates the PDF and returns the local filename."""
        try:
            return self.generator.generate(report_id, context)
        except Exception as e:
            logger.error(f"ReportService failed to generate PDF: {e}")
            raise e
