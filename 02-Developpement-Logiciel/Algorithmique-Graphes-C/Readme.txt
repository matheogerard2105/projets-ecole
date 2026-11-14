Notre projet contient 3 fichiers .c et un fichier.h. Pour compiler ces derniers, il suffit d’écrire la commande suivante dans le terminal en veillant à être dans le dossier envoyé  :

gcc -o main main.c procedures.c buildGraph.c

Ensuite, pour exécuter le programme, il faut écrire la commande suivante :

./main <nom du fichier test> <nom du fichier de sortie>

Par exemple, avec un fichier test existant “test1.txt” et un fichier de sortie (fichier écrasé si existant) “sortie1.txt”, il faut exécuter la commande :

./main test1.txt sortie1.txt

Attention ! Pour fonctionner, le programme a besoin d’un fichier test sous format DIMACS.

Les fichiers test du fichier sont :
test1.txt = R1
test2.txt = R2
test3.max = G 100 300
test4.txt = G 900 2700
text 5.max = G 2500 7500
