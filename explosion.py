import itertools
import time
import matplotlib.pyplot as plt
from clingo.control import Control

def test_direct_encoding_explosion(k_values, target_b=1):
    print("==========================================================")
    print(" START EXPERIMENT 1: NAIVE DIRECT PARITY O(2^k)")
    print("==========================================================\n")
    
    times = []
    for k in k_values:
        print(f"--- Naive Test voor k = {k} actieve atomen ---")
        
        atoms = [f"v{i}" for i in range(1, k + 1)]
        rules = [f"{{ {'; '.join(atoms)} }}."] 
        
        for assignment in itertools.product([0, 1], repeat=k):
            if sum(assignment) % 2 != target_b:
                conditions = [atoms[i] if val == 1 else f"not {atoms[i]}" 
                              for i, val in enumerate(assignment)]
                rules.append(f":- {', '.join(conditions)}.")
        
        asp_program = "\n".join(rules)
        rule_count = len(rules) - 1
        print(f"Aantal gegenereerde rules: {rule_count}")
        
        ctl = Control(["0"])
        start_add = time.time()
        ctl.add("base", [], asp_program)
        add_time = time.time() - start_add
        
        start_ground = time.time()
        ctl.ground([("base", [])])
        ground_time = time.time() - start_ground
        
        total_time = add_time + ground_time
        print(f"Totale vertraging    : {total_time:.4f} seconden\n")
        times.append(total_time)
        
    return times


def test_linear_encoding(k_values, target_b=1):
    print("==========================================================")
    print(" START EXPERIMENT 2: LINEAR AUXILIARY DECOMPOSITION O(k)")
    print("==========================================================\n")
    
    times = []
    for k in k_values:
        print(f"--- Lineaire Test voor k = {k} actieve atomen ---")
        
        atoms = [f"v{i}" for i in range(1, k + 1)]
        rules = [f"{{ {'; '.join(atoms)} }}."] 
        
        if k >= 2:
            rules.append("q_2 :- v1, not v2.")
            rules.append("q_2 :- v2, not v1.")
            
            for i in range(3, k):
                rules.append(f"q_{i} :- q_{i-1}, not v{i}.")
                rules.append(f"q_{i} :- v{i}, not q_{i-1}.")
            
            rules.append(f":- q_{k-1}, v{k}.")
            rules.append(f":- not q_{k-1}, not v{k}.")
        
        asp_program = "\n".join(rules)
        rule_count = len(rules) - 1
        print(f"Aantal gegenereerde rules: {rule_count}")
        
        ctl = Control(["0"])
        start_add = time.time()
        ctl.add("base", [], asp_program)
        add_time = time.time() - start_add
        
        start_ground = time.time()
        ctl.ground([("base", [])])
        ground_time = time.time() - start_ground
        
        total_time = add_time + ground_time
        print(f"Totale vertraging    : {total_time:.4f} seconden\n")
        times.append(total_time)
        
    return times


if __name__ == "__main__":
    k_values = [5, 10, 15, 18, 20, 21, 22]
    
    time_naive = test_direct_encoding_explosion(k_values)
    time_lineair = test_linear_encoding(k_values)
    
    # 2. Genereer de publicatie-klare grafiek
    print("Data verzameld. Grafiek wordt nu gegenereerd...")
    
    plt.figure(figsize=(8, 5))
    plt.plot(k_values, time_naive, marker='o', color='red', linewidth=2, label='Naive Direct Parity $\mathcal{O}(2^k)$')
    plt.plot(k_values, time_lineair, marker='s', color='blue', linewidth=2, label='Auxiliary Linear Decomposition $\mathcal{O}(k)$')

    plt.yscale('log')
    plt.xticks(k_values)
    plt.xlabel('Number of atoms in parity constraint ($k$)', fontsize=12)
    plt.ylabel('Grounding & Parsing Time (seconds) [Log Scale]', fontsize=12)
    plt.title('Combinatorial Explosion: Direct vs Linear Decomposition', fontsize=14, pad=15)

    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.legend(fontsize=11)

    plt.tight_layout()
    plt.savefig('explosion_graph.png', dpi=300)
    print("Done!")