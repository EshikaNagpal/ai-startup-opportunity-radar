def generate_founder_decision(opportunities):

    if not opportunities:
        return None

    ranked = sorted(
        opportunities,
        key=lambda x: x.get("opportunity_score", 0),
        reverse=True
    )

    winner = ranked[0]

    reasons = []

    if winner.get("opportunity_score", 0) >= 75:
        reasons.append("Highest overall opportunity score")

    if winner.get("willingness_to_pay", 0) >= 4:
        reasons.append("Strong willingness to pay")

    if winner.get("frequency_estimate", 0) >= 4:
        reasons.append("High frequency customer pain")

    if winner.get("severity", 0) >= 4:
        reasons.append("Severe customer problem")

    if winner.get("competition_level", 5) <= 2:
        reasons.append("Relatively low competition")

    reasons.append("Clear target customer segment")
    reasons.append("Fast MVP validation potential")

    confidence = min(
        95,
        int(winner.get("opportunity_score", 0))
    )

    return {
        "startup": winner["startup_idea"],
        "score": winner["opportunity_score"],
        "confidence": confidence,
        "reasons": reasons
    }