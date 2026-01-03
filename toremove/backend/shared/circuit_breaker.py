import time
import logging
import threading
from typing import Callable, Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"

@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    last_failure_time: Optional[float] = None
    state_changes: int = 0

class CircuitBreaker:
    """Circuit breaker pattern for resilient service-to-service communication"""

    def __init__(self, service_name: str, failure_threshold: int = 5, timeout: int = 60,
                 success_threshold: int = 3, monitoring_enabled: bool = True):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold  # Successes needed to close from half-open
        self.monitoring_enabled = monitoring_enabled

        # State management
        self._state = CircuitBreakerState.CLOSED
        self._lock = threading.Lock()
        self._half_open_success_count = 0

        # Metrics
        self.metrics = CircuitBreakerMetrics()

        logger.info(f"Initialized circuit breaker for {service_name} "
                   f"(threshold: {failure_threshold}, timeout: {timeout}s)")

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        with self._lock:
            return self._state

    def call(self, func: Callable) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self._state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._set_state(CircuitBreakerState.HALF_OPEN)
                    logger.info(f"Circuit breaker for {self.service_name} entering half-open state")
                else:
                    self._record_call(success=False)
                    raise CircuitBreakerOpenError(f"Circuit breaker open for {self.service_name}")

        try:
            result = func()
            self._record_call(success=True)
            return result
        except Exception as e:
            self._record_call(success=False)
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.metrics.last_failure_time is None:
            return True
        return time.time() - self.metrics.last_failure_time > self.timeout

    def _record_call(self, success: bool):
        """Record call metrics and update state"""
        with self._lock:
            self.metrics.total_calls += 1

            if success:
                self.metrics.successful_calls += 1
                self.metrics.consecutive_failures = 0

                if self._state == CircuitBreakerState.HALF_OPEN:
                    self._half_open_success_count += 1
                    if self._half_open_success_count >= self.success_threshold:
                        self._set_state(CircuitBreakerState.CLOSED)
                        self._half_open_success_count = 0
                        logger.info(f"Circuit breaker for {self.service_name} closed after successful calls")
            else:
                self.metrics.failed_calls += 1
                self.metrics.consecutive_failures += 1
                self.metrics.last_failure_time = time.time()

                if self._state == CircuitBreakerState.HALF_OPEN:
                    self._set_state(CircuitBreakerState.OPEN)
                    self._half_open_success_count = 0
                    logger.warning(f"Circuit breaker for {self.service_name} reopened due to failure in half-open state")
                elif (self._state == CircuitBreakerState.CLOSED and
                      self.metrics.consecutive_failures >= self.failure_threshold):
                    self._set_state(CircuitBreakerState.OPEN)
                    logger.warning(f"Circuit breaker for {self.service_name} opened after {self.metrics.consecutive_failures} consecutive failures")

    def _set_state(self, new_state: CircuitBreakerState):
        """Set circuit breaker state with logging"""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            self.metrics.state_changes += 1
            logger.info(f"Circuit breaker for {self.service_name} state changed: {old_state.value} -> {new_state.value}")

    def reset(self):
        """Manually reset the circuit breaker"""
        with self._lock:
            self._set_state(CircuitBreakerState.CLOSED)
            self.metrics = CircuitBreakerMetrics()
            self._half_open_success_count = 0
            logger.info(f"Circuit breaker for {self.service_name} manually reset")

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        with self._lock:
            return {
                'service_name': self.service_name,
                'state': self._state.value,
                'total_calls': self.metrics.total_calls,
                'successful_calls': self.metrics.successful_calls,
                'failed_calls': self.metrics.failed_calls,
                'consecutive_failures': self.metrics.consecutive_failures,
                'success_rate': (self.metrics.successful_calls / self.metrics.total_calls * 100) if self.metrics.total_calls > 0 else 0,
                'last_failure_time': self.metrics.last_failure_time,
                'state_changes': self.metrics.state_changes,
                'failure_threshold': self.failure_threshold,
                'timeout': self.timeout,
            }

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass