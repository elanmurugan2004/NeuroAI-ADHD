import numpy as np
import pandas as pd

from ml.model_loader import load_ensemble_models


def _safe_list(value):
    if value is None:
        return []
    return [str(x) for x in value]


def _prepare_input_dataframe(X_df: pd.DataFrame, meta: dict) -> pd.DataFrame:
    if X_df is None or len(X_df) == 0:
        raise ValueError("Input dataframe is empty.")

    X_df = X_df.copy()
    X_df.columns = [str(c) for c in X_df.columns]

    phenotype_cols = _safe_list(meta.get("phenotype_cols"))
    selected_conn_cols = _safe_list(meta.get("selected_conn_cols"))
    feature_cols = _safe_list(meta.get("feature_cols"))

    if not feature_cols:
        feature_cols = phenotype_cols + selected_conn_cols

    if not feature_cols:
        raise ValueError("No feature columns found in ensemble metadata.")

    categorical_cols = set(_safe_list(meta.get("categorical_cols")))
    numeric_cols = set(_safe_list(meta.get("numeric_cols")))

    # Add missing columns in one shot to avoid dataframe fragmentation warnings
    missing_data = {}
    for col in feature_cols:
        if col not in X_df.columns:
            if col.startswith("conn_"):
                missing_data[col] = 0.0
            elif col in categorical_cols:
                missing_data[col] = np.nan
            else:
                missing_data[col] = np.nan

    if missing_data:
        X_df = pd.concat([X_df, pd.DataFrame([missing_data])], axis=1)

    # Keep only training-time columns and same order
    X_df = X_df.reindex(columns=feature_cols)

    # Convert numeric columns safely
    for col in feature_cols:
        if col.startswith("conn_") or col in numeric_cols or col in {"age", "iq"}:
            X_df[col] = pd.to_numeric(X_df[col], errors="coerce")

    return X_df


def predict_adhd_ensemble(X_df: pd.DataFrame):
    bilstm, transformer, preprocessor, meta = load_ensemble_models()

    X_ready = _prepare_input_dataframe(X_df, meta)

    X = preprocessor.transform(X_ready)

    if hasattr(X, "toarray"):
        X = X.toarray()

    X = np.asarray(X, dtype=np.float32)

    if X.ndim != 2:
        raise ValueError(f"Expected 2D transformed input, got shape {X.shape}")

    n_features = X.shape[1]
    X_seq = X.reshape(X.shape[0], n_features, 1)

    bilstm_probs = bilstm.predict(X_seq, verbose=0).ravel()
    transformer_probs = transformer.predict(X_seq, verbose=0).ravel()

    # simple average ensemble
    ensemble_probs = (bilstm_probs + transformer_probs) / 2.0

    final_prob = float(ensemble_probs[0])
    bilstm_prob = float(bilstm_probs[0])
    transformer_prob = float(transformer_probs[0])

    predicted_label = "ADHD" if final_prob >= 0.5 else "Control"
    confidence = round(max(final_prob, 1.0 - final_prob) * 100.0, 2)

    return {
        "adhd_score": round(final_prob, 4),
        "control_probability": round(1.0 - final_prob, 4),
        "predicted_label": predicted_label,
        "confidence": confidence,
        "bilstm_probability": round(bilstm_prob, 4),
        "transformer_probability": round(transformer_prob, 4),
    }