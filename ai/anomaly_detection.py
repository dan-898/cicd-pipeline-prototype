"""
CI/CD Pipeline - AI Anomaly Detection
Analyseert build-logs op afwijkingen met Isolation Forest.
"""

import json
import sys
import os
from datetime import datetime


def load_history(path="builds_history.json"):
    """Laad de buildhistorie uit het JSON-bestand."""
    if not os.path.exists(path):
        return {"builds": []}
    with open(path, "r") as f:
        return json.load(f)


def save_history(history, path="builds_history.json"):
    """Sla de bijgewerkte buildhistorie op."""
    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def extract_features(build_data):
    """Zet builddata om naar feature-vector voor het ML-model."""
    return [
        build_data.get("duration_seconds", 0),
        build_data.get("test_failures", 0),
        build_data.get("log_size_bytes", 0),
        build_data.get("files_changed", 0),
    ]


def detect_anomaly(current_build, history):
    """
    Detecteer of de huidige build afwijkend is.
    Gebruikt Isolation Forest als voldoende history beschikbaar is,
    anders een eenvoudige drempelwaarde-check.
    """
    builds = history.get("builds", [])

    print(f"Huidige build data: {current_build}")
    print(f"Beschikbare buildhistorie: {len(builds)} builds")

    if len(builds) < 5:
        print("Te weinig buildhistorie voor ML-model.")
        print("Drempelwaarde-check wordt gebruikt.")
        return simple_threshold_check(current_build)

    try:
        from sklearn.ensemble import IsolationForest
        import numpy as np

        X = np.array([extract_features(b) for b in builds])
        current = np.array([extract_features(current_build)])

        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X)

        prediction = model.predict(current)[0]
        score = model.score_samples(current)[0]
        is_anomaly = prediction == -1
        confidence = abs(score)

        print(f"Isolation Forest: {'ANOMALIE' if is_anomaly else 'Normaal'}")
        print(f"Score: {score:.4f} | Confidence: {confidence:.2%}")

        return {
            "is_anomaly": is_anomaly,
            "method": "isolation_forest",
            "score": float(score),
            "confidence": float(confidence)
        }

    except ImportError:
        print("scikit-learn niet beschikbaar, gebruik drempelwaarde-check.")
        return simple_threshold_check(current_build)


def simple_threshold_check(build_data):
    """Eenvoudige drempelwaarde-check als fallback."""
    is_anomaly = False
    reasons = []

    if build_data.get("duration_seconds", 0) > 300:
        is_anomaly = True
        reasons.append("Build duurde langer dan 5 minuten")

    if build_data.get("test_failures", 0) > 0:
        is_anomaly = True
        reasons.append(f"{build_data['test_failures']} tests gefaald")

    if build_data.get("log_size_bytes", 0) > 1_000_000:
        is_anomaly = True
        reasons.append("Log ongewoon groot")

    return {
        "is_anomaly": is_anomaly,
        "method": "threshold",
        "reasons": reasons,
        "score": -1.0 if is_anomaly else 1.0,
        "confidence": 0.9 if is_anomaly else 0.5
    }


def main():
    """Hoofdfunctie: analyseer de huidige build."""
    current_build = {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": int(os.environ.get("BUILD_DURATION", 60)),
        "test_failures": int(os.environ.get("TEST_FAILURES", 0)),
        "log_size_bytes": int(os.environ.get("LOG_SIZE_BYTES", 10000)),
        "files_changed": int(os.environ.get("FILES_CHANGED", 1)),
        "build_number": os.environ.get("BUILD_NUMBER", "0"),
    }

    history = load_history()
    result = detect_anomaly(current_build, history)

    current_build["anomaly_result"] = result
    history["builds"].append(current_build)
    save_history(history)

    print("\n" + "=" * 50)
    print("AI ANOMALY DETECTION RESULTAAT")
    print("=" * 50)

    if result["is_anomaly"]:
        print("STATUS: ANOMALIE GEDETECTEERD")
        if "reasons" in result:
            for r in result["reasons"]:
                print(f"Reden: {r}")
        print("ACTIE: Pipeline stopt - rollback wordt gestart.")
        sys.exit(1)
    else:
        print("STATUS: Normaal - geen anomalieën gevonden")
        print("ACTIE: Deployment gaat door.")
        sys.exit(0)


if __name__ == "__main__":
    main()