import numpy as np
import urllib.parse
import matplotlib.pyplot as plt
import time

def scan_with_add(arr):
    """ Opération de scan pour la normalisation robuste du vecteur v. """
    return np.cumsum(arr)

def load_wikispeedia_numpy(articles_file, paths_file):
    """ Charge et purifie le graphe pour ne garder que les articles actifs. """
    active_articles = set()
    with open(paths_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip(): continue
            parts = line.split('\t')
            path_elements = parts[3].split(';')
            for item in path_elements:
                if item != '<': active_articles.add(item)

    articles = []
    with open(articles_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip(): continue
            name = line.strip()
            if name in active_articles: articles.append(name)
    
    name_to_id = {name: i for i, name in enumerate(articles)}
    n = len(articles)
    A = np.zeros((n, n), dtype=np.int8)
    
    with open(paths_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip(): continue
            parts = line.split('\t')
            path_elements = parts[3].split(';')
            stack = []
            for item in path_elements:
                if item == '<':
                    if stack: stack.pop()
                else:
                    if stack:
                        u_name, v_name = stack[-1], item
                        if u_name in name_to_id and v_name in name_to_id:
                            A[name_to_id[u_name], name_to_id[v_name]] = 1
                    stack.append(item)
    return articles, A, n

def compute_pagerank_numpy(A, n, beta=0.85, epsilon=1e-6, max_iter=200, dtype=np.float64, personalization=None):
    """
    Calcule le PageRank. 
    q0 est initialisé sur v si personalization est présent.
    """
    # 1. Vecteur v (Téléportation)
    if personalization is not None:
        v = np.zeros(n, dtype=dtype)
        for node_id, weight in personalization.items():
            v[node_id] = weight
        total_sum = scan_with_add(v)[-1] 
        v = np.divide(v, total_sum)
        # INITIALISATION q0 = v (Consigne TP Petiton)
        r = np.copy(v)
    else:
        v = np.divide(np.ones(n, dtype=dtype), n)
        r = np.divide(np.ones(n, dtype=dtype), n)

    # 2. Matrice de transition P
    d_out = A.sum(axis=1)
    P = np.zeros((n, n), dtype=dtype)
    mask = np.greater(d_out, 0)
    P[mask] = np.divide(A[mask].astype(dtype), d_out[mask][:, np.newaxis])
    P_T = np.transpose(P)

    start_time = time.time()
    for i in range(max_iter):
        dangling_mass = np.sum(r[np.equal(d_out, 0)])
        
        # Formule matricielle complète
        r_next = np.multiply(beta, np.dot(P_T, r))
        r_next = np.add(r_next, np.multiply(beta, np.multiply(dangling_mass, v)))
        r_next = np.add(r_next, np.multiply(np.subtract(1.0, beta), v))

        error = np.linalg.norm(np.subtract(r_next, r), ord=1)
        if error < epsilon:
            return r_next, np.add(i, 1), np.subtract(time.time(), start_time), error
        r = r_next

    return r, max_iter, np.subtract(time.time(), start_time), error

def display_top(articles, scores, error, title="Top Articles", top_n=10):
    print(f"\n{title} (Erreur: {error:.2e})")
    indices = np.argsort(scores)[::-1]
    for i in range(min(top_n, len(indices))):
        idx = indices[i]
        name = urllib.parse.unquote(articles[idx])
        print(f"Rang {i+1:2d}: {name:30} Score: {scores[idx]:.6f}")
    return indices # On retourne les indices pour sélection ultérieure

def plot_performance_analysis(A, n):
    betas = [0.1, 0.5, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98]
    res64 = {"iters": [], "times": []}
    res32 = {"iters": [], "times": []}

    for b in betas:
        _, it64, t64, _ = compute_pagerank_numpy(A, n, beta=b, dtype=np.float64)
        res64["iters"].append(it64); res64["times"].append(t64)
        
        _, it32, t32, _ = compute_pagerank_numpy(A, n, beta=b, dtype=np.float32)
        res32["iters"].append(it32); res32["times"].append(t32)

    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    plt.plot(betas, res64["times"], 'o-', label='64-bit', color='blue')
    plt.plot(betas, res32["times"], 's--', label='32-bit', color='red')
    plt.title('Beta vs Temps de calcul'); plt.legend(); plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.plot(betas, res64["iters"], 'o-', label='64-bit', color='blue')
    plt.plot(betas, res32["iters"], 's--', label='32-bit', color='red')
    plt.title('Beta vs Itérations'); plt.legend(); plt.grid(True, alpha=0.3)
    plt.savefig('analyse_performance_pagerank.png')
    
    
if __name__ == "__main__":
    articles, A, n = load_wikispeedia_numpy('articles.tsv', 'paths_finished.tsv')
    print(f"Graphe purifié : {n} articles actifs.")

    # 1. PageRank Global (Base)
    print("\n--- ÉTAPE 1 : PageRank Global ---")
    scores_glob, it_glob, t_glob, err_glob = compute_pagerank_numpy(A, n, beta=0.85)
    sorted_indices = display_top(articles, scores_glob, err_glob, top_n=51)

    # 2. Sélection automatique des nœuds pour le PPR (Consigne 4)
    # Rang 5 à 10 (on prend le 7ème par ex) et Rang 20 à 50 (on prend le 35ème)
    idx_5_10 = sorted_indices[6]  # Index 6 = 7ème place
    idx_20_50 = sorted_indices[34] # Index 34 = 35ème place
    
    targets = [articles[idx_5_10], articles[idx_20_50]]

    # 3. Lancement des PPR
    print("\n--- ÉTAPE 2 : PageRank Personnalisé (PPR) ---")
    for target_name in targets:
        tid = articles.index(target_name)
        print(f"\n>>> Lancement PPR focus sur : {target_name}")
        # q0 est ici initialisé sur le noeud cible dans compute_pagerank_numpy
        s_ppr, it_p, t_p, err_p = compute_pagerank_numpy(A, n, personalization={tid: 1.0})
        display_top(articles, s_ppr, err_p, title=f"Résultats PPR {target_name}", top_n=10)

    # 4. Génération des courbes pour le rapport
    print("\n--- ÉTAPE 3 : Génération des courbes de performance ---")
    plot_performance_analysis(A, n)
