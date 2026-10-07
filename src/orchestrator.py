import clingo
from src.encoder import generate_random_affine_system

def las_vegas_sampling_orchestrator(base_program_str, atoms, m, max_restarts=1000):
    """
    Orchestrates the Las Vegas restart loop with Python-driven constraint injection.
    """
    print(f"[*] Pre-screening base program feasibility...")
    base_ctl = clingo.Control()
    base_ctl.add("base", [], base_program_str)
    base_ctl.ground([("base", [])])
    
    base_result = base_ctl.solve()
    if not base_result.satisfiable:
        print("[-] Base program is UNSAT. No solution space to partition.")
        return None
    print("[+] Base program verified SAT. Initiating restart loop...")

    # Las Vegas Restart Loop (Theorem 3)
    for trial in range(1, max_restarts + 1):
        # 1. Sample fresh random affine constraints (A, b)
        random_constraints = generate_random_affine_system(atoms, m)
        
        # 2. Construct extended program
        extended_program = base_program_str + "\n" + random_constraints

        print(extended_program)
        
        # 3. Execute Clingo on the randomized configuration
        ctl = clingo.Control(["--opt-mode=opt"])
        ctl.add("base", [], extended_program)
        ctl.ground([("base", [])])
        
        surviving_models = []
        result = ctl.solve(on_model=lambda model: surviving_models.append(
            [str(atom) for atom in model.symbols(atoms=True) if str(atom) in atoms]
        ))
        
        if result.satisfiable and surviving_models:
            print(f"[+] Success on trial {trial}! Isolated {len(surviving_models)} model(s).")
            return surviving_models[0] # Return the uniquely isolated sample
            
    print(f"[-] Reached max restarts ({max_restarts}) without finding a surviving model.")
    return None