import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import seaborn as sns 
from src.load_data import *

def load_and_split_data_by_class():
    """
    Loads participant data from 'Metadata_Participants.csv' 
    and separates rows by 'Class' ("ASD" vs. "TD").

    Returns:
      tuple (df, df_asd, df_td):
        df (pd.DataFrame): The full metadata DataFrame.
        df_asd (pd.DataFrame): Rows where Class == "ASD".
        df_td (pd.DataFrame): Rows where Class == "TD".
    """
    df = pd.read_csv(metadata_participants)  
    df_asd = df[df["Class"] == "ASD"]
    df_td = df[df["Class"] == "TD"]
    return df, df_asd, df_td

def compare_all_metrics(df_asd, df_td):
    """
    Performs Welch's t-tests on five metrics, returning p-values and means.
    
    Metrics tested:
      - Avg_Gaze_Deviation
      - Avg_Fixation_Deviation
      - Avg_Saccade_Deviation
      - Saccade_Frequency
      - Avg_Saccade_Duration

    Parameters:
      df_asd (pd.DataFrame): Rows from metadata where Class == "ASD"
      df_td (pd.DataFrame): Rows from metadata where Class == "TD"

    Returns:
      dict: A dictionary keyed by metric name, each value is another dict with:
        {
          "ASD_mean": float,
          "TD_mean":  float,
          "p_value":  float
        }
    """
    metrics = [
        "Avg_Gaze_Deviation",
        "Avg_Fixation_Deviation",
        "Avg_Saccade_Deviation",
        "Saccade_Frequency",
        "Avg_Saccade_Duration"
    ]

    results = {}
    for metric in metrics:
        asd_vals = df_asd[metric].dropna()
        td_vals = df_td[metric].dropna()

        # Welch's t-test
        _, p_val = ttest_ind(asd_vals, td_vals, equal_var=False)

        results[metric] = {
            "ASD_mean": asd_vals.mean(),
            "TD_mean": td_vals.mean(),
            "p_value": p_val
        }

    return results

def get_significance_stars(p_val):
    """
    Returns the appropriate string for p-value significance:
      - p < 0.001: '***'
      - p < 0.01: '**'
      - p < 0.05: '*'
      - otherwise: ''
    
    Parameters:
      p_val (float): The p-value to interpret.
    
    Returns:
      str: The star label.
    """
    if p_val < 0.001:
        return "***"
    elif p_val < 0.01:
        return "**"
    elif p_val < 0.05:
        return "*"
    else:
        return ""

def plot_individual_boxplots(df_asd, df_td, results):
    """
    Generates a separate boxplot figure for each metric in 'results',
    comparing ASD vs. TD distributions. Significant metrics receive 
    a star label above a bracket.

    Parameters:
      df_asd (pd.DataFrame): ASD subset.
      df_td (pd.DataFrame): TD subset.
      results (dict): Output from 'compare_all_metrics'.
    """
    for metric, stats in results.items():
        asd_vals = df_asd[metric].dropna()
        td_vals = df_td[metric].dropna()
        p_val = stats["p_value"]
        star_label = get_significance_stars(p_val)

        plt.figure()
        box_data = [asd_vals, td_vals]
        bp = plt.boxplot(box_data, positions=[1,2], patch_artist=True, widths=0.5)

        # Color the boxes
        bp['boxes'][0].set_facecolor("lightskyblue")
        bp['boxes'][1].set_facecolor("palegreen")

        # Set X labels
        plt.xticks([1,2], ["ASD", "TD"])
        plt.title(f"{metric}")  # or f"{metric} {star_label}" if you wish
        plt.ylabel(metric)

        if star_label:  # If there's at least one star
            # Place the bracket/asterisks above the top of both distributions
            max_val = max(asd_vals.max(), td_vals.max())
            min_val = min(asd_vals.min(), td_vals.min())
            offset = 0.02 * (max_val - min_val) if max_val != min_val else 1.0
            y = max_val + offset
            h = offset

            # Draw bracket
            plt.plot([1, 1, 2, 2], [y, y+h, y+h, y], color="black", linewidth=1.3)
            # Put the significance label above the bracket
            plt.text(1.5, y + h, star_label, ha='center', va='bottom', fontsize=14, color="black")

        plt.show()

def plot_significant_subplots(df_asd, df_td, results):
    """
    Creates a single figure with multiple subplots (side-by-side),
    only for metrics where p<0.05 in 'results'.

    Each subplot is a boxplot comparing ASD vs. TD. 
    If a metric is not significant (p>=0.05), it is excluded.

    Parameters:
      df_asd (pd.DataFrame): ASD subset.
      df_td (pd.DataFrame): TD subset.
      results (dict): The result of compare_all_metrics.
    """
    # Identify which metrics are significant at p<0.05
    sig_metrics = [m for m, st in results.items() if st["p_value"] < 0.05]
    if not sig_metrics:
        print("No metrics are significant at p<0.05.")
        return

    num_metrics = len(sig_metrics)
    fig, axes = plt.subplots(1, num_metrics, figsize=(5*num_metrics, 5))

    # If only one metric is significant, axes won't be a list, so make it one
    if num_metrics == 1:
        axes = [axes]

    for ax, metric in zip(axes, sig_metrics):
        asd_vals = df_asd[metric].dropna()
        td_vals = df_td[metric].dropna()
        p_val = results[metric]["p_value"]
        star_label = get_significance_stars(p_val)

        box_data = [asd_vals, td_vals]
        bp = ax.boxplot(box_data, positions=[1,2], patch_artist=True, widths=0.5)
        
        # Color the boxes
        bp['boxes'][0].set_facecolor("lightskyblue")
        bp['boxes'][1].set_facecolor("palegreen")

        ax.set_xticks([1,2])
        ax.set_xticklabels(["ASD", "TD"])
        ax.set_title(metric)
        ax.set_ylabel(metric)

        if star_label:
            max_val = max(asd_vals.max(), td_vals.max())
            min_val = min(asd_vals.min(), td_vals.min())
            offset = 0.02 * (max_val - min_val) if max_val != min_val else 1.0
            y = max_val + offset
            h = offset

            ax.plot([1, 1, 2, 2], [y, y+h, y+h, y], color="black", linewidth=1.3)
            ax.text(1.5, y + h, star_label, ha='center', va='bottom', fontsize=14, color="black")

    plt.tight_layout()
    plt.show()

def plot_distribution_kde_by_group(df, metric, title=None):
    """
    Plots a KDE (kernel density estimate) for 'metric', coloring by ASD vs. TD.
    
    Parameters:
    df (pd.DataFrame): A DataFrame containing the metric column and a 'Class' column 
                         (where values are 'ASD' or 'TD').
    metric (str): The name of the numeric column to plot.
    title (str, optional): Custom plot title.
    """
    plt.figure(figsize=(10, 6))
    custom_palette = {"ASD": "lightskyblue", "TD": "palegreen"}
    sns.kdeplot(
        data=df,
        x=metric,
        hue="Class",
        fill=True,
        common_norm=False,  # separate normalization per group
        alpha=0.6,
        palette=custom_palette
    )
    plt.title(title if title else f"Distribution of {metric} by Class")
    plt.xlabel(metric)
    plt.ylabel("Density")
    plt.grid(True, linestyle=":", alpha=0.7)
    plt.legend(labels=["TD", "ASD"])
    plt.show()