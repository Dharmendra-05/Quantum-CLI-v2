#!/usr/bin/env python3
"""
Quantum-CLI Toolkit — Main Entry Point
A terminal-based, AI-integrated physics engine.
"""

import sys
import logging
import argparse
from pathlib import Path

# Ensure project root is always on sys.path (supports running from any CWD)
_PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_PROJECT_ROOT))

from frontend.cli_ui import QuantumCLI
from core.ai_agent import AIAgent
from core.physics_engine import PhysicsEngine
from core.latex_generator import LaTeXGenerator


def _configure_logging(verbose: bool = False) -> None:
    """Centralise logging config.  Physics/agent modules use their own named loggers."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    """Parse CLI arguments, wire up components, and launch the interactive REPL."""
    parser = argparse.ArgumentParser(
        description="Quantum-CLI Toolkit — AI-Integrated Physics Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py\n"
            "  python main.py --export-dir /tmp/quantum_out\n"
            "  python main.py --no-rich\n"
            "  python main.py --verbose\n"
        ),
    )
    parser.add_argument(
        "--export-dir",
        type=str,
        default="assets/exports",
        help="Directory for plots and LaTeX files (default: assets/exports)",
    )
    parser.add_argument(
        "--no-rich",
        action="store_true",
        help="Disable Rich terminal output and fall back to plain text",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging",
    )
    args = parser.parse_args()

    _configure_logging(args.verbose)

    # Resolve export directory relative to the project root so it is stable
    # regardless of the working directory the user invokes the script from.
    export_path = (_PROJECT_ROOT / args.export_dir).resolve()
    export_path.mkdir(parents=True, exist_ok=True)

    # Wire up core components (dependency injection keeps modules decoupled)
    physics_engine = PhysicsEngine(export_dir=export_path)
    ai_agent = AIAgent(physics_engine)
    latex_gen = LaTeXGenerator(export_dir=export_path)

    cli = QuantumCLI(
        ai_agent=ai_agent,
        latex_generator=latex_gen,
        export_dir=export_path,
        use_rich=not args.no_rich,
    )

    try:
        cli.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
