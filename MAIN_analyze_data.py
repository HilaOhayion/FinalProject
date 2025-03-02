from src.data_visualization import load_and_split_data_by_class, compare_all_metrics
from src.data_visualization import plot_individual_boxplots, plot_significant_subplots
from src.data_visualization import plot_distribution_kde_by_group

def main():
    df, df_asd, df_td = load_and_split_data_by_class()
    comparison_results = compare_all_metrics(df_asd, df_td)
    
    # Generate individual boxplots
    plot_individual_boxplots(df_asd, df_td, comparison_results)
    
    # Plot only the metrics that turned out significant
    plot_significant_subplots(df_asd, df_td, comparison_results)

    # Density plots for overall gaze deviation and saccade frequency
    plot_distribution_kde_by_group(df, "Avg_Gaze_Deviation", "Distribution of Gaze Deviation by Group")
    plot_distribution_kde_by_group(df, "Saccade_Frequency", "Distribution of Saccade Frequency by Group")

if __name__ == "__main__":
    main()