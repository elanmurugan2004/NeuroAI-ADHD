import numpy as np
from collections import defaultdict
from ml.model_loader import load_multimodal_model


def clean_feature_name(name: str) -> str:
    if "__" in name:
        return name.split("__", 1)[1]
    return name


def shorten_region_name(name: str) -> str:
    name = str(name)
    replacements = {
        "Inferior Temporal Gyrus, temporooccipital part": "Inferior Temporal Gyrus",
        "Parahippocampal Gyrus, anterior division": "Parahippocampal Gyrus",
        "Parahippocampal Gyrus, posterior division": "Parahippocampal Gyrus",
        "Temporal Fusiform Cortex, anterior division": "Fusiform Cortex",
        "Temporal Fusiform Cortex, posterior division": "Fusiform Cortex",
        "Cingulate Gyrus, anterior division": "Cingulate Gyrus",
        "Cingulate Gyrus, posterior division": "Cingulate Gyrus",
    }
    return replacements.get(name, name)


def score_to_level(score: float) -> str:
    if score >= 3:
        return "High"
    if score >= 1:
        return "Moderate"
    return "Supportive"


def build_clinical_summary(top_regions):
    if not top_regions:
        return "AI-based region summary is not available for this scan."

    names = [r["name"] for r in top_regions[:3]]

    if len(names) >= 3:
        return (
            f"AI analysis of this uploaded scan highlights {names[0]}, {names[1]}, "
            f"and {names[2]} as the most influential regions for the current prediction."
        )
    if len(names) == 2:
        return (
            f"AI analysis of this uploaded scan highlights {names[0]} and {names[1]} "
            f"as the most influential regions for the current prediction."
        )
    return f"AI analysis of this uploaded scan highlights {names[0]} as the most influential region."


def build_recommendation(predicted_label: str, confidence: float) -> str:
    if confidence < 70:
        return "Low-confidence AI result. Specialist clinical review is recommended before final interpretation."
    if predicted_label == "ADHD":
        return "AI output suggests ADHD-related pattern support. Correlate with behavioral, clinical, and imaging review."
    return "AI output suggests control/non-ADHD pattern support. Correlate with clinical assessment before final decision."


def explain_multimodal_prediction(X, region_labels=None, connection_mapping=None, predicted_label=None, confidence=None):
    pipeline, meta = load_multimodal_model()

    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]

    try:
        X_transformed = preprocessor.transform(X)

        if hasattr(X_transformed, "toarray"):
            X_dense = X_transformed.toarray()
        else:
            X_dense = np.asarray(X_transformed)

        feature_names = preprocessor.get_feature_names_out()

        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            sample_vals = X_dense[0]

            raw_pairs = []
            for name, imp, val in zip(feature_names, importances, sample_vals):
                score = float(abs(imp) * abs(val))
                raw_pairs.append((name, score))

            raw_pairs = sorted(raw_pairs, key=lambda x: x[1], reverse=True)

            region_scores = defaultdict(float)

            for name, score in raw_pairs:
                cleaned = clean_feature_name(name)

                if cleaned.startswith("conn_") and region_labels is not None and connection_mapping is not None:
                    if cleaned in connection_mapping:
                        i, j = connection_mapping[cleaned]
                        if i < len(region_labels) and j < len(region_labels):
                            region_a = shorten_region_name(region_labels[i])
                            region_b = shorten_region_name(region_labels[j])
                            region_scores[region_a] += float(score)
                            region_scores[region_b] += float(score)

                elif cleaned == "age":
                    region_scores["Age"] += float(score)
                elif cleaned in ["sex", "gender", "gender_Male", "gender_Female"]:
                    region_scores["Gender"] += float(score)
                elif cleaned in ["iq", "fsiq"]:
                    region_scores["IQ"] += float(score)

            top_regions = []
            seen = set()
            for name, score in sorted(region_scores.items(), key=lambda x: x[1], reverse=True):
                short_name = shorten_region_name(name)
                if short_name in seen:
                    continue
                seen.add(short_name)
                top_regions.append({
                    "name": short_name,
                    "impact": round(score, 4),
                    "level": score_to_level(score)
                })
                if len(top_regions) == 3:
                    break

            clinical_summary = build_clinical_summary(top_regions)
            recommendation = build_recommendation(predicted_label or "", float(confidence or 0))

            return {
                "top_regions": top_regions,
                "clinical_summary": clinical_summary,
                "recommendation": recommendation
            }

        return {
            "top_regions": [],
            "clinical_summary": "AI-based region summary is not available for this scan.",
            "recommendation": "Clinical review is recommended."
        }

    except Exception:
        return {
            "top_regions": [],
            "clinical_summary": "AI-based region summary is not available for this scan.",
            "recommendation": "Clinical review is recommended."
        }