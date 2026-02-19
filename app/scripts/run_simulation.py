"""
Complete simulation orchestrator.
1. Creates org/factory/machine hierarchy
2. Runs measurement simulators for all machines
"""

import argparse
import threading
import time
from uuid import UUID

from app.enums import MachineType
from app.scripts.data_generator import MachineSimulator
from app.scripts.setup_generator import SetupGenerator


def setup_hierarchy(
    org_name: str, num_factories: int, machines_per_factory: int, api_url: str
) -> list[dict]:
    """Create the organizational hierarchy and return all created machines."""
    print("Step 1: Creating organizational hierarchy...\n")

    generator = SetupGenerator(api_url=api_url)
    result = generator.generate_hierarchy(
        org_name=org_name,
        num_factories=num_factories,
        machines_per_factory=machines_per_factory,
    )

    machines = []
    for factory_data in result["factories"]:
        machines.extend(factory_data["machines"])

    print(f"\nFound {len(machines)} machines\n")
    return machines


def run_simulators(machines: list[dict], interval: float, duration: float | None, api_url: str):
    """Run measurement simulators for all machines in parallel using threads."""
    print("Step 2: Starting measurement simulators...\n")
    print(f"   Machines: {len(machines)}")
    print(f"   Interval: {interval}s per machine")
    print(f"   Duration: {duration}s" if duration else "   Duration: Continuous (Ctrl+C to stop)")
    print()

    threads: list[tuple[threading.Thread, str, str]] = []

    for machine in machines:
        machine_id = machine["id"]
        machine_type = machine["machine_type"]

        simulator = MachineSimulator(
            machine_id=UUID(machine_id),
            machine_type=MachineType(machine_type),
            api_url=api_url,
        )

        thread = threading.Thread(
            target=simulator.run,
            kwargs={"interval_seconds": interval, "duration_seconds": duration},
            daemon=True,
        )
        thread.start()
        threads.append((thread, machine["name"], machine_id))

        print(f"   Started simulator for: {machine['name']} ({machine_type})")

    print(f"\nAll {len(threads)} simulators running!")
    print("   Press Ctrl+C to stop all simulators\n")

    try:
        if duration:
            for thread, _, _ in threads:
                thread.join()
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping all simulators...")
        print("All simulators stopped (daemon threads terminated).")


def main():
    parser = argparse.ArgumentParser(
        description="Complete simulation: Setup hierarchy + Run measurements"
    )

    parser.add_argument(
        "org_name",
        type=str,
        help="Name of the organization to create",
    )

    parser.add_argument(
        "--factories",
        type=int,
        default=2,
        help="Number of factories per organization (default: 2)",
    )

    parser.add_argument(
        "--machines",
        type=int,
        default=3,
        help="Number of machines per factory (default: 3)",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between measurements per machine (default: 1.0)",
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Total runtime in seconds (default: run forever)",
    )

    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)",
    )

    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only create hierarchy, don't run simulators",
    )

    args = parser.parse_args()

    machines = setup_hierarchy(
        org_name=args.org_name,
        num_factories=args.factories,
        machines_per_factory=args.machines,
        api_url=args.api_url,
    )

    if args.setup_only:
        print("Setup complete (--setup-only flag used)")
        return

    run_simulators(
        machines=machines,
        interval=args.interval,
        duration=args.duration,
        api_url=args.api_url,
    )


if __name__ == "__main__":
    main()
