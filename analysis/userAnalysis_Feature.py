from collections import Counter
from typing import List
import config
import matplotlib.pyplot as plt
from data_loader import DataLoader
from model import Issue


class CommentAnalysis:
    def __init__(self):
        #Initialize analysis with user parameter.
        self.user: str = config.get_parameter('user')

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()
        commenters = []

        # Extract comment authors
        for issue in issues:
            for event in issue.events:
                if event.event_type == 'commented':
                    commenters.append(event.author)

        # Count and sort by frequency
        counts = Counter(commenters)
        top_contributors = counts.most_common(10)  # Only top 10

        top_values = [val for name, val in top_contributors]
        other_total = sum(counts.values()) - sum(top_values)
        
        # Combine top 10 with "Others" into a single list of tuples
        all_data = top_contributors + [("Others", other_total)]

        #Sort legend by percentage
        all_data.sort(key=lambda item: item[1], reverse=True)

        names_sorted, values_sorted = zip(*all_data)# Unzip
        legend_labels = [f"{name} ({count})" for name, count in all_data]

        SMALL_SLICE_THRESHOLD = 5.0  # Slices smaller than 5% will be annotated
        total_values = float(sum(values_sorted))

        explode = []
        for value in values_sorted:
            percentage = (value / total_values) * 100
            if percentage < SMALL_SLICE_THRESHOLD:
                explode.append(0.1)
            else:
                explode.append(0)

        # Create figure
        plt.figure(figsize=(10, 7))
        
        wedges, texts, autotexts = plt.pie(values_sorted,
                                         explode=tuple(explode), 
                                         autopct="%1.1f%%",
                                         startangle=140,
                                         pctdistance=0.9, 
                                         labeldistance=1.1) 

        plt.title("Top Comment Contributors (Grouped)")

        #Arrow to display percentage
        if autotexts:
            for i, label in enumerate(autotexts):
                percentage = (values_sorted[i] / total_values) * 100
                if percentage < SMALL_SLICE_THRESHOLD:
                    pos = label.get_position()
                    pct_text = label.get_text()
                    label.set_visible(False)
                    plt.annotate(pct_text,
                                 xy=pos, xycoords='data',
                                 xytext=(pos[0] * 1.2, pos[1] * 1.2),
                                 textcoords='data',
                                 arrowprops=dict(arrowstyle="->",
                                                 connectionstyle="arc3,rad=0.2",
                                                 color='black'),
                                 horizontalalignment='center',
                                 verticalalignment='center',
                                 fontsize=9)

        plt.legend(legend_labels, 
                   title="Contributors", 
                   bbox_to_anchor=(1.2, 0.5), 
                   loc="center left")

        plt.tight_layout()
        plt.show()