const sep = ';';
/* Renvoie sous forme d'une liste les valeurs contenues 
 dans une chaîne de caractère en utilisant le séparateur
 défini en constante.
Param :   line : String
return :  values : list of String 
*/
function getCsvValuesFromLine(line) {
    var values = line.split(sep);
    value = values.map(function(value){
        return value.replace(/\"/g, '');
    });
    return values;
}

/*Renvoie sous forme d'une liste d'Object 
 (voir doc : Object key-values)les informations
 contenues dans un fichier CSV passé sous la forme
 d'une liste de chaînes de caractères.
Param :   lines : list of String
return :  people : list of String 
*/
function getLinesFromHTML(lines){
  //on récupère la première ligne comme header et on la retire
  var headers = getCsvValuesFromLine(lines[0]);
  lines.shift();
  //On crée un tableau pour contenir les individus du dataset
  var people = [];
  for(var i=0; i<lines.length; i+=1){
    //chaque case est un Object rempli avec les paires clé/valeur
    people[i] = {};
    var lineValues = getCsvValuesFromLine(lines[i]);
    for (var j=0; j<lineValues.length; j+=1){
      people[i][headers[j]] = lineValues[j];
    }
  }
  return people;
}

//variable globale pour le contenu (texte) du CSV
var CSVcontent;

//Filereader pour le flux de lecture
const fileInput = document.getElementById('csv')
const readFile = () => {
  const reader = new FileReader()
  reader.onload = () => {
    CSVcontent = reader.result;
  }
  // lit le fichier et appelle l'événement "onload" ensuite
  reader.readAsText(fileInput.files[0])
}

//Définition de la fonction associé au bouton "load"
var btn = document.querySelector('button');
btn.onclick = function() {
    document.getElementById('out').innerHTML="";
    var lines = CSVcontent.split('\n');
    console.log(getCsvValuesFromLine(lines[0]));
    console.log(getLinesFromHTML(lines));
    affichage(getLinesFromHTML(CSVcontent.split('\n')))
}

fileInput.addEventListener('change', readFile)

/*




SEPARATION ENTRE LE READFILE DE BASE DONNE ET LA SUITE DU SCRIPT QUE L'ON A REALISE




*/

/** Première partie permettants le tracé 
 * du graphique à plusieurs facteurs*/

//Initialisation des paramètres
let parametre="SEXE";
let etude="ACTEU";
let titre;
let titre1="Inégalité autour de l'emploi";
let titre2="Sexe";
let mode1=document.getElementById("ACTEU");
let donnee=document.getElementById("donnee")
mode1.addEventListener("click",tomode2);
init_boutons();

// Fonctions permettants le changement du thème du graphique
function tomode1() {
  let newButton = document.createElement("button");
  newButton.innerHTML = "Inégalité de l'ancienneté sans emploi";
  titre1="Inégalité autour de l'emploi";
  newButton.id = "ACTEU";
  etude="ACTEU";
  newButton.addEventListener("click", tomode2);
  this.replaceWith(newButton);
  affichage(getLinesFromHTML(CSVcontent.split('\n')));
}
function tomode2() {
  let newButton = document.createElement("button");
  newButton.innerHTML = "Inégalité autour de l'emploi";
  titre1="Inégalité de l'ancienneté sans emploi";
  newButton.id = "ANCSSEMP";
  etude="ANCSSEMP";
  newButton.addEventListener("click", tomode1);
  this.replaceWith(newButton);
  affichage(getLinesFromHTML(CSVcontent.split('\n')));
}

// Fonctions permettant le choix du facteur pour le graphique
function init_boutons(){
  let optionA = document.createElement("option");
  optionA.class = "donnee";
  optionA.id="SEXE";
  optionA.textContent = "Sexe";
  donnee.appendChild(optionA);
  optionA.addEventListener("click",choixdonnee);
  let optionB = document.createElement("option");
  optionB.class = "donnee";
  optionB.id="AGE6";
  optionB.textContent = "Age";
  donnee.appendChild(optionB);
  optionB.addEventListener("click",choixdonnee);
  let optionC = document.createElement("option");
  optionC.class = "donnee";
  optionC.id="DIP7";
  optionC.textContent = "Diplome";
  donnee.appendChild(optionC);
  optionC.addEventListener("click",choixdonnee);
  let optionD = document.createElement("option");
  optionD.class = "donnee";
  optionD.id="APCS1";
  optionD.textContent = "Classe Socio-Pro";
  donnee.appendChild(optionD);
  optionD.addEventListener("click",choixdonnee);
}
function choixdonnee(){
  titre2=this.textContent;
  parametre=this.id;
  affichage(getLinesFromHTML(CSVcontent.split('\n')));
}

// Fonction permettant la récupération des valeurs nécessaires
//  au tracé du diagramme
function listex(c,d){
  let x=[];
  for (var don of Object.keys(d)){
    x.push(parseInt(d[don][c]));
  }
  return x;
}

// Fonction permettant de remplacer les nombres récupérés
// dans les données par leur signification (correspondant 
// au nom des séries)
function traductionname(l,e){
  l2=[]
  for (var c in l){
    if (e=="ACTEU"){
      l2=["Emploi","Chômage","Inactif"];
    }
    if (e=="ANCSSEMP"){
    l2=["- 1 mois", "1-3 mois","3-6mois","6-12mois","12-18 mois", "18-24 mois","2-4 ans","4-10 ans", "+10 ans","Sans réponse"];
    }
  }
  return l2;
}

// Fonction permettant de remplacer les nombres récupérés
// dans les données par leur signification (correspondant 
// aux différentes catégories (exemple : homme/femme))
function listey(p,l){
  l2=[];
  if(p=="SEXE"){
    l2=["Homme","Femme"];
  }
  else if(p=="AGE6"){
    l2=["15-24ans","25-49ans","50-64ans","65-89ans"];
  }
  else if(p=="DIP7"){
    l2=["Bac+5 et +","Bac+3/4","Bac+2" ,"Bac","CAP","Brevet","Aucun diplôme"];
  }
  else if (p=="APCS1"){
    l2=["","Agriculteurs", "Artisants", "Cadre","Ouvriers","Prof.Intermédiaires","Employés"];
  }
  else{
    l2=l;
  }
  return l2;
}

// Fonction permettant le tracé du diagramme 
// quelques soit les facteurs choisis 
// grâce au travail réalisé prcédemment

function mutliple(all_datas){
  // Stocke le titre en fonction du sujet
  titre=titre1+" selon le facteur suivant : "+titre2;
  //Crée un dictionnaire de dictionnaire d'occurence afin de mettre
  // en relation deux variables que l'on a choisi et récupérer
  // avant (parametre et etude)
  var dic={};
  for (var x of all_datas) {
      if (x[etude] && x[parametre]) {
        var p = x[parametre];
        if ((!(p in dic))){
            dic[p] = {}
        }
        var actif = x[etude]
        if (!(actif in dic[p])) {
              dic[p][actif] = 0
            }
            dic[p][actif] += 1
      }
  }
  yy=[];
  ly=[]
  lname=[];
  let k=0;
  //Parcours du dictionnaire à la recherche des différentes série
  for (var don of Object.keys(dic)){
    yy.push(don);
    for (var name of Object.keys(dic[don])){
      if (k==0){
        lname.push(name);
      }
    }
    k++;
  }
  lname2=traductionname(lname,etude);
  ldata=[];
  //Recherche pour chaque série (exemple :inactif,emploi,chômeur),
  //les données qui lui correspondent
  for (let j=0; j<lname.length; j++){
    var data={
      y: listey(parametre,yy),
      x: listex(lname[j],dic),
      type: 'bar',orientation:'h',
      name: lname2[j],
    }
    ldata.push(data);
  }
  // Met en forme le graphique 
  var layout = {
    orientation:'h',//barre horizontale et empilée
    barmode: 'stack',
    title: {
      text: titre, //Met le titre stocké
      font: { 
        family: "Arial, sans-serif",
        size: 24,
        color: 'rgb(200,200,200)',
      }},
      width:857.5,
      height:560,
      paper_bgcolor: 'rgb(30,30,30)',
      plot_bgcolor: 'rgb(30,30,30)',
      legend: {
        x: 1,  
        y: 1,
        font: { 
          size: 12,
          color: 'rgb(200,200,200)'
         } 
      }
    };
    Plotly.newPlot('h5',ldata, layout);
}

// Fonction traçant le diagramme de Répartition de l'activité
// Voici la documentatiojn détaillée (même logique pour toutes
//  les fonctions qui suivent)
function actif(all_datas) {
  //On crée un dictionnaire d'occurence des différentes
  // valeurs prises par la variable ACTEU (Statut d'activité
  // au sens du BIT) à savoir 1(pour en emploi)
  // 2 pour chômeur et 3 pour inactif
  var di_actif = {}
  for (var x of all_datas) {
      if (x["ACTEU"]) {
          var actif = x["ACTEU"]
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
      }
  }
  // On crée nos listes de valeurs pour les axes x et y
  var xx = ["Emploi","Chômage","Inactif"]
  var yy = []
  for (var actif in di_actif) {
      yy.push(di_actif[actif]);
  }

  // On les utilises pour mettre en places les données du graphique
  var data = [
    {
      labels: xx,
      values: yy,
      type: 'pie' // diagramme circulaire
    }
  ];
  // Permet de mettre en forme le graphique comme on le souhaite sur la page
  var layout={
    title: {
      text: "Répartition de l'activité",
      font: { 
        family: "Arial, sans-serif",
        size: 24,
        color: 'rgb(200,200,200)',
      }
    },
    width:490,
    height:300,
    paper_bgcolor: 'rgb(30,30,30)',
    legend: {
      x: 1,  
      y: 1,
      font: { 
        size: 12,
        color: 'rgb(200,200,200)'
       } 
    }
  };
  // Affiche le graphique dans la zone d'id 'c1' du html
  Plotly.newPlot('c1', data,layout);
}

// Fonction traçant le diagramme de l'ancienneté des sans emplois
function ancien(all_datas) {
  var di_actif = {}
  for (var x of all_datas) {
      if (x["ANCSSEMP"]) {
          var actif = x["ANCSSEMP"]
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
      }
  }
  var xx = ["- 1 mois", "1-3 mois","3-6mois","6-12mois","12-18 mois", "18-24 mois","2-4 ans","4-10 ans", "+10 ans"];
  var yy = [di_actif[1],di_actif[2],di_actif[3],di_actif[4],di_actif[5],di_actif[6],di_actif[7],di_actif[8],di_actif[9]];
  var data = [
    {
      labels: xx,
      values: yy,
      type: 'pie'
    }
  ];
  var layout={
    title: {
      text: "Répartition de l'ancienneté des sans emploi",
      font: { 
        family: "Arial, sans-serif",
        size: 24,
        color: 'rgb(200,200,200)',
      }
    },
    width:490,
    height:300,
    paper_bgcolor: 'rgb(30,30,30)',
    legend: {
      x: 1,  
      y: 1,
      font: { 
        size: 12 ,
        color: 'rgb(200,200,200)',

      },
    }
  };
  Plotly.newPlot('c2', data,layout);
}

// Fonction traçant le diagramme de Répartition des âges
function age(all_datas) {
  var di_actif = {};
  for (var x of all_datas) {
      if (x["AGE6"]) {
          var actif = x["AGE6"]
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
      }
  }
  var xx = ["15-24ans", "25-49ans", "50-64 ans"];
  var yy = [di_actif['15'],di_actif['25'],di_actif['50']];
  var data = [
    {
      x: xx,
      y: yy,
      type: 'bar',
      marker: {
        color: "aquamarine",
      }
    }
  ];
  var layout={
    title: {
      text: "Répartition par tranche d'âge",
      font: { 
        family: "Arial, sans-serif",
        size: 24,
        color: 'rgb(200,200,200)',
      }
      
    },
    width:428.75,
    height:300,
    paper_bgcolor: 'rgb(30,30,30)',
    plot_bgcolor: 'rgb(30,30,30)',
    legend: {
      x: 1,  
      y: 1,
      font: { 
        size: 12,
        color: 'rgb(200,200,200)'
       } 
    }
  };
  Plotly.newPlot('h1', data, layout);
}

// Fonction traçant le diagramme de Répartition des secteurs d'activité
function activite(all_datas) {
  var di_actif = {};
  for (var x of all_datas) {
      if (x["NAFG004UN"]) {
          var actif = x["NAFG004UN"]
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
      }
  }
  var xx = ["Agriculture", "Construction", "Industrie","Tertiaire"];
  var yy = [di_actif['ES'],di_actif['EU'],di_actif['ET'],di_actif['EV']];
  var data = [
    {
      y: xx,
      x: yy,
      type: 'bar',
      orientation: 'h',
      marker: {
        color: "aquamarine",
      }
    }
  ];
  var layout={
    title: {
      text: "Répartition par secteurs d'activité",
      font: { 
        family: "Arial, sans-serif",
        size: 24,
        color: 'rgb(200,200,200)',
      }
    },
    width:428.75,
    height:300,
    paper_bgcolor: 'rgb(30,30,30)',
    plot_bgcolor: 'rgb(30,30,30)',
    legend: {
      x: 1,  
      y: 1,
      font: { 
        size: 12,
        color: 'rgb(200,200,200)'
       } 
    }
  };
  Plotly.newPlot('h2', data,layout);
}

// Fonction traçant le diagramme de Répartition des diplomes
function diplome(all_datas) {
  var di_actif = {};
  for (var x of all_datas) {
      if (x["DIP7"]) {
          var actif = x["DIP7"]
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
      }
  }
  var xx = ["Aucun diplôme", "Brevet-CAP", "Bac/Bac+2","Bac+3 et +"];
  var yy = [di_actif['7'],di_actif['6']+di_actif['5'],di_actif['4']+di_actif['3'],di_actif['2']+di_actif['1']];
  var data = [
    {
      x: xx,
      y: yy,
      type: 'bar',
      marker: {
        color: "aquamarine",
      }
    }
  ]
  var layout={
    title: {
      text: "Répartition par diplômes",
      font: { 
        family: "Arial, sans-serif",
        size: 24,
        color: 'rgb(200,200,200)',
      }
      
    },
    width:428.75,
    height:300,
    paper_bgcolor: 'rgb(30,30,30)',
    plot_bgcolor: 'rgb(30,30,30)',
    legend: {
      x: 1,  
      y: 1,
      font: { 
        size: 12,
        color: 'rgb(200,200,200)'
       } 
    }
  };
  Plotly.newPlot('h3', data,layout);
}

// Fonction traçant le diagramme de Répartition des classes socio-professionnels
function socio(all_datas) {
  var di_actif = {};
  for (var x of all_datas) {
      if (x["APCS1"]) {
          var actif = x["APCS1"]
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
      }
  }
  var xx = ["Agriculteurs", "Artisants", "Cadre","Ouvriers","Prof.Intermédiaires","Employés"];
  var yy = [di_actif['1'],di_actif['2'],di_actif['3'],di_actif['6'],di_actif['4'],di_actif['5']];
  var data = [
    {
      y: xx,
      x: yy,
      type: 'bar',
      orientation: 'h',
      marker: {
        color: "aquamarine",
      }
    }
  ]
  var layout={
    title: {
      text: "Répartition par classes",
      font: { 
        family: "Arial, sans-serif",
        size: 24,
        color: 'rgb(200,200,200)',
      }
      
    },
    width:428.75,
    height:300,
    paper_bgcolor: 'rgb(30,30,30)',
    plot_bgcolor: 'rgb(30,30,30)',
    legend: {
      x: 1,  
      y: 1,
      font: { 
        size: 12,
        color: 'rgb(200,200,200)'
       } 
    }
  };
  Plotly.newPlot('h4', data,layout);
}

//Zones pour mettre les chiffres importants
s1=document.getElementById("s1");
s2=document.getElementById("s2");
s3=document.getElementById("s3");
s4=document.getElementById("s4");
s5=document.getElementById("s5");

//Fonction calculant et affichant la parité homme-femme
function sexe(all_datas) {
  var di_actif = {};
  for (var x of all_datas) {
      if (x["SEXE"]) {
          var actif = x["SEXE"]
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
      }
  }
  var h=Math.round((di_actif[1]/(di_actif[2]+di_actif[1]))*100);
  var f=Math.round((di_actif[2]/(di_actif[2]+di_actif[1]))*100);
  s1.innerHTML=h+"%";
  s2.innerHTML=f+"%";
}

//Fonction calculant et affichant le souhait de travailler des inactifs
function souhait(all_datas) {
  var di_actif = {};
  var n=0;
  for (var x of all_datas) {
      if (x["SOU_C"]) {
          var actif = x["SOU_C"]
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
          n++;
      }
  }
  s5.innerHTML=Math.round((1-di_actif['4']/n)*100)+"%";
}

//Fonction calculant et affichant la part de ceux en âge de travailler
function age2(all_datas) {
  var di_actif = {};
  var n=0;
  for (var x of all_datas) {
      if (x["AGE6"]) {
          var actif = x["AGE6"];
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
          n++;
      }
  }
  var s=+di_actif['65']+di_actif['90'];
  console.log(s);
  s3.innerHTML=100-Math.round((s/n*100))+"%";
}

//Fonction calculant et affichant le taux de chômage parmis les actifs
function chomage(all_datas) {
  var di_actif = {};
  var n=0;
  for (var x of all_datas) {
      if (x["ACTEU"]) {
          var actif = x["ACTEU"];
          if (!(actif in di_actif)) {
              di_actif[actif] = 0
          }
          di_actif[actif] += 1
      }
  }
  var s=di_actif['2']/(di_actif['2']+di_actif['1']);
  s4.innerHTML=Math.round(100*s)+"%";
}

//Fonction qui appelle toutes les fonctions d'affichage précédentes
function affichage (all_datas){
  actif(all_datas);
  ancien(all_datas);
  age(all_datas);
  activite(all_datas);
  diplome(all_datas);
  socio(all_datas);
  sexe(all_datas);
  souhait(all_datas);
  age2(all_datas);
  chomage(all_datas);
  mutliple(all_datas);
}