/*
 *  buildGraph.c
 *
 *  Created by Bernard Carré
 *
 *  Squelette de code C de la fonction buildGraph.
 *  Ce code ne fait que lire les données d'un fichier au format DIMACS et les reafficher.
 *  Inscruster les lignes de code necessaires pour construire votre SD a partir des donnees ainsi obtenues.
 *
 *  Avec un main de test : fournir un fichier DIMACS en parametre.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "procedures.h"
#define MAX_LINE_SIZE 256

struct graphe* buildGraph(char *file_name) {

 char ligne[MAX_LINE_SIZE]; // pour le passage de ligne
 int n_nodes; // nombre de sommets
 int m_arcs; // nombre d'arcs
 int source; // numero de la saource
 int puits; // numero du puits

 // Ouverture du fichier si possible sinon exit on error
 FILE * fp = fopen(file_name,"r");
 if (fp==NULL) {
     fprintf(stderr, "%s non accessible\n", file_name);
     exit(1);
 }

 // Lecture du fichier
 // c Pb de ﬂot max : ligne de commentaire, on passe ...
 fgets(ligne,MAX_LINE_SIZE,fp);

 //c pb lines (nodes, links) : ligne de commentaire, on passe ...
 fgets(ligne,MAX_LINE_SIZE,fp);

 //p NODES ARCS
 getc(fp);getc(fp); //on passe l'entete 'p '
 // nombre de sommets
 fscanf(fp,"%d",&n_nodes);
 // nombre d'arcs
 fscanf(fp,"%d",&m_arcs);

 struct graphe* g = malloc(sizeof(struct graphe));
    g->taille = n_nodes;
    g->tableau = calloc(n_nodes, sizeof(struct sommet));
 // terminer le traitement de cette ligne :
 fgets(ligne,MAX_LINE_SIZE,fp);

 //c source : ligne de commentaire, on passe ...
 fgets(ligne,MAX_LINE_SIZE,fp);
 //n ID s : determine la source
 getc(fp);getc(fp); //on passe l'entete 'n '
 fscanf(fp,"%d", &source);
g->source=source;


 // terminer le traitement de cette ligne :
 fgets(ligne,MAX_LINE_SIZE,fp);

 //c sink : ligne de commentaire, on passe ...
 fgets(ligne,MAX_LINE_SIZE,fp);
 //n ID t : determine le puits
 getc(fp);getc(fp); //n
 fscanf(fp,"%d", &puits);
 g->puit=puits;
 // terminer le traitement de cette ligne :
 fgets(ligne,MAX_LINE_SIZE,fp);

 //c arc (from, to, capa) : ligne de commentaire, on passe ...
 fgets(ligne,MAX_LINE_SIZE,fp);

 //lire les m_arcs lignes au format "a SRC DST CAP" de DIMACS pour obtenir les donnees d'arcs
 {
     int a; // pour iterer sur les arcs
     int src, dst, cap; // donnees correspondantes (SRC DST CAP)

     for(a=1;a<=m_arcs;a++) {
         struct arc* arc1 = malloc(sizeof(struct arc));
         getc(fp);getc(fp); //on passe l'entete 'a '
         fscanf(fp,"%d",&src);
         fscanf(fp,"%d",&dst);
         fscanf(fp,"%d",&cap);
         arc1->dest=dst;
         arc1->val=0;
         arc1->capacité=cap;
         arc1->suivant = g->tableau[src-1].successeur;
            g->tableau[src-1].successeur = arc1;
     }
 }

 fclose(fp);
 return g;
}
