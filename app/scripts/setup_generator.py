"""
Setup generator - Creates organizations, factories, and machines.
"""

import argparse
import random
from typing import Any
from uuid import UUID

import httpx

from app.enums import IndustryType, MachineType


class SetupGenerator:
    """Generates a complete organizational hierarchy via the API."""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.client = httpx.Client(base_url=api_url, timeout=30.0, follow_redirects=True)

    def create_organization(self, name: str) -> dict[str, Any]:
        """Create an organization."""
        payload = {"name": name, "is_active": True}
        response = self.client.post("/api/v1/organizations", json=payload)
        response.raise_for_status()
        org = response.json()
        print(f"Created organization: {org['name']} ({org['id']})")
        return org

    def create_factory(
        self,
        organization_id: UUID,
        name: str,
        industry: IndustryType,
        country_code: str,
        city: str,
    ) -> dict[str, Any]:
        """Create a factory."""
        payload = {
            "organization_id": str(organization_id),
            "name": name,
            "industry": industry.value,
            "country_code": country_code,
            "city": city,
            "postal_code": f"{random.randint(10000, 99999)}",
            "is_active": True,
        }
        response = self.client.post("/api/v1/factories", json=payload)
        response.raise_for_status()
        factory = response.json()
        print(f"   Created factory: {factory['name']} ({factory['id']})")
        return factory

    def create_machine(
        self,
        factory_id: UUID,
        name: str,
        machine_type: MachineType,
    ) -> dict[str, Any]:
        """Create a machine."""
        manufacturers = {
            MachineType.WELDING: ["KUKA", "ABB", "Fanuc", "Yaskawa"],
            MachineType.LATHE: ["DMG MORI", "Mazak", "Okuma", "Haas"],
            MachineType.PRESS: ["Schuler", "Aida", "Komatsu", "Fagor"],
            MachineType.CONVEYOR: ["Siemens", "Bosch Rexroth", "SEW-EURODRIVE"],
            MachineType.ASSEMBLY: ["Festo", "SMC", "Parker Hannifin"],
        }

        payload = {
            "factory_id": str(factory_id),
            "name": name,
            "machine_type": machine_type.value,
            "manufacturer": random.choice(manufacturers.get(machine_type, ["Generic"])),
            "serial_number": f"{machine_type.value.upper()}-{random.randint(1000, 9999)}",
            "meta": {},
        }
        response = self.client.post("/api/v1/machines", json=payload)
        response.raise_for_status()
        machine = response.json()
        print(f"      Created machine: {machine['name']} ({machine['id']})")
        return machine

    def generate_hierarchy(
        self,
        org_name: str,
        num_factories: int,
        machines_per_factory: int,
    ) -> dict[str, Any]:
        """
        Generate a complete hierarchy.

        Returns a dict with the structure:
        {
            "organization": {...},
            "factories": [
                {
                    "factory": {...},
                    "machines": [...]
                },
                ...
            ]
        }
        """
        print(f"\nGenerating hierarchy for: {org_name}")
        print(f"   Factories: {num_factories}")
        print(f"   Machines per factory: {machines_per_factory}\n")

        # Create organization
        org = self.create_organization(org_name)

        # Sample data for variety
        industries = list(IndustryType)
        cities = [
            ("DE", "Berlin"),
            ("DE", "Munich"),
            ("DE", "Stuttgart"),
            ("US", "Detroit"),
            ("US", "Chicago"),
            ("JP", "Tokyo"),
            ("JP", "Osaka"),
        ]
        machine_types = list(MachineType)

        factories_data = []

        # Create factories
        for i in range(num_factories):
            industry = random.choice(industries)
            country_code, city = random.choice(cities)

            factory = self.create_factory(
                organization_id=UUID(org["id"]),
                name=f"{org_name} {city} Plant",
                industry=industry,
                country_code=country_code,
                city=city,
            )

            machines = []

            # Create machines for this factory
            for j in range(machines_per_factory):
                machine_type = random.choice(machine_types)
                machine = self.create_machine(
                    factory_id=UUID(factory["id"]),
                    name=f"{machine_type.value.title()} Unit {j + 1}",
                    machine_type=machine_type,
                )
                machines.append(machine)

            factories_data.append({"factory": factory, "machines": machines})

        result = {"organization": org, "factories": factories_data}

        print("\nHierarchy created successfully!")
        print(f"   Organization: {org['name']}")
        print(f"   Total factories: {num_factories}")
        print(f"   Total machines: {num_factories * machines_per_factory}")

        return result


def main():
    parser = argparse.ArgumentParser(description="Generate organizational hierarchy")

    parser.add_argument("org_name", type=str, help="Name of the organization")
    parser.add_argument(
        "--factories",
        type=int,
        default=2,
        help="Number of factories to create (default: 2)",
    )
    parser.add_argument(
        "--machines",
        type=int,
        default=3,
        help="Number of machines per factory (default: 3)",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    generator = SetupGenerator(api_url=args.api_url)

    try:
        generator.generate_hierarchy(
            org_name=args.org_name,
            num_factories=args.factories,
            machines_per_factory=args.machines,
        )
    except httpx.HTTPError as e:
        print(f"\nAPI Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
