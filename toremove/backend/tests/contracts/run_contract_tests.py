#!/usr/bin/env python3
"""
Contract Testing Runner for DjangoCRM Microservices

This script runs contract tests to ensure services communicate correctly.
"""

import sys
import os
import json
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from tests.contracts import ContractTestRunner
from tests.contracts.service_contracts import create_all_contracts

def main():
    """Run contract tests for all services"""
    print("🧪 DjangoCRM Contract Testing")
    print("=" * 50)

    # Create test runner
    runner = ContractTestRunner()

    # Create contracts for all services
    # Note: These are mock URLs for testing - replace with actual service URLs when services are running
    base_urls = {
        'identity': 'http://localhost:8001',
        'audit': 'http://localhost:8002',
        'notification': 'http://localhost:8003',
        'project': 'http://localhost:8004',
        'accounting': 'http://localhost:8005',
        'hr': 'http://localhost:8006',
        'sales': 'http://localhost:8007'
    }

    contracts = create_all_contracts(base_urls)

    # Add contracts to runner
    for contract in contracts:
        runner.add_contract(contract)

    # Run tests
    print(f"Running contract tests for {len(contracts)} services...")
    results = runner.run_all_tests()

    # Generate and print report
    report = runner.generate_report(results)
    print(report)

    # Save detailed results to file
    output_file = backend_dir / "contract_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Detailed results saved to: {output_file}")

    # Exit with appropriate code
    if results['summary']['all_passed']:
        print("✅ All contract tests passed!")
        return 0
    else:
        print("❌ Some contract tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())