import numpy as np
from ml.model_loader import load_multimodal_model


def explain_multimodal_prediction(X):
    pipeline, meta = load_multimodal_model()

    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]

    try:
        X_transformed = preprocessor.transform(X)

        # convert sparse to dense if needed
        if hasattr(X_transformed, "toarray"):
            X_dense = X_transformed.toarray()
        else:
            X_dense = np.asarray(X_transformed)

        feature_names = preprocessor.get_feature_names_out()

        # Fallback explanation using feature importances × sample values
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            sample_vals = X_dense[0]

            pairs = []
            for name, imp, val in zip(feature_names, importances, sample_vals):
                score = float(imp) * float(abs(val))
                pairs.append((name, score))

            pairs = sorted(pairs, key=lambda x: abs(x[1]), reverse=True)[:8]

            return [
                {"feature": name, "impact": round(score, 4)}
                for name, score in pairs
            ]

        return [{"feature": "model_explanation", "impact": 0.0}]

    except Exception as e:
        return [
            {"feature": "explanation_fallback", "impact": 0.0},
            {"feature": f"reason: {str(e)}", "impact": 0.0},
        ]