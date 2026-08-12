"""Simple fund recommender utility that selects top funds by Sharpe.
"""

import pandas as pd, os

BASE = os.path.dirname(__file__)

def recommend(risk_appetite: str):
    """
    risk_appetite: "Low" | "Moderate" | "High"
    Returns top 3 funds by Sharpe within matching risk_grade.
    """
    risk_map = {
        "Low":      ["Low"],
        "Moderate": ["Moderate", "Moderately High"],
        "High":     ["High", "Very High", "Moderately High"],
    }
    sc  = pd.read_csv(os.path.join(BASE, "fund_scorecard.csv"), index_col=0)
    fm  = pd.read_csv(os.path.join(BASE, "data", "processed", "fund_master_clean.csv"))
    rg  = fm.set_index("scheme_code")["risk_grade"].to_dict()
    sc["risk_grade"] = sc["scheme_code"].map(rg)

    grades  = risk_map.get(risk_appetite, ["Moderate"])
    filtered = sc[sc["risk_grade"].isin(grades)].nlargest(3, "sharpe")

    cols = ["scheme_name", "risk_grade", "sharpe", "cagr_3y", "alpha_annual", "score"]
    result = filtered[cols].copy()
    result.columns = ["Fund", "Risk Grade", "Sharpe", "CAGR 3Y", "Alpha %", "Score"]
    result["Fund"] = result["Fund"].str.replace(" Direct Growth", "").str.replace(" Mutual Fund", "")
    result = result.reset_index(drop=True)
    result.index += 1

    print(f"\n  Top 3 Funds for {risk_appetite} risk appetite:")
    print(result.to_string())
    return result

if __name__ == "__main__":
    for r in ["Low", "Moderate", "High"]:
        recommend(r)
        print()
