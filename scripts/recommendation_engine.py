print("NEW RECOMMENDATION ENGINE LOADED")
def generate_recommendation(
    top_opportunity,
    top_trend
):

    if (
        "Customer" in top_trend
        or "Feedback" in top_trend
        or "Discovery" in top_trend
    ):

        return {
            "startup_idea":
                "AI Customer Discovery Platform",

            "target_customer":
                "Startup Founders and Product Teams",

            "difficulty":
                "Medium",

            "reason":
                "Customer research and feedback problems appear repeatedly across the dataset."
        }

    elif (
        "Competitor" in top_trend
        or "Market Intelligence" in top_trend
    ):

        return {
            "startup_idea":
                "Competitor Intelligence Platform",

            "target_customer":
                "Founders and Growth Teams",

            "difficulty":
                "Medium",

            "reason":
                "Companies spend significant time manually tracking competitors and market movements."
        }

    elif (
        "Validation" in top_trend
        or "Market Validation" in top_trend
    ):

        return {
            "startup_idea":
                "AI Startup Validation Assistant",

            "target_customer":
                "Early-Stage Founders",

            "difficulty":
                "High",

            "reason":
                "Validating startup ideas remains a recurring and costly founder problem."
        }

    else:

        return {
            "startup_idea":
                "Founder Workflow Automation Platform",

            "target_customer":
                "Startup Founders",

            "difficulty":
                "Medium",

            "reason":
                "Multiple operational pain points suggest demand for workflow automation."
        }