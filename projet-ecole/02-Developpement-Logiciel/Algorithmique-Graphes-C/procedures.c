#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "procedures.h"
#include <limits.h>  // pour INT_MAX
struct graphe* buildRG (struct graphe*R,int d){
    int i;
    //Initialisation du graphe d'écart
    struct graphe* E = malloc(sizeof(struct graphe));
    E->taille = d;
    E->tableau = calloc(d, sizeof(struct sommet));
    E->source=R->source;
    E->puit=R->puit;
    for (i=0;i<d;i++){
        struct arc *actuel=R->tableau[i].successeur; // se place dans la bonne liste de successeur
        while (actuel){
                //Création de l'arc dans le sens du réseau
                struct arc *arc1=malloc(sizeof(struct arc));
                arc1->dest=actuel->dest;
                arc1->val=(actuel->capacité)-(actuel->val); // On rappelle que arc1->val correspond à la capacité résiduelle alors que actuel->val correspond au flot
                arc1->capacité=actuel->capacité;
                arc1->suivant = E->tableau[i].successeur;
                E->tableau[i].successeur = arc1;
                //Création de l'arc dans le sens inverse du réseau
                struct arc *arc2=malloc(sizeof(struct arc));
                arc2->dest=i+1;
                arc2->val=actuel->val;
                arc2->capacité=actuel->capacité;
                arc2->suivant = E->tableau[actuel->dest -1].successeur;
                E->tableau[actuel->dest -1].successeur = arc2;
            actuel=actuel->suivant; //passage au successeur suivant
        }
    }
    return E;
}
int* shortestPath(struct graphe* E, int s, int p) {
    int n = E->taille;
    int* parent = malloc(n * sizeof(int)); // Tableaux des parents
    bool* visite = calloc(n, sizeof(bool)); // Sommé visité ou non
    int* file = malloc(n * sizeof(int)); // File d'exploration en largeur
    int debut = 0, fin = 0;
    for (int i = 0; i < n; i++) {
        parent[i] = -1; // aucun parent connu
    }
    // Parcours d'exploration en largeur'
    file[fin++] = s-1;
    visite[s-1] = true;
    bool chemintrouve = false;
    while (debut < fin && !chemintrouve) {
        int sommetActuel = file[debut++];
        struct arc* actuel = E->tableau[sommetActuel].successeur;
        while (actuel != NULL) {
            int voisin = actuel->dest - 1;
            // Si le sommet voisin n'a pas encore été visité et que la capacité résiduelle > 0
            if (!visite[voisin] && actuel->val > 0) {
                visite[voisin] = true;
                parent[voisin] = sommetActuel;
                file[fin++] = voisin;
                // Si on a atteint p, on peut s’arrêter
                if (voisin == p-1) {
                    chemintrouve = true;
                    break;
                }
            }
            actuel = actuel->suivant;
        }
    }
    // Libération de la mémoire temporaire
    free(file);
    free(visite);
    // Si aucun chemin trouvé, libérer aussi le tableau parent
    if (!chemintrouve) {
        free(parent);
        return NULL;
    }
    // Retourne le tableau des parents (chemin)
    return parent;
}
int minCapa(struct graphe* E, int* parent) {
    int min = INT_MAX;
    int sommet = E->puit - 1;
    while (sommet != E->source - 1) {
        int parentSommet = parent[sommet];
        struct arc* arcCourant = E->tableau[parentSommet].successeur;
        // Recherche de l'arc
        while (arcCourant && arcCourant->dest != sommet + 1) {
            arcCourant = arcCourant->suivant;
        }
        if (!arcCourant) {
            fprintf(stderr, "Erreur : arc (%d → %d) introuvable dans minCapa\n", parentSommet + 1, sommet + 1);
            exit(EXIT_FAILURE);
        }
        if (arcCourant->val < min) {
            min = arcCourant->val;
        }
        sommet = parentSommet;
    }
    return min;
}
void updateFlowInRG(struct graphe* E, int* parent, int k) {
    int sommet = E->puit - 1;
    while (sommet != E->source - 1) {
        int parentSommet = parent[sommet];
        // Réduction de la capacité résiduelle dans le sens direct
        struct arc* arcDirect = E->tableau[parentSommet].successeur;
        while (arcDirect && arcDirect->dest != sommet + 1) {
            arcDirect = arcDirect->suivant;
        }
        if (arcDirect) {
            arcDirect->val -= k;
        }
        // Augmentation de la capacité résiduelle dans le sens inverse
        struct arc* arcInverse = E->tableau[sommet].successeur;
        while (arcInverse && arcInverse->dest != parentSommet + 1) {
            arcInverse = arcInverse->suivant;
        }
        if (arcInverse) {
            arcInverse->capacité += k;
        }
        sommet = parentSommet;
    }
}
void updateFlowInNet(struct graphe* R, struct graphe* E, int* parent, int k) {
    int sommet = R->puit - 1;
    while (sommet != R->source - 1) {
        int parentSommet = parent[sommet];
        // Recherche de l'arc direct
        struct arc* arcDirect = R->tableau[parentSommet].successeur;
        while (arcDirect && arcDirect->dest != sommet + 1) {
            arcDirect = arcDirect->suivant;
        }
        if (arcDirect) {
            arcDirect->val += k; // Augemantation du flux dans le bon sens
        } else {
            // Si l'arc direct n'existe pas, réduction du flux dans l'arc retour
            struct arc* arcInverse = R->tableau[sommet].successeur;
            while (arcInverse && arcInverse->dest != parentSommet + 1) {
                arcInverse = arcInverse->suivant;
            }
            if (arcInverse) {
                arcInverse->val -= k;
            }
            else {
                fprintf(stderr, "Erreur : arc (%d ↔ %d) introuvable dans le réseau\n", parentSommet + 1, sommet + 1);
                exit(EXIT_FAILURE);
            }
        }
        sommet = parentSommet;
    }
}
