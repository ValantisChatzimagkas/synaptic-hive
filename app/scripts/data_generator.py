"""
Data generator for simulating machine measurements.
Sends realistic measurement data to the API at configurable intervals.
"""

import argparse
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import httpx

from app.enums import MachineType


@dataclass
class Measurement:
    machine_id: str
    timestamp: str
    voltage: Optional[float] = None
    current: Optional[float] = None
    rpm: Optional[int] = None
    torque: Optional[float] = None
    additional_metrics: dict = None

    def __post_init__(self):
        if self.additional_metrics is None:
            self.additional_metrics = {}


class MachineSimulator:
    """Simulates a single machine sending measurements."""

    def __init__(
        self,
        machine_id: UUID,
        machine_type: MachineType,
        api_url: str = "http://localhost:8000",
    ):
        self.machine_id = machine_id
        self.machine_type = machine_type
        self.api_url = api_url
        self.client = httpx.Client(base_url=api_url, timeout=10.0, follow_redirects=True)

    def generate_measurement(self) -> Measurement:
        """
        Generate a realistic measurement based on machine type.
        Adds some randomness and occasional anomalies.
        """

        measurement = Measurement(
            machine_id=str(self.machine_id),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        if self.machine_type == MachineType.WELDING:
            base_voltage = 220
            base_current = 15

            # Add random variation (±5%)
            voltage = base_voltage + random.uniform(-11, 11)
            current = base_current + random.uniform(-0.75, 0.75)

            if random.random() < 0.05:
                voltage += random.uniform(20, 40)  # Voltage spike

            measurement.voltage = round(voltage, 2)
            measurement.current = round(current, 2)
            measurement.additional_metrics = {
                "arc_stability": round(random.uniform(0.85, 0.99), 3),
                "wire_feed_rate": round(random.uniform(4.5, 5.5), 2),
            }

        elif self.machine_type == MachineType.LATHE:
            base_rpm = 1500
            base_torque = 45

            rpm = int(base_rpm + random.uniform(-150, 150))
            torque = base_torque + random.uniform(-5, 5)

            if random.random() < 0.05:
                rpm = int(rpm * 1.3)  # Over-speeding

            measurement.rpm = rpm
            measurement.torque = round(torque, 2)
            measurement.additional_metrics = {
                "cutting_depth": round(random.uniform(2.0, 3.5), 2),
                "coolant_flow": round(random.uniform(8.0, 12.0), 1),
            }

        elif self.machine_type == MachineType.PRESS:
            base_voltage = 380
            base_current = 25

            measurement.voltage = round(base_voltage + random.uniform(-15, 15), 2)
            measurement.current = round(base_current + random.uniform(-2, 2), 2)
            measurement.additional_metrics = {
                "pressure": round(random.uniform(80, 120), 1),
                "force": round(random.uniform(45, 55), 1),
            }

        elif self.machine_type == MachineType.CONVEYOR:
            base_rpm = 60
            measurement.rpm = int(base_rpm + random.uniform(-5, 5))
            measurement.additional_metrics = {
                "belt_tension": round(random.uniform(75, 85), 1),
                "speed_mps": round(random.uniform(1.8, 2.2), 2),
            }

        elif self.machine_type == MachineType.ASSEMBLY:
            measurement.voltage = round(220 + random.uniform(-10, 10), 2)
            measurement.current = round(10 + random.uniform(-1, 1), 2)
            measurement.additional_metrics = {
                "cycle_count": random.randint(45, 55),
                "error_count": random.randint(0, 2),
            }

        return measurement

    def send_measurement(self) -> bool:
        """Send a measurement to the API. Returns True if successful."""
        measurement = self.generate_measurement()

        try:
            # Convert dataclass to dict, exclude None values
            payload = {k: v for k, v in asdict(measurement).items() if v is not None}
            response = self.client.post("/api/v1/measurements", json=payload)
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP {e.response.status_code}: {e.response.text}")
            return False
        except Exception as e:
            print(f"❌ Error sending measurement: {e}")
            return False

    def run(self, interval_seconds: float, duration_seconds: float | None = None):
        """
        Run the simulator, sending measurements at the specified interval.
        """
        start_time = time.time()
        sent_count = 0
        error_count = 0

        print(f"🤖 Starting simulator for machine {self.machine_id} ({self.machine_type.value})")
        print(f"📊 Sending 1 measurement every {interval_seconds}s")

        try:
            while True:
                if self.send_measurement():
                    sent_count += 1
                    print(f"✅ Sent measurement #{sent_count}", end="\r")
                else:
                    error_count += 1

                time.sleep(interval_seconds)

                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")

        elapsed = time.time() - start_time
        print("\n📈 Summary:")
        print(f"   Total sent: {sent_count}")
        print(f"   Errors: {error_count}")
        print(f"   Duration: {elapsed:.1f}s")
        print(f"   Rate: {sent_count / elapsed:.2f} msg/sec")


def main():
    parser = argparse.ArgumentParser(description="Simulate machine measurements")

    parser.add_argument("machine_id", type=str, help="UUID of the machine to simulate")
    parser.add_argument(
        "machine_type",
        type=str,
        choices=[mt.value for mt in MachineType],
        help="Type of machine",
    )
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between measurements")
    parser.add_argument("--duration", type=float, default=None, help="Total runtime in seconds")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000", help="API base URL")

    args = parser.parse_args()

    simulator = MachineSimulator(
        machine_id=UUID(args.machine_id),
        machine_type=MachineType(args.machine_type),
        api_url=args.api_url,
    )

    simulator.run(interval_seconds=args.interval, duration_seconds=args.duration)


if __name__ == "__main__":
    main()
