import time
import csv
import collections
import clingo
import numpy as np
from src.encoder import generate_random_affine_system

def run_las_vegas_trial(base_program_str, atoms, m, max_restarts=500):
    """
    Executes a Las Vegas sampling loop until a model is found or max_restarts is reached.
    Returns the found model, the number of restarts used, and elapsed time.
    """
    start_time = time.time()
    
    for trial in range(1, max_restarts + 1):
        random_constraints = generate_random_affine_system(atoms, m)
        extended_program = base_program_str + "\n" + random_constraints
        
        ctl = clingo.Control(["--opt-mode=opt"])
        ctl.add("base", [], extended_program)
        ctl.ground([("base", [])])
        
        surviving_models = []
        result = ctl.solve(on_model=lambda model: surviving_models.append(
            tuple(sorted([str(atom) for atom in model.symbols(atoms=True) if str(atom) in atoms]))
        ))
        
        if result.satisfiable and surviving_models:
            elapsed_time = time.time() - start_time
            return surviving_models[0], trial, elapsed_time
            
    return None, max_restarts, time.time() - start_time

def run_unified_evaluation():
    base_program = """
        node(1..10).
        { chosen(X) : node(X) }.
        :- chosen(X), chosen(Y), Y == X + 1.
    """
    vocabulary_atoms = [f"chosen({i})" for i in range(1, 11)]
    
    m_values = [2, 4, 6, 8, 10, 12]
    num_samples_per_m = 1000  # Number of successful models to collect per m
    total_possible_models = 144
    results_file = "results/unified_evaluation_data.csv"
    
    print("[*] Starting unified empirical evaluation (Efficiency + Uniformity)...")
    
    all_results = []
    
    for m in m_values:
        print(f"\n--- Evaluating for m = {m} ---")
        restarts_list = []
        models_list = []
        
        while len(models_list) < num_samples_per_m:
            model, restarts, duration = run_las_vegas_trial(base_program, vocabulary_atoms, m)
            
            if model is not None:
                restarts_list.append(restarts)
                models_list.append(model)
                if len(models_list) % 20 == 0:
                    print(f"    Collected {len(models_list)}/{num_samples_per_m} samples...")

        # --- Calculate Efficiency Metrics ---
        mean_restarts = np.mean(restarts_list)
        std_restarts = np.std(restarts_list)
        
        # --- Calculate Uniformity Metrics ---
        unique_models = len(set(models_list))
        coverage_pct = (unique_models / total_possible_models) * 100
        
        # Calculate Coefficient of Variation (CV) across ALL 144 possible models
        counter = collections.Counter(models_list)
        counts = list(counter.values())
        # Pad with 0s for models that were never found (to penalize poor coverage)
        counts.extend([0] * (total_possible_models - unique_models))
        
        cv = np.std(counts) / np.mean(counts) if np.mean(counts) > 0 else 0
        
        all_results.append({
            "m": m,
            "mean_trials": round(mean_restarts, 2),
            "std_trials": round(std_restarts, 2),
            "coverage_pct": round(coverage_pct, 2),
            "uniformity_cv": round(cv, 4)
        })
        
        print(f"[+] m={m} -> Mean Restarts: {mean_restarts:.2f}, Coverage: {coverage_pct:.1f}%, CV: {cv:.4f}")

    # Save to unified CSV
    with open(results_file, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["m", "mean_trials", "std_trials", "coverage_pct", "uniformity_cv"])
        writer.writeheader()
        writer.writerows(all_results)
        
    print(f"\n[+] Unified evaluation complete! Data saved to {results_file}")

if __name__ == "__main__":
    run_unified_evaluation()