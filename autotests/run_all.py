#!/usr/bin/env python3
"""
Swiss Data Airlock — Central Test Runner
Orchestrates core, backend, and frontend test suites.

Usage:
    python autotests/run_all.py              # Run all tests
    python autotests/run_all.py --core       # Core only
    python autotests/run_all.py --backend    # Backend only
    python autotests/run_all.py --verbose    # Verbose output
    python autotests/run_all.py --coverage   # With coverage report
    python autotests/run_all.py --help       # Show help
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

AUTOTESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = AUTOTESTS_DIR.parent

CORE_DIR = AUTOTESTS_DIR / "core"
BACKEND_DIR = AUTOTESTS_DIR / "backend"

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def banner(text: str):
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}\n")


def run_pytest(
    target_dir: Path,
    label: str,
    verbose: bool = False,
    coverage: bool = False,
    cov_targets: list[str] | None = None,
) -> tuple[bool, float]:
    """Run pytest on target_dir. Returns (success, duration_seconds)."""
    print(f"{BOLD}Running {label} tests...{RESET}")

    cmd = [sys.executable, "-m", "pytest", str(target_dir), "-v"]
    if not verbose:
        cmd.append("-q")

    if coverage and cov_targets:
        cmd += ["--cov"] + [str(PROJECT_ROOT / t) for t in cov_targets]

    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    duration = time.time() - t0

    success = result.returncode == 0
    color = GREEN if success else RED
    status = "PASSED" if success else "FAILED"
    print(f"\n{color}{BOLD}{label}: {status}{RESET} ({duration:.1f}s)\n")
    return success, duration


def main():
    parser = argparse.ArgumentParser(
        description="Swiss Data Airlock — Central Test Runner"
    )
    parser.add_argument("--core", action="store_true", help="Run core tests only")
    parser.add_argument("--backend", action="store_true", help="Run backend tests only")
    parser.add_argument("--verbose", action="store_true", help="Verbose pytest output")
    parser.add_argument("--coverage", action="store_true", help="Enable coverage report")
    args = parser.parse_args()

    banner("Swiss Data Airlock — Test Suite")

    results = {}
    total_t0 = time.time()

    # Determine what to run
    run_core = True
    run_backend = True

    if args.core and not args.backend:
        run_backend = False
    elif args.backend and not args.core:
        run_core = False

    # ---- Core Tests ----
    if run_core:
        if CORE_DIR.exists() and any(CORE_DIR.glob("test_*.py")):
            ok, dur = run_pytest(
                CORE_DIR,
                "CORE",
                verbose=args.verbose,
                coverage=args.coverage,
                cov_targets=["core/"] if args.coverage else None,
            )
            results["core"] = (ok, dur)
        else:
            print(f"{YELLOW}SKIP: No core test files found{RESET}\n")
            results["core"] = (None, 0)

    # ---- Backend Tests ----
    if run_backend:
        if BACKEND_DIR.exists() and any(BACKEND_DIR.glob("test_*.py")):
            ok, dur = run_pytest(
                BACKEND_DIR,
                "BACKEND",
                verbose=args.verbose,
                coverage=args.coverage,
                cov_targets=["back/"] if args.coverage else None,
            )
            results["backend"] = (ok, dur)
        else:
            print(f"{YELLOW}SKIP: No backend test files found{RESET}\n")
            results["backend"] = (None, 0)

    # ---- Summary ----
    total_duration = time.time() - total_t0
    banner("SUMMARY")

    all_passed = True
    for label, (ok, dur) in results.items():
        if ok is None:
            status = f"{YELLOW}SKIPPED{RESET}"
        elif ok:
            status = f"{GREEN}PASSED{RESET}"
        else:
            status = f"{RED}FAILED{RESET}"
            all_passed = False
        print(f"  {label.upper():12s} {status}  ({dur:.1f}s)")

    print(f"\n  Total: {total_duration:.1f}s")
    print()

    if all_passed:
        print(f"{GREEN}{BOLD}All tests passed!{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}Some tests failed.{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
