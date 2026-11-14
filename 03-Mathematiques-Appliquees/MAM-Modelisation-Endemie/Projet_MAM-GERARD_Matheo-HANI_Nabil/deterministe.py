import numpy as np
import matplotlib.pyplot as plt
import math
import statistics as stats
import tkinter as tk
from tkinter import messagebox
import random 
from datetime import date, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
from matplotlib import cm # Importation pour les schémas de couleurs

# ==============================================================================
# --- PARTIE 1 : MODÈLE MARKOVIEN (STOCHASTIQUE) - CHAÎNE DE MARKOV ---
# ==============================================================================

class MarkovEndemicModel:
    """
    Classe utilisée principalement pour encapsuler les constantes A et N0.
    """
    def __init__(self, N, I0, p):
        self.N = N
        self.I0 = I0
        self.p = p
        self.q = 1 - p
        self.A = self._calculate_A()
        self.N0 = self._calculate_N0()

    def _calculate_A(self):
        """Calcule la constante A du modèle déterministe (A = -N * ln(q))."""
        if self.q <= 0 or self.q >= 1:
            return float('inf')
        return self.N * math.log(1 / self.q)

    def _calculate_N0(self):
        """Calcule la taille critique N0 (N0 = 1 / -ln(q))."""
        if self.q <= 0 or self.q >= 1:
            return float('inf')
        return 1 / math.log(1 / self.q)

def simulate_markov_step(I_n, N, q):
    """Simule un pas de temps de la Chaîne de Markov (CM) stochastique."""
    i = I_n
    if i == 0:
        return 0

    N_sains = N - i
    p_succes = 1 - (q ** i)
    I_next = np.random.binomial(n=N_sains, p=p_succes, size=1)[0]
    return I_next

def run_markov_simulation(N, I0, p, steps):
    """Exécute la simulation stochastique."""
    q = 1 - p
    I_history = [I0]
    current_I = I0
    
    for _ in range(steps):
        current_I = simulate_markov_step(current_I, N, q)
        I_history.append(current_I)
        if current_I == 0 and I_history[-2] == 0:
             break
    return I_history

# ==============================================================================
# --- PARTIE 2 : MODÈLE DÉTERMINISTE ---
# ==============================================================================

def calculate_A(N, p):
    """Calcule la constante A. A = N * ln(1/q)."""
    q = 1 - p
    if q <= 0 or q >= 1:
        return float('inf')
    return N * math.log(1 / q)

def calculate_deterministic_I(I_n, N, q):
    """Calcule I_{n+1} à partir de I_n pour un pas de temps déterministe."""
    i = I_n
    I_next = (N - i) * (1 - (q ** i))
    return int(round(I_next)) 

def run_deterministic_simulation(N, I0, p, steps):
    """Exécute la simulation déterministe."""
    q = 1 - p
    I_history = [I0]
    current_I = I0
    
    for _ in range(steps):
        current_I = calculate_deterministic_I(current_I, N, q)
        I_history.append(current_I)
    return I_history

# --- 3. FONCTION DE VISUALISATION ET DE COMPARAISON ---

def display_reasoning(N, p, I0, A, N0, comparison_label):
    """Affiche le raisonnement dans la console, avec plus d'explications du cours."""
    print("\n" + "="*80)
    print("ANALYSE DÉTAILLÉE DES RÉSULTATS (Modèles MAM et Déterministe)")
    print("="*80)
    print(f"Paramètres : N={N}, I₀={I0} (Généré), Taux de Contact p={p}")

    # Raisonnement Déterministe (Potentiel d'endémie)
    print("\n[I] ANALYSE DU POTENTIEL D'ENDÉMIE (Modèle Déterministe - Basé sur l'Espérance)")
    print("-> Constante de Phase A: A ≈ {:.4f}".format(A))
    print(f"-> Taille Critique N₀: N₀ ≈ {N0:.2f}")

    if A > 1:
        equilibrium_level = N * (1 - 1/A)
        print(f"\n* RÉSULTAT THÉORIQUE (A > 1) : Régime Endémique Potentiel")
        print(f"  * Niveau d'Équilibre Potentiel (I*) ≈ {equilibrium_level:.2f} personnes.")
        print("  * Justification : La condition A > 1 est remplie. Selon le Lemme du point fixe (Projet MAM, Page 2), la suite $x_n$ converge vers $x^* \in ]0, 1/2[$. Cela définit l'équilibre déterministe.")
        print("  * Interprétation : Bien que le potentiel existe (Endémie), cet équilibre est **métastable** en stochastique.")
    else:
        print(f"\n* RÉSULTAT THÉORIQUE (A ≤ 1) : Extinction Déterministe")
        print("  * Justification : Selon le Lemme du point fixe, la suite $x_n$ converge vers 0. La force d'infection moyenne est insuffisante.")
    
    # Raisonnement Stochastique (Analyse du résultat réel)
    print("\n[II] COMPORTEMENT STOCHASTIQUE (CHAÎNE DE MARKOV - Loi Binomiale)")
    print("-> Processus : La transition est régie par la Loi Binomiale, introduisant le 'bruit' stochastique.")
    print("-> Classes d'États : L'état $I=0$ est la seule **Classe Récurrente** accessible (MAM: Chapitre 2). Les états $I>0$ sont **Transients**.")
    print("-> Convergence : La convergence vers $I=0$ (Extinction) est **certaine** ($P(T < \infty) = 1$) dans ce modèle à espace d'états fini (MAM: Prop. 2.2.8).")
    print(f"Observation de la Simulation : {comparison_label}")


def plot_comparison(N, I0, p, markov_results, deterministic_results):
    """Trace les courbes des deux modèles pour comparaison."""
    
    steps_markov = len(markov_results) - 1
    steps_det = len(deterministic_results) - 1
    
    # Calcul des constantes pour le tracé
    model_ref = MarkovEndemicModel(N, I0, p)
    A = model_ref.A
    N0 = model_ref.N0

    plt.figure(figsize=(12, 7))

    # 1. Tracé de la simulation stochastique (Chaîne de Markov)
    plt.plot(np.arange(steps_markov + 1), markov_results, marker='o', linestyle='-', color='#17A589', alpha=0.9, label='1. Stochastique (Chaîne de Markov)')

    # 2. Tracé de la simulation déterministe
    plt.plot(np.arange(steps_det + 1), deterministic_results, linestyle='--', color='#E74C3C', linewidth=2.5, label='2. Déterministe ($E[I_n]$)')

    # 3. Ligne de référence de l'Équilibre/Extinction Déterministe (Projet MAM)
    if A > 1:
        equilibrium_level = N * (1 - 1/A)
        plt.axhline(y=equilibrium_level, color='#2C3E50', linestyle=':', label=f'Équilibre Potentiel $I^*$ (A ≈ {A:.2f})')
        comparison_label = f"A ≈ {A:.2f} (> 1) : Déterministe = Endémie Potentielle / Markovien = Extinction certaine (Métastabilité)"
    else:
        plt.axhline(y=0, color='red', linestyle=':', label=f'Extinction $I^*=0$ (A ≈ {A:.2f})')
        comparison_label = f"A ≈ {A:.2f} (≤ 1) : Les deux modèles convergent vers l'Extinction"


    plt.title(f'Comparaison des Modèles d\'Endémie (N={N}, I₀={I0}, p={p})')
    plt.suptitle(comparison_label, fontsize=10)
    plt.xlabel('Temps (Pas de temps n)')
    plt.ylabel('Nombre d\'Infectés ($I_n$)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.show()
    
    display_reasoning(N, p, I0, A, N0, comparison_label)

# --- NOUVELLE FONCTION : ANALYSE DE SENSIBILITÉ ---

def plot_p_sensitivity(N, I0, p_base, weeks=100):
    """
    Affiche l'évolution du modèle DÉTERMINISTE pour une plage de valeurs de p.
    Ceci illustre le Phénomène de Transition de Phase (A > 1).
    """
    
    # Plage de p pour montrer la transition (basse, moyenne, haute)
    p_values = [0.01, 0.02, 0.05, 0.08, 0.1]
    
    plt.figure(figsize=(12, 7))
    
    # Utilisation d'une carte de couleurs pour distinguer les courbes
    cmap = cm.get_cmap('tab10', len(p_values))
    
    # --- COMMENTAIRE D'ANALYSE DE SENSIBILITÉ ---
    print("\n" + "="*80)
    print("ANALYSE DE SENSIBILITÉ : IMPACT DU TAUX p SUR LA DYNAMIQUE DÉTERMINISTE")
    print("="*80)
    print("Chaque courbe montre la convergence de I_n pour un taux p différent (Modèle Déterministe).")
    print(f"La population est fixée à N={N} (Départ I₀={I0}).")
    
    if N > 1 / calculate_A(1, p_values[0]) and N > 0:
        print("\nObservation : La taille N est suffisante pour que l'ENDÉMIE soit possible.")
    else:
        print("\nObservation : La taille N est faible. L'extinction déterministe est probable pour la plupart des taux p.")
    
    print("\nRésultats :")
    
    # ----------------------------------------------------
    
    for idx, p_rate in enumerate(p_values):
        if p_rate <= 0 or p_rate >= 1: continue

        A = calculate_A(N, p_rate)
        results = run_deterministic_simulation(N, I0, p_rate, weeks)
        
        # Détermination de la couleur et du style de ligne
        color = cmap(idx)
        linestyle = '-' if A > 1 else ':' # Ligne pleine si endémique potentiel (A>1)

        label = f"p={p_rate:.4f} (A={A:.2f})"

        # Analyse du comportement pour la console
        if A > 1:
            equilibrium_level = N * (1 - 1/A)
            print(f"  * {label}: Endémique (A>1). Converge vers I* ≈ {equilibrium_level:.0f}.")
        else:
            print(f"  * {label}: Non-Endémique (A<=1). Converge vers 0.")

        # Tracé de la courbe
        plt.plot(np.arange(len(results)), results, linestyle=linestyle, color=color, label=label)

        # Marquer l'équilibre potentiel I*
        if A > 1:
            equilibrium_level = N * (1 - 1/A)
            plt.plot(weeks, equilibrium_level, marker='o', color=color, markersize=8)

    
    plt.axhline(y=0, color='black', linewidth=0.8)
    
    plt.title(f'Analyse de Sensibilité du Modèle DÉTERMINISTE (N={N}, I₀={I0})')
    plt.suptitle(f"Effet de p sur le Seuil d'Endémie A (A=1 est le seuil de transition)", fontsize=10)
    plt.xlabel('Temps (Pas de temps n)')
    plt.ylabel('Nombre d\'Infectés ($I_n$)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Taux p et Constante A")
    plt.show()

# --- 4. GESTION DES ENTRÉES UTILISATEUR ET EXÉCUTION (TKINTER GUI) ---

class EndemicGUI:
    """Crée l'interface graphique pour la saisie des paramètres."""
    def __init__(self, master):
        self.master = master
        master.title("Simulation de Modèle Markovien d'Endémie")

        # Variables de saisie (initialisées pour un exemple)
        self.N_var = tk.StringVar(master, value='50000') 
        self.p = 0.05
        
        # Configuration des widgets
        tk.Label(master, text="SIMULATEUR STOCHASTIQUE (MAM)", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        tk.Label(master, text="Taille de la Population N :").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.N_entry = tk.Entry(master, textvariable=self.N_var).grid(row=1, column=1, padx=10, pady=5)

        tk.Label(master, text="Infectés Initiaux I₀ :", font=("Helvetica", 10, "italic")).grid(row=2, column=0, padx=10, pady=5, sticky='w')
        tk.Label(master, text="(GÉNÉRÉ ALÉATOIREMENT)", font=("Helvetica", 10, "italic")).grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        tk.Label(master, text=f"Taux de Contact p (fixé) : {self.p}").grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        
        # Bouton Lancer Simulation Unique
        tk.Button(master, text="Lancer Simulation Stochastique (100 sem.)", command=self.run_simulation_from_gui, bg='#0077b6', fg='white').grid(row=4, column=0, columnspan=2, pady=10)
        
        # Bouton Lancer Analyse de Sensibilité
        tk.Button(master, text="Analyse Sensibilité (Variation de p)", command=self.run_sensitivity_analysis, bg='#2a9d8f', fg='white').grid(row=5, column=0, columnspan=2, pady=10)
        
    def run_simulation_from_gui(self):
        """Récupère les données de la GUI, génère I₀ aléatoirement et lance la simulation."""
        try:
            N = int(self.N_var.get())
            
            if N <= 0:
                 messagebox.showerror("Erreur de Saisie", "La population N doit être supérieure à 0.")
                 return
            
            # 1. Génération Aléatoire de I₀ 
            max_i0 = max(1, N // 5) 
            I0 = random.randint(1, max_i0 if max_i0 < N else N)
            
            print(f"\n--- Paramètres Générés : N = {N}, I₀ = {I0}, p = {self.p} ---")
            
            # Paramètres de simulation
            WEEKS = 100
            
            # 2. Simulations
            markov_results = run_markov_simulation(N, I0, self.p, WEEKS)
            deterministic_results = run_deterministic_simulation(N, I0, self.p, WEEKS)
            
            # 3. Affichage des résultats
            self.master.destroy() # Ferme la fenêtre de saisie
            plot_comparison(N, I0, self.p, markov_results, deterministic_results)

        except ValueError:
            messagebox.showerror("Erreur de Saisie", "Veuillez vous assurer que N est un nombre entier valide.")

    def run_sensitivity_analysis(self):
        """Lance l'analyse de sensibilité pour différentes valeurs de p."""
        try:
            N = int(self.N_var.get())
            
            if N <= 0:
                 messagebox.showerror("Erreur de Saisie", "La population N doit être supérieure à 0.")
                 return

            # Génération d'un I0 fixe pour la comparaison
            I0 = max(1, N // 100) # Petit I0 pour voir l'établissement de la dynamique
            
            self.master.destroy()
            plot_p_sensitivity(N, I0, self.p)

        except ValueError:
            messagebox.showerror("Erreur de Saisie", "Veuillez vous assurer que N est un nombre entier valide.")


def main():
    """Fonction principale pour initialiser la GUI."""
    root = tk.Tk()
    app = EndemicGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()