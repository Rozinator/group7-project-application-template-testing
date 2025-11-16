from typing import List, Dict
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from model import Issue

class IssueResolutionTimeAnalyzer:
    """
    Analyzes GitHub issue labels to identify common issue types and their
    impact on resolution times.
    """

    def run(self, issues: List[Issue]):
        
        # 1. Calculate frequency data for all labels
        label_counts = self._calculate_label_frequency(issues)
        
        # 2. Calculate resolution time data for relevant labels
        avg_resolution_by_label = self._calculate_avg_resolution_time(issues)

        self.plot_label_frequency(label_counts)

        self.plot_resolution_time_by_label(avg_resolution_by_label)

        self.plot_frequency_vs_resolution_time(label_counts, avg_resolution_by_label)

    def _get_labels_for_issue(self, issue: Issue) -> set:
        """Helper method to gather labels"""
        if hasattr(issue, 'labels') and isinstance(issue.labels, list):
            return set(issue.labels)
        return set()


    def _calculate_label_frequency(self, issues: List[Issue]) -> Counter:
        """Calculates the occurrences of each label across all issues."""
        label_counts = Counter()
        for issue in issues:
            issue_labels = self._get_labels_for_issue(issue)
            label_counts.update(list(issue_labels))
        return label_counts

    def _calculate_avg_resolution_time(self, issues: List[Issue]) -> dict:
        """Calculates the average resolution time for labels on 10+ closed issues."""
        resolution_times_by_label: Dict[str, List[int]] = defaultdict(list)
        for issue in issues:
            if issue.state == 'closed' and issue.created_date and issue.updated_date:
                resolution_time = (issue.updated_date - issue.created_date).days
                issue_labels = self._get_labels_for_issue(issue)
                for label in issue_labels:
                    resolution_times_by_label[label].append(resolution_time)

        avg_resolution_by_label = {}
        for label, times in resolution_times_by_label.items():
            if len(times) >= 10:
                avg_resolution_by_label[label] = np.mean(times)
        return avg_resolution_by_label

    def plot_label_frequency(self, label_counts: Counter):
        """Plots the top 15 most common labels."""

        most_common_labels = label_counts.most_common(15)
        labels, counts = zip(*most_common_labels)

        plt.figure(figsize=(12, 8))
        plt.barh(labels, counts, color='teal')
        plt.xlabel('Total Number of Issues')
        plt.ylabel('Label')
        plt.title('Top 15 Most Common Issue Labels')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()

    def plot_resolution_time_by_label(self, avg_resolution_by_label: dict):
        """Plots the average resolution time for qualifying labels."""
        
        sorted_labels = sorted(avg_resolution_by_label.items(), key=lambda item: item[1], reverse=True)
        labels, avg_times = zip(*sorted_labels)

        plt.figure(figsize=(12, 8))
        plt.barh(labels, avg_times, color='coral')
        plt.xlabel('Average Resolution Time (Days)')
        plt.ylabel('Label')
        plt.title('Average Resolution Time (for labels on at least 10 closed issues)')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()

    def plot_frequency_vs_resolution_time(self, label_counts: Counter, avg_resolution_by_label: dict):
        """
        Creates a scatter plot to show the relationship between a label's
        frequency and its average resolution time.
        """
        labels_to_plot = list(avg_resolution_by_label.keys())
        
        frequencies = [label_counts[label] for label in labels_to_plot]
        avg_times = [avg_resolution_by_label[label] for label in labels_to_plot]

        plt.figure(figsize=(12, 8))

        plt.scatter(frequencies, avg_times, alpha=0.7, s=100, color='steelblue')

        plt.title('Label Frequency vs. Average Resolution Time', fontsize=16)
        plt.xlabel('Total Frequency (Number of Issues)', fontsize=12)
        plt.ylabel('Average Resolution Time (Days)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)

        for i, label in enumerate(labels_to_plot):
            plt.annotate(label, (frequencies[i], avg_times[i]), textcoords="offset points", xytext=(5,-10), ha='left', fontsize=9)

        plt.tight_layout()
        plt.show()