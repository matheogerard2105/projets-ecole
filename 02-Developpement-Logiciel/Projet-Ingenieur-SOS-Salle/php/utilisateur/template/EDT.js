const SKIP_JOUR_PLUS = 5;
const SKIP_JOUR_MOINS = 1;
const SKIP_SEMAINE_PLUS = 53;
const SKIP_SEMAINE_MOINS = 1;

const edtGridDay = document.querySelector('.edt-grid-day');
const edtGridWeek = document.querySelector('.edt-grid-week');
const titre = document.getElementById('titre-date');

const btnJourMoins = document.getElementById('-1jourButton');
const btnJour = document.getElementById('jourButton');
const btnJourPlus = document.getElementById('+1jourButton');

const btnSemaineMoins = document.getElementById('-1semaineButton');
const btnSemaine = document.getElementById('semaineButton');
const btnSemainePlus = document.getElementById('+1semaineButton');

// 1. Fonction utilitaire indispensable en JS pour convertir (Année, Semaine, Jour) en Date réelle
function getDateFromISO(annee, semaine, jour) {
    // Le 4 janvier est toujours dans la semaine 1 (norme ISO 8601)
    let date = new Date(annee, 0, 4);
    let jourDeLaSemaine = date.getDay() || 7; // getDay() renvoie 0 pour Dimanche, on le passe à 7
    
    // On calcule la différence de jours pour retomber sur la bonne date
    let ecart = (semaine - 1) * 7 + (jour - jourDeLaSemaine);
    date.setDate(date.getDate() + ecart);
    return date;
}

function toStringTitreJour(jour, semaine, annee) {
    let date = getDateFromISO(annee, semaine, jour);
    let jourMois = date.getDate();
    let moisIndex = date.getMonth() + 1; // getMonth() commence à 0, donc on fait +1
    let anneeReelle = date.getFullYear();

    // 2. On récupère les noms dans les objets convertis de PHP (sans écraser le paramètre "jour")
    let nomJour = JOURS[jour];
    let nomMois = MOIS[moisIndex];

    return nomJour + " " + jourMois + " " + nomMois + " " + anneeReelle;
}

function toStringTitreSemaine(semaine, annee) {
    let dateDeb = getDateFromISO(annee, semaine, 1); // 1 = Lundi
    let dateFin = getDateFromISO(annee, semaine, 7); // 7 = Dimanche

    // Fonction pour forcer 2 chiffres (ex: "9" devient "09")
    const formatDeuxChiffres = (num) => String(num).padStart(2, '0');

    let debStr = formatDeuxChiffres(dateDeb.getDate()) + "/" + formatDeuxChiffres(dateDeb.getMonth() + 1) + "/" + annee;
    let finStr = formatDeuxChiffres(dateFin.getDate()) + "/" + formatDeuxChiffres(dateFin.getMonth() + 1) + "/" + annee;

    return "Semaine " + semaine + " (du " + debStr + " au " + finStr + ")";
}

function affichageJourSemaine(){
    if (versionPrint === 'jour') {
        edtGridDay.style.display = 'grid';
        edtGridWeek.style.display = 'none';
        // désactivation des buttons semaines
        btnSemaineMoins.disabled = true;
        btnSemainePlus.disabled = true;
        //activation des boutons jours
        btnJourMoins.disabled = false;
        btnJourPlus.disabled = false;
        //
        titre.textContent = toStringTitreJour(jour, semaine, annee);

    } else if (versionPrint === 'semaine') {
        edtGridDay.style.display = 'none';
        edtGridWeek.style.display = 'grid';
        // activation des buttons semaines
        btnSemaineMoins.disabled = false;
        btnSemainePlus.disabled = false;
        // désactivation des boutons jours
        btnJourMoins.disabled = true;
        btnJourPlus.disabled = true;

        titre.textContent = toStringTitreSemaine(semaine, annee);
    }
}

affichageJourSemaine();


function limits(jour, semaine, annee) {
    if (jour < SKIP_JOUR_MOINS) {
        jour = SKIP_JOUR_PLUS;
        semaine--;
    } else if (jour > SKIP_JOUR_PLUS) {
        jour = SKIP_JOUR_MOINS;
        semaine++;
    };
    if (semaine < SKIP_SEMAINE_MOINS) {
        semaine = SKIP_SEMAINE_PLUS;
        annee--;
    } else if (semaine > SKIP_SEMAINE_PLUS) {
        semaine = SKIP_SEMAINE_MOINS;
        annee++;
    };
    return { jour, semaine, annee };
}

function isSalle(select){
    const regex = new RegExp('([A-Z][0-9]{3})');
    return regex.test(select);
}

function navigate(btn, jour, semaine, annee, version, select){
    btn.onclick = () => {
        let url;
        if (isSalle(select)) {
            url = 'Salle-EDT.php?version=' + version + '&jour=' + jour + '&semaine=' + semaine + '&annee=' + annee;
            url += '&salle=' + select;
        } else {
            url = 'EDT.php?version=' + version + '&jour=' + jour + '&semaine=' + semaine + '&annee=' + annee;
            url += '&formation=' + select;
        }
        window.location.href = url;
    };
}

function BtnVueJour(){
    navigate(btnJour, jour, semaine, annee, "jour", select);
}

function updateBtnMoins1jour(){
    const new_date = limits(jour - 1, semaine, annee);
    navigate(btnJourMoins, new_date.jour, new_date.semaine, new_date.annee, versionPrint, select);
}

function updateBtnPlus1jour(){
    const new_date = limits(jour + 1, semaine, annee);
    navigate(btnJourPlus, new_date.jour, new_date.semaine, new_date.annee, versionPrint, select);
}

function BtnVueSemaine(){
    navigate(btnSemaine, jour, semaine, annee, "semaine", select);
}

function updateBtnMoins1semaine(){
    const new_date = limits(jour, semaine - 1, annee);
    navigate(btnSemaineMoins, new_date.jour, new_date.semaine, new_date.annee, versionPrint, select);
}

function updateBtnPlus1semaine(){
    const new_date = limits(jour, semaine + 1, annee);
    navigate(btnSemainePlus, new_date.jour, new_date.semaine, new_date.annee, versionPrint, select);
}

BtnVueJour();
updateBtnMoins1jour();
updateBtnPlus1jour();
BtnVueSemaine();
updateBtnMoins1semaine();
updateBtnPlus1semaine();