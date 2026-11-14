/* Declaration des variables globales */
var partiefinie = false;
let L=5;
let C=3;
let coup=-1;
let lastcolor;
let couleur2 = ["red", "blue", "green", "yellow", "brown", "black",
"white", "purple", "orange", "pink"];
let col=couleur2;
let couleur=[];
let currentColor = "red";

/* Declaration des variables HTML */
let zonecoup=document.getElementById("coup");
let grille=document.getElementById("grille");
let choixc=document.getElementById("choixc");
choixc.addEventListener("click",bouton2);
let palettediv=document.getElementById("palette");
let defi=document.getElementById("defi");
defi.addEventListener("click",fdefi)
let sel=document.getElementById("sel");
let choixLong = document.getElementById("taille");
let choixNbcolor = document.getElementById("nbcouleur");
let rejouer = document.getElementById("rejouer");
rejouer.addEventListener("click",reset);

/* Fonction creationcol : crée un tableau de 10 couleurs aléatoires */
function creationcol(){
     couleur=[];
     for (let j=0;j<10;j++){
        couleur.push("rgb("+Math.round((Math.random()*256)).toString()+","+Math.round((Math.random()*256)).toString()+","+Math.round((Math.random()*256)).toString()+")")
     }
}


/* Fonction bouton2 : permet de changer les couleurs de la grille lorsqu'on appuie sur*/
function bouton2(){
    partiefinie = false;
     if (this.class=="al"){
         this.class="cla";
         this.innerHTML="Couleurs aléatoires";
         col=couleur2;
         grille.innerHTML="";
         palettediv.innerHTML="";
         init_palette();
         init();
     }
     else {
         this.class="al";
         this.innerHTML="Couleurs classiques";
         col=couleur;
         grille.innerHTML="";
         palettediv.innerHTML="";
         creationcol();
         init_palette();
         init();
     }
}

/* Fonction fdefi : permet de changer le mode de jeu */
function fdefi(){
    partiefinie = false;
     if  (this.innerHTML=="Mode Defi"){
         this.innerHTML="Mode Chill";
         grille.innerHTML="";
         palettediv.innerHTML="";
         creationcol();
         init_palette();
         init();
     }
     else{
         this.innerHTML="Mode Defi";
         grille.innerHTML="";
         palettediv.innerHTML="";
         creationcol();
         init_palette();
         init();
     }
}


/* Fonction init_boutons : initialise les boutons de choix de longueur et de nombre de couleurs */
function init_boutons(){
     for (let i=5;i<51;i++){
         let optionL = document.createElement("option");
         optionL.value = i;
         optionL.class = "longueur_";
         optionL.id=i;
         optionL.textContent = i;
         choixLong.appendChild(optionL);
         optionL.addEventListener("click",longueur);
     }
     for (let i= 3;i<11;i++){
         let optionC = document.createElement("option");
         optionC.value = i;
         optionC.class= "couleur_";
         optionC.id=i;
         optionC.textContent = i;
         choixNbcolor.appendChild(optionC);
         optionC.addEventListener("click",coulor);
     }
}


/* Fonction longueur : permet de changer la longueur de la grille */
function longueur(){
     partiefinie = false;
     L=this.id;
     grille.innerHTML="";
     init();
}

/* Fonction coulor : permet de changer le nombre de couleurs */
function coulor(){
    partiefinie = false;
     C=this.id;
     grille.innerHTML="";
     palettediv.innerHTML=""
     creationcol();
     init_palette();
     init();
}

/* Fonction tirage : tire un nombre aléatoire entre 0 et n */
function tirage(n){
     return Math.floor(Math.random()*n);
}

/* Fonction init : initialise la grille de jeu */
function init(){
    sel.style.backgroundColor="white";
    sel.innerHTML="AUCUNE";
    coup=-1;
    let tableau=document.createElement("table");
    for (let i=0;i<L;i++){
        let ligne=document.createElement("tr");
        for (let j=0;j<L;j++){
            let carre=document.createElement("td")
            carre.setAttribute ("id",i.toString()+','+j.toString());
            carre.setAttribute ("class","case");
            carre.value=0;
            carre.style.backgroundColor=col[tirage(C)];
            carre.style.width=(500/L).toString()+"px";
            carre.style.height=(500/L).toString()+"px";
            ligne.appendChild(carre);
        }
        tableau.appendChild(ligne);
    }
    grille.appendChild(tableau);
    reset_value();
}

/* Fonction changementcouleur : change la couleur des cases adjacentes de la même couleur */
function changementcouleur(){
    if (partiefinie == false){
        lastcolor=this.style.backgroundColor
        this.style.backgroundColor=currentColor;
        if (currentColor!=lastcolor){
            let coordonée=[];
            let i=0;
            for (let j=0; j<2;j++){
                let c='';
                while (this.id[i]!=','&& i<this.id.length){
                    c=c+this.id[i];
                    i++;
                }
                i++;
                coordonée.push(c);
            }
            verif_adjacent(parseInt(coordonée[0]),parseInt(coordonée[1]));
            reset_value();
        }
    }
}

/* Fonction changeCurrentCol : change la couleur courante */
function changeCurrentCol(){
     currentColor = this.id;
     sel.style.backgroundColor=currentColor;
     sel.innerHTML="";
     let carre=document.getElementsByTagName("td");
     for (let i=0;i<carre.length;i++){
         carre[i].addEventListener("click",changementcouleur);
     }
}

function verif_adjacent(i,j){
     let caseselectionné=document.getElementById(i.toString()+","+j.toString());
     caseselectionné.value=1;
     if (i==0){
        let casebas=document.getElementById((i+1).toString()+","+j.toString());
        if(casebas.style.backgroundColor==lastcolor && casebas.value==0){
            casebas.style.backgroundColor=currentColor;
            verif_adjacent(i+1,j);
        }
    }
    else if (i==L-1){
        let casehaut=document.getElementById((i-1).toString()+","+j.toString());
        if(casehaut.style.backgroundColor==lastcolor && casehaut.value==0){
            casehaut.style.backgroundColor=currentColor;
            verif_adjacent(i-1,j);
        }
    }
    else{
        let casehaut=document.getElementById((i-1).toString()+","+j.toString());
        let casebas=document.getElementById((i+1).toString()+","+j.toString());
        if(casehaut.style.backgroundColor==lastcolor && casehaut.value==0){
            casehaut.style.backgroundColor=currentColor;
            verif_adjacent(i-1,j);
        }
        if(casebas.style.backgroundColor==lastcolor && casebas.value==0){
            casebas.style.backgroundColor=currentColor;
            verif_adjacent(i+1,j);
        }
    }
    if (j==0){
        let casedroite=document.getElementById(i.toString()+","+(j+1).toString());
        if(casedroite.style.backgroundColor==lastcolor && casedroite.value==0){
            casedroite.style.backgroundColor=currentColor;
            verif_adjacent(i,j+1);
        }
    }
    else if (j==L-1){
        let casegauche=document.getElementById((i).toString()+","+(j-1).toString());
        if(casegauche.style.backgroundColor==lastcolor && casegauche.value==0){
            casegauche.style.backgroundColor=currentColor;
            verif_adjacent(i,j-1);
        }
    }
    else{
        let casegauche=document.getElementById((i).toString()+","+(j-1).toString());
        let casedroite=document.getElementById((i).toString()+","+(j+1).toString());
        if(casegauche.style.backgroundColor==lastcolor && casegauche.value==0){
            casegauche.style.backgroundColor=currentColor;
            verif_adjacent(i,j-1);
        }
        if(casedroite.style.backgroundColor==lastcolor && casedroite.value==0){
            casedroite.style.backgroundColor=currentColor;
            verif_adjacent(i,j+1);
        }
    }
}

/* Fonction reset_value : remet la grille à zéro */
function reset_value(){
    let v=0;
    let carre1=document.getElementById("0,0");
    for (let i=0;i<L;i++){
        for (let j=0;j<L;j++){
            let carre=document.getElementById(i.toString()+","+j.toString());
            carre.value=0;
            console.log(carre.value);
            if (v==i*L+j && carre.style.backgroundColor==carre1.style.backgroundColor){
                v=v+1;
            }
        }
    }
    if (defi.innerHTML=="Mode Chill"){
        coup = coup+1;
        if (coup>=2*L && v!=L**2 && partiefinie == false){
            zonecoup.innerHTML="Vous avez perdu !";
            partiefinie = true;
        }
        else if(coup<=2*L && v==L**2 && partiefinie == false){
            zonecoup.innerHTML="Vous avez gagné en " + coup + " coups !";
            partiefinie = true;
            }
        else{
            zonecoup.innerHTML="Nombre de coup(s) : "+coup.toString()+'/'+(2*L).toString();
        }
    }
    else{
        zonecoup.innerHTML='';
        if(coup<=2*L && v==L**2 && partiefinie == false){
            zonecoup.innerHTML="Vous avez gagné !";
            partiefinie = true;
        }    
    }
}

/* Fonction init_palette : initialise la palette de couleur */
function init_palette(){
     let palette=col;
     for (let i=0; i<C;i++){
        let peinture = document.createElement("div");
        let couleur = palette[i];
        peinture.id = couleur;
        peinture.style.height = "50px";
        peinture.style.width = "100%";
        peinture.style.outline = "3px solid";
        peinture.style.backgroundColor = couleur;
        peinture.style.display="inline-block";
        peinture.addEventListener("click",changeCurrentCol);
        palettediv.appendChild(peinture);
    }
}

/* Fonction reset : Reinitialise la partie */
function reset(){
    partiefinie = false;
    grille.innerHTML="";
    palettediv.innerHTML="";
    init_palette();
    init();
}

/* Initialisation du jeu */
init_palette();
init_boutons();
init();
creationcol();