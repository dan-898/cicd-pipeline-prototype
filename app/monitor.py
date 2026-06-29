"""
System Health Monitor
Controleert CPU-gebruik, schijfruimte en geheugen.
"""

import psutil


def get_cpu_usage():
    """Geeft het huidige CPU-gebruik terug als percentage (0-100)."""
    return psutil.cpu_percent(interval=1)


def get_disk_usage(path="/"):
    """Geeft schijfgebruik terug als percentage."""
    usage = psutil.disk_usage(path)
    return round((usage.used / usage.total) * 100, 2)


def get_memory_usage():
    """Geeft geheugengebruik terug als percentage."""
    memory = psutil.virtual_memory()
    return round(memory.percent, 2)


def check_system_health():
    """
    Controleert de algehele systeemgezondheid.
    Geeft een dict terug met status per component.
    """
    cpu = get_cpu_usage()
    disk = get_disk_usage()
    memory = get_memory_usage()

    health = {
        "cpu_percent": cpu,
        "disk_percent": disk,
        "memory_percent": memory,
        "status": "healthy"
    }

    warnings = []
    if cpu > 90:
        warnings.append("CPU-gebruik kritiek hoog")
    if disk > 85:
        warnings.append("Schijfruimte bijna vol")
    if memory > 90:
        warnings.append("Geheugengebruik kritiek hoog")

    if warnings:
        health["status"] = "warning"
        health["warnings"] = warnings

    return health


def is_healthy(health_data):
    """Geeft True terug als het systeem gezond is."""
    return health_data.get("status") == "healthy"


if __name__ == "__main__":
    result = check_system_health()
    print(f"Systeemstatus: {result['status']}")
    print(f"CPU: {result['cpu_percent']}%")
    print(f"Schijf: {result['disk_percent']}%")
    print(f"Geheugen: {result['memory_percent']}%")
    if "warnings" in result:
        for w in result["warnings"]:
            print(f"WAARSCHUWING: {w}")
