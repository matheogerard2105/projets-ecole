"use strict";

const State = { S: "sain", I: "infecte" };

// --- Dans l'objet Config, ajoutez une valeur par défaut pour speed ---
let Config = {
    N: 30,
    I0: 5,
    p: 0.05,
    maxSteps: 500,
    timeStep: 200 // Vitesse initiale (ms)
};
const Simulation = function() {
    this.population = [];
    this.history = { I: [], S: [] };
    this.stepCount = 0;
    this.timer = null;
    this.chart = null;
    this.svg = null;
};

Simulation.prototype.init = function() {
    this.createUI();
    this.reset();
};

// Modifiez reset pour effacer l'info de pause
Simulation.prototype.reset = function() {
    clearInterval(this.timer);
    this.timer = null;
    this.stepCount = 0;
    this.population = [];
    this.history = { I: [], S: [] };

    // Initialisation de la population N
    for (let i = 0; i < Config.N; i++) {
        this.population.push({ state: State.S });
    }

    // --- MODIFICATION : I0 n'est plus aléatoire, on utilise Config.I0 ---
    // On s'assure que I0 ne dépasse pas N au cas où
    let initialInfected = Math.min(Config.I0, Config.N);
    for (let i = 0; i < initialInfected; i++) {
        this.population[i].state = State.I;
    }

    let infoDisplay = document.getElementById('simulation-info');
    if (infoDisplay) infoDisplay.innerHTML = "";

    this.updateData();
    this.render();
    document.getElementById('start-btn').innerText = "Démarrer";
};

Simulation.prototype.step = function() {
    if (this.stepCount >= Config.maxSteps) return this.pause();

    // 1. Compter les infectés à l'instant n (In = i) 
    let i = this.population.filter(p => p.state === State.I).length;
    
    // 2. Probabilité d'infection pour un sain : 1 - q^i 
    let q = 1 - Config.p;
    let probInfection = 1 - Math.pow(q, i);

    // 3. Calcul de l'état à n+1
    this.population = this.population.map(ind => {
        if (ind.state === State.I) {
            // Un infecté à n devient sain à n+1 
            return { state: State.S };
        } else {
            // Un sain est infecté avec proba 1 - q^i
            return { state: Math.random() < probInfection ? State.I : State.S };
        }
    });

    this.stepCount++;
    this.updateData();
    this.updateUI();
};

Simulation.prototype.updateData = function() {
    let infected = this.population.filter(p => p.state === State.I).length;
    this.history.I.push(infected);
    this.history.S.push(Config.N - infected);
};

Simulation.prototype.render = function() {
    // Grille de points
    const cols = 50;
    const rows = Math.ceil(Config.N / cols);
    const size = 10;

    if (!this.svg) {
        this.svg = SVG().addTo('#simulation-grid').size(cols * size, rows * size);
    } else {
        this.svg.clear();
        this.svg.size(cols * size, rows * size);
    }

    this.population.forEach((ind, idx) => {
        let x = (idx % cols) * size;
        let y = Math.floor(idx / cols) * size;
        this.svg.circle(size - 2).move(x, y).attr({
            fill: ind.state === State.I ? '#e74c3c' : '#3498db',
            id: 'p-' + idx
        });
    });

    this.initChart();
};

Simulation.prototype.updateUI = function() {
    this.population.forEach((ind, idx) => {
        this.svg.findOne('#p-' + idx).attr({
            fill: ind.state === State.I ? '#e74c3c' : '#3498db'
        });
    });
    this.updateChart();
};

// --- Fonctions auxiliaires (UI et Chart) ---
Simulation.prototype.createUI = function() {
    const root = document.getElementById('controls-container');
    root.innerHTML = "";

    const addSlider = (label, min, max, val, key, step = 1) => {
        let group = document.createElement('div');
        group.className = 'slider-group';
        group.innerHTML = `<label>${label}: <b id="lbl-${key}">${val}</b></label>
                           <input type="range" id="input-${key}" min="${min}" max="${max}" step="${step}" value="${val}">`;
        
        let input = group.querySelector('input');
        input.oninput = (e) => {
            let v = parseFloat(e.target.value);
            Config[key] = v;
            document.getElementById(`lbl-${key}`).innerText = v;
            
            if(key === 'N') {
                let i0Slider = document.getElementById('input-I0');
                if (i0Slider) {
                    i0Slider.max = v;
                    if (Config.I0 > v) {
                        Config.I0 = v;
                        i0Slider.value = v;
                        document.getElementById('lbl-I0').innerText = v;
                    }
                }
                this.reset(); 
            }
            // Si on change la vitesse pendant que ça tourne, on redémarre le timer
            if(key === 'timeStep' && this.timer) {
                this.pause();
                this.start();
            }
            if(key === 'I0') this.reset();
        };
        root.appendChild(group);
    };

    addSlider("Population (N)", 10, 100, Config.N, 'N');
    addSlider("Infectés initiaux (I0)", 1, Config.N, Config.I0, 'I0');
    addSlider("Proba contagion (p)", 0.01, 0.1, Config.p, 'p', 0.01);
    // NOUVEAU : Slider de vitesse (Intervalle en ms, donc plus petit = plus rapide)
    addSlider("Intervalle (ms) - Plus petit = Plus vite", 0, 1000, Config.timeStep, 'timeStep', 10);
    addSlider("Durée maximale", 50, 1000, Config.maxSteps, 'maxSteps');

// Création d'un conteneur dédié aux boutons pour garantir l'alignement
    let btnArea = document.createElement('div');
    btnArea.style.display = "flex";
    btnArea.style.flexDirection = "column";
    btnArea.style.width = "100%";

    let btn = document.createElement('button');
    btn.id = 'start-btn';
    btn.innerText = "Démarrer";
    btn.onclick = () => this.timer ? this.pause() : this.start();
    btnArea.appendChild(btn);

    let resetBtn = document.createElement('button');
    resetBtn.id = 'reset-btn'; // On lui donne un ID pour le cibler si besoin
    resetBtn.innerText = "Réinitialiser";
    resetBtn.style.backgroundColor = "#6c757d";
    resetBtn.onclick = () => this.reset();
    btnArea.appendChild(resetBtn);
    
    root.appendChild(btnArea);   
};

Simulation.prototype.start = function() {
    document.getElementById('start-btn').innerText = "Pause";
    this.timer = setInterval(() => this.step(), Config.timeStep);
};

Simulation.prototype.pause = function() {
    document.getElementById('start-btn').innerText = "Continuer";
    clearInterval(this.timer);
    this.timer = null;

    // Affiche le nombre d'infectés au moment de la pause
    let currentI = this.population.filter(p => p.state === State.I).length;
    let infoDisplay = document.getElementById('simulation-info');
    if (!infoDisplay) {
        infoDisplay = document.createElement('div');
        infoDisplay.id = 'simulation-info';
        document.getElementById('left-panel').appendChild(infoDisplay);
    }
    infoDisplay.innerHTML = `<strong>Pause :</strong> ${currentI} infectés à l'instant n=${this.stepCount}`;
};

Simulation.prototype.initChart = function() {
    let ctx = document.getElementById('simulationChart').getContext('2d');
    if(this.chart) this.chart.destroy();
    this.chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [0],
            datasets: [{ label: 'Infectés', data: [this.history.I[0]], borderColor: '#e74c3c', fill: false }]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { yAxes: [{ ticks: { beginAtZero: true, max: Config.N } }] } }
    });
};

Simulation.prototype.updateChart = function() {
    this.chart.data.labels.push(this.stepCount);
    this.chart.data.datasets[0].data.push(this.history.I[this.stepCount]);
    this.chart.update();
};

const sim = new Simulation();
sim.init();