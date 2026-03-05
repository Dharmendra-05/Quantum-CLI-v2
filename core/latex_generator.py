"""
LaTeX Generator Module
======================
Produces standalone .tex documents for physics results.
Uses SymPy for symbolic expression rendering.
"""

import logging
from pathlib import Path
from typing import Optional

import sympy as sp
from sympy import latex as sp_latex

logger = logging.getLogger(__name__)


class LaTeXGenerator:
    """
    Generates and saves LaTeX documents for QHO and KSS results.
    """

    def __init__(self, export_dir: Path) -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _save_tex(self, content: str, filename: str) -> Path:
        """Write *content* to <export_dir>/<filename>.tex and return the path."""
        filepath = self.export_dir / f"{filename}.tex"
        filepath.write_text(content, encoding="utf-8")
        logger.info("LaTeX saved → %s", filepath)
        return filepath

    @staticmethod
    def _preamble(title: str) -> str:
        """Return a minimal but complete LaTeX preamble."""
        return (
            r"\documentclass{article}" + "\n"
            r"\usepackage[utf8]{inputenc}" + "\n"
            r"\usepackage{amsmath, amssymb}" + "\n"
            r"\usepackage[a4paper, margin=1in]{geometry}" + "\n"
            r"\usepackage{hyperref}" + "\n\n"
            rf"\title{{{title}}}" + "\n"
            r"\author{Quantum-CLI Toolkit}" + "\n"
            r"\date{\today}" + "\n"
        )

    # ── Document generators ───────────────────────────────────────────────────

    def harmonic_oscillator_tex(self, n: int, energy: float) -> str:
        """
        Full LaTeX document for QHO level n.

        Parameters
        ----------
        n      : Quantum number.
        energy : Energy eigenvalue in Joules.
        """
        x = sp.Symbol("x", real=True)
        try:
            H_n     = sp.hermite(n, x)
            psi_sym = H_n * sp.exp(-x ** 2 / 2)
            psi_tex = sp_latex(psi_sym)
        except Exception:
            logger.warning("SymPy failed to evaluate H_%d; using placeholder.", n)
            psi_tex = r"H_{n}(x)\,e^{-x^2/2}"

        e_nat  = n + 0.5
        x_tp   = sp.sqrt(2 * n + 1)

        doc = self._preamble("Quantum Harmonic Oscillator Results")
        doc += rf"""
\begin{{document}}
\maketitle

\section{{Energy Level $n = {n}$}}

The energy eigenvalue is
\[
  E_{{{n}}} = \hbar\omega\!\left(n + \tfrac{{1}}{{2}}\right)
            = {e_nat}\,\hbar\omega
            = {energy:.6e}~\text{{J}}.
\]

\section{{Wavefunction in Natural Units ($\hbar = m = \omega = 1$)}}

With the dimensionless coordinate $x$ expressed in units of
$x_0 = \sqrt{{\hbar/m\omega}}$, the normalised wavefunction is
\[
  \psi_{{{n}}}(x)
  = \frac{{1}}{{\sqrt{{\sqrt{{\pi}}\,2^{{{n}}}\,{n}!}}}}
    \,H_{{{n}}}(x)\,e^{{-x^2/2}},
\]
where $H_{{{n}}}$ is the physicists' Hermite polynomial of degree ${n}$.
Explicitly:
\[
  \psi_{{{n}}}(x) \;\propto\; {psi_tex}.
\]

The classical turning points satisfy $E_n = \tfrac{{1}}{{2}}x_{{tp}}^2$,
giving
\[
  x_{{tp}} = \pm\sqrt{{2n+1}} = \pm{sp_latex(x_tp)} \approx \pm{float(x_tp):.4f}\,x_0.
\]

\end{{document}}
"""
        return doc

    def kss_bound_tex(self, bound_value: float) -> str:
        """
        Full LaTeX document for the KSS viscosity bound.

        Parameters
        ----------
        bound_value : ħ/(4π k_B) in K·s.
        """
        doc = self._preamble("KSS Viscosity Bound in QCD")
        doc += rf"""
\begin{{document}}
\maketitle

\section{{The Kovtun--Son--Starinets (KSS) Bound}}

Via the AdS/CFT (gauge/gravity) duality, Kovtun, Son, and Starinets (2005)
conjectured that for \emph{{any}} relativistic fluid described by a
classical gravity dual,
\[
  \frac{{\eta}}{{s}} \;\geq\; \frac{{\hbar}}{{4\pi k_B}},
\]
where $\eta$ is the shear viscosity and $s$ the entropy density.

\section{{Numerical Value}}

Using CODATA 2018 fundamental constants:
\[
  \frac{{\hbar}}{{4\pi k_B}}
  = \frac{{1.054\,571\,817 \times 10^{{-34}}~\text{{J\,s}}}}
         {{4\pi \times 1.380\,649 \times 10^{{-23}}~\text{{J/K}}}}
  = {bound_value:.6e}~\text{{K\,s}}.
\]

\section{{Physical Significance}}

The quark-gluon plasma (QGP) created at RHIC and the LHC has been measured
with $\eta/s$ very close to---but above---this bound, making it the most
perfect liquid known in nature and the first experimental realisation of a
strongly-coupled quantum fluid near the KSS limit.

\end{{document}}
"""
        return doc

    # ── High-level API ────────────────────────────────────────────────────────

    def generate_and_save(self, topic: str, **kwargs) -> Optional[Path]:
        """
        Generate and save a LaTeX document for the given physics topic.

        Parameters
        ----------
        topic    : 'harmonic_oscillator' or 'kss_bound'.
        **kwargs : Topic-specific keyword arguments.

        Returns
        -------
        Path to the saved .tex file, or None if the topic is unknown.
        """
        if topic == "harmonic_oscillator":
            n      = int(kwargs.get("n", 0))
            energy = float(kwargs.get("energy", 0.0))
            return self._save_tex(self.harmonic_oscillator_tex(n, energy), f"qho_n{n}")

        if topic == "kss_bound":
            bound = float(kwargs.get("bound_value", 0.0))
            return self._save_tex(self.kss_bound_tex(bound), "kss_bound")

        logger.warning("Unknown LaTeX topic: %r", topic)
        return None
