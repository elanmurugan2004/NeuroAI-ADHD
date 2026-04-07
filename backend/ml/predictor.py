from ml.model_loader import load_multimodal_model


def predict_adhd_multimodal(X):
    pipeline, meta = load_multimodal_model()

    proba = pipeline.predict_proba(X)[0, 1]
    pred = int(proba >= 0.5)

    label = "ADHD" if pred == 1 else "Control"
    confidence = round(max(proba, 1 - proba) * 100, 2)

    return {
        "adhd_score": round(float(proba), 4),
        "predicted_label": label,
        "confidence": confidence,
        "control_probability": round(float(1 - proba), 4),
    }