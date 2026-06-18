from scoring_engine import calculate_opportunity_score

def rank_opportunities(opportunities):
    for opportunity in opportunities:
        score = calculate_opportunity_score(opportunity)
        opportunity["opportunity_score"] = score

    ranked_opportunities = sorted(
        opportunities,
        key=lambda opportunity: opportunity["opportunity_score"],
        reverse=True
    )

    return ranked_opportunities