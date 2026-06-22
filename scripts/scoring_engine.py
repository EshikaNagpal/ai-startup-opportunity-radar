def calculate_opportunity_score(opportunity):

    severity = opportunity["severity"]
    frequency = opportunity["frequency_estimate"]
    willingness = opportunity["willingness_to_pay"]
    evidence = opportunity["evidence_strength"]
    competition = opportunity["competition_level"]

    weighted_score = (
        severity * 0.25
        + frequency * 0.20
        + willingness * 0.30
        + evidence * 0.15
        + (10 - competition) * 0.10
    )

    return round(weighted_score * 18, 2)