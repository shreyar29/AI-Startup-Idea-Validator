import html
from datetime import datetime
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.spider import SpiderChart

from .theme import BRAND_PRIMARY, BRAND_SECONDARY, BRAND_SUCCESS, BRAND_WARNING, BRAND_ERROR, BRAND_GRAY, BRAND_LIGHT_GRAY
from .models import ReportContext

def safe_str(val, default="Data Unavailable"):
    if val is None or val == "" or val == []: return default
    if isinstance(val, list): return html.escape(", ".join([str(v) for v in val]))
    return html.escape(str(val))

def build_cover_page(story, styles, report_id, context: ReportContext):
    idea_desc = context.idea.get("description", "Startup Validation Report")
    story.append(Spacer(1, 2.5 * inch))
    story.append(Paragraph("VentureLens", ParagraphStyle('VL', fontName='Helvetica-Bold', fontSize=16, textColor=BRAND_SECONDARY, alignment=1)))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("DUE DILIGENCE & STARTUP INTELLIGENCE", styles['CoverSubtitle']))
    story.append(Spacer(1, 0.5 * inch))
    
    display_idea = (idea_desc[:120] + '...') if len(idea_desc) > 120 else idea_desc
    story.append(Paragraph(safe_str(display_idea), styles['CoverTitle']))
    
    story.append(Spacer(1, 2 * inch))
    story.append(HRFlowable(width="50%", thickness=1, color=BRAND_GRAY, spaceBefore=10, spaceAfter=10, hAlign='CENTER'))
    story.append(Paragraph(f"Report ID: {report_id}", styles['CoverMeta']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['CoverMeta']))
    story.append(PageBreak())

def build_toc(story, styles):
    story.append(Paragraph("Table of Contents", styles['TOCHeading']))
    sections = [
        "1. Executive Summary & Dashboard",
        "2. Startup Viability Scorecard",
        "3. Market Intelligence",
        "4. Competitive Landscape",
        "5. SWOT Analysis",
        "6. Risk Assessment",
        "7. Founder Action Plan",
        "8. Appendix & References"
    ]
    for s in sections:
        story.append(Paragraph(s, styles['TOCItem']))
    story.append(PageBreak())

def build_executive_dashboard(story, styles, context: ReportContext):
    eval_data = context.final_evaluation
    story.append(Paragraph("1. Executive Summary & Dashboard", styles['SectionHeader']))
    
    score_data = eval_data.startup_score
    overall_score = score_data.overall_score
    verdict = score_data.verdict
    
    score_color = BRAND_SUCCESS if overall_score >= 75 else (BRAND_WARNING if overall_score >= 40 else BRAND_ERROR)
    
    # Core KPIs
    data = [
        [
            Paragraph(str(overall_score), ParagraphStyle('Sc', parent=styles['KPIValue'], textColor=score_color, fontSize=28)),
            Paragraph(safe_str(verdict), ParagraphStyle('Vd', parent=styles['KPIValue'], fontSize=16, textColor=BRAND_PRIMARY)),
            Paragraph(str(score_data.confidence_level), styles['KPIValue'])
        ],
        [
            Paragraph("OVERALL SCORE (0-100)", styles['KPILabel']),
            Paragraph("VERDICT", styles['KPILabel']),
            Paragraph("AI CONFIDENCE", styles['KPILabel'])
        ]
    ]
    t = Table(data, colWidths=[2.2 * inch, 2.6 * inch, 2.2 * inch])
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), BRAND_LIGHT_GRAY),
        ('BOX', (0,0), (-1,-1), 1, BRAND_GRAY),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * inch))
    
    # Extended KPI Dashboard
    ext_data = [
        [
            Paragraph(str(score_data.market_score), styles['KPIValue']),
            Paragraph(str(score_data.competition_score), styles['KPIValue']),
            Paragraph(str(score_data.execution_score), styles['KPIValue'])
        ],
        [
            Paragraph("MARKET ATTRACTIVENESS", styles['KPILabel']),
            Paragraph("COMPETITION INTENSITY", styles['KPILabel']),
            Paragraph("EXECUTION COMPLEXITY", styles['KPILabel'])
        ]
    ]
    t2 = Table(ext_data, colWidths=[2.3 * inch, 2.4 * inch, 2.3 * inch])
    t2.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, BRAND_GRAY),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.4 * inch))
    
    # Executive Recommendation
    story.append(Paragraph("Executive Recommendation", styles['SubHeader']))
    exec_summary = eval_data.executive_summary
    if isinstance(exec_summary, dict):
        rec_text = exec_summary.get("founder_recommendation") or exec_summary.get("market_fit") or "Data Unavailable"
    else:
        rec_text = str(exec_summary) if exec_summary else "Data Unavailable"
        
    story.append(Paragraph(safe_str(rec_text), styles['BodyText']))
    
    # Top Opportunities and Risks Summary
    story.append(Spacer(1, 0.2 * inch))
    opps = eval_data.swot.opportunities[:2]
    risks = eval_data.risk.top_risks[:2]
    
    if opps or risks:
        summ_data = [
            [Paragraph("<b>Top Opportunities</b>", styles['BodyText']), Paragraph("<b>Top Risks</b>", styles['BodyText'])],
            [
                Paragraph("<br/>".join([f"• {safe_str(o)}" for o in opps]) if opps else "None identified", styles['BodyText']),
                Paragraph("<br/>".join([f"• {safe_str(r)}" for r in risks]) if risks else "None identified", styles['BodyText'])
            ]
        ]
        t3 = Table(summ_data, colWidths=[3.5 * inch, 3.5 * inch])
        t3.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#eff6ff")), # Blue
            ('BACKGROUND', (1,0), (1,-1), colors.HexColor("#fef2f2")), # Red
            ('BOX', (0,0), (-1,-1), 1, BRAND_GRAY),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t3)
    
    story.append(PageBreak())

def build_startup_scorecard(story, styles, context: ReportContext):
    score_data = context.final_evaluation.startup_score
    if not score_data or score_data.market_score == 0:
        return
        
    story.append(Paragraph("2. Startup Viability Scorecard", styles['SectionHeader']))
    
    d = Drawing(400, 250)
    chart = SpiderChart()
    chart.x = 100
    chart.y = 20
    chart.width = 200
    chart.height = 200
    
    chart.data = [[
        score_data.market_score,
        score_data.competition_score,
        score_data.execution_score,
        score_data.risk_score,
        score_data.gtm_score
    ]]
    
    chart.labels = ['Market', 'Competition', 'Execution', 'Risk (Safety)', 'GTM']
    chart.strands[0].fillColor = colors.Color(59/255, 130/255, 246/255, alpha=0.3)
    chart.strands[0].strokeColor = BRAND_SECONDARY
    chart.strands[0].strokeWidth = 2
    
    d.add(chart)
    story.append(d)
    story.append(Spacer(1, 0.2 * inch))
    
    if score_data.score_explanation:
        story.append(Paragraph("Score Breakdown", styles['SubHeader']))
        for exp in score_data.score_explanation:
            story.append(Paragraph(f"• {safe_str(exp)}", styles['BodyText']))
            
    story.append(PageBreak())

def build_market_intelligence(story, styles, context: ReportContext):
    market = context.final_evaluation.market
    if not market or (not market.market_size and not market.market_trends):
        return
        
    story.append(Paragraph("3. Market Intelligence", styles['SectionHeader']))
    
    data = [
        [
            Paragraph(safe_str(market.market_size), styles['KPIValue']),
            Paragraph(safe_str(market.growth_rate), styles['KPIValue']),
            Paragraph(safe_str(market.market_maturity), styles['KPIValue'])
        ],
        [
            Paragraph("MARKET SIZE", styles['KPILabel']),
            Paragraph("GROWTH RATE (CAGR)", styles['KPILabel']),
            Paragraph("MATURITY", styles['KPILabel'])
        ]
    ]
    
    t = Table(data, colWidths=[2.3 * inch, 2.4 * inch, 2.3 * inch])
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,0), (-1,-1), BRAND_LIGHT_GRAY),
        ('BOX', (0,0), (-1,-1), 1, BRAND_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * inch))
    
    if market.market_trends:
        story.append(Paragraph("Macro Trends & Drivers", styles['SubHeader']))
        for t_item in market.market_trends:
            story.append(Paragraph(f"• {safe_str(t_item)}", styles['BodyText']))
            
    story.append(PageBreak())

def build_competitor_matrix(story, styles, context: ReportContext):
    comp_analysis = context.final_evaluation.competitor
    competitors = comp_analysis.competitors
    
    if not competitors:
        return
        
    story.append(Paragraph("4. Competitive Landscape", styles['SectionHeader']))
    story.append(Paragraph("Market Positioning", styles['SubHeader']))
    
    table_data = [["Competitor", "Strengths", "Weaknesses"]]
    for c in competitors[:5]:
        table_data.append([
            Paragraph(safe_str(c.name), styles['BodyTextBold']),
            Paragraph(safe_str(c.strengths), styles['BodyText']),
            Paragraph(safe_str(c.weaknesses), styles['BodyText'])
        ])
        
    t = Table(table_data, colWidths=[1.5 * inch, 2.75 * inch, 2.75 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, BRAND_GRAY),
        ('BOX', (0,0), (-1,-1), 1, BRAND_PRIMARY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BRAND_LIGHT_GRAY])
    ]))
    story.append(t)
    
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Market Whitespace (Gap Analysis)", styles['SubHeader']))
    story.append(Paragraph(safe_str(comp_analysis.gap_analysis), styles['BodyText']))
    
    story.append(PageBreak())

def build_swot_matrix(story, styles, context: ReportContext):
    swot = context.final_evaluation.swot
    if not swot.strengths and not swot.weaknesses:
        return
        
    story.append(Paragraph("5. SWOT Analysis", styles['SectionHeader']))
    
    def _get_list_str(items):
        if not items: return "N/A"
        return "<br/>• ".join([html.escape(str(i)) for i in items[:4]])
        
    data = [
        [
            Paragraph(f"<b>STRENGTHS</b><br/><br/>• {_get_list_str(swot.strengths)}", styles['BodyText']),
            Paragraph(f"<b>WEAKNESSES</b><br/><br/>• {_get_list_str(swot.weaknesses)}", styles['BodyText'])
        ],
        [
            Paragraph(f"<b>OPPORTUNITIES</b><br/><br/>• {_get_list_str(swot.opportunities)}", styles['BodyText']),
            Paragraph(f"<b>THREATS</b><br/><br/>• {_get_list_str(swot.threats)}", styles['BodyText'])
        ]
    ]
    
    t = Table(data, colWidths=[3.5 * inch, 3.5 * inch], rowHeights=[3 * inch, 3 * inch])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 2, BRAND_PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 1, BRAND_GRAY),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f0fdf4")), 
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#fef2f2")), 
        ('BACKGROUND', (0,1), (0,1), colors.HexColor("#eff6ff")), 
        ('BACKGROUND', (1,1), (1,1), colors.HexColor("#fffbeb")), 
        ('PADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t)
    story.append(PageBreak())

def build_risk_assessment(story, styles, context: ReportContext):
    risk = context.final_evaluation.risk
    if not risk.top_risks:
        return
        
    story.append(Paragraph("6. Risk Assessment", styles['SectionHeader']))
    
    story.append(Paragraph(f"Overall Risk Level: <b>{safe_str(risk.risk_level)}</b>", styles['SubHeader']))
    story.append(Spacer(1, 0.2 * inch))
    
    table_data = [["Critical Risk Factor", "Proposed Mitigation"]]
    risks = risk.top_risks[:5]
    mitigations = risk.mitigations[:5]
    
    # Pad mitigations to match risks
    while len(mitigations) < len(risks):
        mitigations.append("Requires mitigation strategy.")
        
    for r, m in zip(risks, mitigations):
        table_data.append([
            Paragraph(safe_str(r), styles['BodyText']),
            Paragraph(safe_str(m), styles['BodyText'])
        ])
        
    t = Table(table_data, colWidths=[3.5 * inch, 3.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, BRAND_GRAY),
        ('BOX', (0,0), (-1,-1), 1, BRAND_PRIMARY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BRAND_LIGHT_GRAY])
    ]))
    story.append(t)
    story.append(PageBreak())

def build_action_plan(story, styles, context: ReportContext):
    mvp = context.final_evaluation.mvp
    gtm = context.final_evaluation.gtm
    
    if not mvp.core_features and not gtm.launch_channels:
        return
        
    story.append(Paragraph("7. Founder Action Plan", styles['SectionHeader']))
    
    if mvp.core_features:
        story.append(Paragraph("MVP Roadmap", styles['SubHeader']))
        for f in mvp.core_features:
            story.append(Paragraph(f"• [PRIORITY] {safe_str(f)}", styles['BodyText']))
        story.append(Spacer(1, 0.2 * inch))
        
    channels = gtm.acquisition_channels or gtm.launch_channels
    if channels:
        story.append(Paragraph("Go-To-Market Strategy (0-90 Days)", styles['SubHeader']))
        for c in channels:
            story.append(Paragraph(f"• {safe_str(c)}", styles['BodyText']))
            
    story.append(PageBreak())

def build_appendix(story, styles, raw_context_dict: dict):
    story.append(Paragraph("8. Appendix & References", styles['SectionHeader']))
    story.append(Paragraph("Sources utilized for this report's intelligence generation.", styles['BodyText']))
    story.append(Spacer(1, 0.2 * inch))
    
    evidence = set()
    for k, v in raw_context_dict.items():
        if isinstance(v, dict):
            ev = v.get("evidence", [])
            if isinstance(ev, list):
                for e in ev:
                    if isinstance(e, str) and e.startswith("http"):
                        evidence.add(e)
                        
    if evidence:
        for i, e in enumerate(sorted(list(evidence))):
            story.append(Paragraph(f"[{i+1}] {html.escape(e)}", styles['BodyText']))
    else:
        story.append(Paragraph("No external sources cited.", styles['DataUnavailable']))
