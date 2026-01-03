#!/usr/bin/env python3
"""
Chaos Engineering Runner for DjangoCRM Microservices

This script runs chaos engineering experiments to test system resilience.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from tests.chaos import (
    ChaosExperimentRunner,
    DockerChaosInjector,
    MetricsCollector,
    create_standard_experiments,
    ExperimentResult
)

def main():
    """Run chaos engineering experiments"""
    print("🔥 DjangoCRM Chaos Engineering")
    print("=" * 50)

    # Create chaos injector and metrics collector
    injector = DockerChaosInjector("test-service")  # Will be overridden per experiment
    metrics_collector = MetricsCollector()
    runner = ChaosExperimentRunner(injector, metrics_collector)

    # Get experiments to run
    experiments = create_standard_experiments()

    print(f"Running {len(experiments)} chaos experiments...")
    print()

    results = []

    for experiment in experiments:
        print(f"🧪 Running experiment: {experiment.name}")
        print(f"   Description: {experiment.description}")
        print(f"   Target: {experiment.target_service}")
        print(f"   Chaos Type: {experiment.chaos_type.value}")
        print(f"   Severity: {experiment.severity.value}")
        print(f"   Duration: {experiment.duration_seconds}s")
        print("   Parameters:", experiment.parameters)
        print()

        # Create injector for this specific service
        service_injector = DockerChaosInjector(experiment.target_service)
        experiment_runner = ChaosExperimentRunner(service_injector, metrics_collector)

        # Run the experiment
        result = experiment_runner.run_experiment(experiment)
        results.append(result)

        # Print result
        status = "✅ PASSED" if result.success else "❌ FAILED"
        duration = result.end_time - result.start_time

        print(f"   Result: {status}")
        print(".1f")
        print(f"   Observations: {len(result.observations)}")
        for obs in result.observations:
            print(f"     - {obs}")

        if result.errors:
            print(f"   Errors: {len(result.errors)}")
            for error in result.errors:
                print(f"     - {error}")

        print()

    # Generate summary report
    print("=" * 50)
    print("CHAOS EXPERIMENT SUMMARY")
    print("=" * 50)

    total_experiments = len(results)
    successful_experiments = sum(1 for r in results if r.success)
    failed_experiments = total_experiments - successful_experiments

    print(f"Total Experiments: {total_experiments}")
    print(f"Successful: {successful_experiments}")
    print(f"Failed: {failed_experiments}")
    print(".1f")

    if successful_experiments == total_experiments:
        print("🎉 All chaos experiments completed successfully!")
        print("Your microservices architecture shows good resilience.")
    else:
        print("⚠️  Some experiments failed.")
        print("Consider improving resilience for the failed scenarios.")

    # Save detailed results
    output_file = backend_dir / "chaos_experiment_results.json"
    results_data = []
    for result in results:
        result_dict = {
            'experiment': {
                'name': result.experiment.name,
                'description': result.experiment.description,
                'chaos_type': result.experiment.chaos_type.value,
                'target_service': result.experiment.target_service,
                'severity': result.experiment.severity.value,
                'duration_seconds': result.experiment.duration_seconds,
                'parameters': result.experiment.parameters,
                'success_criteria': result.experiment.success_criteria
            },
            'start_time': result.start_time,
            'end_time': result.end_time,
            'success': result.success,
            'observations': result.observations,
            'metrics_before': result.metrics_before,
            'metrics_after': result.metrics_after,
            'errors': result.errors
        }
        results_data.append(result_dict)

    with open(output_file, 'w') as f:
        json.dump(results_data, f, indent=2, default=str)

    print(f"\n📄 Detailed results saved to: {output_file}")

    # Exit with appropriate code
    return 0 if successful_experiments == total_experiments else 1

if __name__ == "__main__":
    sys.exit(main())