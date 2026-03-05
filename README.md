# ⚛️ Quantum-CLI Toolkit
### A Terminal-Based, AI-Integrated Computational Physics Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/SciPy-1.17-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white"/>
  <img src="https://img.shields.io/badge/NumPy-2.4-013243?style=for-the-badge&logo=numpy&logoColor=white"/>
  <img src="https://img.shields.io/badge/Rich-CLI-11557C?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

---

## 🔭 Overview
The **Quantum-CLI Toolkit** is a headless, terminal-first computational physics environment. It leverages an AI parser to translate natural language commands into high-performance NumPy/SciPy operations. Designed for researchers and Linux power users, it generates publication-ready plots and LaTeX reports entirely from the command line.

## 🧮 The Physics Engine

This toolkit currently simulates two primary physical domains:

### 1. 1D Quantum Harmonic Oscillator (QHO)
Calculates exact, analytic eigenstates and probability densities using physicists' Hermite polynomials $H_n(\xi)$. 
The energy quantization is given by:
$$E_n = \left(n + \frac{1}{2}\right)\hbar\omega$$

### 2. Quantum Chromodynamics (QCD) & The KSS Bound
A specialized module evaluating non-perturbative properties of quark-gluon plasmas. It calculates the Kovtun-Son-Starinets (KSS) bound for the ratio of shear viscosity $\eta$ to entropy density $s$:
$$\frac{\eta}{s} \ge \frac{\hbar}{4\pi k_B}$$
This represents the most perfect fluid allowed by the laws of quantum mechanics.

## 🏗️ Project Architecture

```text
quantum-cli-toolkit/
├── main.py                 # CLI entry point and event loop
├── core/
│   ├── __init__.py
│   ├── physics_engine.py   # OOP math backend (NumPy/SciPy)
│   ├── ai_agent.py         # Natural language command parser
│   └── latex_generator.py  # Auto-compiles physics data to .tex
├── frontend/
│   ├── __init__.py
│   └── cli_ui.py           # Rich-based Text User Interface (TUI)
└── assets/
    ├── exports/            # Auto-saved Matplotlib plots & LaTeX PDFs
    └── logs/               # Application debug logs
