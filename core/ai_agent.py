"""
AI Agent Module
===============
Rule-based natural language parser that maps user CLI commands to
PhysicsEngine method calls.  Uses pre-compiled regex patterns for speed
and validates all numeric parameters before dispatching to the engine.
"""

import re
import logging
from typing import Any, Dict, Optional

from core.physics_engine import PhysicsEngine, QuantumHarmonicOscillator

logger = logging.getLogger(__name__)

# Propagate MAX_N so the agent and the engine share a single source of truth
_MAX_N: int = QuantumHarmonicOscillator.MAX_N


class AIAgent:
    """
    Interprets natural-language CLI commands and invokes PhysicsEngine methods.

    Design
    ------
    - parse()   → converts raw user text to a structured command dict
    - execute() → dispatches the structured command to the physics engine
    - All numeric parameters are validated inside execute() helper methods
      so that the engine only ever receives well-formed inputs.
    """

    def __init__(self, physics_engine: PhysicsEngine) -> None:
        self.physics = physics_engine
        self.command_history: list[str] = []

        # Pre-compile all patterns once at construction time
        self._re_help    = re.compile(r"\b(help|\?)\b")
        self._re_exit    = re.compile(r"\b(exit|quit|bye)\b")
        self._re_ho      = re.compile(
            r"\b(harmonic|oscillator|qho|wavefunction|probability)\b"
        )
        self._re_kss     = re.compile(
            r"\b(kss|kovtun|son|starinets|bound|qcd|quark|gluon|plasma)\b"
        )
        self._re_n_eq    = re.compile(r"\bn\s*=\s*(\d+)\b")
        self._re_level   = re.compile(r"\blevel\s+(\d+)\b")
        self._re_range   = re.compile(
            r"\brange\s+([-+]?\d*\.?\d+)\s+to\s+([-+]?\d*\.?\d+)\b"
        )
        self._re_sample  = re.compile(r"\b(sample|data|hypothetical)\b")

    # ── Public API ─────────────────────────────────────────────────────────────

    def parse(self, user_input: str) -> Dict[str, Any]:
        """
        Tokenise and classify raw user input into a structured command.

        Returns
        -------
        {
          'action'        : 'harmonic_oscillator' | 'kss_bound' |
                            'help' | 'exit' | 'unknown',
          'parameters'    : dict   – action-specific parameters,
          'confidence'    : float  – simulated confidence in [0, 1],
          'original_input': str,
        }
        """
        text = user_input.strip()
        self.command_history.append(text)
        norm = re.sub(r"\s+", " ", text.lower())

        base: Dict[str, Any] = {
            "action":         "unknown",
            "parameters":     {},
            "confidence":     0.0,
            "original_input": text,
        }

        if self._re_help.search(norm):
            return {**base, "action": "help", "confidence": 1.0}

        if self._re_exit.search(norm):
            return {**base, "action": "exit", "confidence": 1.0}

        if self._re_ho.search(norm):
            return {
                **base,
                "action":     "harmonic_oscillator",
                "confidence": 0.9,
                "parameters": self._parse_ho_params(norm),
            }

        if self._re_kss.search(norm):
            return {
                **base,
                "action":     "kss_bound",
                "confidence": 0.85,
                "parameters": {
                    "sample_data": bool(self._re_sample.search(norm))
                },
            }

        return base

    def execute(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the parsed command and return a result dict.

        Returns
        -------
        {
          'success': bool,
          'message': str,
          'data'   : dict | None,
        }
        """
        action = parsed["action"]
        params = parsed["parameters"]

        if action == "help":
            # The CLI layer handles help rendering; we just signal success.
            return {"success": True, "message": "__help__", "data": None}

        if action == "exit":
            return {"success": True, "message": "Exiting…", "data": None}

        if action == "harmonic_oscillator":
            return self._exec_harmonic_oscillator(params)

        if action == "kss_bound":
            return self._exec_kss_bound(params)

        # Unknown — produce a clean plain-text message (no Rich markup here;
        # the CLI layer applies its own styling)
        return {
            "success": False,
            "message": (
                f"I didn't understand: \"{parsed['original_input']}\".\n"
                f"Type 'help' to see available commands."
            ),
            "data": None,
        }

    # ── Private: parameter parsing ─────────────────────────────────────────────

    def _parse_ho_params(self, norm: str) -> Dict[str, Any]:
        """
        Extract QHO parameters from the normalised input string.

        n       : defaults to 0 if not specified; clamped to MAX_N.
        x_range : None (let the engine auto-compute) unless user specifies one.
        """
        params: Dict[str, Any] = {"n": 0, "x_range": None}

        # Extract quantum number n
        m = self._re_n_eq.search(norm) or self._re_level.search(norm)
        if m:
            n_raw = int(m.group(1))
            if n_raw > _MAX_N:
                logger.warning(
                    "Requested n=%d exceeds MAX_N=%d; clamping to %d.",
                    n_raw, _MAX_N, _MAX_N,
                )
                n_raw = _MAX_N
            params["n"] = n_raw

        # Extract optional x range (in natural units)
        rm = self._re_range.search(norm)
        if rm:
            x_min, x_max = float(rm.group(1)), float(rm.group(2))
            if x_min < x_max:
                params["x_range"] = (x_min, x_max)
            else:
                logger.warning(
                    "Ignoring invalid x_range (%.2f, %.2f): min ≥ max.",
                    x_min, x_max,
                )

        return params

    # ── Private: execution helpers ─────────────────────────────────────────────

    def _exec_harmonic_oscillator(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            n       = params.get("n", 0)
            x_range = params.get("x_range", None)   # None → engine auto-computes
            result  = self.physics.harmonic_oscillator_wavefunction(
                n=n, x_range=x_range, save_plot=True
            )
            msg = (
                f"Harmonic oscillator  n = {n}\n"
                f"  Energy   : {result['energy']:.6e} J"
                f"  =  {result['energy_nat']:.1f} \u0127\u03c9\n"
                f"  x_tp     : \u00b1{result['x_tp']:.4f} x\u2080  "
                f"(classical turning point)"
            )
            if result["plot_path"]:
                msg += f"\n  Plot     : {result['plot_path']}"
            return {"success": True, "message": msg, "data": result}

        except (TypeError, ValueError) as exc:
            return {
                "success": False,
                "message": f"Parameter error: {exc}",
                "data":    None,
            }
        except Exception as exc:
            logger.exception("Unexpected error computing harmonic oscillator")
            return {
                "success": False,
                "message": f"Computation failed: {exc}",
                "data":    None,
            }

    def _exec_kss_bound(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            sample = bool(params.get("sample_data", False))
            result = self.physics.kss_bound(
                generate_sample_data=sample, save_plot=True
            )
            bound = result["bound_value"]
            msg = (
                f"KSS bound:  \u03b7/s \u2265 \u0127/(4\u03c0 k\u1d0f)"
                f" = {bound:.6e} K\u00b7s\n"
                "  Universal lower bound from gauge/gravity (AdS/CFT) duality.\n"
                "  QGP at RHIC/LHC saturates this bound — the most perfect\n"
                "  liquid ever measured."
            )
            if result["plot_path"]:
                msg += f"\n  Plot     : {result['plot_path']}"
            return {"success": True, "message": msg, "data": result}

        except Exception as exc:
            logger.exception("Unexpected error computing KSS bound")
            return {
                "success": False,
                "message": f"Computation failed: {exc}",
                "data":    None,
            }
