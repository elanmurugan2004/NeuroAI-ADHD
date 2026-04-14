from typing import List
import pandas as pd

from ml.model_loader import load_ensemble_models


def _get_expected_columns(meta, preprocessor) -> List[str]:
    numeric_cols = list(meta.get("numeric_cols", [])) if isinstance(meta, dict) else []
    categorical_cols = list(meta.get("categorical_cols", [])) if isinstance(meta, dict) else []

    if numeric_cols or categorical_cols:
        return numeric_cols + categorical_cols

    if hasattr(preprocessor, "feature_names_in_"):
        return list(preprocessor.feature_names_in_)

    raise ValueError("Could not determine expected input columns for ensemble models.")


def _prepare_input_dataframe(X_df: pd.DataFrame, meta, preprocessor) -> pd.DataFrame:
    if X_df is None or X_df.empty:
        raise ValueError("Prediction input DataFrame is empty.")

    X_df = X_df.copy()

    expected_cols = _get_expected_columns(meta, preprocessor)
    numeric_cols = set(meta.get("numeric_cols", [])) if isinstance(meta, dict) else set()
    categorical_cols = set(meta.get("categorical_cols", [])) if isinstance(meta, dict) else set()

    if not numeric_cols and not categorical_cols:
        for col in expected_cols:
            if col.startswith("conn_") or col in {"age", "iq"}:
                numeric_cols.add(col)
            else:
                categorical_cols.add(col)

    missing_numeric = [col for col in expected_cols if col not in X_df.columns and col in numeric_cols]
    missing_categorical = [col for col in expected_cols if col not in X_df.columns and col in categorical_cols]

    frames = [X_df]

    if missing_numeric:
        frames.append(pd.DataFrame(0.0, index=X_df.index, columns=missing_numeric))

    if missing_categorical:
        frames.append(pd.DataFrame("Unknown", index=X_df.index, columns=missing_categorical))

    X_df = pd.concat(frames, axis=1)

    for col in expected_cols:
        if col in numeric_cols:
            X_df[col] = pd.to_numeric(X_df[col], errors="coerce")
        else:
            X_df[col] = X_df[col].astype(str)

    X_df = X_df[expected_cols].copy()
    return X_df


def predict_adhd_ensemble(X_df: pd.DataFrame):
    bilstm, transformer, preprocessor, meta = load_ensemble_models()

    X_df = _prepare_input_dataframe(X_df, meta, preprocessor)

    X = preprocessor.transform(X_df)

    if hasattr(X, "toarray"):
        X = X.toarray()

    n_features = X.shape[1]
    if n_features <= 0:
        raise ValueError("Preprocessed feature count is zero.")

    X = X.reshape(X.shape[0], n_features, 1)

    bilstm_prob = float(bilstm.predict(X, verbose=0)[0][0])
    transformer_prob = float(transformer.predict(X, verbose=0)[0][0])

    final_prob = (bilstm_prob + transformer_prob) / 2.0

    predicted_label = "ADHD" if final_prob >= 0.5 else "Control"
    confidence = round(max(final_prob, 1 - final_prob) * 100, 2)

    return {
        "adhd_score": round(final_prob, 4),
        "control_probability": round(1 - final_prob, 4),
        "predicted_label": predicted_label,
        "confidence": confidence,
        "bilstm_probability": round(bilstm_prob, 4),
        "transformer_probability": round(transformer_prob, 4),
    }