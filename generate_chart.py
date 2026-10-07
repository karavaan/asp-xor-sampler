import pandas as pd
import matplotlib.pyplot as plt

def generate_3panel_figure():
    # 1. Load the unified data
    try:
        df = pd.read_csv("results/unified_evaluation_data.csv")
    except FileNotFoundError:
        print("[!] Error: 'results/unified_evaluation_data.csv' not found. Run experiments first.")
        return

    # 2. Set up academic styling
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'figure.autolayout': True
    })

    # 3. Create 1-row, 3-column subplots
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2))
    optimal_m = 7.18

    # --- Panel (a): Restart Efficiency ---
    axes[0].errorbar(df['m'], df['mean_trials'], yerr=df['std_trials'], 
                     fmt='o-', color='#1f77b4', ecolor='#aec7e8', elinewidth=1.5, capsize=3, label='Empirical')
    axes[0].axvline(x=optimal_m, color='red', linestyle='--', alpha=0.7, label='Optimum')
    axes[0].set_title('(a) Restart Efficiency')
    axes[0].set_xlabel('Constraint Dimension ($m$)')
    axes[0].set_ylabel('Mean Restart Trials')
    
    # Use log scale for the Y axis to handle outliers at m=12 just like your old boxplot!
    axes[0].set_ylim(bottom=0)
    axes[0].grid(True, which="both", linestyle=':', alpha=0.6)
    axes[0].legend(loc='upper left', frameon=True)

    # --- Panel (b): Solution Coverage ---
    axes[1].plot(df['m'], df['coverage_pct'], 's-', color='#2ca02c', linewidth=1.5, markersize=5)
    axes[1].axvline(x=optimal_m, color='red', linestyle='--', alpha=0.7)
    axes[1].axhline(y=100, color='gray', linestyle=':', alpha=0.5)
    axes[1].set_title('(b) Solution Coverage')
    axes[1].set_xlabel('Constraint Dimension ($m$)')
    axes[1].set_ylabel('Unique Models Discovered (%)')
    axes[1].set_ylim(0, 105)
    axes[1].grid(True, linestyle=':', alpha=0.6)

    # --- Panel (c): Statistical Uniformity ---
    axes[2].plot(df['m'], df['uniformity_cv'], 'd-', color='#ff7f0e', linewidth=1.5, markersize=5)
    axes[2].axvline(x=optimal_m, color='red', linestyle='--', alpha=0.7)
    axes[2].set_title('(c) Statistical Uniformity')
    axes[2].set_xlabel('Constraint Dimension ($m$)')
    axes[2].set_ylabel('Freq. Coefficient of Variation')
    axes[2].grid(True, linestyle=':', alpha=0.6)

    plt.show()
    print("[+] Unified 3-panel chart successfully generated as 'results/fig_empirical_evaluation.pdf'!")

if __name__ == "__main__":
    generate_3panel_figure()