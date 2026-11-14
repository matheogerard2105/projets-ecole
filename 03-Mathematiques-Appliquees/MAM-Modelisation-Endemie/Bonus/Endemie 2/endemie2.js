/**
 * Logique des individus
 */
const State = {
  S: "susceptible",
  I: "infectious",
  R: "recovered"
}

const Individual = function(state = State.S) {
  this.state = state;
}

Individual.prototype.infect = function(rate) {
  if (this.state == State.S && Math.random() <= rate) {
    this.state = State.I;
  }
}

Individual.prototype.recover = function(rate) {
  if (this.state == State.I && Math.random() <= rate) {
    this.state = State.R;
  }
}

/**
 * Configuration et Initialisation
 */
let StochasticSimulationDefaultConfig = {
  Nx: 10,
  Ny: 10,
  iRate: .2,
  rRate: .1,
  travelRadius: 3,
  nMeeting: 4,
  percentStartInfected: .01,
  maxSteps: 500,
  dotRadius: 8,
  dotPadding: 2,
  colorSusceptible: 'rgba(0, 0, 255, .5)',
  colorSusceptibleBg: 'rgba(0, 0, 255, .1)',
  colorInfected: 'rgba(255, 0, 0, .5)',
  colorInfectedBg: 'rgba(255, 0, 0, .1)',
  colorRecovered: 'rgba(0, 255, 0, .5)',
  colorRecoveredBg: 'rgba(0, 255, 0, .1)',
  timeBetweenSteps: 100,
}

const StochasticSimulation = function(ctx, config) {
  this.ctx = document.getElementById(ctx);
  this.config = Object.assign(StochasticSimulationDefaultConfig, config);
  this.N = this.config.Nx * this.config.Ny;
  
  this.individuals = [];
  this.infected = [];
  this.changedState = [];
  this.nSusceptible = [];
  this.nInfected = [];
  this.nRecovered = [];
  this.chart = null;
  this.svgArea = null;
  this.runInterval = null;
}

// Gestion des états de la simulation
StochasticSimulation.prototype.setup = function() {
  this.setupSimulation();
  this.setupDraw();
}

StochasticSimulation.prototype.reset = function() {
  this.pause();
  this.setupSimulation();
  this.resetDraw();
}

StochasticSimulation.prototype.pause = function() {
  if (this.runInterval != null) {
    clearInterval(this.runInterval);
    this.runInterval = null;
  }
}

StochasticSimulation.prototype.run = function() {
  this.runInterval = setInterval(() => {
    if (this.infected.length == 0 || this.nInfected.length > this.config.maxSteps) {
      clearInterval(this.runInterval);
    } else {
      this.step();
    }
  }, this.config.timeBetweenSteps);
}

StochasticSimulation.prototype.step = function() {
  if (this.infected.length != 0) {
    this.stepSimulation();
    this.updateDraw();
  }
}

/**
 * Moteur de calcul (Mathématiques)
 */
StochasticSimulation.prototype.toGridCoordinates = function(index) {
  let x = index % this.config.Nx;
  return [x, (index - x) / this.config.Nx];
}

StochasticSimulation.prototype.toIndex = function(coo) {
  return coo[1] * this.config.Nx + coo[0];
}

StochasticSimulation.prototype.inGrid = function(coo) {
  return coo[0] >= 0 && coo[0] < this.config.Nx && coo[1] >= 0 && coo[1] < this.config.Ny;
}

StochasticSimulation.prototype.selectNeighboursOf = function(index) {
  let coo = this.toGridCoordinates(index);
  let neighbours = [];

  // Recherche des voisins par distance de Manhattan
  for (let d = 1; d <= this.config.travelRadius; d++) {
    for (let i = -d; i <= d; i++) {
      let c = d - Math.abs(i);
      let nc = [coo[0] + i, coo[1] + c];
      if (this.inGrid(nc)) neighbours.push(this.toIndex(nc));
      if (c != 0) {
        nc[1] -= 2 * c;
        if (this.inGrid(nc)) neighbours.push(this.toIndex(nc));
      }
    }
  }

  if (neighbours.length <= this.config.nMeeting) return neighbours;

  // Sélection aléatoire parmi les voisins trouvés
  let selected = [];
  for (let i = 0; i < this.config.nMeeting; i++) {
    let index = parseInt(Math.random() * neighbours.length);
    selected.push(neighbours[index]);
    neighbours.splice(index, 1);
  }
  return selected;
}

StochasticSimulation.prototype.setupSimulation = function() {
  this.individuals = [];
  for (let i = 0; i < this.N; i++) this.individuals.push(new Individual());

  this.infected = [];
  this.changedState = [];
  this.numStartInfected = Math.round(this.config.percentStartInfected * this.N);

  // Infection initiale aléatoire
  for (let i = 0; i < this.numStartInfected; i++) {
    let index = parseInt(Math.floor(Math.random() * this.N));
    this.individuals[index].state = State.I;
    this.infected.push(index);
    this.changedState.push(index);
  }

  this.nSusceptible = [this.N - this.numStartInfected];
  this.nInfected = [this.numStartInfected];
  this.nRecovered = [0];
}

StochasticSimulation.prototype.stepSimulation = function() {
  if (this.infected.length == 0) return;

  let newInfected = [];
  this.changedState = [];
  let newlyInfected = 0;
  let newlyRecovered = 0;

  // Cycle de guérison et d'infection
  this.infected.forEach(index => {
    let individual = this.individuals[index];
    individual.recover(this.config.rRate);
    
    if (individual.state == State.I) {
      newInfected.push(index);
      this.changedState.push(index);

      this.selectNeighboursOf(index).forEach(indexOther => {
        let other = this.individuals[indexOther];
        if (other.state == State.S) {
          other.infect(this.config.iRate);
          if (other.state == State.I) {
            newInfected.push(indexOther);
            this.changedState.push(indexOther);
            newlyInfected++;
          }
        }
      });
    } else {
      newlyRecovered++;
      this.changedState.push(index);
    }
  });

  this.infected = newInfected;
  this.nSusceptible.push(this.nSusceptible.slice(-1)[0] - newlyInfected)
  this.nInfected.push(this.infected.length);
  this.nRecovered.push(this.nRecovered.slice(-1)[0] + newlyRecovered);
}

/**
 * Interface Graphique et Visualisation
 */
function makeSlider(parent, name, min, max, step, getValueCallback, setValueCallback) {
  let container = document.createElement('p');
  container.classList.add("sliderContainer");
  parent.appendChild(container);

  let slider = document.createElement('input');
  slider.type = 'range';
  slider.min = min; slider.max = max; slider.step = step;
  slider.value = getValueCallback();
  container.appendChild(slider);

  let label = document.createElement('label');
  label.innerHTML = ' ' + name + ' : ';
  container.appendChild(label);

  let outputSlider = document.createElement('output');
  outputSlider.value = getValueCallback();
  container.appendChild(outputSlider);

  slider.addEventListener('input', () => {
    outputSlider.value = slider.value;
    setValueCallback(slider.value);
  });
}

StochasticSimulation.prototype.setupDraw = function() {
  this.ctx.innerHTML = '';
  let inputsArea = document.createElement('div');
  this.ctx.appendChild(inputsArea);

  // Création des contrôles
  makeSlider(inputsArea, 'Initialement infectés, I(0) (%)', 0.1, 10, 0.1, () => this.config.percentStartInfected * 100, v => { this.config.percentStartInfected = v / 100; this.reset(); });
  makeSlider(inputsArea, 'Taux d\'infection, β (%)', 0, 100, 1, () => this.config.iRate * 100, v => this.config.iRate = v / 100);
  makeSlider(inputsArea, 'Taux de guérison, γ (%)', 0, 100, 1, () => this.config.rRate * 100, v => this.config.rRate = v / 100);
  makeSlider(inputsArea, 'Rayon, r<sub>m</sub>', 1, 20, 1, () => this.config.travelRadius, v => this.config.travelRadius = v);
  makeSlider(inputsArea, 'Rencontres, n<sub>m</sub>', 1, 50, 1, () => this.config.nMeeting, v => this.config.nMeeting = v);
  makeSlider(inputsArea, 'Temps maximal', 200, 2000, 100, () => this.config.maxSteps, v => this.config.maxSteps = v);

  // Boutons d'action
  let btnCont = document.createElement('p');
  inputsArea.appendChild(btnCont);

  let startBtn = document.createElement('input');
  startBtn.type = 'button'; startBtn.value = 'Démarrer';
  startBtn.onclick = () => {
    if (this.runInterval == null) { this.run(); startBtn.value = 'Pause'; }
    else { this.pause(); startBtn.value = 'Continuer'; }
  };

  let resetBtn = document.createElement('input');
  resetBtn.type = 'button'; resetBtn.value = 'Recommencer';
  resetBtn.onclick = () => { this.reset(); startBtn.value = 'Démarrer'; };

  btnCont.append(startBtn, resetBtn);

  // Visualisation Grid & Chart
  let sz = this.config.dotRadius + this.config.dotPadding;
  this.svgArea = SVG().addTo(this.ctx).size(this.config.Nx * sz, this.config.Ny * sz);

  let canvas = document.createElement('canvas');
  this.ctx.appendChild(canvas);
  this.chart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        { label: 'S', data: [], borderColor: this.config.colorSusceptible, fill: false },
        { label: 'I', data: [], borderColor: this.config.colorInfected, fill: false },
        { label: 'R', data: [], borderColor: this.config.colorRecovered, fill: false }
      ]
    },
    options: { scales: { yAxes: [{ ticks: { beginAtZero: true, max: 100 } }] } }
  });

  this.resetDraw();
}

StochasticSimulation.prototype.resetDraw = function() {
  let sz = this.config.dotRadius + this.config.dotPadding;
  this.svgArea.clear();

  for (let i = 0; i < this.config.Nx; i++) {
    for (let j = 0; j < this.config.Ny; j++) {
      let idx = this.toIndex([i, j]);
      this.svgArea.circle(this.config.dotRadius)
        .attr({ fill: (this.individuals[idx].state == State.S) ? this.config.colorSusceptible : this.config.colorInfected })
        .move(i * sz, j * sz).addClass(`dot-${idx}`);
    }
  }

  this.chart.data.labels = [0];
  this.chart.data.datasets[0].data = [this.nSusceptible[0] / this.N * 100];
  this.chart.data.datasets[1].data = [this.nInfected[0] / this.N * 100];
  this.chart.data.datasets[2].data = [this.nRecovered[0] / this.N * 100];
  this.chart.update();
}

StochasticSimulation.prototype.updateDraw = function() {
  this.changedState.forEach(index => {
    let ind = this.individuals[index];
    this.svgArea.findOne(`.dot-${index}`).attr({ fill: (ind.state == State.I) ? this.config.colorInfected : this.config.colorRecovered });
  });

  this.chart.data.labels.push(this.chart.data.labels.length);
  this.chart.data.datasets[0].data.push(this.nSusceptible.slice(-1)[0] / this.N * 100);
  this.chart.data.datasets[1].data.push(this.nInfected.slice(-1)[0] / this.N * 100);
  this.chart.data.datasets[2].data.push(this.nRecovered.slice(-1)[0] / this.N * 100);
  this.chart.update();
}

// Initialisation
let sim = new StochasticSimulation('simulation', { Nx: 50, Ny: 20 });
sim.setup();