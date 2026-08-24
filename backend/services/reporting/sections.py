import html
from datetime import datetime
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
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
    story.append(Paragraph("STRATEGIC DUE DILIGENCE REPORT", styles['CoverSubtitle']))
    story.append(Spacer(1, 0.5 * inch))
    
    display_idea = (idea_desc[:120] + '...') if len(idea_desc) > 120 else idea_desc
    story.append(Paragraph(safe_str(display_idea), styles['CoverTitle']))
    
    story.append(Spacer(1, 2 * inch))
    story.append(HRFlowable(width="50%", thickness=1, color=BRAND_GRAY, spaceBefore=10, spaceAfter=10, hAlign='CENTER'))
    story.append(Paragraph("Prepared by VentureLens AI Consulting Group", styles['CoverMeta']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['CoverMeta']))
    story.append(PageBreak())

def build_toc(story, styles):
    story.append(Paragraph("Table of Contents", styles['TOCHeading']))
    sections = [
        "1. Executive Summary",
        "2. Startup Score Explanation",
        "3. Market Insights",
        "4. Customer Insights",
        "5. Competitive Landscape",
        "6. SWOT Interpretation",
        "7. Risk Analysis",
        "8. MVP Roadmap",
        "9. GTM Roadmap",
        "10. Final Verdict"
    ]
    for s in sections:
        story.append(Paragraph(s, styles['TOCItem']))
    story.append(PageBreak())

def build_consulting_section(story, styles, title, summary, analysis, why_matters, recommendation, risk_level, next_actions):
    story.append(Paragraph(title, styles['SectionHeader']))
    
    # Executive Summary Box
    summ_data = [[Paragraph("<b>Executive Summary</b>", styles['BodyTextBold'])],
                 [Paragraph(safe_str(summary), styles['BodyText'])]]
    t_summ = Table(summ_data, colWidths=[7 * inch])
    t_summ.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BRAND_LIGHT_GRAY),
        ('BOX', (0,0), (-1,-1), 1, BRAND_SECONDARY),
        ('PADDING', (0,0), (-1,-1), 12)
    ]))
    story.append(t_summ)
    story.append(Spacer(1, 0.2 * inch))
    
    # Analysis
    story.append(Paragraph("Analysis", styles['SubHeader']))
    story.append(Paragraph(safe_str(analysis), styles['BodyText']))
    
    # Why It Matters
    story.append(Paragraph("Why It Matters", styles['SubHeader']))
    story.append(Paragraph(safe_str(why_matters), styles['BodyText']))
    
    # Strategic Recommendation
    story.append(Paragraph("Strategic Recommendation", styles['SubHeader']))
    story.append(Paragraph(safe_str(recommendation), styles['BodyText']))
    story.append(Spacer(1, 0.1 * inch))
    
    # Scorecard: Risk Level & Next Actions
    color = BRAND_PRIMARY
    if "High" in risk_level: color = BRAND_ERROR
    elif "Medium" in risk_level: color = BRAND_WARNING
    elif "Low" in risk_level: color = BRAND_SUCCESS

    scorecard_data = [
        [Paragraph("<b>Risk Level</b>", ParagraphStyle('ScoreH1', parent=styles['BodyTextBold'], textColor=colors.white)), 
         Paragraph("<b>Next Actions</b>", ParagraphStyle('ScoreH2', parent=styles['BodyTextBold'], textColor=colors.white))],
        [
            Paragraph(safe_str(risk_level), ParagraphStyle('ScoreV1', parent=styles['BodyTextBold'], textColor=color)),
            Paragraph(safe_str(next_actions), styles['BodyText'])
        ]
    ]
    t_score = Table(scorecard_data, colWidths=[2 * inch, 5 * inch])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BRAND_PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.25, BRAND_GRAY),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_score)
    story.append(PageBreak())

def build_executive_summary(story, styles, context: ReportContext):
    eval_data = context.final_evaluation
    score_data = eval_data.startup_score
    
    build_consulting_section(
        story, styles, 
        title="1. Executive Summary",
        summary=f"The proposed startup idea has achieved an overall viability score of {score_data.overall_score}/100 with a verdict of '{score_data.verdict}'.",
        analysis=f"The AI evaluated the market attractiveness ({score_data.market_score}/25), competition intensity ({score_data.competition_score}/25), execution complexity ({score_data.execution_score}/25), and GTM strategy ({score_data.gtm_score}/25).",
        why_matters="A structured due diligence assessment helps founders avoid building products nobody wants and investors avoid misallocating capital.",
        recommendation=eval_data.executive_summary if isinstance(eval_data.executive_summary, str) else "Focus on core validation before scaling.",
        risk_level=f"{eval_data.risk.overall_risk_level} Risk",
        next_actions="Review the subsequent sections for deep-dive analysis into market, competition, and go-to-market strategies."
    )

def build_startup_scorecard(story, styles, context: ReportContext):
    score_data = context.final_evaluation.startup_score
    safe_explanations = [e.get("explanation", e.get("reason", str(e))) if isinstance(e, dict) else str(e) for e in score_data.score_explanation] if score_data.score_explanation else []
    explanations = ", ".join(safe_explanations) if safe_explanations else "No explanations provided."
    
    build_consulting_section(
        story, styles, 
        title="2. Startup Score Explanation",
        summary=f"Score: {score_data.overall_score}/100. Verdict: {score_data.verdict}.",
        analysis=f"The score breakdown relies on qualitative and quantitative analysis across four pillars. Explanations: {explanations}",
        why_matters="Understanding the exact drivers of the viability score identifies immediate areas of improvement and funding requirements.",
        recommendation="Leverage high-scoring areas as unfair advantages when pitching to investors.",
        risk_level="Medium",
        next_actions="De-risk low-scoring pillars by running micro-experiments or pivoting the target audience."
    )

def build_market_insights(story, styles, context: ReportContext):
    market = context.final_evaluation.market
    market_size = market.market_size or "Data Unavailable"
    safe_trends = [t.get("trend", t.get("name", str(t))) if isinstance(t, dict) else str(t) for t in market.market_trends] if market.market_trends else []
    trends = ", ".join(safe_trends) if safe_trends else "No clear trends identified."
    
    build_consulting_section(
        story, styles, 
        title="3. Market Insights",
        summary=f"The market size is estimated at {market_size} with a maturity level of {market.market_maturity}.",
        analysis=f"The market is experiencing a growth rate of {market.growth_rate}. Key macro trends driving adoption include: {trends}.",
        why_matters="A rapidly growing or large TAM (Total Addressable Market) is the #1 prerequisite for venture-scale returns.",
        recommendation="Position the product to capture demand created by the macro trends rather than fighting established paradigms.",
        risk_level="Low to Medium",
        next_actions="Conduct bottom-up TAM/SAM/SOM calculations to validate top-down AI estimates."
    )

def build_customer_insights(story, styles, context: ReportContext):
    customer = context.final_evaluation.customer
    segments = customer.get("target_customer_segments", [])
    pain_points = customer.get("pain_points", [])
    
    safe_segments = [s.get("segment_name", s.get("name", s.get("segment", str(s)))) if isinstance(s, dict) else str(s) for s in segments]
    safe_pain = [p.get("pain_point", p.get("description", p.get("name", str(p)))) if isinstance(p, dict) else str(p) for p in pain_points]
    
    build_consulting_section(
        story, styles, 
        title="4. Customer Insights",
        summary=f"Targeting {len(segments)} core customer segments experiencing critical pain points.",
        analysis=f"Primary segments: {', '.join(safe_segments[:3]) if safe_segments else 'Unknown'}. Core pain points: {', '.join(safe_pain[:3]) if safe_pain else 'Unknown'}.",
        why_matters="Customer obsession is critical. If the pain point is not acute (a 'hair on fire' problem), acquisition costs will outpace lifetime value.",
        recommendation="Develop targeted buyer personas and tailor messaging specifically to the highest-intent segment first.",
        risk_level="Medium",
        next_actions="Conduct 20-30 customer discovery interviews to validate these assumptions."
    )

def build_competitive_landscape(story, styles, context: ReportContext):
    comp = context.final_evaluation.competitor
    competitors = comp.competitors
    gap = comp.gap_analysis
    
    comp_names = [c.get("name", str(c)) if isinstance(c, dict) else getattr(c, "name", str(c)) for c in competitors] if competitors else []
    
    build_consulting_section(
        story, styles, 
        title="5. Competitive Landscape",
        summary=f"The market features established players including {', '.join(comp_names[:3]) if comp_names else 'unknown entities'}.",
        analysis=f"Competitors typically exhibit strong brand presence but struggle with agility. Market Whitespace (Gap Analysis): {gap}",
        why_matters="Entering a red ocean requires a 10x better product or a novel distribution advantage.",
        recommendation="Avoid competing directly on features. Compete on the identified whitespace or target an underserved niche.",
        risk_level="High",
        next_actions="Monitor competitor pricing pages and release notes. Build a differentiation matrix."
    )

def build_swot_interpretation(story, styles, context: ReportContext):
    swot = context.final_evaluation.swot
    
    build_consulting_section(
        story, styles, 
        title="6. SWOT Interpretation",
        summary="A balanced analysis of internal capabilities versus external environmental factors.",
        analysis=f"Strengths: {len(swot.strengths)}. Weaknesses: {len(swot.weaknesses)}. Opportunities: {len(swot.opportunities)}. Threats: {len(swot.threats)}.",
        why_matters="SWOT provides a structured framework for strategic planning and resource allocation.",
        recommendation="Double down on strengths to capture identified opportunities while building defensive moats against threats.",
        risk_level="Medium",
        next_actions="Assign ownership to mitigating the top 2 weaknesses."
    )

def build_risk_analysis(story, styles, context: ReportContext):
    risk = context.final_evaluation.risk
    
    safe_risks = [r.get("risk", r.get("description", str(r))) if isinstance(r, dict) else str(r) for r in risk.top_risks] if risk.top_risks else []
    
    build_consulting_section(
        story, styles, 
        title="7. Risk Analysis",
        summary=f"Overall risk is classified as {risk.overall_risk_level} with a score of {risk.overall_risk_score}/100.",
        analysis=f"Top risks include: {', '.join(safe_risks[:3]) if safe_risks else 'Data unavailable'}.",
        why_matters="Unmitigated risks kill startups. Investors look for founders who proactively identify and manage existential threats.",
        recommendation="Establish a risk register and implement the AI-suggested mitigation strategies immediately.",
        risk_level=risk.overall_risk_level,
        next_actions="Prioritize mitigating the risk with the highest probability and impact."
    )

def build_mvp_roadmap(story, styles, context: ReportContext):
    mvp = context.final_evaluation.mvp
    
    safe_features = [f.get("feature", f.get("name", str(f))) if isinstance(f, dict) else str(f) for f in mvp.core_features] if mvp.core_features else []
    
    build_consulting_section(
        story, styles, 
        title="8. MVP Roadmap",
        summary=f"The Minimum Viable Product requires {len(mvp.core_features)} core features for successful market entry.",
        analysis=f"Core requirements: {', '.join(safe_features[:4]) if safe_features else 'Data unavailable'}.",
        why_matters="Overbuilding the MVP burns runway. The goal is to build the minimum feature set required to validate the core hypothesis.",
        recommendation="Strictly adhere to the core features list. Defer all 'nice-to-have' features to post-launch iterations.",
        risk_level="Low",
        next_actions="Create a wireframe and user flow. Seek feedback before writing code."
    )

def build_gtm_roadmap(story, styles, context: ReportContext):
    gtm = context.final_evaluation.gtm
    channels = gtm.acquisition_channels or gtm.launch_channels
    
    # Safely extract string if channel is a dict
    channel_strs = []
    for c in channels:
        if isinstance(c, dict):
            channel_strs.append(c.get('channel') or c.get('name') or str(c))
        else:
            channel_strs.append(str(c))
            
    build_consulting_section(
        story, styles, 
        title="9. GTM Roadmap",
        summary="A targeted Go-To-Market strategy is required to achieve initial traction and lower CAC.",
        analysis=f"Primary acquisition channels: {', '.join(channel_strs[:3]) if channel_strs else 'Direct outreach'}.",
        why_matters="Distribution is often more critical than product. First-time founders focus on product; second-time founders focus on distribution.",
        recommendation="Test 2-3 channels simultaneously with small budgets, then double down on the channel with the lowest CAC.",
        risk_level="High",
        next_actions="Launch a landing page to collect waitlist emails using the primary acquisition channel."
    )

def build_final_verdict(story, styles, context: ReportContext):
    score_data = context.final_evaluation.startup_score
    
    build_consulting_section(
        story, styles, 
        title="10. Final Verdict",
        summary=f"Final Assessment: {score_data.verdict}",
        analysis="Based on the synthesis of market intelligence, competitive whitespace, and execution complexity, the venture presents a defined risk-reward profile.",
        why_matters="Investors need a clear, unequivocal recommendation on viability.",
        recommendation="Proceed with the recommended Next Actions to de-risk the venture and improve the overall viability score.",
        risk_level=context.final_evaluation.risk.overall_risk_level,
        next_actions="Schedule a co-founder alignment meeting to review this report and assign execution tasks."
    )
