from scripts.scoring_engine import calculate_opportunity_score


def rank_opportunities(opportunities):

    for opportunity in opportunities:

        score = calculate_opportunity_score(
            opportunity
        )

        opportunity["opportunity_score"] = score

    opportunities = [
        opp
        for opp in opportunities
        if opp.get("startup_idea") != "Unknown"
    ]

    ranked_opportunities = sorted(
        opportunities,
        key=lambda opportunity: opportunity[
            "opportunity_score"
        ],
        reverse=True
    )

    return ranked_opportunities