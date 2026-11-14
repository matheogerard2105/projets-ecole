#if ! defined (PROCEDURES_H)
#define PROCEDURES_H
struct arc {
    int dest; // destination de l’arc
    int val; //flot (réseau) ou capacité résiduelle (graphe d’écart)
    int capacité; //capacité maximale de l’arc
    struct arc* suivant; //arc vers le successeur suivant
};
struct sommet {
    int nom; // numéro du sommet (commence par 1)
    struct arc * successeur; //liste des successeurs du sommet
};
struct graphe {
    int taille; // nombre de sommet du graphe
    int source; // numéro du sommet source du graphe
    int puit; // numéro du sommet puit du graphe
    struct sommet *tableau; //tableau des sommets
};

/**********************************************************************
 * PROTOTYPES DES FONCTIONS (TYPE ABSTRAIT)
 **********************************************************************/

/**********************************************************************/
/* Fonction buildGraph : retour d'une structure graphe                */
/* Construit votre SD à partir d'un fichier au format DIMACS          */
/**********************************************************************/
extern struct graphe * buildGraph ();

/**********************************************************************/
/* Fonction buildRG : retour d'une structure graphe                   */
/* Construit le graphe d’écart à partir d'un réseau et d'un flot nul  */
/*  R : struct graphe * - Réseau - Donnee                             */
/*  d : int - nombre de sommet du réseau - Donnee                     */
/**********************************************************************/
extern struct graphe* buildRG (struct graphe *R, int d);

/**********************************************************************/
/* Fonction shortestPath : retour d'un tableau d'entier               */
/* Détermine le plus court chemin en nombre d'arc permettant d'aller  */
/* de s à p à partir d'un graphe d'écart                              */
/*  E : struct graphe * - Graphe d'écart - Donnee                     */
/*  s : int - Numéro du sommet source - Donnee                        */
/*  p : int - Numéro du sommet puit - Donnee                          */
/**********************************************************************/
extern int* shortestPath (struct graphe *E,int s, int p);

/**********************************************************************/
/* Fonction mincCapa : retour d'un entier                             */
/* Détermine l'arc de plus petite capacité d'un chemin et renvoie     */
/* cette dernière                                                     */
/*  E : struct graphe * - Graphe d'écart - Donnée                     */
/*  parent : Tableau d'int - Chemin - Donnée                   */
/**********************************************************************/
extern int minCapa(struct graphe* E, int* parent);

/***************************************************************/
/* Action updateFlowInRG                                       */
/* Met à jour le graphe d'écart à partir d'un chemin et d'une  */
/* augmentation de flot                                        */
/*  E : struct graphe * - Graphe d'écart - Donnee/Résultat     */
/*  parent : Tableau d'int - Chemin - Donnée                   */
/*  k : int - augmentation du flot - Donnée                    */
/***************************************************************/
extern void updateFlowInRG(struct graphe* E, int* parent, int k);

/***************************************************************/
/* Action updateFlowInNet                                      */
/* Met à jour le flot dans le réseau et donc les flux courant  */
/* de chacun des arcs à partir du graphe d'écart               */
/*  R : struct graphe * - Réseau         - Résultat            */
/*  E : struct graphe * - Graphe d'écart - Donnee              */
/*  parent : Tableau d'int - Chemin - Donnée                   */
/*  k : int - augmentation du flot - Donnée                    */
/***************************************************************/
extern void updateFlowInNet(struct graphe* R, struct graphe *E, int* parent, int k);

#endif
