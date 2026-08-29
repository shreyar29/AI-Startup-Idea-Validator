from reportlab.lib import colors
from reportlab.lib.styles import StyleSheet1, ParagraphStyle

# Branding Colors
BRAND_PRIMARY = colors.HexColor("#0f172a")    # Slate 900
BRAND_SECONDARY = colors.HexColor("#3b82f6")  # Blue 500
BRAND_ACCENT = colors.HexColor("#6366f1")     # Indigo 500
BRAND_SUCCESS = colors.HexColor("#10b981")    # Emerald 500
BRAND_WARNING = colors.HexColor("#f59e0b")    # Amber 500
BRAND_ERROR = colors.HexColor("#ef4444")      # Red 500
BRAND_GRAY = colors.HexColor("#64748b")       # Slate 500
BRAND_LIGHT_GRAY = colors.HexColor("#f8fafc") # Slate 50
BRAND_WHITE = colors.white

def get_theme_styles() -> StyleSheet1:
    styles = StyleSheet1()
    
    # Cover Page
    styles.add(ParagraphStyle(name='CoverTitle', fontName='Helvetica-Bold', fontSize=36, leading=42, textColor=BRAND_PRIMARY, alignment=1))
    styles.add(ParagraphStyle(name='CoverSubtitle', fontName='Helvetica', fontSize=18, leading=24, textColor=BRAND_GRAY, alignment=1))
    styles.add(ParagraphStyle(name='CoverMeta', fontName='Helvetica-Oblique', fontSize=12, leading=16, textColor=BRAND_GRAY, alignment=1))
    
    # Headers
    styles.add(ParagraphStyle(name='SectionHeader', fontName='Helvetica-Bold', fontSize=24, leading=30, textColor=BRAND_PRIMARY, spaceBefore=24, spaceAfter=16))
    styles.add(ParagraphStyle(name='SubHeader', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=BRAND_PRIMARY, spaceBefore=16, spaceAfter=8))
    
    # Text
    styles.add(ParagraphStyle(name='BodyText', fontName='Helvetica', fontSize=10, leading=16, textColor=colors.black, spaceAfter=12))
    styles.add(ParagraphStyle(name='BodyTextBold', fontName='Helvetica-Bold', fontSize=10, leading=16, textColor=BRAND_PRIMARY, spaceAfter=12))
    styles.add(ParagraphStyle(name='DataUnavailable', fontName='Helvetica-Oblique', fontSize=10, textColor=BRAND_GRAY, spaceAfter=12))
    styles.add(ParagraphStyle(name='ListItemText', fontName='Helvetica', fontSize=10, leading=16, textColor=colors.black, spaceAfter=6, leftIndent=15, bulletIndent=5))
    
    # KPI / Dashboard Cards
    styles.add(ParagraphStyle(name='KPIValue', fontName='Helvetica-Bold', fontSize=20, textColor=BRAND_SECONDARY, alignment=1))
    styles.add(ParagraphStyle(name='KPILabel', fontName='Helvetica-Bold', fontSize=8, textColor=BRAND_GRAY, alignment=1, spaceBefore=6))
    
    # TOC
    styles.add(ParagraphStyle(name='TOCHeading', fontName='Helvetica-Bold', fontSize=24, leading=30, textColor=BRAND_PRIMARY, spaceBefore=24, spaceAfter=24))
    styles.add(ParagraphStyle(name='TOCItem', fontName='Helvetica', fontSize=12, leading=20, textColor=BRAND_PRIMARY, spaceAfter=8))

    return styles
