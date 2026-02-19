# scripts/run_simulation.py
"""
Complete simulation orchestrator.
1. Creates org/factory/machine hierarchy
2. Runs measurement simulators for all machines
"""

import argparse
import subprocess
import sys
import time

import httpx


def setup_hierarchy(org_name: str, num_factories: int, machines_per_factory: int, api_url: str):
    """Run the setup generator and return the created hierarchy."""
    print("🔧 Step 1: Creating organizational hierarchy...\n")

    cmd = [
        sys.executable,
        "scripts/setup_generator.py",
        org_name,
        "--factories",
        str(num_factories),
        "--machines",
        str(machines_per_factory),
        "--api-url",
        api_url,
    ]

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print("\n❌ Failed to create hierarchy")
        exit(1)

    # Fetch the created organization and its machines
    print("\n📊 Fetching created machines...")
    client = httpx.Client(base_url=api_url, timeout=10.0)

    # Get all machines (we just created them, so they should be the most recent)
    response = client.get("/api/v1/machines")
    response.raise_for_status()
    machines = response.json()

    print(f"✅ Found {len(machines)} machines\n")
    return machines


def run_simulators(machines: list, interval: float, duration: float | None, api_url: str):
    """Run measurement simulators for all machines in parallel."""
    print("🚀 Step 2: Starting measurement simulators...\n")
    print(f"   Machines: {len(machines)}")
    print(f"   Interval: {interval}s per machine")
    print(f"   Duration: {duration}s" if duration else "   Duration: Continuous (Ctrl+C to stop)")
    print()

    processes = []

    for machine in machines:
        machine_id = machine["id"]
        machine_type = machine["machine_type"]

        cmd = [
            sys.executable,
            "scripts/data_generator.py",
            machine_id,
            machine_type,
            "--interval",
            str(interval),
            "--api-url",
            api_url,
        ]

        if duration:
            cmd.extend(["--duration", str(duration)])

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        processes.append((proc, machine["name"], machine_id))

        print(f"   ✅ Started simulator for: {machine['name']} ({machine_type})")

    print(f"\n🔥 All {len(processes)} simulators running!")
    print("   Press Ctrl+C to stop all simulators\n")

    try:
        # Wait for all processes
        for proc, name, _ in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping all simulators...")
        for proc, name, machine_id in processes:
            proc.terminate()
            print(f"   ⏹️  Stopped: {name} ({machine_id})")

        # Wait for clean shutdown
        time.sleep(1)
        print("\n✅ All simulators stopped.")


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

    # Step 1: Create hierarchy
    machines = setup_hierarchy(
        org_name=args.org_name,
        num_factories=args.factories,
        machines_per_factory=args.machines,
        api_url=args.api_url,
    )

    if args.setup_only:
        print("✅ Setup complete (--setup-only flag used)")
        return

    # Step 2: Run simulators
    run_simulators(
        machines=machines,
        interval=args.interval,
        duration=args.duration,
        api_url=args.api_url,
    )


if __name__ == "__main__":
    main()
