"""
Physics Engine Module
=====================
Implements core physics calculations: 1D Quantum Harmonic Oscillator (QHO) and
the Kovtun–Son–Starinets (KSS) viscosity bound from non-perturbative QCD.

UNIT CONVENTION
---------------
QHO wavefunction calculations use **natural / dimensionless units** where
ħ = m = ω = 1.  In these units α = √(mω/ħ) = 1 and x is measured in
multiples of the characteristic length scale  x₀ = √(ħ/mω).

  - energy()          → SI Joules      (uses scipy.constants.hbar)
  - wavefunction(x)   → dimensionless x  (x is in units of x₀)
  - plot x-axis label → "x / x₀  (dimensionless)"

This choice avoids the catastrophic numerical underflow that occurs when SI
positions (metres) are multiplied by α ≈ 3×10¹⁶ m⁻¹, which drives the
Gaussian exp(−α²x²/2) to exactly zero for any x > ~10⁻¹⁶ m.
"""

# ── Matplotlib backend MUST be set before pyplot is imported ─────────────────
import matplotlib
matplotlib.use("Agg")          # Headless / no-GUI — essential for WSL / servers
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import constants
from scipy.special import hermite as _scipy_hermite
from scipy.special import factorial
from pathlib import Path
import logging
from typing import Dict, Optional, Tuple, Union

logger = logging.getLogger(__name__)


# ── Dark-theme colour palette (GitHub-dark) ───────────────────────────────────
_BG       = "#0d1117"
_AX_BG    = "#161b22"
_GRID     = "#21262d"
_BORDER   = "#30363d"
_TEXT     = "#c9d1d9"
_TEXT_DIM = "#8b949e"
_BLUE     = "#58a6ff"
_BLUE_LT  = "#79c0ff"
_GREEN    = "#3fb950"
_ORANGE   = "#d29922"
_RED      = "#f85149"


def _style_axes(ax: plt.Axes) -> None:
    """Apply the dark-theme palette to a Matplotlib Axes object in-place."""
    ax.set_facecolor(_AX_BG)
    ax.tick_params(colors=_TEXT_DIM, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(_BORDER)
    ax.xaxis.label.set_color(_TEXT_DIM)
    ax.yaxis.label.set_color(_TEXT_DIM)
    ax.title.set_color(_TEXT)
    ax.grid(True, color=_GRID, linewidth=0.6, alpha=0.85)


# ─────────────────────────────────────────────────────────────────────────────
# Quantum Harmonic Oscillator
# ─────────────────────────────────────────────────────────────────────────────

class QuantumHarmonicOscillator:
    """
    1D Quantum Harmonic Oscillator.

    Wavefunction calculations operate in **natural units** (ħ = m = ω = 1)
    so that α = 1 and x is dimensionless (in units of x₀ = √(ħ/mω)).
    Physical energies are returned in SI Joules via ``energy()``.

    Attributes
    ----------
    mass  : float – particle mass in kg  (default 1.0)
    omega : float – angular frequency in rad/s  (default 1.0)
    hbar  : float – reduced Planck constant from scipy.constants (J·s)
    """

    #: Highest quantum number supported before Hermite polynomial evaluation
    #: becomes numerically unreliable due to catastrophic cancellation.
    MAX_N: int = 15

    def __init__(self, mass: float = 1.0, omega: float = 1.0) -> None:
        if mass <= 0:
            raise ValueError(f"mass must be positive, got {mass!r}")
        if omega <= 0:
            raise ValueError(f"omega must be positive, got {omega!r}")
        self.mass  = float(mass)
        self.omega = float(omega)
        self.hbar  = constants.hbar   # J·s  (CODATA 2018)

    # ── Physical observables ──────────────────────────────────────────────────

    def energy(self, n: int) -> float:
        """
        Energy eigenvalue  E_n = ħω(n + ½)  in **Joules**.

        Raises
        ------
        TypeError  if n is not an integer.
        ValueError if n < 0 or n > MAX_N.
        """
        self._validate_n(n)
        return self.hbar * self.omega * (n + 0.5)

    def energy_natural(self, n: int) -> float:
        """Energy in natural units: E_n / (ħω) = n + ½."""
        self._validate_n(n)
        return float(n) + 0.5

    def x0(self) -> float:
        """Characteristic length scale  x₀ = √(ħ/(mω))  in metres."""
        return float(np.sqrt(self.hbar / (self.mass * self.omega)))

    def classical_turning_point(self, n: int) -> float:
        """
        Classical turning point in **natural units**:  x_tp = √(2n + 1).

        Derivation: E_n = ½mω²x_tp² → x_tp = √(2E_n/(mω²)) = √(2n+1) · x₀.
        In dimensionless coordinates (divide by x₀): x_tp = √(2n + 1).
        """
        self._validate_n(n)
        return float(np.sqrt(2 * n + 1))

    # ── Wavefunction ──────────────────────────────────────────────────────────

    def wavefunction(
        self, n: int, x: npt.NDArray[np.float64]
    ) -> npt.NDArray[np.float64]:
        """
        Normalised wavefunction  ψ_n(x)  in **natural units** (α = 1):

            ψ_n(x) = [1 / (√π · 2ⁿ · n!)]^(1/2)  ·  H_n(x)  ·  exp(−x²/2)

        Normalisation: ∫ |ψ_n(x)|² dx = 1  (x dimensionless in units of x₀).

        Parameters
        ----------
        n : quantum number  (0 ≤ n ≤ MAX_N)
        x : position array in **natural units** (dimensionless)

        Returns
        -------
        Array with the same shape as x.
        """
        self._validate_n(n)
        x = np.asarray(x, dtype=np.float64)

        # Prefactor  — stable for n ≤ MAX_N ≈ 15
        norm = float(factorial(n, exact=False))          # n!  as float64
        prefactor = 1.0 / np.sqrt(np.sqrt(np.pi) * (2.0 ** n) * norm)

        H_n = _scipy_hermite(n)(x)                      # scipy poly1d object
        return prefactor * H_n * np.exp(-0.5 * x ** 2)

    def probability_density(
        self, n: int, x: npt.NDArray[np.float64]
    ) -> npt.NDArray[np.float64]:
        """Probability density  |ψ_n(x)|²  in natural units."""
        return self.wavefunction(n, x) ** 2

    # ── Plotting ──────────────────────────────────────────────────────────────

    def plot_wavefunction(
        self,
        n: int,
        x_range: Optional[Tuple[float, float]] = None,
        num_points: int = 1200,
        save_path: Optional[Union[str, Path]] = None,
    ) -> plt.Figure:
        """
        Two-panel figure: ψ_n(x) (top) and |ψ_n(x)|² (bottom).

        Classically forbidden regions are shaded red.  Classical turning points
        ±x_tp = ±√(2n+1) are marked with dashed vertical lines and annotated.

        Parameters
        ----------
        n          : Quantum number.
        x_range    : (x_min, x_max) in **natural units**.  Auto-computed when
                     None to comfortably frame the classical turning points.
        num_points : Grid resolution.
        save_path  : PNG output path.  Figure is **always** closed after saving
                     to prevent memory leaks.

        Returns
        -------
        Closed Matplotlib Figure object (do not attempt to display it).
        """
        self._validate_n(n)

        # ── Auto-compute x_range to frame the classical turning points ────────
        x_tp = self.classical_turning_point(n)
        if x_range is None:
            pad = max(2.5, 0.4 * x_tp)
            x_range = (-(x_tp + pad), x_tp + pad)
        else:
            xlo, xhi = float(x_range[0]), float(x_range[1])
            if xlo >= xhi:
                raise ValueError(
                    f"x_range must satisfy x_min < x_max, got ({xlo}, {xhi})"
                )
            x_range = (xlo, xhi)

        x    = np.linspace(x_range[0], x_range[1], num_points)
        psi  = self.wavefunction(n, x)
        prob = self.probability_density(n, x)
        E_nat = self.energy_natural(n)

        # ── Figure / axes setup ───────────────────────────────────────────────
        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(10, 7.5),
            facecolor=_BG, constrained_layout=True,
        )
        fig.suptitle(
            rf"Quantum Harmonic Oscillator  ·  $n = {n}$"
            rf"  ·  $E_{{{n}}} = {E_nat:.1f}\,\hbar\omega$",
            color=_TEXT, fontsize=13, fontweight="bold",
        )

        # Shared decoration for both axes
        for ax in (ax1, ax2):
            _style_axes(ax)
            # Shade classically forbidden regions
            ax.axvspan(x_range[0], -x_tp, alpha=0.12, color=_RED, lw=0)
            ax.axvspan( x_tp, x_range[1], alpha=0.12, color=_RED, lw=0)
            # Classical turning-point markers
            ax.axvline(-x_tp, color=_RED, alpha=0.50, lw=0.9, ls="--")
            ax.axvline( x_tp, color=_RED, alpha=0.50, lw=0.9, ls="--")

        # ── Panel 1: Wavefunction ─────────────────────────────────────────────
        ax1.plot(x, psi, color=_BLUE, lw=1.8, label=rf"$\psi_{{{n}}}(x)$")
        ax1.axhline(0.0, color=_BORDER, lw=0.6)
        ax1.set_ylabel(rf"$\psi_{{{n}}}(x)$", fontsize=11)
        ax1.legend(
            facecolor=_BG, edgecolor=_BORDER, labelcolor=_TEXT,
            fontsize=10, loc="upper right",
        )

        # ── Panel 2: Probability density ──────────────────────────────────────
        ax2.fill_between(x, prob, alpha=0.22, color=_GREEN)
        ax2.plot(x, prob, color=_GREEN, lw=1.8, label=rf"$|\psi_{{{n}}}(x)|^2$")
        ax2.set_xlabel(
            r"Position   $x\,/\,x_0$   (dimensionless,  "
            r"$x_0 = \sqrt{\hbar / m\omega}$)",
            fontsize=10,
        )
        ax2.set_ylabel(r"$|\psi_n(x)|^2$", fontsize=11)

        # Annotate turning points on probability panel
        y_peak = float(np.max(prob))
        for sign_val, ha in ((-x_tp, "right"), (x_tp, "left")):
            sign_str = "−" if sign_val < 0 else "+"
            ax2.annotate(
                rf"$x_\mathrm{{tp}}{sign_str}{x_tp:.2f}\,x_0$",
                xy=(sign_val, 0.0),
                xytext=(sign_val + (0.4 if ha == "left" else -0.4), y_peak * 0.55),
                color=_RED, fontsize=8, alpha=0.88, ha=ha,
                arrowprops=dict(arrowstyle="->", color=_RED, alpha=0.5, lw=0.8),
            )
        ax2.legend(
            facecolor=_BG, edgecolor=_BORDER, labelcolor=_TEXT,
            fontsize=10, loc="upper right",
        )

        # ── Save ──────────────────────────────────────────────────────────────
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=_BG)
            logger.info("Saved wavefunction plot → %s", save_path)

        plt.close(fig)   # Always close — prevents memory leak across sessions
        return fig

    # ── Validation ────────────────────────────────────────────────────────────

    @classmethod
    def _validate_n(cls, n: object) -> None:
        if not isinstance(n, (int, np.integer)):
            raise TypeError(
                f"Quantum number n must be an integer, "
                f"got {type(n).__name__}: {n!r}"
            )
        if int(n) < 0:
            raise ValueError(f"Quantum number n must be ≥ 0, got {n}")
        if int(n) > cls.MAX_N:
            raise ValueError(
                f"n = {n} exceeds MAX_N = {cls.MAX_N} "
                "(numerical stability limit for Hermite polynomial evaluation)"
            )


# ─────────────────────────────────────────────────────────────────────────────
# QCD Concepts — KSS Bound
# ─────────────────────────────────────────────────────────────────────────────

class QCDConcepts:
    """
    Selected non-perturbative QCD concepts.

    Currently implements the Kovtun–Son–Starinets (KSS) viscosity bound:

        η/s  ≥  ħ / (4π k_B)

    derived via the AdS/CFT (gauge/gravity) duality.
    """

    def __init__(self) -> None:
        self.hbar = constants.hbar   # J·s
        self.k_B  = constants.k      # J/K

    def kss_bound_value(self) -> float:
        """
        The KSS lower bound  ħ/(4π k_B)  in K·s  ( = J·s / (J/K) ).

        This is the universal minimum shear viscosity-to-entropy-density
        ratio predicted for any quantum field theory with a gravity dual.
        """
        return self.hbar / (4.0 * np.pi * self.k_B)

    def generate_hypothetical_qgp_data(
        self,
        T_min_MeV: float = 170.0,
        T_max_MeV: float = 500.0,
        num_points: int = 25,
        seed: int = 42,
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """
        Generate illustrative QGP data that sits above the KSS bound.

        Temperature range spans the QGP deconfinement regime (≈170–500 MeV/k_B).
        Data is purely hypothetical — it mimics the near-perfect-liquid behaviour
        observed at RHIC and the LHC where η/s is very close to the KSS bound.

        Parameters
        ----------
        T_min_MeV : minimum temperature in MeV (deconfinement onset ≈ 170 MeV)
        T_max_MeV : maximum temperature in MeV
        num_points: number of data points
        seed      : RNG seed for reproducibility

        Returns
        -------
        (T_Kelvin, eta_over_s)  both as float64 arrays.
        """
        rng = np.random.default_rng(seed)
        MeV_to_K = 1e6 * constants.eV / constants.k  # 1 MeV ≈ 1.16×10¹⁰ K

        T_K   = np.linspace(T_min_MeV * MeV_to_K, T_max_MeV * MeV_to_K, num_points)
        bound = self.kss_bound_value()

        # Near-perfect-liquid: η/s starts ~1.5× bound near T_c, decreases gradually
        t_norm  = (T_K - T_K[0]) / (T_K[-1] - T_K[0])  # [0, 1]
        noise   = rng.normal(0.0, 0.04, num_points)
        eta_s   = bound * (1.5 - 0.3 * t_norm + noise)
        eta_s   = np.maximum(eta_s, bound * 1.005)       # strictly above the bound
        return T_K, eta_s

    def plot_kss_bound(
        self,
        hypothetical_data: Optional[Tuple[npt.NDArray, npt.NDArray]] = None,
        save_path: Optional[Union[str, Path]] = None,
    ) -> plt.Figure:
        """
        Plot the KSS bound as a horizontal line with the forbidden region shaded.

        Optionally overlays hypothetical QGP data.  Temperature axis is expressed
        in units of the deconfinement temperature T_c ≈ 170 MeV/k_B.

        Parameters
        ----------
        hypothetical_data : Optional (T_array [K], eta_s_array [K·s]).
        save_path         : PNG output path.

        Returns
        -------
        Closed Matplotlib Figure.
        """
        bound_val = self.kss_bound_value()

        # Temperature axis in units of T_c  (QGP regime: 0.8 T_c – 5 T_c)
        MeV_to_K = 1e6 * constants.eV / constants.k
        T_c = 170.0 * MeV_to_K                            # ≈ 1.97×10¹² K
        T   = np.linspace(0.80 * T_c, 5.0 * T_c, 500)
        bound_line = np.full_like(T, bound_val)

        fig, ax = plt.subplots(figsize=(10, 6), facecolor=_BG)
        _style_axes(ax)

        # ── KSS bound line ───────────────────────────────────────────────────
        ax.semilogy(
            T / T_c, bound_line,
            color=_ORANGE, lw=2.2, ls="--", zorder=3,
            label=(
                rf"KSS bound: $\hbar/(4\pi k_B)"
                rf" \approx {bound_val:.3e}$ K·s"
            ),
        )

        # ── Hypothetical QGP data ─────────────────────────────────────────────
        if hypothetical_data is not None:
            T_data, eta_s_data = hypothetical_data
            ax.semilogy(
                T_data / T_c, eta_s_data,
                "o", color=_BLUE_LT, markersize=5, alpha=0.85, zorder=4,
                label="Hypothetical QGP  (near-perfect liquid)",
            )

        # ── Set y-limits BEFORE fill_between so the shading is correct ────────
        y_lo = bound_val * 0.06
        y_hi = bound_val * 40.0
        ax.set_ylim(y_lo, y_hi)

        # ── Shade forbidden region (below the KSS bound) ──────────────────────
        ax.fill_between(
            T / T_c, y_lo, bound_line,
            alpha=0.16, color=_RED, lw=0, zorder=1,
            label=r"Forbidden:  $\eta/s < \hbar/4\pi k_B$",
        )

        # ── Legend (called AFTER fill_between so all labels are captured) ──────
        ax.legend(facecolor=_BG, edgecolor=_BORDER, labelcolor=_TEXT, fontsize=10)

        # ── Labels and title ──────────────────────────────────────────────────
        ax.set_xlabel(
            r"Temperature   $T / T_c$   ($T_c \approx 170\,\mathrm{MeV}/k_B$)",
            fontsize=11,
        )
        ax.set_ylabel(
            r"Shear viscosity / entropy density   $\eta/s$   (K·s)",
            fontsize=11,
        )
        ax.set_title(
            "Kovtun–Son–Starinets (KSS) Bound  ·  Quark-Gluon Plasma",
            color=_TEXT, fontsize=13, fontweight="bold",
        )
        ax.yaxis.set_major_formatter(ticker.LogFormatterMathtext())

        # Annotate the bound value directly on the line
        ax.annotate(
            rf"$\hbar/4\pi k_B \approx {bound_val:.3e}$ K·s",
            xy=(T[-1] / T_c, bound_val),
            xytext=(T[-1] / T_c - 0.6, bound_val * 5.5),
            color=_ORANGE, fontsize=9, alpha=0.92,
            arrowprops=dict(arrowstyle="->", color=_ORANGE, alpha=0.6, lw=0.8),
        )

        # ── Save ──────────────────────────────────────────────────────────────
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=_BG)
            logger.info("Saved KSS bound plot → %s", save_path)

        plt.close(fig)
        return fig


# ─────────────────────────────────────────────────────────────────────────────
# High-level Façade
# ─────────────────────────────────────────────────────────────────────────────

class PhysicsEngine:
    """
    Thin façade that exposes a clean, unified API over all physics sub-modules.

    Instantiated once in ``main.py`` and injected into the AIAgent and CLI,
    keeping ``core`` modules fully decoupled from the ``frontend``.
    """

    def __init__(self, export_dir: Path) -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.qho = QuantumHarmonicOscillator()
        self.qcd = QCDConcepts()

    def harmonic_oscillator_wavefunction(
        self,
        n: int,
        x_range: Optional[Tuple[float, float]] = None,
        save_plot: bool = True,
    ) -> Dict:
        """
        Compute QHO wavefunction for level n and optionally save a plot.

        Parameters
        ----------
        n        : Quantum number  (0 ≤ n ≤ QuantumHarmonicOscillator.MAX_N).
        x_range  : (x_min, x_max) in natural units.  Auto-computed if None.
        save_plot: Whether to write a PNG to the export directory.

        Returns
        -------
        {
          'n'          : int,
          'energy'     : float  (Joules),
          'energy_nat' : float  (ħω),
          'x_range'    : tuple  (natural units),
          'x_tp'       : float  (natural units),
          'plot_path'  : str | None,
        }
        """
        # Coerce and validate type here so errors surface with a clean message
        if not isinstance(n, (int, np.integer)):
            raise TypeError(
                f"Quantum number n must be an integer, "
                f"got {type(n).__name__}: {n!r}"
            )
        n = int(n)

        energy     = self.qho.energy(n)
        energy_nat = self.qho.energy_natural(n)
        x_tp       = self.qho.classical_turning_point(n)

        # Resolve the actual x_range used (for reporting back to caller)
        if x_range is None:
            pad = max(2.5, 0.4 * x_tp)
            x_range_actual: Tuple[float, float] = (-(x_tp + pad), x_tp + pad)
        else:
            x_range_actual = (float(x_range[0]), float(x_range[1]))

        result: Dict = {
            "n":          n,
            "energy":     energy,
            "energy_nat": energy_nat,
            "x_range":    x_range_actual,
            "x_tp":       x_tp,
            "plot_path":  None,
        }

        if save_plot:
            plot_path = self.export_dir / f"qho_n{n}_wavefunction.png"
            self.qho.plot_wavefunction(n, x_range=x_range_actual, save_path=plot_path)
            result["plot_path"] = str(plot_path)

        return result

    def kss_bound(
        self,
        generate_sample_data: bool = True,
        save_plot: bool = True,
    ) -> Dict:
        """
        Compute the KSS bound value and optionally save an illustrative plot.

        Parameters
        ----------
        generate_sample_data : Overlay hypothetical QGP data on the plot.
        save_plot            : Whether to write a PNG.

        Returns
        -------
        {'bound_value': float  (K·s),  'plot_path': str | None}
        """
        bound_value = self.qcd.kss_bound_value()
        result: Dict = {"bound_value": bound_value, "plot_path": None}

        if save_plot:
            hyp_data = (
                self.qcd.generate_hypothetical_qgp_data()
                if generate_sample_data else None
            )
            plot_path = self.export_dir / "kss_bound.png"
            self.qcd.plot_kss_bound(hypothetical_data=hyp_data, save_path=plot_path)
            result["plot_path"] = str(plot_path)

        return result
