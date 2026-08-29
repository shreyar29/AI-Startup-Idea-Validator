export const calculatePillars = (data) => {
  if (!data) return { strongest: null, weakest: null, scores: [] };
  
  const scores = [
    { label: 'Execution Feasibility', score: data.execution_score },
    { label: 'Market Potential', score: data.market_score },
    { label: 'Customer Demand', score: data.customer_score },
    { label: 'Go-To-Market Fit', score: data.gtm_score },
    { label: 'Competitive Position', score: data.competition_score },
    { label: 'Risk Profile', score: data.risk_score }
  ].filter(s => s.score != null);

  // Avoid array mutation
  const sortedScores = [...scores].sort((a, b) => b.score - a.score);
  
  return {
    strongest: sortedScores[0] || null,
    weakest: sortedScores[sortedScores.length - 1] || null,
    scores: sortedScores
  };
};

export const generateVeraInsight = (strongest, weakest) => {
  if (!strongest || !weakest) {
    return "Analysis complete. Please review the detailed scores below.";
  }

  if (strongest.score - weakest.score > 10) {
    return `Your strongest area is ${strongest.label.toLowerCase()} (${strongest.score}/100). Your biggest challenge is ${weakest.label.toLowerCase()} (${weakest.score}/100).`;
  } else if (strongest.score >= 80) {
    return "Exceptionally balanced and strong idea. All core pillars are performing highly.";
  } else {
    return `The idea shows consistent but moderate potential across the board. Focus on differentiating your ${weakest.label.toLowerCase()} to boost viability.`;
  }
};

export const getScoreInterpretation = (score) => {
  if (score >= 90) return { label: 'Excellent', color: 'text-emerald-400' };
  if (score >= 75) return { label: 'Strong', color: 'text-blue-400' };
  if (score >= 60) return { label: 'Moderate', color: 'text-yellow-400' };
  if (score >= 40) return { label: 'Weak', color: 'text-orange-400' };
  return { label: 'High Risk', color: 'text-red-400' };
};

export const getInvestmentReadiness = (score) => {
  if (score >= 85) return 'Highly Investable';
  if (score >= 70) return 'Seed Ready';
  if (score >= 50) return 'Needs Validation';
  return 'Pre-Ideation';
};
