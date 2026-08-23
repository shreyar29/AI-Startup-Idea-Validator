import os
import uuid
import logging
from typing import Dict, Any
from pptx import Presentation
from pptx.util import Inches, Pt

logger = logging.getLogger("export.ppt")

class PPTExporter:
    @staticmethod
    async def generate_pitch_deck(report_data: Dict[str, Any]) -> str:
        """
        Generates a Pitch Deck PPTX from the mesh analysis payload.
        Returns the file path to the generated PPTX.
        """
        logger.info(f"Generating Pitch Deck for idea: {report_data.get('startup_idea', 'Unknown')}")
        
        output_dir = os.path.join(os.getcwd(), "exports", "ppt")
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"pitch_deck_{uuid.uuid4().hex[:8]}.pptx"
        filepath = os.path.join(output_dir, filename)
        
        prs = Presentation()
        
        # Title Slide
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        title.text = "Startup Pitch Deck"
        subtitle.text = report_data.get('startup_idea', 'New Venture')
        
        analysis = report_data.get('analysis_payload', {})
        
        def add_bullet_slide(prs, title_text, bullets):
            slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(slide_layout)
            shapes = slide.shapes
            title_shape = shapes.title
            body_shape = shapes.placeholders[1]
            title_shape.text = title_text
            tf = body_shape.text_frame
            for i, item in enumerate(bullets):
                if i == 0:
                    tf.text = item
                else:
                    p = tf.add_paragraph()
                    p.text = item
                
        # MVP Features
        mvp = analysis.get('mvp_agent', {})
        if mvp:
            features = [f.get('feature_name', '') for f in mvp.get('core_features', [])][:5]
            if features:
                add_bullet_slide(prs, "MVP Core Features", features)
                
        # Market
        market = analysis.get('market_agent', {})
        if market:
            market_points = [
                f"TAM: {market.get('tam_estimate', 'N/A')}",
                f"Growth Rate: {market.get('cagr_estimate', 'N/A')}"
            ]
            add_bullet_slide(prs, "Market Overview", market_points)
            
        prs.save(filepath)
        return filepath
