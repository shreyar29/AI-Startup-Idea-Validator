class ConfidenceCalculator:
    """Component responsible for calculating search confidence."""
    
    def calculate(self, total_accepted: int, total_relevance: int, total_trusted: int, categories_with_results: int, total_categories: int) -> str:
        """
        Calculates confidence based on acceptance rate, relevance scores,
        trusted sources, and category coverage.
        """
        avg_score = (total_relevance / total_accepted) if total_accepted > 0 else 0
        trusted_ratio = (total_trusted / total_accepted) if total_accepted > 0 else 0
        category_coverage = (categories_with_results / total_categories) if total_categories > 0 else 0

        # Confidence Algorithm
        # Weightings: Count (25%), Avg Score (25%), Trusted (25%), Coverage (25%)
        # Normalization targets: 15 results, 10 avg score, 30% trusted, 100% coverage
        score_val = min(1.0, total_accepted / 15) * 0.25
        score_val += min(1.0, avg_score / 10) * 0.25
        score_val += min(1.0, trusted_ratio / 0.3) * 0.25
        score_val += category_coverage * 0.25
        
        if score_val >= 0.8:
            return "High"
        elif score_val >= 0.4:
            return "Medium"
        else:
            return "Low"
