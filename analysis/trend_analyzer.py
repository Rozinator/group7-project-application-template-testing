# analysis/trend_analyzer.py
import pandas as pd
import matplotlib.pyplot as plt

class TrendAnalyzer:
    """
    Analyzes how many issues were created each month.
    """

    def run(self, issues, events):
        print("Running Trend Analysis...")

        data = []
        for issue in issues:
            if issue.created_date:
                data.append({"created_date": issue.created_date})

        if not data:
            print("No valid issue creation dates found in the dataset!")
            return

        df = pd.DataFrame(data)
        df["month"] = df["created_date"].dt.to_period("M")
        monthly_counts = df["month"].value_counts().sort_index()

        plt.figure(figsize=(10, 5))
        monthly_counts.plot(kind="bar", color="teal")
        plt.title("Issue Creation Trend (Poetry Repository)")
        plt.xlabel("Month")
        plt.ylabel("Number of Issues Created")
        plt.tight_layout()
        plt.show()
