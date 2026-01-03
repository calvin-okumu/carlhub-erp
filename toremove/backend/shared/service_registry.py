"""
Service Registry for Microservices Architecture

This module provides service discovery and registration capabilities.
"""

import json
import time
import threading
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class ServiceInstance:
    """Represents a service instance"""
    service_name: str
    instance_id: str
    host: str
    port: int
    health_check_url: Optional[str] = None
    metadata: Dict[str, Any] = None
    registered_at: float = None
    last_heartbeat: float = None
    status: str = "up"  # up, down, unknown

    def __post_init__(self):
        if self.registered_at is None:
            self.registered_at = time.time()
        if self.last_heartbeat is None:
            self.last_heartbeat = time.time()
        if self.metadata is None:
            self.metadata = {}

    @property
    def base_url(self) -> str:
        """Get the base URL for this service instance"""
        return f"http://{self.host}:{self.port}"

    @property
    def is_healthy(self) -> bool:
        """Check if service instance is healthy"""
        return self.status == "up"

    def update_heartbeat(self):
        """Update the last heartbeat timestamp"""
        self.last_heartbeat = time.time()

    def mark_down(self):
        """Mark service instance as down"""
        self.status = "down"
        logger.warning(f"Service instance {self.service_name}:{self.instance_id} marked as down")

class ServiceRegistry:
    """Centralized service registry for service discovery"""

    def __init__(self, cleanup_interval: int = 60):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self._lock = threading.Lock()
        self.cleanup_interval = cleanup_interval
        self._cleanup_thread = None
        self._running = False

    def start(self):
        """Start the service registry"""
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        logger.info("Service registry started")

    def stop(self):
        """Stop the service registry"""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join()
        logger.info("Service registry stopped")

    def register_service(self, instance: ServiceInstance) -> bool:
        """Register a service instance"""
        with self._lock:
            if instance.service_name not in self.services:
                self.services[instance.service_name] = []

            # Check if instance already exists
            existing = next(
                (inst for inst in self.services[instance.service_name]
                 if inst.instance_id == instance.instance_id),
                None
            )

            if existing:
                # Update existing instance
                existing.host = instance.host
                existing.port = instance.port
                existing.health_check_url = instance.health_check_url
                existing.metadata.update(instance.metadata)
                existing.update_heartbeat()
                existing.status = "up"
                logger.info(f"Updated service instance: {instance.service_name}:{instance.instance_id}")
            else:
                # Add new instance
                self.services[instance.service_name].append(instance)
                logger.info(f"Registered new service instance: {instance.service_name}:{instance.instance_id}")

            return True

    def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """Deregister a service instance"""
        with self._lock:
            if service_name in self.services:
                original_length = len(self.services[service_name])
                self.services[service_name] = [
                    inst for inst in self.services[service_name]
                    if inst.instance_id != instance_id
                ]

                if len(self.services[service_name]) < original_length:
                    logger.info(f"Deregistered service instance: {service_name}:{instance_id}")
                    return True

            return False

    def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """Get all healthy instances of a service"""
        with self._lock:
            instances = self.services.get(service_name, [])
            return [inst for inst in instances if inst.is_healthy]

    def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
        """Get all registered services"""
        with self._lock:
            return dict(self.services)

    def heartbeat(self, service_name: str, instance_id: str) -> bool:
        """Update heartbeat for a service instance"""
        with self._lock:
            if service_name in self.services:
                for instance in self.services[service_name]:
                    if instance.instance_id == instance_id:
                        instance.update_heartbeat()
                        return True
            return False

    def _cleanup_loop(self):
        """Background cleanup of stale service instances"""
        while self._running:
            try:
                self._cleanup_stale_instances()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def _cleanup_stale_instances(self):
        """Remove stale service instances"""
        stale_threshold = time.time() - (self.cleanup_interval * 3)  # 3x cleanup interval

        with self._lock:
            for service_name, instances in self.services.items():
                original_count = len(instances)
                healthy_instances = []

                for instance in instances:
                    if instance.last_heartbeat > stale_threshold:
                        healthy_instances.append(instance)
                    else:
                        instance.mark_down()
                        logger.warning(f"Removed stale service instance: {service_name}:{instance.instance_id}")

                self.services[service_name] = healthy_instances

                if len(healthy_instances) != original_count:
                    logger.info(f"Cleaned up {original_count - len(healthy_instances)} stale instances for {service_name}")

# Global service registry instance
service_registry = ServiceRegistry()

# Service discovery client
class ServiceDiscoveryClient:
    """Client for service discovery"""

    def __init__(self, registry: ServiceRegistry = None):
        self.registry = registry or service_registry

    def discover_service(self, service_name: str) -> Optional[ServiceInstance]:
        """Discover a healthy service instance using round-robin"""
        instances = self.registry.get_service_instances(service_name)
        if not instances:
            return None

        # Simple round-robin (in production, use more sophisticated load balancing)
        if hasattr(self, '_last_index'):
            self._last_index[service_name] = (self._last_index.get(service_name, 0) + 1) % len(instances)
        else:
            self._last_index = {service_name: 0}

        return instances[self._last_index[service_name]]

    def get_service_url(self, service_name: str, path: str = "") -> Optional[str]:
        """Get the full URL for a service endpoint"""
        instance = self.discover_service(service_name)
        if instance:
            return f"{instance.base_url}{path}"
        return None

# Service registration helper
def register_service(service_name: str, host: str, port: int,
                    instance_id: str = None, health_check_url: str = None,
                    metadata: Dict[str, Any] = None) -> ServiceInstance:
    """Helper function to register a service"""
    if instance_id is None:
        instance_id = f"{service_name}-{host}:{port}"

    instance = ServiceInstance(
        service_name=service_name,
        instance_id=instance_id,
        host=host,
        port=port,
        health_check_url=health_check_url,
        metadata=metadata or {}
    )

    service_registry.register_service(instance)
    return instance

# Service heartbeat helper
def send_heartbeat(service_name: str, instance_id: str):
    """Send heartbeat for a service instance"""
    service_registry.heartbeat(service_name, instance_id)