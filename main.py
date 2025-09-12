"""Main entrypoint for AEB Safety-Critical System Prototype."""
from aeb.simulation import AEBSimulation

def main():
    print("AEB Safety-Critical System Prototype")
    print("=" * 50)
    print("Demonstrating requirement validation for urban collision avoidance\n")

    simulation = AEBSimulation()
    simulation.run_requirement_validation_tests()

    print("\n" + "=" * 50)
    print("AEB Prototype Demonstration Complete")
    print("This prototype validates the safety-critical requirement")
    print("engineering methodology for urban AEB systems.")

if __name__ == "__main__":
    main()
