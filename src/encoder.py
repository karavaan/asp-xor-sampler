import random

def compile_xor_constraint(active_atoms, b_j, constraint_id):
    """
    Compiles a single high-arity affine XOR constraint into linear ASP rules 
    using auxiliary atoms, avoiding exponential grounding overhead (O(|K|)).
    """
    rules = []
    k_len = len(active_atoms)
    
    if k_len < 2:
        raise ValueError("Parity constraint must involve at least 2 active atoms.")
    
    # Base case: |K| == 2
    if k_len == 2:
        y, z = active_atoms[0], active_atoms[1]
        if b_j == 0:
            # Rule out (1,0) and (0,1)
            rules.append(f":- {y}, not {z}.")
            rules.append(f":- {z}, not {y}.")
        else:
            # Rule out (1,1) and (0,0)
            rules.append(f":- {y}, {z}.")
            rules.append(f":- not {y}, not {z}.")
        return "\n".join(rules)
    
    # Inductive / Chain case: |K| >= 3
    # Introduce auxiliary atoms p_2, ..., p_{|K|-1}
    aux_atoms = [f"p_{constraint_id}_{r}" for r in range(2, k_len)]
    
    # 1. Base relation for p_2 = k_1 \oplus k_2
    y, z = active_atoms[0], active_atoms[1]
    p2 = aux_atoms[0]
    rules.append(f"{p2} :- {y}, not {z}.")
    rules.append(f"{p2} :- {z}, not {y}.")
    
    # 2. Recursive steps for intermediate auxiliary atoms
    for r in range(3, k_len):
        prev_p = aux_atoms[r - 3]
        curr_p = aux_atoms[r - 2]
        k_curr = active_atoms[r - 1]
        
        rules.append(f"{curr_p} :- {prev_p}, not {k_curr}.")
        rules.append(f"{curr_p} :- {k_curr}, not {prev_p}.")
        
    # 3. Terminal condition against the final atom and target bit b_j
    p_last = aux_atoms[-1]
    k_last = active_atoms[-1]
    
    if b_j == 0:
        rules.append(f":- {p_last}, not {k_last}.")
        rules.append(f":- {k_last}, not {p_last}.")
    else:
        rules.append(f":- {p_last}, {k_last}.")
        rules.append(f":- not {p_last}, not {k_last}.")
        
    return "\n".join(rules)

def generate_random_affine_system(atoms, m, max_arity=5):
    """
    Samples a random affine constraint system (A, b) of dimension m.
    """
    constraint_block = []
    for j in range(m):
        # Select a random subset of active atoms for this row
        arity = random.randint(2, min(max_arity, len(atoms)))
        active_subset = random.sample(atoms, arity)
        b_j = random.choice([0, 1])
        
        # Compile row into linear auxiliary rules
        row_rules = compile_xor_constraint(active_subset, b_j, constraint_id=j)
        constraint_block.append(row_rules)
        
    return "\n".join(constraint_block)