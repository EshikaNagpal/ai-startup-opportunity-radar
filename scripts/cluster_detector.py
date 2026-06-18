import json

with open(
    "data/processed/test_opportunities.json",
    "r",
    encoding="utf-8"
) as f:
    opportunities = json.load(f)

clusters = {
    "Customer Discovery": [],
    "Competitive Intelligence": [],
    "Market Research": [],
    "Other": []
}

for opp in opportunities:

    problem = opp["problem"].lower()

    if "customer" in problem:
        clusters["Customer Discovery"].append(opp)

    elif "competitor" in problem:
        clusters["Competitive Intelligence"].append(opp)

    elif "market" in problem:
        clusters["Market Research"].append(opp)

    else:
        clusters["Other"].append(opp)

print("\nCLUSTER REPORT\n")

for cluster_name, cluster_opportunities in clusters.items():

    if len(cluster_opportunities) == 0:
        continue

    print(f"{cluster_name}")
    print("-" * len(cluster_name))

    for opp in cluster_opportunities:
        print(f"- {opp['problem']}")

    print()