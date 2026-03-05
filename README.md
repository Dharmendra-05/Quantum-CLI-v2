<div align="center">

                              ```
                                 ██████  ██    ██  █████  ███    ██ ████████ ██    ██ ███    ███
                                ██    ██ ██    ██ ██   ██ ████   ██    ██    ██    ██ ████  ████
                                ██    ██ ██    ██ ███████ ██ ██  ██    ██    ██    ██ ██ ████ ██
                                ██ ▄▄ ██ ██    ██ ██   ██ ██  ██ ██    ██    ██    ██ ██  ██  ██
                                 ██████   ██████  ██   ██ ██   ████    ██     ██████  ██      ██
                                    ▀▀
                                ██████ ██      ██
                               ██      ██      ██
                               ██      ██      ██
                               ██      ██      ██
                                ██████ ███████ ██
                              ```

# Quantum-CLI Toolkit

**An AI-Integrated, Terminal-First Computational Physics Engine**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20WSL%20%7C%20macOS-lightgrey?style=flat-square)]()
[![Rich](https://img.shields.io/badge/UI-Rich%20Terminal-blueviolet?style=flat-square)](https://github.com/Textualize/rich)
[![SciPy](https://img.shields.io/badge/Physics-NumPy%20%7C%20SciPy-0C55A5?style=flat-square)](https://scipy.org/)
[![SymPy](https://img.shields.io/badge/CAS-SymPy-3B5526?style=flat-square)](https://www.sympy.org/)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=flat-square)]()

> *"Where the terminal meets the quantum."*
>
> A premium developer tool for exploring quantum mechanics and non-perturbative QCD —
> entirely from your terminal, with AI-guided natural language commands, publication-quality plots,
> and LaTeX export built in.

</div>

---

## Table of Contents

- [Overview](#overview)
- [Feature Highlights](#feature-highlights)
- [Architecture](#architecture)
  - [Project Structure](#project-structure)
  - [Data Flow](#data-flow)
  - [Component Breakdown](#component-breakdown)
- [Physics Engine](#physics-engine)
  - [Quantum Harmonic Oscillator](#quantum-harmonic-oscillator)
  - [KSS Viscosity Bound](#kss-viscosity-bound)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the CLI](#running-the-cli)
- [CLI Commands](#cli-commands)
- [Output & Exports](#output--exports)
- [Configuration](#configuration)
- [Roadmap — Upcoming Modules](#roadmap--upcoming-modules)
- [Technical Design Decisions](#technical-design-decisions)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Quantum-CLI Toolkit** is a terminal-based computational physics engine designed for physicists,
students, and developers who want a fast, scriptable, and beautiful interface for quantum
calculations — no Jupyter notebook, no GUI, no overhead.

At its core the toolkit couples a **rule-based AI agent** (a natural language parser) with a
rigorous **physics engine** backed by NumPy, SciPy, and SymPy. You type a plain-English
command — the agent interprets it, validates parameters, dispatches it to the correct
physics routine, generates a publication-quality dark-theme plot, and optionally exports a
full LaTeX document — all inside a single, self-contained terminal session.

The UI layer is built entirely on the [Rich](https://github.com/Textualize/rich) library,
giving you gradient banners, live spinners, colour-coded result panels, and structured data
tables that make the output feel like a premium developer tool rather than a script.

---

## Feature Highlights

| Feature | Detail |
|---|---|
| 🧠 **AI Natural Language Parser** | Type commands in plain English; the agent extracts quantum numbers, ranges, and flags automatically |
| ⚛ **QHO Wavefunction Solver** | Normalised ψ_n(x) and \|ψ_n(x)\|² up to n = 15, with classically forbidden region shading |
| 🌡 **KSS Viscosity Bound** | Computes ħ/(4πk_B) from CODATA constants; overlays hypothetical QGP data on a publication-ready plot |
| 📄 **LaTeX Export** | One-prompt export of full standalone `.tex` documents with symbolic SymPy expressions |
| 🎨 **Premium Rich UI** | Gradient ASCII banner, `console.status()` live spinners, colour-coded Panels and Tables |
| 🖤 **Dark-Theme Plots** | All Matplotlib output uses a GitHub-dark palette; headless `Agg` backend for WSL compatibility |
| 🔒 **Numerical Safety** | Natural-unit QHO prevents SI-unit Gaussian underflow; `MAX_N = 15` enforced to avoid Hermite instability |
| 📁 **Auto-managed Exports** | `assets/exports/` created at runtime if absent; never crashes on a missing directory |
| ⌨ **Plain-text Fallback** | `--no-rich` flag disables all Rich output for piped/scripted use |
| 🪵 **Centralised Logging** | `--verbose` flag enables DEBUG-level logging; all modules use named loggers |

---

## Architecture

### Project Structure

```
quantum-cli-toolkit/
│
├── main.py                    ← Entry point: arg parsing, DI wiring, REPL launch
│
├── core/                      ← Pure physics & logic — no UI dependencies
│   ├── __init__.py
│   ├── physics_engine.py      ← QuantumHarmonicOscillator, QCDConcepts, PhysicsEngine façade
│   ├── ai_agent.py            ← Natural language parser + command dispatcher
│   └── latex_generator.py     ← SymPy-backed LaTeX document generator
│
├── frontend/                  ← Terminal UI — depends on core, never imported by core
│   ├── __init__.py
│   └── cli_ui.py              ← Rich-powered REPL: banner, panels, spinners, prompts
│
└── assets/
    └── exports/               ← Auto-created at runtime; PNG plots + .tex files land here
```

> **Dependency rule:** `core/` modules have **zero imports from `frontend/`**.
> The UI layer imports from `core/`, never the reverse.
> This is enforced by design and prevents circular dependency crashes.

---

### Data Flow

The complete pipeline for a single user command:

```
User types:  "harmonic oscillator n=4"
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│  frontend/cli_ui.py  ·  QuantumCLI.run()                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Prompt.ask()  →  raw string input                   │   │
│  └──────────────────────────┬───────────────────────────┘   │
│                             │ user_input                     │
│                             ▼                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  _process_command()                                   │   │
│  │  1. ai.parse(user_input)        [instant, no spinner] │   │
│  │     → { action: "harmonic_oscillator", n: 4, ... }   │   │
│  │                                                       │   │
│  │  2. console.status("⚛ Solving…")  [live spinner]     │   │
│  │     ai.execute(parsed)                                │   │
│  │        └─ physics.harmonic_oscillator_wavefunction()  │   │
│  │              ├─ qho.wavefunction(n=4, x)              │   │
│  │              ├─ qho.probability_density(n=4, x)       │   │
│  │              ├─ qho.energy(n=4)       → SI Joules     │   │
│  │              └─ qho.plot_wavefunction() → PNG saved   │   │
│  │                                                       │   │
│  │  3. _display_ho_result(data)   [Rich Panel + Table]   │   │
│  │                                                       │   │
│  │  4. _offer_latex()             [optional Prompt]      │   │
│  │     └─ latex.generate_and_save("harmonic_oscillator") │   │
│  │           └─ sympy.hermite(4, x)  →  .tex saved       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
  assets/exports/
  ├── qho_n4_wavefunction.png   ← dark-theme Matplotlib plot
  └── qho_n4.tex                ← standalone LaTeX document
```

---

### Component Breakdown

#### `main.py` — Entry Point & Dependency Injection

The root script is intentionally thin. It owns three responsibilities and nothing else:

1. **Argument parsing** via `argparse` (`--export-dir`, `--no-rich`, `--verbose`)
2. **Dependency wiring** — instantiates `PhysicsEngine`, `AIAgent`, `LaTeXGenerator`, and `QuantumCLI` in the correct order, injecting each into the next
3. **Launching the REPL** with a top-level `KeyboardInterrupt` guard

All components receive their dependencies via constructor arguments (dependency injection).
No module reaches for global state or imports a sibling's internals directly.

---

#### `core/physics_engine.py` — The Physics Engine

Three classes, each with a single responsibility:

| Class | Role |
|---|---|
| `QuantumHarmonicOscillator` | Wavefunction math, energy eigenvalues, classical turning points, plotting |
| `QCDConcepts` | KSS bound computation, hypothetical QGP data generation, bound plot |
| `PhysicsEngine` | Thin façade — the only class the rest of the application ever touches |

The façade pattern keeps `AIAgent` and `QuantumCLI` decoupled from the internal class
hierarchy. If `QuantumHarmonicOscillator` is refactored or replaced, nothing outside
`physics_engine.py` changes.

---

#### `core/ai_agent.py` — The AI Agent

A rule-based natural language interpreter using pre-compiled regular expressions.
It simulates an AI command parser without any external model dependency, making the
toolkit fully self-contained and offline-capable.

The agent exposes a strict two-method API:

```python
parsed = agent.parse("harmonic oscillator n=7 range -10 to 10")
# → { 'action': 'harmonic_oscillator', 'parameters': {'n': 7, 'x_range': (-10.0, 10.0)}, ... }

result = agent.execute(parsed)
# → { 'success': True, 'message': '...', 'data': { 'energy': ..., 'plot_path': ... } }
```

All numeric extraction and type validation happens inside the agent, so the physics
engine is never handed a string where it expects an integer.

---

#### `core/latex_generator.py` — LaTeX Export

Generates complete, compilable standalone `.tex` documents using SymPy for symbolic
expression rendering. For the QHO, SymPy evaluates `sp.hermite(n, x)` and converts the
result to LaTeX notation automatically — so `n=3` produces `H_3(x) = 8x^3 - 12x`
rendered properly as a mathematical expression.

Both documents include a full preamble (`amsmath`, `amssymb`, `geometry`, `hyperref`) and
are ready to compile with `pdflatex` without modification.

---

#### `frontend/cli_ui.py` — The Rich Terminal UI

The UI layer is fully decoupled from physics logic. It knows how to:

- **Render** structured result dicts as styled `Panel` + `Table` combinations
- **Display** live `console.status()` spinners during computation
- **Route** special commands (`help`, `exit`) before they ever reach the physics engine
- **Degrade gracefully** to plain text with `--no-rich`

The `_process_command()` method is the central dispatch point:

```
parse()  →  route special  →  execute() [under spinner]  →  display  →  offer LaTeX
```

---

## Physics Engine

### Quantum Harmonic Oscillator

The 1D QHO is the cornerstone of quantum mechanics. The toolkit solves it exactly using
the Hermite polynomial representation of the energy eigenstates.

**Unit Convention: Natural Units (ħ = m = ω = 1)**

Wavefunction calculations operate in dimensionless natural units where the position `x`
is expressed in multiples of the characteristic length scale x₀ = √(ħ/mω). This is a
deliberate design choice, not a simplification.

Using SI units would set α = √(mω/ħ) ≈ 3×10¹⁶ m⁻¹ for default parameters. For any
x in the range (-5, 5) metres, the Gaussian factor becomes:

```
exp(−α²x²/2) = exp(−~10³⁴)  ≡  0.0   (IEEE 754 underflow)
```

Every wavefunction would be identically zero. Natural units eliminate this entirely.
Physical energies are still returned in SI Joules via `scipy.constants.hbar`.

**The Wavefunction Formula**

$$\psi_n(x) = \frac{1}{\sqrt{\sqrt{\pi}\, 2^n\, n!}} \; H_n(x) \; e^{-x^2/2}$$

where x is dimensionless (in units of x₀) and H_n is the physicists' Hermite polynomial
of degree n, evaluated via `scipy.special.hermite`.

**What the Plot Shows**

Each plot is a two-panel dark-theme figure:

- **Top panel:** ψ_n(x) — the wavefunction, showing nodes and oscillations
- **Bottom panel:** |ψ_n(x)|² — the probability density, with `fill_between` shading
- **Both panels:** Classically forbidden regions shaded red; classical turning points
  ±x_tp = ±√(2n+1) marked with dashed vertical lines and annotated with arrows

**Supported levels:** n = 0 through n = 15. Above n = 15, Hermite polynomial evaluation
via double-precision arithmetic suffers catastrophic cancellation and the results are
unreliable. This limit is enforced in `QuantumHarmonicOscillator.MAX_N`.

---

### KSS Viscosity Bound

The Kovtun–Son–Starinets (KSS) bound is a landmark result in non-perturbative QCD,
derived via the AdS/CFT (gauge/gravity) duality:

$$\frac{\eta}{s} \;\geq\; \frac{\hbar}{4\pi k_B}$$

where η is the shear viscosity and s is the entropy density of any relativistic quantum
fluid that admits a classical gravity dual.

**Why It Matters**

The quark-gluon plasma (QGP) produced at RHIC and the LHC has been experimentally
measured with η/s very close to — but always above — this bound. This makes QGP the most
perfect liquid ever created in a laboratory, and the KSS bound the most stringent
constraint on fluid dynamics in all of physics.

**Numerical Value (CODATA 2018)**

```
ħ / (4π k_B)  =  1.054571817 × 10⁻³⁴ J·s
                 ────────────────────────────────
                 4π × 1.380649 × 10⁻²³ J/K

              ≈  6.079 × 10⁻¹³  K·s
```

**What the Plot Shows**

- Horizontal dashed amber line: the KSS bound value (constant, temperature-independent)
- Red shaded region below the line: classically forbidden (no fluid can exist here)
- Optional blue data points: hypothetical QGP measurements in the deconfinement regime
  (T ≈ 170–500 MeV/k_B), illustrating near-perfect-liquid behaviour near the bound
- Temperature axis expressed in units of the deconfinement temperature T_c ≈ 170 MeV/k_B

---

## Getting Started

### Prerequisites

- Python **3.10** or later
- A Linux, WSL, or macOS terminal
- `pip` package manager

Optional but recommended:

- A terminal with **true-colour** support (Windows Terminal, iTerm2, GNOME Terminal, Kitty)
  for full gradient rendering
- `pdflatex` for compiling the exported `.tex` files

---

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/quantum-cli-toolkit.git
cd quantum-cli-toolkit
```

**2. Create a virtual environment** (strongly recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should contain:

```
numpy>=1.24
scipy>=1.11
matplotlib>=3.7
sympy>=1.12
rich>=13.0
```

**4. Verify the install**

```bash
python3 -c "import rich, scipy, sympy, matplotlib; print('All dependencies OK')"
```

---

### Running the CLI

**Standard launch (full Rich UI):**

```bash
python3 main.py
```

**Custom export directory:**

```bash
python3 main.py --export-dir ~/physics_results
```

**Plain-text mode (for piped/scripted use):**

```bash
python3 main.py --no-rich
```

**Verbose debug logging:**

```bash
python3 main.py --verbose
```

**Show help without entering the REPL:**

```bash
python3 main.py --help
```

---

## CLI Commands

Once inside the REPL, the AI agent interprets natural language. You don't need to memorise
exact syntax — the agent is designed to handle natural phrasing.

| Intent | Example inputs |
|---|---|
| **QHO ground state** | `harmonic oscillator`, `qho n=0`, `wavefunction` |
| **QHO excited state** | `harmonic oscillator n=5`, `oscillator level 3` |
| **QHO with custom range** | `harmonic oscillator n=4 range -8 to 8` |
| **KSS bound (bare)** | `kss bound`, `show kovtun bound`, `qcd viscosity` |
| **KSS bound + QGP data** | `kss bound with sample data`, `show kss with hypothetical data` |
| **Help table** | `help`, `?` |
| **Exit** | `exit`, `quit`, `bye` |

**Example session:**

```
quantum❯  harmonic oscillator n=3

  ┌─────────────────────────────────────────────────┐
  │ ✔  Quantum Harmonic Oscillator                  │
  │  Quantum level   n = 3                          │
  │  Energy (SI)     5.274e-34 J                    │
  │  Energy (nat.)   3.5 ħω                         │
  │  Classical x_tp  ±2.6458 x₀                    │
  │  Plot saved      assets/exports/qho_n3_...png   │
  └─────────────────────────────────────────────────┘

  Generate LaTeX report? [y/n] (n): y
  📄  LaTeX saved → assets/exports/qho_n3.tex

quantum❯  kss bound with sample data

  ┌────────────────────────────────────────────────────────┐
  │ ✔  KSS Viscosity Bound                                 │
  │  Bound  η/s ≥    6.079443e-13 K·s                     │
  │  Formula         ħ / (4π k_B)                         │
  │  Physical system Quark-Gluon Plasma (QGP)              │
  │  Reference       Kovtun, Son & Starinets (2005)        │
  │  Plot saved      assets/exports/kss_bound.png          │
  └────────────────────────────────────────────────────────┘
```

---

## Output & Exports

All exports land in `assets/exports/` (or your `--export-dir` path), which is created
automatically if it does not exist.

| File | Generated by | Description |
|---|---|---|
| `qho_n{N}_wavefunction.png` | QHO command | Two-panel dark-theme wavefunction plot |
| `kss_bound.png` | KSS command | KSS bound plot with optional QGP data overlay |
| `qho_n{N}.tex` | LaTeX export (QHO) | Standalone LaTeX with SymPy symbolic expressions |
| `kss_bound.tex` | LaTeX export (KSS) | Standalone LaTeX with CODATA numerical values |

**Compiling a LaTeX export:**

```bash
cd assets/exports
pdflatex qho_n3.tex
```

---

## Configuration

All runtime options are set via command-line flags — no config files required.

| Flag | Default | Description |
|---|---|---|
| `--export-dir PATH` | `assets/exports` | Output directory for plots and LaTeX files |
| `--no-rich` | `False` | Disable Rich UI; fall back to plain text |
| `--verbose` | `False` | Enable DEBUG-level logging to stdout |

The export path is always resolved relative to the `main.py` directory, so the CLI
behaves consistently regardless of which working directory you invoke it from.

---

## Roadmap — Upcoming Modules

The Quantum-CLI Toolkit is under active development. The following physics modules and
platform features are planned for future releases.

---

### 🔬 v1.1 — Quantum Mechanics Expansion

**Finite Square Well**
Numerical shooting-method solution for bound states in a finite potential well.
Transcendental eigenvalue equation solved with `scipy.optimize.brentq`. Interactive
depth and width parameters.

**Hydrogen Atom Radial Wavefunctions**
Exact analytical solutions R_nl(r) via associated Laguerre polynomials. 2D
probability density contour plots for s, p, d orbitals. Bohr radius units.

**Particle in a Box (1D and 2D)**
Exact analytical solutions for infinite square well in 1D and 2D. Heatmap
visualisation of probability density in 2D. Energy level ladder diagram.

**Quantum Tunnelling**
Transfer matrix method for rectangular barrier. Transmission and reflection
coefficients T(E) and R(E) as functions of energy. Evanescent wave visualisation
inside the barrier.

---

### 🌊 v1.2 — Wave Mechanics & Field Theory

**Fourier Analysis of Wavefunctions**
Momentum-space representation ψ̃(p) via FFT. Side-by-side position/momentum
space panels illustrating the Heisenberg uncertainty principle numerically.

**1D Schrödinger Equation — Arbitrary Potential**
Numerix solver (Numerov method) for any user-supplied V(x). Supports double-well
potentials, Morse potential, and Pöschl–Teller. Bound state spectrum output.

**Coherent States**
Time-evolution of coherent states |α⟩ in the QHO. Animated GIF output of the
Wigner function showing the state rotating in phase space.

---

### 🔴 v1.3 — Quantum Chromodynamics & Heavy-Ion Physics

**Running Coupling αs(Q²)**
One-loop and two-loop QCD running coupling constant as a function of momentum
scale Q. Asymptotic freedom visualised with the Landau pole and ΛQCD marked.

**Debye Screening in QGP**
Debye screening mass m_D(T) as a function of temperature in the QGP phase.
Colour-electric screening vs colour-magnetic sector comparison.

**Quark-Gluon Plasma Phase Diagram**
Schematic T–μ (temperature vs baryon chemical potential) phase diagram.
Marking: hadronic phase, QGP phase, colour superconductivity region, and
the conjectured critical endpoint.

**Bjorken Flow**
Bjorken's 1D hydrodynamic model for heavy-ion collisions. Energy density
ε(τ) as a function of proper time τ. Entropy production and cooling rate
computation.

---

### 🤖 v1.4 — AI Agent Upgrade

**LLM Backend Integration**
Optional integration with a local LLM (Ollama / llama.cpp) or cloud API
(Anthropic Claude, OpenAI) for true natural language understanding, multi-turn
context, and physics Q&A. The rule-based parser remains the default for
offline/low-latency use.

**Parameter Inference from Context**
Agent learns from command history within a session. "Run it again for n=5"
or "now try with sample data" resolved correctly using session context.

**Error Explanation**
When a computation fails or a parameter is invalid, the agent provides a
physics-aware explanation rather than a raw Python exception message.

---

### 📊 v1.5 — Visualisation & Export Upgrades

**Interactive Plots via Plotext**
In-terminal ASCII plots using `plotext` as a zero-dependency preview before
the full Matplotlib PNG is generated. Renders inline in the terminal without
opening any files.

**Animated GIF Export**
Time-evolution animations for wave packets and coherent states. Uses
Matplotlib's `FuncAnimation` with the `Pillow` writer. Frame rate and
duration configurable from the CLI.

**Jupyter Notebook Export**
`--export-notebook` flag generates a `.ipynb` file containing all code,
results, and inline plots from the current session. Runnable in JupyterLab
with zero modification.

**PDF Report**
Single-command `--export-pdf` generates a multi-section PDF report
combining all plots and LaTeX from a session, compiled via `pdflatex`
or the `reportlab` pure-Python backend.

---

### ⚡ v2.0 — Multi-Particle & Many-Body Physics

**Variational Quantum Eigensolver (VQE) Simulator**
Classical simulation of the VQE algorithm for small molecular Hamiltonians.
Helium ground state energy estimation. Bridge to quantum computing concepts
without requiring actual quantum hardware.

**Density Functional Theory (DFT) — Toy Model**
Thomas–Fermi and Kohn–Sham DFT for 1D electron gas. Demonstrates
self-consistent field iteration. Exchange-correlation functional comparison.

**Bose–Einstein Condensation**
Gross–Pitaevskii equation solver in 1D and 2D (imaginary time evolution).
Phase diagram for BEC transition. Vortex structure visualisation in 2D.

---

## Technical Design Decisions

**Why natural units for the QHO?**
SI units with default parameters (m = 1 kg, ω = 1 rad/s) produce α ≈ 3×10¹⁶ m⁻¹.
For x in metres, the Gaussian `exp(-α²x²/2)` underflows to exactly zero in IEEE 754
double precision for any x > ~10⁻¹⁶ m. Natural units eliminate this entirely while
preserving the full physical content. See `physics_engine.py` module docstring.

**Why `matplotlib.use("Agg")` before any other matplotlib import?**
WSL and headless Linux environments have no display server. Any attempt to initialise
the default interactive backend crashes immediately with a `cannot connect to X server`
error. The `Agg` (Anti-Grain Geometry) backend renders to raster buffers in memory and
writes directly to files — no display required. It must be set before `pyplot` is first
imported, hence the placement at the very top of `physics_engine.py`.

**Why dependency injection in `main.py`?**
Each component (`PhysicsEngine`, `AIAgent`, `LaTeXGenerator`, `QuantumCLI`) receives its
dependencies via constructor arguments. No module imports another module's instances from
a global. This means any component can be mocked, replaced, or tested in isolation without
touching the rest of the codebase.

**Why a façade (`PhysicsEngine`) over the physics sub-classes?**
`AIAgent` and `QuantumCLI` only ever call `PhysicsEngine.harmonic_oscillator_wavefunction()`
and `PhysicsEngine.kss_bound()`. If `QuantumHarmonicOscillator` is later refactored, split
into multiple classes, or backed by a GPU solver, nothing outside `physics_engine.py` changes.

**Why `MAX_N = 15`?**
SciPy's `hermite(n)` returns a `numpy.poly1d` object computed from the recurrence relation.
For n > ~15, the large intermediate polynomial coefficients combined with the `exp(-x²/2)`
Gaussian cause catastrophic numerical cancellation in double precision. The wavefunction
ceases to be properly normalised. `MAX_N` is enforced at both the agent (clamping with a
warning) and the engine (raising a `ValueError`) so the limit is communicated clearly.

---

## Contributing

Contributions are welcome. Before opening a pull request:

1. Fork the repository and create a feature branch: `git checkout -b feature/new-module`
2. Follow the existing code style: type hints on all public methods, named loggers per module, docstrings on every class and method
3. Keep `core/` free of any `frontend/` imports — the dependency direction is one-way
4. New physics modules belong in `core/physics_engine.py` (or a new submodule imported through the `PhysicsEngine` façade)
5. New CLI commands require: a parser pattern in `ai_agent.py`, a display method in `cli_ui.py`, and a LaTeX template in `latex_generator.py`

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ⚛ by physicists, for physicists — and the developers who love them.

*"The career of a young theoretical physicist consists of treating the harmonic oscillator in ever-increasing levels of abstraction."*
— Sidney Coleman

</div>
