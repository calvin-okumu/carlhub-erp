"""
Contract Testing Framework for DjangoCRM Microservices

This framework provides contract testing capabilities to ensure services
communicate correctly through well-defined APIs.
"""

import json
import requests
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ContractTestResult(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ContractViolation:
    """Represents a contract violation"""
    service: str
    endpoint: str
    method: str
    expected: Dict[str, Any]
    actual: Dict[str, Any]
    error_message: str

@dataclass
class ContractTestCase:
    """Represents a single contract test case"""
    name: str
    service: str
    method: str
    endpoint: str
    request_data: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    expected_response_schema: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None

class ServiceContract:
    """Base class for service contracts"""

    def __init__(self, service_name: str, base_url: str):
        self.service_name = service_name
        self.base_url = base_url
        self.test_cases: List[ContractTestCase] = []
        self.violations: List[ContractViolation] = []

    def add_test_case(self, test_case: ContractTestCase):
        """Add a test case to this contract"""
        self.test_cases.append(test_case)

    def validate_response(self, response: requests.Response,
                         expected_schema: Optional[Dict[str, Any]] = None) -> List[str]:
        """Validate response against expected schema"""
        errors = []

        # Check status code
        if response.status_code != 200:
            errors.append(f"Expected status 200, got {response.status_code}")

        # Check content type
        if 'content-type' in response.headers:
            content_type = response.headers['content-type']
            if 'application/json' not in content_type:
                errors.append(f"Expected JSON response, got {content_type}")

        # Basic JSON validation
        try:
            response_data = response.json()
        except ValueError:
            errors.append("Response is not valid JSON")
            return errors

        # Schema validation (basic structure check)
        if expected_schema:
            errors.extend(self._validate_schema(response_data, expected_schema))

        return errors

    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Basic schema validation"""
        errors = []

        if not isinstance(data, dict):
            errors.append("Response data is not a dictionary")
            return errors

        for key, expected_type in schema.items():
            if key not in data:
                errors.append(f"Missing required field: {key}")
                continue

            actual_value = data[key]
            if expected_type == "string" and not isinstance(actual_value, str):
                errors.append(f"Field {key} should be string, got {type(actual_value)}")
            elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                errors.append(f"Field {key} should be number, got {type(actual_value)}")
            elif expected_type == "boolean" and not isinstance(actual_value, bool):
                errors.append(f"Field {key} should be boolean, got {type(actual_value)}")
            elif expected_type == "array" and not isinstance(actual_value, list):
                errors.append(f"Field {key} should be array, got {type(actual_value)}")

        return errors

    def run_tests(self) -> Dict[str, Any]:
        """Run all contract tests for this service"""
        results = {
            'service': self.service_name,
            'total_tests': len(self.test_cases),
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'violations': [],
            'test_results': []
        }

        for test_case in self.test_cases:
            result = self._run_single_test(test_case)
            results['test_results'].append(result)

            if result['status'] == ContractTestResult.PASSED:
                results['passed'] += 1
            elif result['status'] == ContractTestResult.FAILED:
                results['failed'] += 1
                results['violations'].extend(result.get('violations', []))
            else:
                results['skipped'] += 1

        return results

    def _run_single_test(self, test_case: ContractTestCase) -> Dict[str, Any]:
        """Run a single contract test"""
        url = f"{self.base_url}{test_case.endpoint}"

        try:
            # Make the request
            response = requests.request(
                method=test_case.method,
                url=url,
                json=test_case.request_data,
                headers=test_case.headers,
                timeout=10
            )

            # Validate response
            validation_errors = self.validate_response(
                response, test_case.expected_response_schema
            )

            if validation_errors:
                return {
                    'test_name': test_case.name,
                    'status': ContractTestResult.FAILED,
                    'violations': validation_errors,
                    'response_status': response.status_code,
                    'error': 'Contract violations found'
                }
            else:
                return {
                    'test_name': test_case.name,
                    'status': ContractTestResult.PASSED,
                    'response_status': response.status_code
                }

        except requests.RequestException as e:
            return {
                'test_name': test_case.name,
                'status': ContractTestResult.FAILED,
                'error': f"Request failed: {str(e)}"
            }
        except Exception as e:
            return {
                'test_name': test_case.name,
                'status': ContractTestResult.FAILED,
                'error': f"Test execution failed: {str(e)}"
            }

class ContractTestRunner:
    """Runner for contract tests across multiple services"""

    def __init__(self):
        self.contracts: List[ServiceContract] = []

    def add_contract(self, contract: ServiceContract):
        """Add a contract to the test runner"""
        self.contracts.append(contract)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run contract tests for all services"""
        overall_results = {
            'total_services': len(self.contracts),
            'total_tests': 0,
            'total_passed': 0,
            'total_failed': 0,
            'total_skipped': 0,
            'service_results': [],
            'summary': {}
        }

        for contract in self.contracts:
            service_results = contract.run_tests()
            overall_results['service_results'].append(service_results)

            overall_results['total_tests'] += service_results['total_tests']
            overall_results['total_passed'] += service_results['passed']
            overall_results['total_failed'] += service_results['failed']
            overall_results['total_skipped'] += service_results['skipped']

        # Generate summary
        overall_results['summary'] = {
            'success_rate': (overall_results['total_passed'] / overall_results['total_tests'] * 100) if overall_results['total_tests'] > 0 else 0,
            'all_passed': overall_results['total_failed'] == 0,
            'total_violations': sum(len(r.get('violations', [])) for r in overall_results['service_results'])
        }

        return overall_results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable test report"""
        report = []
        report.append("=" * 60)
        report.append("CONTRACT TESTING REPORT")
        report.append("=" * 60)
        report.append(f"Services Tested: {results['total_services']}")
        report.append(f"Total Tests: {results['total_tests']}")
        report.append(f"Passed: {results['total_passed']}")
        report.append(f"Failed: {results['total_failed']}")
        report.append(f"Skipped: {results['total_skipped']}")
        report.append(".1f")
        report.append(f"All Passed: {results['summary']['all_passed']}")
        report.append("")

        for service_result in results['service_results']:
            report.append(f"Service: {service_result['service']}")
            report.append(f"  Tests: {service_result['total_tests']}, "
                         f"Passed: {service_result['passed']}, "
                         f"Failed: {service_result['failed']}")

            if service_result['violations']:
                report.append("  Violations:")
                for violation in service_result['violations']:
                    report.append(f"    - {violation}")

            report.append("")

        return "\n".join(report)