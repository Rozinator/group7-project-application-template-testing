from typing import List
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
from model import Issue

class IssuesCategoryTrendAnalyzer:
    """
    Analyzes and compares the creation trends of the most frequent issue labels over time.
    This provides a comprehensive view of how the project's focus (e.g., documentation,
    specific components, bugs, features) has shifted as it matures.
    """

    def run(self, issues: List[Issue]):
        self.analyze_top_label_trends(issues, top_n=6)

    def _calculate_label_frequency(self, issues: List[Issue]) -> Counter:
        """Helper to calculate the occurrences of each label across all issues."""
        label_counts = Counter()
        for issue in issues:
            if hasattr(issue, 'labels') and isinstance(issue.labels, list):
                label_counts.update(issue.labels)
        return label_counts

    def analyze_top_label_trends(self, issues: List[Issue], top_n: int):
      
        # 1. Identify the top N most frequent labels
        label_counts = self._calculate_label_frequency(issues)
        top_labels = {label for label, count in label_counts.most_common(top_n)}
        print(f"Analyzing trends for the top {len(top_labels)} labels: {top_labels}")

        # 2. Prepare the data in a long format
        # Each row is a single label assignment on a specific date
        data = []
        for issue in issues:
            if issue.created_date and hasattr(issue, 'labels') and issue.labels:
                for label in issue.labels:
                    if label in top_labels:
                        data.append({'created_date': issue.created_date, 'label': label})

        df = pd.DataFrame(data)
        df['created_date'] = pd.to_datetime(df['created_date'])

        # 3. Group by time period (Quarter) and count each label
        # .size() is used to count rows in each group
        counts_by_time = df.set_index('created_date').groupby([
            pd.Grouper(freq='Q'), 
            'label'
        ]).size()
        
        # 4. Pivot the data to get labels as columns
        plot_df = counts_by_time.unstack(level='label', fill_value=0)

        # 5. Create the multi-line plot
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(15, 8))

        plot_df.plot(
            kind='line',
            ax=ax,
            linewidth=2.5,
            marker='o',
            markersize=5,
            colormap='viridis'
        )

        ax.set_title(f'Trend of Top {top_n} Most Common Issue Labels Over Time', fontsize=16)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Number of New Issues Created (per Quarter)', fontsize=12)
        ax.legend(title='Label Type')
        ax.set_ylim(0)

        plt.tight_layout()
        plt.show()