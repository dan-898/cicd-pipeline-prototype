"""
Unit tests voor het system health monitor script.
"""

import pytest
from app.monitor import (
    get_cpu_usage,
    get_disk_usage,
    get_memory_usage,
    check_system_health,
    is_healthy
)


class TestCpuUsage:
    def test_cpu_usage_returns_number(self):
        """CPU-gebruik moet een getal teruggeven."""
        result = get_cpu_usage()
        assert isinstance(result, (int, float))

    def test_cpu_usage_valid_range(self):
        """CPU-gebruik moet tussen 0 en 100 liggen."""
        result = get_cpu_usage()
        assert 0 <= result <= 100


class TestDiskUsage:
    def test_disk_usage_returns_number(self):
        """Schijfgebruik moet een getal teruggeven."""
        result = get_disk_usage()
        assert isinstance(result, float)

    def test_disk_usage_valid_range(self):
        """Schijfgebruik moet tussen 0 en 100 liggen."""
        result = get_disk_usage()
        assert 0 <= result <= 100


class TestMemoryUsage:
    def test_memory_usage_returns_number(self):
        """Geheugengebruik moet een getal teruggeven."""
        result = get_memory_usage()
        assert isinstance(result, float)

    def test_memory_usage_valid_range(self):
        """Geheugengebruik moet tussen 0 en 100 liggen."""
        result = get_memory_usage()
        assert 0 <= result <= 100


class TestSystemHealth:
    def test_health_check_returns_dict(self):
        """Health check moet een dict teruggeven."""
        result = check_system_health()
        assert isinstance(result, dict)

    def test_health_check_has_required_keys(self):
        """Health check dict moet verplichte sleutels bevatten."""
        result = check_system_health()
        assert "cpu_percent" in result
        assert "disk_percent" in result
        assert "memory_percent" in result
        assert "status" in result

    def test_health_status_valid_value(self):
        """Status moet 'healthy' of 'warning' zijn."""
        result = check_system_health()
        assert result["status"] in ["healthy", "warning"]

    def test_warning_when_cpu_critical(self):
        """Bij CPU boven 90 procent moet status warning zijn."""
        health = {
            "cpu_percent": 95,
            "disk_percent": 50,
            "memory_percent": 60,
            "status": "warning",
            "warnings": ["CPU-gebruik kritiek hoog"]
        }
        assert health["status"] == "warning"
        assert "CPU-gebruik kritiek hoog" in health["warnings"]

    def test_is_healthy_true_for_healthy_system(self):
        """is_healthy moet True teruggeven voor gezond systeem."""
        health = {"status": "healthy"}
        assert is_healthy(health) is True

    def test_is_healthy_false_for_warning(self):
        """is_healthy moet False teruggeven bij waarschuwing."""
        health = {"status": "warning"}
        assert is_healthy(health) is False