#include <stdio.h>
#include <stdlib.h>
#include "procedures.h"

int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage : %s <fichier_DIMACS> <fichier_sortie>\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    char* fichier_entree = argv[1];
    char* fichier_sortie = argv[2];
    struct graphe* R = buildGraph(fichier_entree);
    int max_flow = 0;
    while (1) {
        struct graphe* E = buildRG(R, R->taille);
        int* parent = shortestPath(E, R->source, R->puit);
        if (!parent) {
            // Plus de chemin → flot maximum atteint
            free(E);
            break;
        }
        int k = minCapa(E, parent);
        updateFlowInRG(E, parent, k);
        updateFlowInNet(R, E, parent, k);
        max_flow += k;
        free(parent);
        free(E); // Libération simplifiée, à étendre si gestion mémoire complète
    }
    // Écriture du résultat dans un fichier texte
    FILE* out = fopen(fichier_sortie, "w");
    if (!out) {
        perror("Erreur ouverture fichier sortie");
        exit(EXIT_FAILURE);
    }
    fprintf(out, "Flot maximum : %d\n", max_flow);
    fprintf(out, "Flux courant de chaque arc :\n");
    for (int i = 0; i < R->taille; i++) {
        struct arc* a = R->tableau[i].successeur;
        while (a) {
            fprintf(out, "Arc de %d à %d : %d / %d\n", i + 1, a->dest, a->val, a->capacité);
            a = a->suivant;
        }
    }
    fclose(out);
    printf("Résultat écrit dans %s\n", fichier_sortie);
    return 0;
}
