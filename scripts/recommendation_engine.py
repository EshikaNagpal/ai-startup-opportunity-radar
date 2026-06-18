def generate_recommendation(
    top_opportunity,
    top_trend
):

    if top_trend == "Customer Research":

        return {
            "startup_idea":
                "Customer Feedback Intelligence Platform",

            "target_customer":
                "Startup Founders and Product Managers",

            "difficulty":
                "Medium",

            "reason":
                "Customer research pain appears frequently and shows strong business value."
        }

    elif top_trend == "Competitive Intelligence":

        return {
            "startup_idea":
                "Competitor Monitoring Platform",

            "target_customer":
                "Founders and Growth Teams",

            "difficulty":
                "Medium",

            "reason":
                "Companies constantly track competitors manually."
        }

    elif top_trend == "Startup Validation":

        return {
            "startup_idea":
                "AI Startup Validation Assistant",

            "target_customer":
                "Early-Stage Founders",

            "difficulty":
                "High",

            "reason":
                "Idea validation is a recurring founder pain."
        }

    else:

        return {
            "startup_idea":
                "Investigate Further",

            "target_customer":
                "Unknown",

            "difficulty":
                "Unknown",

            "reason":
                "Not enough information available."
        }