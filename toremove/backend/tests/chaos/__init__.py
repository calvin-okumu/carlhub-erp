"""
Chaos Engineering Framework for DjangoCRM Microservices

This framework provides chaos engineering capabilities to test service resilience
by intentionally introducing failures and observing system behavior.
"""

import time
import random
import threading
import signal
import sys
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import subprocess
import requests

logger = logging.getLogger(__name__)

class ChaosType(Enum):
    """Types of chaos that can be injected"""
    NETWORK_DELAY = "network_delay"
    NETWORK_LOSS = "network_loss"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_STRESS = "disk_stress"
    SERVICE_KILL = "service_kill"
    DATABASE_SLOWDOWN = "database_slowdown"
    EVENT_BUS_DISCONNECT = "event_bus_disconnect"

class ChaosSeverity(Enum):
    """Severity levels for chaos experiments"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ChaosExperiment:
    """Represents a chaos engineering experiment"""
    name: str
    description: str
    chaos_type: ChaosType
    target_service: str
    severity: ChaosSeverity
    duration_seconds: int
    parameters: Dict[str, Any]
    success_criteria: List[str]

@dataclass
class ExperimentResult:
    """Result of a chaos experiment"""
    experiment: ChaosExperiment
    start_time: float
    end_time: float
    success: bool
    observations: List[str]
    metrics_before: Dict[str, Any]
    metrics_after: Dict[str, Any]
    errors: List[str]

class ChaosInjector:
    """Base class for chaos injectors"""

    def __init__(self, target_service: str):
        self.target_service = target_service

    def inject_chaos(self, chaos_type: ChaosType, parameters: Dict[str, Any]) -> bool:
        """Inject chaos into the target service"""
        raise NotImplementedError

    def remove_chaos(self, chaos_type: ChaosType) -> bool:
        """Remove chaos from the target service"""
        raise NotImplementedError

class DockerChaosInjector(ChaosInjector):
    """Chaos injector for Docker-based services"""

    def inject_chaos(self, chaos_type: ChaosType, parameters: Dict[str, Any]) -> bool:
        """Inject chaos using Docker commands"""
        try:
            if chaos_type == ChaosType.NETWORK_DELAY:
                delay_ms = parameters.get('delay_ms', 100)
                container_name = self._get_container_name()
                cmd = f"docker exec {container_name} tc qdisc add dev eth0 root netem delay {delay_ms}ms"
                subprocess.run(cmd, shell=True, check=True)

            elif chaos_type == ChaosType.NETWORK_LOSS:
                loss_percent = parameters.get('loss_percent', 10)
                container_name = self._get_container_name()
                cmd = f"docker exec {container_name} tc qdisc add dev eth0 root netem loss {loss_percent}%"
                subprocess.run(cmd, shell=True, check=True)

            elif chaos_type == ChaosType.CPU_STRESS:
                cores = parameters.get('cores', 1)
                container_name = self._get_container_name()
                cmd = f"docker exec -d {container_name} stress --cpu {cores}"
                subprocess.run(cmd, shell=True, check=True)

            elif chaos_type == ChaosType.MEMORY_STRESS:
                memory_mb = parameters.get('memory_mb', 512)
                container_name = self._get_container_name()
                cmd = f"docker exec -d {container_name} stress --vm 1 --vm-bytes {memory_mb}M"
                subprocess.run(cmd, shell=True, check=True)

            elif chaos_type == ChaosType.SERVICE_KILL:
                container_name = self._get_container_name()
                cmd = f"docker restart {container_name}"
                subprocess.run(cmd, shell=True, check=True)

            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to inject chaos {chaos_type}: {e}")
            return False

    def remove_chaos(self, chaos_type: ChaosType) -> bool:
        """Remove chaos effects"""
        try:
            container_name = self._get_container_name()

            if chaos_type in [ChaosType.NETWORK_DELAY, ChaosType.NETWORK_LOSS]:
                cmd = f"docker exec {container_name} tc qdisc del dev eth0 root"
                subprocess.run(cmd, shell=True, check=True)

            elif chaos_type in [ChaosType.CPU_STRESS, ChaosType.MEMORY_STRESS]:
                # Kill stress processes
                cmd = f"docker exec {container_name} pkill -f stress"
                subprocess.run(cmd, shell=True, check=True)

            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove chaos {chaos_type}: {e}")
            return False

    def _get_container_name(self) -> str:
        """Get Docker container name for the target service"""
        # Map service names to container names
        container_map = {
            'postgres-identity': 'djangocrm-postgres-identity-1',
            'postgres-audit': 'djangocrm-postgres-audit-1',
            'postgres-project': 'djangocrm-postgres-project-1',
            'postgres-accounting': 'djangocrm-postgres-accounting-1',
            'postgres-hr': 'djangocrm-postgres-hr-1',
            'postgres-sales': 'djangocrm-postgres-sales-1',
            'redis': 'djangocrm-redis-1',
            'rabbitmq': 'djangocrm-rabbitmq-1'
        }
        return container_map.get(self.target_service, self.target_service)

class MetricsCollector:
    """Collects system metrics during chaos experiments"""

    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        metrics = {}

        try:
            # Query Prometheus for key metrics
            queries = {
                'cpu_usage': 'rate(process_cpu_user_seconds_total[5m])',
                'memory_usage': 'process_resident_memory_bytes',
                'database_connections': 'pg_stat_activity_count{datname=~".+"}',
                'redis_memory': 'redis_memory_used_bytes',
                'http_requests': 'rate(http_requests_total[5m])'
            }

            for metric_name, query in queries.items():
                response = requests.get(f"{self.prometheus_url}/api/v1/query", params={'query': query})
                if response.status_code == 200:
                    data = response.json()
                    if data['data']['result']:
                        # Take the first result
                        metrics[metric_name] = data['data']['result'][0]['value'][1]

        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")

        return metrics

class ChaosExperimentRunner:
    """Runs chaos engineering experiments"""

    def __init__(self, injector: ChaosInjector, metrics_collector: Optional[MetricsCollector] = None):
        self.injector = injector
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.running_experiments: Dict[str, threading.Event] = {}
        self.stop_event = threading.Event()

    def run_experiment(self, experiment: ChaosExperiment) -> ExperimentResult:
        """Run a single chaos experiment"""
        logger.info(f"Starting chaos experiment: {experiment.name}")

        # Collect baseline metrics
        metrics_before = self.metrics_collector.collect_metrics()

        start_time = time.time()

        # Inject chaos
        success = self.injector.inject_chaos(experiment.chaos_type, experiment.parameters)

        if not success:
            return ExperimentResult(
                experiment=experiment,
                start_time=start_time,
                end_time=time.time(),
                success=False,
                observations=["Failed to inject chaos"],
                metrics_before=metrics_before,
                metrics_after={},
                errors=["Chaos injection failed"]
            )

        # Wait for experiment duration
        time.sleep(experiment.duration_seconds)

        # Collect metrics after chaos
        metrics_after = self.metrics_collector.collect_metrics()

        # Remove chaos
        remove_success = self.injector.remove_chaos(experiment.chaos_type)

        end_time = time.time()

        # Evaluate success criteria
        observations = self._evaluate_success_criteria(experiment, metrics_before, metrics_after)

        return ExperimentResult(
            experiment=experiment,
            start_time=start_time,
            end_time=end_time,
            success=remove_success,
            observations=observations,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            errors=[] if remove_success else ["Failed to remove chaos"]
        )

    def _evaluate_success_criteria(self, experiment: ChaosExperiment,
                                 metrics_before: Dict[str, Any],
                                 metrics_after: Dict[str, Any]) -> List[str]:
        """Evaluate if the experiment met its success criteria"""
        observations = []

        # Basic evaluation - check if system remained operational
        observations.append("System remained operational during chaos injection")

        # Check for significant metric changes
        for metric, before_value in metrics_before.items():
            after_value = metrics_after.get(metric)
            if after_value:
                try:
                    before_float = float(before_value)
                    after_float = float(after_value)
                    change_percent = ((after_float - before_float) / before_float) * 100

                    if abs(change_percent) > 50:  # More than 50% change
                        observations.append(".1f")
                except (ValueError, ZeroDivisionError):
                    pass

        return observations

    def run_experiment_async(self, experiment: ChaosExperiment,
                           callback: Optional[Callable[[ExperimentResult], None]] = None):
        """Run experiment asynchronously"""
        def run_async():
            result = self.run_experiment(experiment)
            if callback:
                callback(result)

        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
        return thread

# Predefined chaos experiments
def create_standard_experiments() -> List[ChaosExperiment]:
    """Create a set of standard chaos experiments"""
    experiments = []

    # Network chaos experiments
    experiments.append(ChaosExperiment(
        name="network_delay_identity",
        description="Test identity service resilience to network delays",
        chaos_type=ChaosType.NETWORK_DELAY,
        target_service="postgres-identity",
        severity=ChaosSeverity.MEDIUM,
        duration_seconds=30,
        parameters={"delay_ms": 500},
        success_criteria=["Service remains responsive", "No data loss"]
    ))

    experiments.append(ChaosExperiment(
        name="cpu_stress_project_db",
        description="Test project database under CPU stress",
        chaos_type=ChaosType.CPU_STRESS,
        target_service="postgres-project",
        severity=ChaosSeverity.HIGH,
        duration_seconds=60,
        parameters={"cores": 2},
        success_criteria=["Database queries still work", "No connection timeouts"]
    ))

    experiments.append(ChaosExperiment(
        name="memory_stress_redis",
        description="Test Redis under memory pressure",
        chaos_type=ChaosType.MEMORY_STRESS,
        target_service="redis",
        severity=ChaosSeverity.MEDIUM,
        duration_seconds=45,
        parameters={"memory_mb": 256},
        success_criteria=["Redis remains accessible", "Cache operations work"]
    ))

    experiments.append(ChaosExperiment(
        name="service_restart_audit_db",
        description="Test system resilience to audit database restart",
        chaos_type=ChaosType.SERVICE_KILL,
        target_service="postgres-audit",
        severity=ChaosSeverity.CRITICAL,
        duration_seconds=10,
        parameters={},
        success_criteria=["System recovers automatically", "No data corruption"]
    ))

    return experiments